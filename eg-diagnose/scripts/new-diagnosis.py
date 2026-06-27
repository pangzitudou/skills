#!/usr/bin/env python3
"""Create an EG diagnosis run directory under /tmp/eg."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml


REQUIRED_CATEGORIES = [
    "code",
    "runtime_data",
    "runtime_behavior",
    "configuration",
    "domain_state",
    "comparative_baseline",
    "external_dependency",
    "user_reproduction_context",
    "change_history",
    "existing_governance",
    "other",
]


def slug(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    normalized = re.sub(r"-+", "-", normalized).strip("-._")
    if not normalized:
        raise SystemExit("repo and task must contain at least one slug character")
    return normalized


def ensure_tmp_eg(path: Path) -> None:
    resolved = path.resolve()
    if resolved != Path("/tmp/eg") and Path("/tmp/eg") not in resolved.parents:
        raise SystemExit("eg-diagnose may write only under /tmp/eg")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an EG diagnosis run under /tmp/eg.")
    parser.add_argument("--repo", required=True, help="Repository or project name.")
    parser.add_argument("--task", required=True, help="Task slug.")
    parser.add_argument("--run-id", help="Explicit run id. Defaults to EG-RUN-<timestamp>-<task>.")
    parser.add_argument("--base-dir", default="/tmp/eg", help="Run directory root; must be under /tmp/eg.")
    args = parser.parse_args()

    repo = slug(args.repo)
    task = slug(args.task)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = args.run_id or f"EG-RUN-{timestamp}-{task}"
    run_id = slug(run_id)
    if not run_id.startswith("EG-RUN-"):
        run_id = f"EG-RUN-{run_id}"

    base_dir = Path(args.base_dir)
    ensure_tmp_eg(base_dir)
    run_dir = base_dir / run_id
    ensure_tmp_eg(run_dir)
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "sources").mkdir()

    source_matrix = {
        "schema": "eg-source-matrix/v1",
        "run_id": run_id,
        "stage": "triage",
        "categories": [
            {
                "category": category,
                "needed": False,
                "reason": "TBD",
                "available": [],
                "missing": [],
                "impact_if_missing": "TBD",
                "access_mode": "read-only",
            }
            for category in REQUIRED_CATEGORIES
        ],
    }
    source_gap = {
        "schema": "eg-source-gap/v1",
        "run_id": run_id,
        "status": "blocked",
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
        "source_matrix": str(run_dir / "source-matrix.yml"),
        "source_gap": str(run_dir / "source-gap.yml"),
        "query_plan": str(run_dir / "query-plan.yml"),
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

    (run_dir / "source-matrix.yml").write_text(
        yaml.safe_dump(source_matrix, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (run_dir / "source-gap.yml").write_text(
        yaml.safe_dump(source_gap, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (run_dir / "query-plan.yml").write_text(
        yaml.safe_dump(query_plan, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (run_dir / "diagnosis.yml").write_text(
        yaml.safe_dump(diagnosis, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (run_dir / "diagnosis-preview.md").write_text(f"# {run_id}\n\n", encoding="utf-8")
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "repo": repo,
                "task": task,
                "diagnosis": str(run_dir / "diagnosis.yml"),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(run_dir / "diagnosis.yml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
