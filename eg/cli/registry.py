"""Artifact registry for the EG diagnose stage.

Single source of truth for scaffolds, filenames, per-write enums, and the
check/seal/render dispatch. Scaffolds write `null` for required leaves (never a
placeholder), so an untouched field fails `eg check` instead of silently
passing. Enum sets are imported from diagnosis_rules so they never drift.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import diagnosis_rules as rules
import diagnosis_render
import store

TMP_EG = Path("/tmp/eg")

FILENAMES = {
    "source-matrix": "source-matrix.yml",
    "source-gap": "source-gap.yml",
    "query-plan": "query-plan.yml",
    "diagnosis": "diagnosis.yml",
}

# Per-write enum checks, keyed by (artifact, field-name). Unambiguous fields
# only; the deep `check` covers the rest (e.g. problem_findings.status, whose
# field name collides with symptoms.status).
ENUMS: dict[tuple[str, str], set[str]] = {
    ("diagnosis", "finding_type"): rules.FINDING_TYPES,
    ("diagnosis", "confidence"): rules.CONFIDENCE,
    ("diagnosis", "strength"): rules.EVIDENCE_STRENGTH,
    ("source-gap", "status"): rules.SOURCE_GAP_STATUS,
    ("query-plan", "operation"): rules.QUERY_OPERATIONS,
}


def slug(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    normalized = re.sub(r"-+", "-", normalized).strip("-._")
    if not normalized:
        raise SystemExit("repo and task must contain at least one slug character")
    return normalized


def resolve_run_dir(run: str) -> Path:
    """Accept a run-id or a path; return the run directory under /tmp/eg."""
    p = Path(run)
    if p.is_absolute() or "/" in run:
        run_dir = p.resolve()
    else:
        run_dir = (TMP_EG / run).resolve()
    if run_dir != TMP_EG and TMP_EG not in run_dir.parents:
        raise SystemExit(f"run dir must be under /tmp/eg: {run_dir}")
    return run_dir


def artifact_path(run_dir: Path, artifact: str) -> Path:
    if artifact not in FILENAMES:
        raise SystemExit(f"unknown artifact {artifact!r}; one of {sorted(FILENAMES)}")
    return run_dir / FILENAMES[artifact]


def merge_key(artifact: str) -> str:
    return artifact


def example(artifact: str) -> dict:
    return _scaffold(
        "EG-RUN-EXAMPLE", "repo", "task",
        TMP_EG / "EG-RUN-EXAMPLE", "<created_at>",
    )[artifact]


# ---- scaffolds ------------------------------------------------------------

def _scaffold(run_id: str, repo: str, task: str, run_dir: Path, timestamp: str) -> dict[str, dict]:
    source_matrix = {
        "schema": "eg-source-matrix/v1",
        "run_id": run_id,
        "stage": "triage",
        "categories": [
            {
                "category": category,
                "needed": None,          # force an explicit true/false
                "reason": None,          # force a real reason
                "available": [],
                "missing": [],
                "impact_if_missing": None,
                "access_mode": "read-only",
            }
            for category in sorted(rules.REQUIRED_CATEGORIES)
        ],
    }
    source_gap = {
        "schema": "eg-source-gap/v1",
        "run_id": run_id,
        "status": None,                  # force complete|degraded|blocked
        "available": [],
        "missing": [],
        "questions_for_user": [],
        "user_response": "",
        "degraded_reason": "",
    }
    query_plan = {
        "schema": "eg-query-plan/v1",
        "run_id": run_id,
        "queries": [],
        "side_effecting_operations": [],
    }
    diagnosis = {
        "schema": "eg-diagnosis/v1",
        "run_id": run_id,
        "stage": "triage",
        "repo": repo,
        "task": task,
        "created_at": timestamp,
        "source_matrix": str(run_dir / FILENAMES["source-matrix"]),
        "source_gap": str(run_dir / FILENAMES["source-gap"]),
        "query_plan": str(run_dir / FILENAMES["query-plan"]),
        "sensitive_material": {
            "stored_locally": False,
            "paths": [],
            "do_not_copy_to_repo": True,
        },
        "symptoms": [],
        "problem_findings": [],
        "root_causes": [],
        "unexplained_symptoms": [],
        "fix_options": [],
        "handoff_to_precipitate": {"proposed_intents": []},
    }
    return {
        "source-matrix": source_matrix,
        "source-gap": source_gap,
        "query-plan": query_plan,
        "diagnosis": diagnosis,
    }


def new_run(repo: str, task: str, run_id: str | None = None) -> Path:
    repo_s = slug(repo)
    task_s = slug(task)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nonce = uuid.uuid4().hex[:8]
    rid = run_id or f"EG-RUN-{timestamp}-{task_s}-{nonce}"
    rid = slug(rid)
    if not rid.startswith("EG-RUN-"):
        rid = f"EG-RUN-{rid}"

    run_dir = (TMP_EG / rid).resolve()
    if run_dir != TMP_EG and TMP_EG not in run_dir.parents:
        raise SystemExit("run dir must be under /tmp/eg")
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "sources").mkdir()

    artifacts = _scaffold(rid, repo_s, task_s, run_dir, timestamp)
    for key, data in artifacts.items():
        store.dump(run_dir / FILENAMES[key], data)
    (run_dir / "diagnosis-preview.md").write_text(f"# {rid}\n\n", encoding="utf-8")
    store.dump(run_dir / "run.json", {"stage": "diagnose", "run_id": rid, "repo": repo_s, "task": task_s})
    store.dump(run_dir / "manifest.json", {
        "run_id": rid,
        "repo": repo_s,
        "task": task_s,
        "diagnosis": str(run_dir / FILENAMES["diagnosis"]),
    })
    return run_dir


# ---- per-write light validation -------------------------------------------

def validate_written(artifact: str, data: Any, path: str = "") -> list[str]:
    """Immediate feedback after merge/set: reject placeholder values and bad
    enum values. Completeness (missing fields) is the job of `eg check`."""
    errors: list[str] = []

    def walk(node: Any, where: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                here = f"{where}.{k}" if where else k
                if isinstance(v, str) and store.is_sentinel(v):
                    errors.append(f"{here} is a placeholder ({v!r}); use a real value or 'defer: <reason>'")
                elif (artifact, k) in ENUMS and isinstance(v, str) and v.strip() and not store.is_deferred(v):
                    allowed = ENUMS[(artifact, k)]
                    candidate = v.strip().upper() if k == "operation" else v.strip()
                    if candidate not in allowed:
                        errors.append(f"{here} must be one of {sorted(allowed)}, got {v!r}")
                walk(v, here)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{where}[{i}]")

    walk(data, path)
    return errors


# ---- check / seal / render ------------------------------------------------

def _collect_deferrals(run_dir: Path) -> list[str]:
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

    for artifact, fname in FILENAMES.items():
        p = run_dir / fname
        if p.exists():
            try:
                walk(store.load(p), artifact)
            except Exception:
                pass
    return out


def check_run(run_dir: Path, artifact: str | None = None) -> tuple[list[str], list[str]]:
    """Return (errors, deferrals). errors empty == ready to seal."""
    diagnosis_path = artifact_path(run_dir, "diagnosis")
    if not diagnosis_path.exists():
        return ([f"missing artifact: {diagnosis_path}"], [])
    data = store.load(diagnosis_path)
    if not isinstance(data, dict):
        return (["diagnosis.yml must be an object"], [])
    errors = rules.validate(data, diagnosis_path, sealed=False)
    return (errors, _collect_deferrals(run_dir))


def render_run(run_dir: Path, artifact: str | None = None) -> Path:
    diagnosis_path = artifact_path(run_dir, "diagnosis")
    data = store.load(diagnosis_path)
    out = run_dir / "diagnosis-preview.md"
    out.write_text(diagnosis_render.render(data), encoding="utf-8")
    return out


def seal_run(run_dir: Path, artifact: str | None = None) -> list[str]:
    """Hard gate: refuse to mark diagnosis-complete unless check passes. On
    success, render the preview, flip stage, and confirm with full validation."""
    errors, _ = check_run(run_dir)
    if errors:
        return errors
    diagnosis_path = artifact_path(run_dir, "diagnosis")
    data = store.load(diagnosis_path)
    data["stage"] = "diagnosis-complete"
    store.dump(diagnosis_path, data)
    render_run(run_dir)  # preview now reflects the sealed stage
    final = rules.validate(data, diagnosis_path, sealed=True)
    if final:
        data["stage"] = "triage"  # revert; do not leave a half-sealed run
        store.dump(diagnosis_path, data)
        render_run(run_dir)
    return final
