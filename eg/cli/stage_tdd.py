"""TDD stage: BDD authored as data -> rendered to docs/bdd; ledger/freeze/handoff
wrap the existing governance scripts (not reimplemented).

Transitional model (same as ADR): repo keeps docs/bdd/*.md so unrefactored
eg-enforce keeps parsing it. The agent authors BDD as data and `eg seal` renders.
The ledger stays JSON machine state; `eg freeze` / `eg govern` / `eg commit-check`
call the strong existing validators.
"""
from __future__ import annotations

import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import bdd_render
import bdd_rules
import mirror
import store

TMP_EG = Path("/tmp/eg")
SCRIPTS = Path(__file__).resolve().parents[2] / "eg-tdd/scripts"
NEW_GOV = SCRIPTS / "new-governance.py"
FREEZE = SCRIPTS / "freeze-enforce-plan.py"
GOVERN = SCRIPTS / "validate-governance.py"
COMMIT = SCRIPTS / "validate-commit-scope.py"

ENUMS: dict[tuple[str, str], set[str]] = {
    ("bdd", "status"): bdd_rules.STATUS,
    ("bdd", "kind"): bdd_rules.KIND,
    ("bdd", "test_surface"): bdd_rules.TEST_SURFACE,
}


def _slug_run(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    normalized = re.sub(r"-+", "-", normalized).strip("-._")
    if not normalized:
        raise SystemExit("value must contain at least one slug character")
    return normalized


def slug(value: str) -> str:
    # Keep unicode word chars (CJK survives); collapse the rest to '-'.
    text = re.sub(r"[^\w]+", "-", value.strip(), flags=re.UNICODE)
    text = text.lower() if text.isascii() else text
    return re.sub(r"-+", "-", text).strip("-_") or "bdd"


def resolve_run_dir(run: str) -> Path:
    p = Path(run)
    run_dir = p.resolve() if (p.is_absolute() or "/" in run) else (TMP_EG / run).resolve()
    if run_dir != TMP_EG and TMP_EG not in run_dir.parents:
        raise SystemExit(f"run dir must be under /tmp/eg: {run_dir}")
    return run_dir


def _meta(run_dir: Path) -> dict:
    return store.load(run_dir / "run.json")


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def _bdd_number(name: str) -> int:
    m = re.search(r"(\d{4})", name)
    if not m:
        raise SystemExit(f"bad bdd name {name!r}; expected bdd-NNNN")
    return int(m.group(1))


def artifact_path(run_dir: Path, name: str) -> Path:
    if name == "ledger":
        return run_dir / "ledger.json"
    if name.lower().startswith("bdd") or re.fullmatch(r"\d{4}", name):
        return run_dir / f"bdd-{_bdd_number(name):04d}.yml"
    raise SystemExit(f"unknown artifact {name!r}; use 'ledger' or 'bdd-NNNN'")


def merge_key(name: str) -> str:
    return "ledger" if name == "ledger" else "bdd"


# ---- new run + bdd-new ----------------------------------------------------

def new_run(repo_root: str, task: str, intent_adr: str, mode: str, run_id: str | None = None) -> Path:
    repo_abs = Path(repo_root).resolve()
    repo_name = repo_abs.name or "repo"
    cmd = [sys.executable, str(NEW_GOV), "--repo", repo_name, "--task", _slug_run(task),
           "--mode", mode, "--intent-adr", intent_adr]
    if run_id:
        cmd += ["--run-id", run_id]
    rc, out, err = _run(cmd)
    if rc != 0:
        raise SystemExit(err.strip() or "new-governance failed")
    ledger_path = Path(out.strip().splitlines()[-1])
    run_dir = ledger_path.parent
    store.dump(run_dir / "run.json", {
        "stage": "tdd",
        "run_id": run_dir.name,
        "task": _slug_run(task),
        "repo_root": str(repo_abs),
        "intent_adr": intent_adr,
        "allocated_bdds": [],
    })
    return run_dir


def _next_bdd_number(repo_root: Path, allocated: list[int]) -> int:
    highest = max(allocated) if allocated else 0
    bdd_dir = repo_root / "docs/bdd"
    if bdd_dir.is_dir():
        # match both eg (NNNN-) and legacy saler (BDD-NNNN-) during transition
        for path in list(bdd_dir.glob("*.md")) + list(bdd_dir.glob("*.yml")):
            m = re.match(r"^(?:BDD-)?(\d{4})", path.name)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1


def bdd_scaffold(bdd_id: str, derived_from: str, title: str, test_surface: str | None = None) -> dict:
    return {
        "schema": "eg-bdd/v1",
        "id": bdd_id,
        "status": "draft",
        "test_surface": test_surface,
        "derived_from": derived_from,
        "title": title,
        "slug": slug(title),
        "notes": "",
        "scenarios": [],
    }


def bdd_new(run_dir: Path, title: str, derived_from: str, test_surface: str | None = None) -> tuple[str, Path]:
    if not bdd_rules.ADR_ID_RE.match(derived_from or ""):
        raise SystemExit("--derived-from must be an intent ADR id (ADR-NNNN)")
    meta = _meta(run_dir)
    repo_root = Path(meta["repo_root"])
    allocated = list(meta.get("allocated_bdds", []))
    number = _next_bdd_number(repo_root, allocated)
    if test_surface is not None and test_surface not in bdd_rules.TEST_SURFACE:
        raise SystemExit(f"--test-surface must be one of {sorted(bdd_rules.TEST_SURFACE)}")
    bdd_id = f"BDD-{number:04d}"
    path = run_dir / f"bdd-{number:04d}.yml"
    store.dump(path, bdd_scaffold(bdd_id, derived_from, title, test_surface))
    allocated.append(number)
    meta["allocated_bdds"] = allocated
    store.dump(run_dir / "run.json", meta)
    return bdd_id, path


# ---- per-write validation -------------------------------------------------

def validate_written(name: str, data: Any) -> list[str]:
    key = merge_key(name)
    errors: list[str] = []

    def walk(node: Any, where: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                here = f"{where}.{k}" if where else k
                if isinstance(v, str) and store.is_sentinel(v):
                    errors.append(f"{here} is a placeholder ({v!r}); use a real value or 'defer: <reason>'")
                elif (key, k) in ENUMS and isinstance(v, str) and v.strip() and not store.is_deferred(v):
                    if v.strip() not in ENUMS[(key, k)]:
                        errors.append(f"{here} must be one of {sorted(ENUMS[(key, k)])}, got {v!r}")
                walk(v, here)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{where}[{i}]")

    walk(data, "")
    return errors


# ---- check / render / seal ------------------------------------------------

def _started_bdds(run_dir: Path) -> list[str]:
    return [f"bdd-{_bdd_number(p.name):04d}" for p in sorted(run_dir.glob("bdd-*.yml"))]


def _deferrals(run_dir: Path) -> list[str]:
    out: list[str] = []

    def walk(node: Any, where: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{where}.{k}" if where else k)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{where}[{i}]")
        elif store.is_deferred(node):
            out.append(f"{where}: {node}")

    for name in _started_bdds(run_dir):
        walk(store.load(artifact_path(run_dir, name)), name)
    return out


def _govern_errors(run_dir: Path, phase: str) -> list[str]:
    meta = _meta(run_dir)
    cmd = [sys.executable, str(GOVERN), str(run_dir / "ledger.json"),
           "--phase", phase, "--repo-root", meta["repo_root"]]
    rc, out, err = _run(cmd)
    if rc == 0:
        return []
    return [ln[len("ERROR: "):] if ln.startswith("ERROR: ") else ln
            for ln in err.splitlines() if ln.strip()]


def _check_bdd(run_dir: Path, name: str) -> list[str]:
    path = artifact_path(run_dir, name)
    if not path.exists():
        return [f"missing artifact: {path}"]
    return bdd_rules.validate_bdd(store.load(path), Path(_meta(run_dir)["repo_root"]))


def check_run(run_dir: Path, artifact: str | None = None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    if artifact == "ledger":
        errors = [f"ledger: {e}" for e in _govern_errors(run_dir, "planning")]
        return (errors, _deferrals(run_dir))
    if artifact:
        return ([f"{artifact}: {e}" for e in _check_bdd(run_dir, artifact)], _deferrals(run_dir))
    names = _started_bdds(run_dir)
    if not names:
        return (["no BDD created yet: eg bdd-new <run> --title ... --derived-from ADR-NNNN"], [])
    for name in names:
        errors += [f"{name}: {e}" for e in _check_bdd(run_dir, name)]
    return (errors, _deferrals(run_dir))


def render_run(run_dir: Path, artifact: str | None = None) -> Path:
    if not artifact or artifact == "ledger":
        raise SystemExit("tdd render needs a bdd artifact: bdd-NNNN")
    data = store.load(artifact_path(run_dir, artifact))
    out = run_dir / f"bdd-{_bdd_number(artifact):04d}.preview.md"
    out.write_text(bdd_render.render_bdd(data), encoding="utf-8")
    return out


def seal_run(run_dir: Path, artifact: str | None = None) -> list[str]:
    if not artifact:
        return ["tdd seal needs a bdd artifact: bdd-NNNN (ledger is sealed via eg freeze / eg govern)"]
    if artifact == "ledger":
        return ["ledger is not sealed; use eg freeze and eg govern --phase final --emit-handoff"]
    path = artifact_path(run_dir, artifact)
    if not path.exists():
        return [f"missing artifact: {path}"]
    data = store.load(path)
    errors = bdd_rules.validate_bdd(data, Path(_meta(run_dir)["repo_root"]))
    if errors:
        return [f"{artifact}: {e}" for e in errors]
    if data.get("status") == "approved":
        data["approved_by"] = "human"
        data.setdefault("approval_source", "chat-confirmation")
        data["approved_at"] = datetime.now(timezone.utc).isoformat()
        store.dump(path, data)
    # docs/bdd/NNNN-slug.yml is the committed source; .md is rendered + git-ignored.
    repo_root = Path(_meta(run_dir)["repo_root"])
    mirror.commit_doc(repo_root, "docs/bdd", f"{_bdd_number(artifact):04d}-{data['slug']}", data)
    return []


# ---- governance wrappers --------------------------------------------------

def freeze(run_dir: Path) -> tuple[int, str, str]:
    return _run([sys.executable, str(FREEZE), str(run_dir / "ledger.json")])


def govern(run_dir: Path, phase: str, emit_handoff: bool) -> tuple[int, str, str]:
    meta = _meta(run_dir)
    mirror.render_all(Path(meta["repo_root"]))  # legacy reader sees .md from committed data
    cmd = [sys.executable, str(GOVERN), str(run_dir / "ledger.json"),
           "--phase", phase, "--repo-root", meta["repo_root"]]
    if emit_handoff:
        handoff = Path(meta["repo_root"]) / ".eg/handoff" / f"{meta['run_id']}.yml"
        handoff.parent.mkdir(parents=True, exist_ok=True)
        cmd += ["--emit-handoff", str(handoff)]
    return _run(cmd)


def commit_check(run_dir: Path, handoff: str) -> tuple[int, str, str]:
    meta = _meta(run_dir)
    mirror.render_all(Path(meta["repo_root"]))
    return _run([sys.executable, str(COMMIT), "--repo-root", meta["repo_root"],
                 "--ledger", str(run_dir / "ledger.json"), "--handoff", handoff])


# ---- schema ---------------------------------------------------------------

def example(name: str) -> dict:
    if name != "bdd":
        raise SystemExit("tdd schema artifact: bdd  (ledger format is owned by new-governance.py)")
    data = bdd_scaffold("BDD-0001", "ADR-0001", "<feature title>")
    data["scenarios"] = [{
        "anchor": "scenario-<slug>", "title": "<scenario title>", "kind": "happy",
        "given": ["<precondition>"], "when": ["<action>"], "then": ["<observable outcome>"],
    }]
    return data
