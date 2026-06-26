#!/usr/bin/env python3
"""Create an EG TDD run directory under /tmp/eg."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def slug(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    normalized = re.sub(r"-+", "-", normalized).strip("-._")
    if not normalized:
        raise SystemExit("repo and task must contain at least one slug character")
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an EG TDD ledger in /tmp/eg.")
    parser.add_argument("--repo", required=True, help="Repository or project name.")
    parser.add_argument("--task", required=True, help="Task slug.")
    parser.add_argument("--mode", required=True, choices=["lite", "full"], help="Risk mode.")
    parser.add_argument("--intent-adr", default="", help="Intent ADR id, e.g. ADR-0001.")
    parser.add_argument("--intent-status", default="review", choices=["review", "approved"])
    parser.add_argument("--run-id", help="Explicit run id. Defaults to EG-RUN-<timestamp>-<task>.")
    parser.add_argument("--base-dir", default="/tmp/eg", help="Run directory root.")
    args = parser.parse_args()

    repo = slug(args.repo)
    task = slug(args.task)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = args.run_id or f"EG-RUN-{timestamp}-{task}"
    run_id = slug(run_id)
    if not run_id.startswith("EG-RUN-"):
        run_id = f"EG-RUN-{run_id}"

    run_dir = Path(args.base_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    ledger = {
        "schema": "eg-ledger/v1",
        "run_id": run_id,
        "stage": "bdd-draft",
        "repo": repo,
        "task": task,
        "mode": args.mode,
        "created_at": timestamp,
        "intent": {"id": args.intent_adr, "status": args.intent_status},
        "bdd": [],
        "related_adrs": [],
        "adr_coverage": [],
        "context_read": [],
        "unknowns": [],
        "acceptance_tests": [],
        "hypotheses": [],
        "cycles": [],
        "sensitivity": [],
        "manual_qa": [],
        "touched_files": [],
    }

    ledger_path = run_dir / "ledger.json"
    ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (run_dir / "notes.md").write_text(f"# {run_id}\n\n", encoding="utf-8")
    print(ledger_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
