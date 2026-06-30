"""Enforce stage: wrap the existing PR-gate scripts under one set of eg verbs.

enforce.py alone assigns enforcement level, next step, and gate — this module
never reimplements that. The new value is the findings guard (eg check) and a
single mental model: pr-context -> select -> (reviewers) -> enforce -> notify ->
fix-handoff. Authoring verbs (merge/set/seal) do not apply here.
"""
from __future__ import annotations

import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import findings_rules
import mirror
import store

TMP_EG = Path("/tmp/eg")
SKILL_DIR = Path(__file__).resolve().parents[2] / "eg-enforce"
SCRIPTS = SKILL_DIR / "scripts"
PROFILE = SKILL_DIR / "enforcement.default.yml"

PR_CONTEXT = SCRIPTS / "pr-context.sh"
SELECT_HANDOFFS = SCRIPTS / "select-handoffs.py"
SELECT_QUALITY = SCRIPTS / "select-quality-context.py"
ENFORCE = SCRIPTS / "enforce.py"
UPDATE_LEDGER = SCRIPTS / "update-finding-ledger.py"
NOTIFY = SCRIPTS / "notify.py"
WRITE_FIX = SCRIPTS / "write-fix-handoff.py"

FINDINGS = {"layer-a": "layer-a-findings.json", "layer-b": "layer-b-findings.json"}


def _slug_run(value: str) -> str:
    n = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    n = re.sub(r"-+", "-", n).strip("-._")
    if not n:
        raise SystemExit("value must contain a slug character")
    return n


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


# ---- new run + pipeline wrappers -------------------------------------------

def new_run(repo_root: str, repo: str, target: str, source: str | None, run_id: str | None = None) -> Path:
    task = _slug_run(repo or "pr")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rid = run_id or f"EG-RUN-{timestamp}-{task}-{uuid.uuid4().hex[:8]}"
    rid = _slug_run(rid)
    if not rid.startswith("EG-RUN-"):
        rid = f"EG-RUN-{rid}"
    run_dir = (TMP_EG / rid).resolve()
    if run_dir != TMP_EG and TMP_EG not in run_dir.parents:
        raise SystemExit("run dir must be under /tmp/eg")
    run_dir.mkdir(parents=True, exist_ok=False)
    store.dump(run_dir / "run.json", {
        "stage": "enforce",
        "run_id": rid,
        "repo_root": str(Path(repo_root).resolve()),
        "repo": repo,
        "target": target,
        "source": source or "",
    })
    return run_dir


def pr_context(run_dir: Path) -> tuple[int, str, str]:
    m = _meta(run_dir)
    cmd = ["bash", str(PR_CONTEXT), "--repo", m["repo"], "--target", m["target"],
           "--output-path", str(run_dir / "pr-context.json"),
           "--diff-path", str(run_dir / "diff.patch")]
    if m.get("source"):
        cmd += ["--source", m["source"]]
    return _run(cmd)


def select(run_dir: Path) -> tuple[int, str, str]:
    m = _meta(run_dir)
    diff = run_dir / "diff.patch"
    if not diff.exists():
        return (2, "", f"missing {diff}; run eg pr-context first or drop a diff.patch in the run dir\n")
    mirror.render_all(Path(m["repo_root"]))  # legacy reader sees .md from committed data
    cmd_h = [sys.executable, str(SELECT_HANDOFFS), "--repo-root", m["repo_root"],
             "--diff", str(diff), "--out", str(run_dir / "selected_handoffs.json")]
    pr_ctx = run_dir / "pr-context.json"
    if pr_ctx.exists():
        cmd_h += ["--pr-context", str(pr_ctx)]
    rc1, out1, err1 = _run(cmd_h)
    cmd_q = [sys.executable, str(SELECT_QUALITY), "--repo-root", m["repo_root"],
             "--diff", str(diff), "--out", str(run_dir / "quality-context.json")]
    rc2, out2, err2 = _run(cmd_q)
    return (rc1 or rc2, out1 + out2, err1 + err2)


# ---- findings guard (check) ------------------------------------------------

def _findings_files(run_dir: Path) -> list[Path]:
    return [run_dir / name for name in FINDINGS.values() if (run_dir / name).exists()]


def check_run(run_dir: Path, artifact: str | None = None) -> tuple[list[str], list[str]]:
    files = _findings_files(run_dir)
    if not files:
        return (["no reviewer findings yet: write layer-a-findings.json / layer-b-findings.json"], [])
    errors: list[str] = []
    for path in files:
        try:
            data = store.load(path)
        except Exception as exc:
            errors.append(f"{path.name}: invalid JSON ({exc})")
            continue
        errors += [f"{path.name}: {e}" for e in findings_rules.validate_findings(data)]
    return (errors, [])


# ---- enforce (gate) + ledger ----------------------------------------------

def enforce(run_dir: Path, facts: str | None) -> tuple[int, str, str]:
    files = _findings_files(run_dir)
    if not files:
        return (2, "", "no reviewer findings to enforce\n")
    guard, _ = check_run(run_dir)
    if guard:
        return (2, "", "findings failed the guard; fix before enforce:\n" + "".join(f"  - {e}\n" for e in guard))
    m = _meta(run_dir)
    mirror.render_all(Path(m["repo_root"]))  # enforce.py reads docs/adr|bdd/*.md
    cmd = [sys.executable, str(ENFORCE), "--profile", str(PROFILE),
           "--artifacts-root", m["repo_root"], "--out", str(run_dir / "feedback.json")]
    for path in files:
        cmd += ["--findings", str(path)]
    if facts:
        cmd += ["--facts", facts]
    handoffs = run_dir / "selected_handoffs.json"
    if handoffs.exists():
        cmd += ["--handoffs", str(handoffs)]
    rc, out, err = _run(cmd)
    # enforce.py exit 1 == gate blocked (a valid result), exit 2 == contract error.
    if rc == 2:
        return (2, out, err)
    led_cmd = [sys.executable, str(UPDATE_LEDGER), "--feedback", str(run_dir / "feedback.json"),
               "--out", str(run_dir / "finding-ledger.json")]
    closure = run_dir / "closure-evidence.json"
    if closure.exists():
        led_cmd += ["--closure-evidence", str(closure)]
    lrc, lout, lerr = _run(led_cmd)
    summary = out + lout + (f"finding-ledger -> {run_dir / 'finding-ledger.json'}\n" if lrc == 0 else "")
    return (rc or lrc, summary, err + lerr)


def notify(run_dir: Path, dry_run: bool) -> tuple[int, str, str]:
    cmd = [sys.executable, str(NOTIFY), "--feedback", str(run_dir / "feedback.json"),
           "--ledger", str(run_dir / "finding-ledger.json")]
    if dry_run:
        cmd.append("--dry-run")
    return _run(cmd)


def fix_handoff(run_dir: Path) -> tuple[int, str, str]:
    m = _meta(run_dir)
    cmd = [sys.executable, str(WRITE_FIX), "--ledger", str(run_dir / "finding-ledger.json"),
           "--repo-root", m["repo_root"], "--feedback", str(run_dir / "feedback.json"),
           "--out", str(run_dir / "fix-handoff.md")]
    for opt, name in (("--pr-context", "pr-context.json"), ("--diff", "diff.patch"),
                      ("--handoffs", "selected_handoffs.json")):
        if (run_dir / name).exists():
            cmd += [opt, str(run_dir / name)]
    return _run(cmd)


# ---- schema + generic-verb stubs ------------------------------------------

def example(name: str) -> dict:
    if name != "findings":
        raise SystemExit("enforce schema artifact: findings")
    return {
        "layer": "A",
        "findings": [{
            "type": "<quality or governance type from enforcement.yml>",
            "artifactRef": None,
            "ruleRef": "<QUALITY-RULES anchor / ADR / BDD / handoff entry>",
            "evidence": "<concrete observation from the diff>",
            "impact": "<why it matters>",
            "location": "<file:line>",
            "humanVerify": False,
        }],
    }


def _no_authoring(*_a, **_k):
    raise SystemExit("ERROR: enforce stage uses eg pr-context / select / enforce / notify / fix-handoff, not merge/set/seal/render")


artifact_path = _no_authoring
merge_key = _no_authoring
validate_written = _no_authoring
seal_run = _no_authoring
render_run = _no_authoring
