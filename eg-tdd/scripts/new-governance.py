#!/usr/bin/env python3
"""Create an EG TDD run directory under /tmp/eg."""
from __future__ import annotations

import argparse
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def slug(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    normalized = re.sub(r"-+", "-", normalized).strip("-._")
    if not normalized:
        raise SystemExit("repo and task must contain at least one slug character")
    return normalized


def ensure_tmp_eg_root(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    tmp_eg = Path("/tmp/eg").resolve()
    if resolved != tmp_eg:
        raise SystemExit(f"base-dir must be /tmp/eg, got: {resolved}")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an EG TDD ledger in /tmp/eg.")
    parser.add_argument("--repo", required=True, help="Repository or project name.")
    parser.add_argument("--task", required=True, help="Task slug.")
    parser.add_argument("--mode", required=True, choices=["lite", "full"], help="Risk mode.")
    parser.add_argument("--intent-adr", default="", help="Intent ADR id, e.g. ADR-0001.")
    parser.add_argument("--intent-status", default="review", choices=["review", "approved"])
    parser.add_argument("--run-id", help="Explicit run id. Defaults to EG-RUN-<timestamp>-<task>-<nonce>.")
    parser.add_argument("--base-dir", default="/tmp/eg", help="Run directory root.")
    args = parser.parse_args()

    repo = slug(args.repo)
    task = slug(args.task)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nonce = uuid.uuid4().hex[:8]
    run_id = args.run_id or f"EG-RUN-{timestamp}-{task}-{nonce}"
    run_id = slug(run_id)
    if not run_id.startswith("EG-RUN-"):
        run_id = f"EG-RUN-{run_id}"

    run_dir = ensure_tmp_eg_root(Path(args.base_dir)) / run_id
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
        "enforce_plan": {
            "schema": "eg-enforce-plan/v1",
            "status": "draft",
            "frozen_at": "",
            "source": "bdd-approval",
            "intent": {"id": args.intent_adr, "status": args.intent_status},
            "bdd": [],
            "related_adrs": [],
            "required_acceptance_tests": [],
            "expected_adversarial_domains": [],
            "manual_qa_expected": [],
            "out_of_scope": [],
            "nfr_checkpoints": [],
        },
        "ci_facts_contract": {
            "schema": "eg-ci-facts-contract/v1",
            "status": "planned",
            "path": "ci-facts.json",
            "producer": "",
            "required_for_statuses": ["green", "merged"],
            "expected_acceptance_test_ids": [],
            "required_result_ids": [],
        },
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
