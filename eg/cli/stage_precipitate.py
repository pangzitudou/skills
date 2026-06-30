"""Precipitation stage: author ADR/CONTEXT as data in /tmp, seal-render to repo.

Transitional model: the repo keeps the .md format eg-tdd/eg-enforce parse. The
agent authors structured data (merge/set); `eg seal <run> <artifact>` renders to
docs/adr/NNNN-slug.md (or CONTEXT.md) and refuses unless the data check AND the
original validate-precipitation.py both pass.
"""
from __future__ import annotations

import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mirror
import precip_render
import precip_rules
import store

TMP_EG = Path("/tmp/eg")
ORIG_VALIDATOR = Path(__file__).resolve().parents[2] / "eg-precipitate/scripts/validate-precipitation.py"

ENUMS: dict[tuple[str, str], set[str]] = {
    ("adr", "type"): precip_rules.TYPES,
    ("adr", "status"): precip_rules.STATUSES,
    ("adr", "domain"): precip_rules.DOMAINS,
}


def slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower())
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "adr"


def _slug_run(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    normalized = re.sub(r"-+", "-", normalized).strip("-._")
    if not normalized:
        raise SystemExit("task must contain at least one slug character")
    return normalized


def resolve_run_dir(run: str) -> Path:
    p = Path(run)
    run_dir = p.resolve() if (p.is_absolute() or "/" in run) else (TMP_EG / run).resolve()
    if run_dir != TMP_EG and TMP_EG not in run_dir.parents:
        raise SystemExit(f"run dir must be under /tmp/eg: {run_dir}")
    return run_dir


def _run_meta(run_dir: Path) -> dict:
    return store.load(run_dir / "run.json")


def _adr_number(name: str) -> int:
    m = re.search(r"(\d{4})", name)
    if not m:
        raise SystemExit(f"bad adr name {name!r}; expected adr-NNNN")
    return int(m.group(1))


def artifact_path(run_dir: Path, name: str) -> Path:
    if name == "context":
        return run_dir / "context.yml"
    if name.lower().startswith("adr") or re.fullmatch(r"\d{4}", name):
        return run_dir / f"adr-{_adr_number(name):04d}.yml"
    raise SystemExit(f"unknown artifact {name!r}; use 'context' or 'adr-NNNN'")


def merge_key(name: str) -> str:
    return "context" if name == "context" else "adr"


# ---- new run + adr-new ----------------------------------------------------

def new_run(repo_root: str, task: str, run_id: str | None = None) -> Path:
    task_s = _slug_run(task)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nonce = uuid.uuid4().hex[:8]
    rid = run_id or f"EG-RUN-{timestamp}-{task_s}-{nonce}"
    rid = _slug_run(rid)
    if not rid.startswith("EG-RUN-"):
        rid = f"EG-RUN-{rid}"
    run_dir = (TMP_EG / rid).resolve()
    if run_dir != TMP_EG and TMP_EG not in run_dir.parents:
        raise SystemExit("run dir must be under /tmp/eg")
    run_dir.mkdir(parents=True, exist_ok=False)

    repo_abs = str(Path(repo_root).resolve())
    store.dump(run_dir / "run.json", {
        "stage": "precipitate",
        "run_id": rid,
        "task": task_s,
        "repo_root": repo_abs,
        "allocated_adrs": [],
    })
    store.dump(run_dir / "context.yml", {
        "schema": "eg-context/v1",
        "name": None,
        "description": None,
        "terms": [],
    })
    return run_dir


def _next_adr_number(repo_root: Path, allocated: list[int]) -> int:
    highest = max(allocated) if allocated else 0
    adr_dir = repo_root / "docs/adr"
    if adr_dir.is_dir():
        for path in list(adr_dir.glob("*.md")) + list(adr_dir.glob("*.yml")):
            m = re.match(r"^(\d{4})-", path.name)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1


def adr_scaffold(adr_id: str, adr_type: str, status: str, title: str, domain: str | None) -> dict:
    data = {
        "schema": "eg-adr/v1",
        "id": adr_id,
        "type": adr_type,
        "status": status,
        "title": title,
        "slug": slug(title),
        "context": None,
        "decision": None,
        "consequences": "",
    }
    if adr_type == "constraint":
        data["domain"] = domain
    if adr_type == "intent":
        data["in_scope"] = []
        data["out_of_scope"] = []
        data["non_goals"] = []
        data["acceptance_seed"] = []
    return data


def adr_new(run_dir: Path, adr_type: str, title: str, status: str, domain: str | None) -> tuple[str, Path]:
    if adr_type not in precip_rules.TYPES:
        raise SystemExit(f"--type must be one of {sorted(precip_rules.TYPES)}")
    if status not in precip_rules.STATUSES:
        raise SystemExit(f"--status must be one of {sorted(precip_rules.STATUSES)}")
    if adr_type == "constraint" and domain not in precip_rules.DOMAINS:
        raise SystemExit(f"constraint --domain must be one of {sorted(precip_rules.DOMAINS)}")
    meta = _run_meta(run_dir)
    repo_root = Path(meta["repo_root"])
    allocated = list(meta.get("allocated_adrs", []))
    number = _next_adr_number(repo_root, allocated)
    adr_id = f"ADR-{number:04d}"
    path = run_dir / f"adr-{number:04d}.yml"
    store.dump(path, adr_scaffold(adr_id, adr_type, status, title, domain))
    allocated.append(number)
    meta["allocated_adrs"] = allocated
    store.dump(run_dir / "run.json", meta)
    return adr_id, path


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

def _context_started(data: dict) -> bool:
    return store.is_filled(data.get("name")) or store.is_filled(data.get("description")) or bool(data.get("terms"))


def _require_seed(adr: dict) -> bool:
    return adr.get("type") == "intent" and adr.get("status") == "approved"


def _check_artifact(run_dir: Path, name: str) -> list[str]:
    path = artifact_path(run_dir, name)
    if not path.exists():
        return [f"missing artifact: {path}"]
    data = store.load(path)
    if merge_key(name) == "context":
        return precip_rules.validate_context(data)
    return precip_rules.validate_adr(data, require_seed=_require_seed(data))


def _started_artifacts(run_dir: Path) -> list[str]:
    names: list[str] = []
    ctx = run_dir / "context.yml"
    if ctx.exists() and _context_started(store.load(ctx)):
        names.append("context")
    for p in sorted(run_dir.glob("adr-*.yml")):
        names.append(f"adr-{_adr_number(p.name):04d}")
    return names


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

    for name in _started_artifacts(run_dir):
        walk(store.load(artifact_path(run_dir, name)), name)
    return out


def check_run(run_dir: Path, artifact: str | None = None) -> tuple[list[str], list[str]]:
    names = [artifact] if artifact else _started_artifacts(run_dir)
    if not names:
        return (["nothing to check: no ADR created and CONTEXT untouched"], [])
    errors: list[str] = []
    for name in names:
        for e in _check_artifact(run_dir, name):
            errors.append(f"{name}: {e}")
    return (errors, _deferrals(run_dir))


def render_run(run_dir: Path, artifact: str | None = None) -> Path:
    """On-demand human preview into the run dir (does NOT touch the repo)."""
    if not artifact:
        raise SystemExit("precipitate render needs an artifact: context | adr-NNNN")
    data = store.load(artifact_path(run_dir, artifact))
    if merge_key(artifact) == "context":
        out = run_dir / "CONTEXT.preview.md"
        out.write_text(precip_render.render_context(data), encoding="utf-8")
    else:
        out = run_dir / f"adr-{_adr_number(artifact):04d}.preview.md"
        out.write_text(precip_render.render_adr(data), encoding="utf-8")
    return out


def seal_run(run_dir: Path, artifact: str | None = None) -> list[str]:
    if not artifact:
        return ["precipitate seal needs an artifact: context | adr-NNNN"]
    errors = _check_artifact(run_dir, artifact)
    if errors:
        return [f"{artifact}: {e}" for e in errors]
    meta = _run_meta(run_dir)
    repo_root = Path(meta["repo_root"])
    data = store.load(artifact_path(run_dir, artifact))

    if merge_key(artifact) == "context":
        # CONTEXT.yml is the committed source; CONTEXT.md is rendered + git-ignored.
        mirror.commit_doc(repo_root, "", "CONTEXT", data)
        return []

    # ADR: render -> stage -> original validator (compat gate on the rendered .md)
    number = _adr_number(artifact)
    staged = run_dir / f"{number:04d}-{data['slug']}.md"
    staged.write_text(precip_render.render_adr(data), encoding="utf-8")
    cmd = [sys.executable, str(ORIG_VALIDATOR), str(staged)]
    if _require_seed(data):
        cmd.append("--require-seed")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        lines = [ln for ln in proc.stderr.splitlines() if ln.strip()]
        return [f"{artifact}: rendered ADR failed original validator"] + [f"  {ln}" for ln in lines]
    # commit the data .yml (source of truth) + render the git-ignored .md
    mirror.commit_doc(repo_root, "docs/adr", f"{number:04d}-{data['slug']}", data)
    return []


# ---- schema ---------------------------------------------------------------

def example(name: str) -> dict:
    if name == "context":
        return {"schema": "eg-context/v1", "name": None, "description": None,
                "terms": [{"term": None, "definition": None, "avoid": []}]}
    kind = name.replace("adr-", "") if name.startswith("adr-") else name
    if kind not in precip_rules.TYPES:
        raise SystemExit("schema artifact: context | adr-intent | adr-decision | adr-constraint")
    return adr_scaffold("ADR-0001", kind, "review", "<title>", "security" if kind == "constraint" else None)
