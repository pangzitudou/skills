#!/usr/bin/env python3
"""Freeze EG enforce plan and CI facts contract after BDD approval."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def die(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def ensure_under_tmp_eg_run(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    tmp_eg = Path("/tmp/eg").resolve()
    try:
        resolved.relative_to(tmp_eg)
    except ValueError:
        die(f"path must be under /tmp/eg/<run-id>: {resolved}")
    if resolved == tmp_eg:
        die("path must include /tmp/eg/<run-id>")
    return resolved


def ensure_output_in_run(path: Path, run_dir: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(run_dir)
    except ValueError:
        die(f"output must stay under run dir {run_dir}: {resolved}")
    return resolved


def load_yaml_object(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        die(f"invalid yaml {path}: {exc}")
    if not isinstance(data, dict):
        die(f"{path} must contain an object")
    return data


def load_ledger(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"not found: {path}")
    except json.JSONDecodeError as exc:
        die(f"invalid json {path}: {exc}")
    if not isinstance(data, dict):
        die("ledger must be a JSON object")
    return data


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def planned_acceptance_ids(plan: dict[str, Any]) -> list[str]:
    tests = plan.get("required_acceptance_tests")
    if not isinstance(tests, list) or not tests:
        die("enforce_plan.required_acceptance_tests must be filled before freezing")
    ids: list[str] = []
    for index, item in enumerate(tests):
        if not isinstance(item, dict) or not is_non_empty_string(item.get("id")):
            die(f"enforce_plan.required_acceptance_tests[{index}].id is required")
        ids.append(str(item["id"]))
    if len(ids) != len(set(ids)):
        die("enforce_plan.required_acceptance_tests contains duplicate ids")
    return ids


def canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze enforce plan and CI facts contract.")
    parser.add_argument("ledger", help="/tmp/eg/<run-id>/ledger.json")
    parser.add_argument("--frozen-at", help="ISO timestamp; default now in UTC")
    parser.add_argument("--out-plan", help="Defaults to sibling enforce-plan.yml")
    parser.add_argument("--out-ci-contract", help="Defaults to sibling ci-facts.contract.json")
    args = parser.parse_args()

    ledger_path = ensure_under_tmp_eg_run(Path(args.ledger))
    data = load_ledger(ledger_path)
    plan = data.get("enforce_plan")
    contract = data.get("ci_facts_contract")
    if not isinstance(plan, dict):
        die("ledger.enforce_plan must be an object")
    if not isinstance(contract, dict):
        die("ledger.ci_facts_contract must be an object")

    if not is_non_empty_string(contract.get("producer")):
        die("ci_facts_contract.producer is required before freezing")
    if not is_non_empty_string(contract.get("path")):
        die("ci_facts_contract.path is required before freezing")

    already_frozen = plan.get("status") == "frozen"
    plan["schema"] = "eg-enforce-plan/v1"
    plan["status"] = "frozen"
    plan["frozen_at"] = plan.get("frozen_at") if already_frozen else (args.frozen_at or datetime.now(timezone.utc).isoformat())
    plan["source"] = "bdd-approval"
    plan["intent"] = data.get("intent")
    plan["bdd"] = data.get("bdd")
    plan["related_adrs"] = data.get("related_adrs")

    expected_at_ids = planned_acceptance_ids(plan)
    contract["schema"] = "eg-ci-facts-contract/v1"
    contract["status"] = "planned"
    contract["required_for_statuses"] = ["green", "merged"]
    contract["expected_acceptance_test_ids"] = expected_at_ids
    contract.setdefault("required_result_ids", [])

    out_plan = ensure_output_in_run(
        Path(args.out_plan) if args.out_plan else ledger_path.parent / "enforce-plan.yml",
        ledger_path.parent,
    )
    out_ci = ensure_output_in_run(
        Path(args.out_ci_contract) if args.out_ci_contract else ledger_path.parent / "ci-facts.contract.json",
        ledger_path.parent,
    )
    frozen_hash = canonical_hash(plan)
    if out_plan.exists():
        existing_plan = load_yaml_object(out_plan)
        existing_hash = canonical_hash(existing_plan)
        if existing_hash != frozen_hash:
            die(f"enforce plan already frozen and differs: {out_plan}")
        if data.get("frozen_enforce_plan_hash") not in (None, "", existing_hash):
            die("ledger.frozen_enforce_plan_hash conflicts with existing enforce-plan.yml")
    if out_ci.exists():
        try:
            existing_contract = json.loads(out_ci.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            die(f"invalid json {out_ci}: {exc}")
        if existing_contract != contract:
            die(f"ci facts contract already frozen and differs: {out_ci}")

    data["enforce_plan"] = plan
    data["ci_facts_contract"] = contract
    data["frozen_enforce_plan_hash"] = frozen_hash

    ledger_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out_plan.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True), encoding="utf-8")
    out_ci.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"frozen enforce plan -> {out_plan}")
    print(f"frozen ci facts contract -> {out_ci}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
