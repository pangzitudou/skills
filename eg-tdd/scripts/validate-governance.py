#!/usr/bin/env python3
"""Validate EG TDD ledger and emit repo handoff."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ARTIFACT_STATUSES = {"draft", "review", "approved", "deprecated"}
INTENT_OK = {"review", "approved"}
BDD_TESTABLE = {"approved"}
BEHAVIOR_KINDS = {"bdd", "spec", "adr", "requirement", "contract"}
TEST_GREEN_STATUSES = {"green", "merged"}
TEST_HANDOFF_STATUSES = {"green", "manual", "deferred", "merged"}
CI_FACT_STATUSES = ["green", "merged"]
AT_ID_RE = re.compile(r"^AT-[0-9]+$")
H_ID_RE = re.compile(r"^H[0-9]+$")
SCENARIO_RE = re.compile(r"^BDD-[0-9]+#scenario-[a-z0-9-]+$")
BDD_ID_RE = re.compile(r"^(BDD-[0-9]+)")
ADR_ID_RE = re.compile(r"(ADR-[0-9]+)")
COVERAGE_REF_RE = re.compile(r"^(BDD-[0-9]+#scenario-[a-z0-9-]+|AT-[0-9]+|H[0-9]+|manual_qa:[A-Za-z0-9._-]+)$")
SCENARIO_ANCHOR_RE = re.compile(r"\{#(scenario-[a-z0-9-]+)\}")


def is_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as exc:
        print(f"invalid json: {exc}", file=sys.stderr)
        raise SystemExit(2)
    if not isinstance(data, dict):
        print("ledger must be a JSON object", file=sys.stderr)
        raise SystemExit(2)
    return data


def ensure_under_tmp_eg_run(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    tmp_eg = Path("/tmp/eg").resolve()
    try:
        resolved.relative_to(tmp_eg)
    except ValueError:
        print(f"path must be under /tmp/eg/<run-id>: {resolved}", file=sys.stderr)
        raise SystemExit(2)
    if resolved == tmp_eg:
        print("path must include /tmp/eg/<run-id>", file=sys.stderr)
        raise SystemExit(2)
    return resolved


def canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def artifact_index(repo_root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for subdir in ("docs/adr", "docs/bdd"):
        root = repo_root / subdir
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.md")):
            fm = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
            aid = fm.get("id")
            if not aid:
                continue
            out[str(aid)] = {
                "path": str(path.relative_to(repo_root)),
                "status": fm.get("status"),
                "type": fm.get("type") or ("bdd" if subdir.endswith("bdd") else "adr"),
                "frontmatter": fm,
            }
    return out


def bdd_scenario_index(repo_root: Path, idx: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    scenarios: dict[str, set[str]] = {}
    for artifact_id, info in idx.items():
        if info.get("type") != "bdd":
            continue
        rel_path = info.get("path")
        if not isinstance(rel_path, str):
            continue
        path = repo_root / rel_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        scenarios[artifact_id] = {f"{artifact_id}#{anchor}" for anchor in SCENARIO_ANCHOR_RE.findall(text)}
    return scenarios


def validate_scenario_ref(
    errors: list[str],
    ref: str,
    path: str,
    bdd_ids: set[str],
    scenario_refs: dict[str, set[str]],
) -> None:
    match = BDD_ID_RE.match(ref)
    bid = match.group(1) if match else ""
    if bid not in bdd_ids:
        errors.append(f"{path} references {bid}, absent from bdd[]")
        return
    if scenario_refs and ref not in scenario_refs.get(bid, set()):
        errors.append(f"{path} references missing BDD scenario anchor {ref}")


def require(errors: list[str], obj: dict[str, Any], key: str, path: str) -> Any:
    if key not in obj:
        errors.append(f"{path}.{key} is required")
        return None
    return obj[key]


def validate_artifact_ref(
    errors: list[str],
    ref: Any,
    path: str,
    idx: dict[str, dict[str, Any]],
    *,
    require_live: bool,
) -> tuple[str, str]:
    if not isinstance(ref, dict):
        errors.append(f"{path} must be an object")
        return "", ""
    aid = require(errors, ref, "id", path)
    status = require(errors, ref, "status", path)
    if not is_str(aid):
        errors.append(f"{path}.id must be a non-empty string")
        aid = ""
    if status not in ARTIFACT_STATUSES:
        errors.append(f"{path}.status must be one of {sorted(ARTIFACT_STATUSES)}")
        status = ""
    if require_live and aid:
        live = idx.get(str(aid))
        if not live:
            errors.append(f"{path}.id {aid} does not exist in docs/adr or docs/bdd")
        else:
            live_status = live.get("status")
            if live_status == "deprecated":
                errors.append(f"{path}.id {aid} is deprecated")
            if status and live_status and status != live_status:
                errors.append(f"{path}.status {status} disagrees with live status {live_status}")
    return str(aid), str(status)


def validate_bdd_approval(errors: list[str], bdd_id: str, idx: dict[str, dict[str, Any]]) -> None:
    live = idx.get(bdd_id)
    if not live:
        return
    fm = live.get("frontmatter", {})
    if fm.get("status") != "approved":
        return
    for key in ("approved_by", "approved_at", "approval_source"):
        if not has_value(fm.get(key)):
            errors.append(f"{bdd_id} is approved but missing {key}")
    if fm.get("approved_by") != "human":
        errors.append(f"{bdd_id}.approved_by must be human")


def artifact_ref_signature(ref: Any) -> tuple[str, str]:
    if not isinstance(ref, dict):
        return "", ""
    return str(ref.get("id") or ""), str(ref.get("status") or "")


def artifact_ref_set(refs: Any) -> set[tuple[str, str]]:
    if not isinstance(refs, list):
        return set()
    return {artifact_ref_signature(ref) for ref in refs if isinstance(ref, dict)}


def related_adr_set(refs: Any) -> set[tuple[str, str, str]]:
    if not isinstance(refs, list):
        return set()
    return {
        (str(ref.get("id") or ""), str(ref.get("type") or ""), str(ref.get("status") or ""))
        for ref in refs if isinstance(ref, dict)
    }


def validate_plan_artifact_list(
    errors: list[str],
    plan: dict[str, Any],
    data: dict[str, Any],
    key: str,
    path: str,
) -> None:
    planned = plan.get(key)
    actual = data.get(key)
    if not isinstance(planned, list) or not planned:
        errors.append(f"{path}.{key} must be a non-empty list")
        return
    if key == "related_adrs":
        if related_adr_set(planned) != related_adr_set(actual):
            errors.append(f"{path}.{key} must match ledger {key}; do not change governance baseline after freeze")
    elif artifact_ref_set(planned) != artifact_ref_set(actual):
        errors.append(f"{path}.{key} must match ledger {key}; do not change governance baseline after freeze")


def validate_enforce_plan(
    errors: list[str],
    data: dict[str, Any],
    bdd_ids: set[str],
    scenario_refs: dict[str, set[str]],
) -> set[str]:
    plan = data.get("enforce_plan")
    required_at_ids: set[str] = set()
    if not isinstance(plan, dict):
        errors.append("enforce_plan must be an object")
        return required_at_ids

    if plan.get("schema") != "eg-enforce-plan/v1":
        errors.append("enforce_plan.schema must be eg-enforce-plan/v1")
    if plan.get("status") != "frozen":
        errors.append("enforce_plan.status must be frozen before planning validation")
    if not is_str(plan.get("frozen_at")):
        errors.append("enforce_plan.frozen_at is required")
    if plan.get("source") != "bdd-approval":
        errors.append("enforce_plan.source must be bdd-approval")

    if artifact_ref_signature(plan.get("intent")) != artifact_ref_signature(data.get("intent")):
        errors.append("enforce_plan.intent must match ledger intent")
    validate_plan_artifact_list(errors, plan, data, "bdd", "enforce_plan")
    validate_plan_artifact_list(errors, plan, data, "related_adrs", "enforce_plan")

    required_tests = plan.get("required_acceptance_tests")
    if not isinstance(required_tests, list) or not required_tests:
        errors.append("enforce_plan.required_acceptance_tests must be non-empty")
        return required_at_ids

    seen: set[str] = set()
    for i, item in enumerate(required_tests):
        path = f"enforce_plan.required_acceptance_tests[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        tid = item.get("id")
        derived = item.get("derived_from")
        if not isinstance(tid, str) or not AT_ID_RE.match(tid):
            errors.append(f"{path}.id must match AT-<number>")
        elif tid in seen:
            errors.append(f"{path}.id duplicates {tid}")
        else:
            seen.add(tid)
            required_at_ids.add(tid)
        if not isinstance(derived, str) or not SCENARIO_RE.match(derived):
            errors.append(f"{path}.derived_from must be BDD-N#scenario-slug")
        else:
            validate_scenario_ref(errors, derived, f"{path}.derived_from", bdd_ids, scenario_refs)
        if not is_str(item.get("expectation")):
            errors.append(f"{path}.expectation is required")

    for key in ("expected_adversarial_domains", "manual_qa_expected", "out_of_scope", "nfr_checkpoints"):
        if not isinstance(plan.get(key), list):
            errors.append(f"enforce_plan.{key} must be a list")
    return required_at_ids


def validate_ci_facts_contract(
    errors: list[str],
    data: dict[str, Any],
    required_at_ids: set[str],
    *,
    final: bool,
) -> None:
    contract = data.get("ci_facts_contract")
    if not isinstance(contract, dict):
        errors.append("ci_facts_contract must be an object")
        return
    if contract.get("schema") != "eg-ci-facts-contract/v1":
        errors.append("ci_facts_contract.schema must be eg-ci-facts-contract/v1")
    expected_status = "ready" if final else "planned"
    if contract.get("status") != expected_status:
        errors.append(f"ci_facts_contract.status must be {expected_status}")
    if not is_str(contract.get("path")):
        errors.append("ci_facts_contract.path is required")
    if not is_str(contract.get("producer")):
        errors.append("ci_facts_contract.producer is required")
    if contract.get("required_for_statuses") != CI_FACT_STATUSES:
        errors.append(f"ci_facts_contract.required_for_statuses must be {CI_FACT_STATUSES}")

    expected_at = contract.get("expected_acceptance_test_ids")
    if not isinstance(expected_at, list):
        errors.append("ci_facts_contract.expected_acceptance_test_ids must be a list")
        expected_at = []
    expected_at_set = {item for item in expected_at if isinstance(item, str)}
    if expected_at_set != required_at_ids:
        errors.append("ci_facts_contract.expected_acceptance_test_ids must match enforce_plan required AT ids")

    required_result_ids = contract.get("required_result_ids")
    if not isinstance(required_result_ids, list):
        errors.append("ci_facts_contract.required_result_ids must be a list")
        required_result_ids = []
    required_result_set = {item for item in required_result_ids if isinstance(item, str)}
    if len(required_result_set) != len(required_result_ids):
        errors.append("ci_facts_contract.required_result_ids must contain unique strings")

    if final:
        green_ids = {
            str(item.get("id"))
            for item in handoff_tests(data)
            if isinstance(item, dict) and item.get("status") in TEST_GREEN_STATUSES and is_str(item.get("id"))
        }
        if required_result_set != green_ids:
            missing = sorted(green_ids - required_result_set)
            extra = sorted(required_result_set - green_ids)
            if missing:
                errors.append(f"ci_facts_contract.required_result_ids missing green/merged tests: {', '.join(missing)}")
            if extra:
                errors.append(f"ci_facts_contract.required_result_ids includes non-green/non-merged tests: {', '.join(extra)}")


def validate_frozen_plan_file(
    errors: list[str],
    data: dict[str, Any],
    ledger_path: Path | None,
) -> None:
    if ledger_path is None:
        return
    plan = data.get("enforce_plan")
    if not isinstance(plan, dict) or plan.get("status") != "frozen":
        return
    frozen_path = ledger_path.parent / "enforce-plan.yml"
    try:
        frozen = yaml.safe_load(frozen_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"frozen enforce plan file missing: {frozen_path}")
        return
    except yaml.YAMLError as exc:
        errors.append(f"invalid frozen enforce plan file {frozen_path}: {exc}")
        return
    if not isinstance(frozen, dict):
        errors.append(f"frozen enforce plan file {frozen_path} must contain an object")
        return
    frozen_hash = canonical_hash(frozen)
    if data.get("frozen_enforce_plan_hash") != frozen_hash:
        errors.append("frozen_enforce_plan_hash must match /tmp/eg/<run-id>/enforce-plan.yml")
    if canonical_hash(plan) != frozen_hash:
        errors.append("ledger.enforce_plan differs from frozen /tmp/eg/<run-id>/enforce-plan.yml")


def validate_context(errors: list[str], data: dict[str, Any]) -> dict[str, str]:
    path_kind: dict[str, str] = {}
    entries = data.get("context_read")
    if not isinstance(entries, list):
        errors.append("context_read must be a list")
        return path_kind
    for i, entry in enumerate(entries):
        path = f"context_read[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{path} must be an object")
            continue
        p = entry.get("path")
        kind = entry.get("kind")
        if not is_str(p):
            errors.append(f"{path}.path is required")
            continue
        if not is_str(kind):
            errors.append(f"{path}.kind is required")
            continue
        if not is_str(entry.get("reason")):
            errors.append(f"{path}.reason is required")
        path_kind[str(p)] = str(kind)
    return path_kind


def adr_id_from_path_or_value(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    match = ADR_ID_RE.search(value)
    return match.group(1) if match else ""


def infer_required_adrs(data: dict[str, Any], idx: dict[str, dict[str, Any]]) -> set[str]:
    required: set[str] = set()
    path_to_adr = {
        info.get("path"): aid
        for aid, info in idx.items()
        if info.get("type") in {"intent", "decision", "constraint"} and info.get("path")
    }
    intent = data.get("intent")
    if isinstance(intent, dict):
        aid = intent.get("id")
        if isinstance(aid, str) and ADR_ID_RE.fullmatch(aid):
            required.add(aid)

    for entry in data.get("context_read", []) or []:
        if isinstance(entry, dict) and entry.get("kind") == "adr":
            aid = adr_id_from_path_or_value(entry.get("path"))
            if not aid:
                aid = path_to_adr.get(entry.get("path"), "")
            if aid:
                required.add(aid)

    for hyp in data.get("hypotheses", []) or []:
        if not isinstance(hyp, dict):
            continue
        aid = adr_id_from_path_or_value(hyp.get("source"))
        if aid:
            required.add(aid)
        for ev in hyp.get("evidence", []) or []:
            if isinstance(ev, dict) and ev.get("kind") == "adr":
                aid = adr_id_from_path_or_value(ev.get("path"))
                if not aid:
                    aid = path_to_adr.get(ev.get("path"), "")
                if aid:
                    required.add(aid)
    return required


def validate_adr_coverage(
    errors: list[str],
    data: dict[str, Any],
    idx: dict[str, dict[str, Any]],
    scenario_refs: dict[str, set[str]],
    *,
    final: bool,
) -> None:
    related = data.get("related_adrs")
    coverage = data.get("adr_coverage")
    if not isinstance(related, list):
        errors.append("related_adrs must be a list")
        return
    if not isinstance(coverage, list):
        errors.append("adr_coverage must be a list")
        return

    related_by_id: dict[str, dict[str, Any]] = {}
    for i, item in enumerate(related):
        path = f"related_adrs[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        aid = item.get("id")
        atype = item.get("type")
        status = item.get("status")
        if not isinstance(aid, str) or not ADR_ID_RE.fullmatch(aid):
            errors.append(f"{path}.id must match ADR-<number>")
            continue
        if aid in related_by_id:
            errors.append(f"{path}.id duplicates {aid}")
        related_by_id[aid] = item
        if atype not in {"intent", "decision", "constraint"}:
            errors.append(f"{path}.type must be intent, decision, or constraint")
        if status not in ARTIFACT_STATUSES:
            errors.append(f"{path}.status must be an artifact status")
        live = idx.get(aid)
        if live:
            if live.get("status") == "deprecated":
                errors.append(f"{path}.id {aid} is deprecated")
            if status and live.get("status") and status != live.get("status"):
                errors.append(f"{path}.status {status} disagrees with live status {live.get('status')}")
            live_type = live.get("type")
            if live_type in {"intent", "decision", "constraint"} and atype and atype != live_type:
                errors.append(f"{path}.type {atype} disagrees with live type {live_type}")

    for aid in sorted(infer_required_adrs(data, idx)):
        if aid not in related_by_id:
            errors.append(f"related_adrs must include required ADR {aid}")

    coverage_by_adr: dict[str, dict[str, Any]] = {}
    for i, item in enumerate(coverage):
        path = f"adr_coverage[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        aid = item.get("adr")
        state = item.get("coverage")
        refs = item.get("covered_by")
        reason = item.get("reason")
        if not isinstance(aid, str) or not ADR_ID_RE.fullmatch(aid):
            errors.append(f"{path}.adr must match ADR-<number>")
            continue
        if aid in coverage_by_adr:
            errors.append(f"{path}.adr duplicates {aid}")
        coverage_by_adr[aid] = item
        if aid not in related_by_id:
            errors.append(f"{path}.adr {aid} is absent from related_adrs")
        if state not in {"covered", "not-applicable", "deferred"}:
            errors.append(f"{path}.coverage is invalid")
        if not isinstance(refs, list):
            errors.append(f"{path}.covered_by must be a list")
            refs = []
        for ref in refs:
            if not isinstance(ref, str) or not COVERAGE_REF_RE.match(ref):
                errors.append(f"{path}.covered_by contains invalid ref {ref!r}")
            elif scenario_refs and SCENARIO_RE.match(ref):
                validate_scenario_ref(errors, ref, f"{path}.covered_by", set(scenario_refs), scenario_refs)
        if not is_str(reason):
            errors.append(f"{path}.reason is required")

    for aid, adr in related_by_id.items():
        cov = coverage_by_adr.get(aid)
        if not cov:
            errors.append(f"adr_coverage missing for {aid}")
            continue
        state = cov.get("coverage")
        refs = cov.get("covered_by") if isinstance(cov.get("covered_by"), list) else []
        atype = adr.get("type")
        if state == "covered" and not refs:
            errors.append(f"adr_coverage for {aid} is covered but covered_by is empty")
        if atype == "intent":
            if state != "covered":
                errors.append(f"intent ADR {aid} must be covered")
            if final:
                if not any(isinstance(ref, str) and SCENARIO_RE.match(ref) for ref in refs):
                    errors.append(f"intent ADR {aid} coverage must include a BDD scenario")
                if not any(isinstance(ref, str) and AT_ID_RE.match(ref) for ref in refs):
                    errors.append(f"intent ADR {aid} coverage must include an AT")
        elif atype == "constraint" and state == "covered" and final:
            if not any(isinstance(ref, str) and (H_ID_RE.match(ref) or ref.startswith("manual_qa:")) for ref in refs):
                errors.append(f"constraint ADR {aid} coverage must include H* or manual_qa:*")


def validate_red_green(errors: list[str], obj: Any, path: str, final: bool) -> None:
    if not isinstance(obj, dict):
        errors.append(f"{path} must be an object")
        return
    red = obj.get("red")
    green = obj.get("green")
    if not isinstance(red, dict):
        errors.append(f"{path}.red must be an object")
    else:
        if not is_str(red.get("command")):
            errors.append(f"{path}.red.command is required")
        if not is_str(red.get("summary")):
            errors.append(f"{path}.red.summary is required")
        if not isinstance(red.get("failed_as_expected"), bool):
            errors.append(f"{path}.red.failed_as_expected must be boolean")
        elif final and red.get("failed_as_expected") is not True:
            errors.append(f"{path}.red.failed_as_expected must be true in final phase")
    if not isinstance(green, dict):
        errors.append(f"{path}.green must be an object")
    else:
        if not is_str(green.get("command")):
            errors.append(f"{path}.green.command is required")
        if not isinstance(green.get("passed"), bool):
            errors.append(f"{path}.green.passed must be boolean")
        elif final and green.get("passed") is not True:
            errors.append(f"{path}.green.passed must be true in final phase")


def validate_acceptance_tests(
    errors: list[str],
    tests: Any,
    bdd_ids: set[str],
    scenario_refs: dict[str, set[str]],
    *,
    final: bool,
) -> list[dict[str, Any]]:
    if not isinstance(tests, list):
        errors.append("acceptance_tests must be a list")
        return []
    if final and not tests:
        errors.append("acceptance_tests must be non-empty in final phase")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, test in enumerate(tests):
        path = f"acceptance_tests[{i}]"
        if not isinstance(test, dict):
            errors.append(f"{path} must be an object")
            continue
        tid = test.get("id")
        name = test.get("name")
        derived = test.get("derived_from")
        if not isinstance(tid, str) or not AT_ID_RE.match(tid):
            errors.append(f"{path}.id must match AT-<number>")
        elif tid in seen:
            errors.append(f"{path}.id duplicates {tid}")
        else:
            seen.add(tid)
        if not is_str(name):
            errors.append(f"{path}.name is required")
        elif isinstance(tid, str) and tid not in name:
            errors.append(f"{path}.name must include test id {tid}")
        if not isinstance(derived, str) or not SCENARIO_RE.match(derived):
            errors.append(f"{path}.derived_from must be BDD-N#scenario-slug")
        else:
            validate_scenario_ref(errors, derived, f"{path}.derived_from", bdd_ids, scenario_refs)
        if test.get("artifact_status") not in ARTIFACT_STATUSES:
            errors.append(f"{path}.artifact_status must be an artifact status")
        if test.get("status") not in TEST_HANDOFF_STATUSES:
            errors.append(f"{path}.status must be one of {sorted(TEST_HANDOFF_STATUSES)}")
        if final and test.get("status") in TEST_GREEN_STATUSES:
            validate_red_green(errors, test, path, final=True)
        out.append(test)
    return out


def validate_hypotheses(
    errors: list[str],
    hypotheses: Any,
    bdd_ids: set[str],
    scenario_refs: dict[str, set[str]],
    idx: dict[str, dict[str, Any]],
    *,
    final: bool,
) -> list[dict[str, Any]]:
    if not isinstance(hypotheses, list):
        errors.append("hypotheses must be a list")
        return []
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, hyp in enumerate(hypotheses):
        path = f"hypotheses[{i}]"
        if not isinstance(hyp, dict):
            errors.append(f"{path} must be an object")
            continue
        hid = hyp.get("id")
        if not isinstance(hid, str) or not H_ID_RE.match(hid):
            errors.append(f"{path}.id must match H<number>")
        elif hid in seen:
            errors.append(f"{path}.id duplicates {hid}")
        else:
            seen.add(hid)

        decision = hyp.get("decision")
        status = hyp.get("status")
        if decision not in {"accepted", "rejected"}:
            errors.append(f"{path}.decision must be accepted or rejected")
        if status not in {"pending", "green", "manual", "deferred", "merged", "rejected"}:
            errors.append(f"{path}.status is invalid")
        if decision == "rejected" and status != "rejected":
            errors.append(f"{path}.status must be rejected when decision is rejected")
        if decision == "accepted" and status == "rejected":
            errors.append(f"{path}.status cannot be rejected when decision is accepted")

        derived = hyp.get("derived_from")
        if not is_str(derived):
            errors.append(f"{path}.derived_from is required")
        elif derived != "internal":
            if not SCENARIO_RE.match(str(derived)):
                errors.append(f"{path}.derived_from must be internal or BDD-N#scenario-slug")
            else:
                validate_scenario_ref(errors, str(derived), f"{path}.derived_from", bdd_ids, scenario_refs)
        else:
            source = hyp.get("source")
            if not is_str(source):
                errors.append(f"{path}.source is required when derived_from is internal")
            elif str(source).split("#", 1)[0] not in idx:
                errors.append(f"{path}.source {source} does not exist")

        evidence = hyp.get("evidence")
        kinds: set[str] = set()
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{path}.evidence must be non-empty")
        else:
            for j, ev in enumerate(evidence):
                ep = f"{path}.evidence[{j}]"
                if not isinstance(ev, dict):
                    errors.append(f"{ep} must be an object")
                    continue
                kind = ev.get("kind")
                if is_str(kind):
                    kinds.add(str(kind))
                if not is_str(ev.get("path")):
                    errors.append(f"{ep}.path is required")
                if not is_str(ev.get("summary")):
                    errors.append(f"{ep}.summary is required")
        if decision == "accepted" and not (kinds & BEHAVIOR_KINDS):
            errors.append(f"{path} is accepted but has no behavior-source evidence")

        if final and status in TEST_GREEN_STATUSES:
            if not is_str(hyp.get("name")):
                errors.append(f"{path}.name is required when status is {status}")
            elif isinstance(hid, str) and hid not in str(hyp.get("name")):
                errors.append(f"{path}.name must include hypothesis id {hid}")
            if hyp.get("artifact_status") not in ARTIFACT_STATUSES:
                errors.append(f"{path}.artifact_status is required when status is {status}")
            validate_red_green(errors, hyp, path, final=True)
        if final and status == "manual":
            manual = hyp.get("manual_qa")
            if not isinstance(manual, list) or not manual:
                errors.append(f"{path}.manual_qa is required when status is manual")
        out.append(hyp)
    return out


def validate(data: dict[str, Any], phase: str, repo_root: Path | None, ledger_path: Path | None) -> list[str]:
    errors: list[str] = []
    final = phase == "final"
    required = [
        "schema", "run_id", "stage", "repo", "task", "mode", "created_at",
        "intent", "bdd", "enforce_plan", "ci_facts_contract", "related_adrs",
        "adr_coverage", "context_read", "unknowns", "acceptance_tests",
        "hypotheses", "cycles", "sensitivity", "manual_qa", "touched_files",
    ]
    for key in required:
        if key not in data:
            errors.append(f"{key} is required")
    if errors:
        return errors

    if data.get("schema") != "eg-ledger/v1":
        errors.append("schema must be eg-ledger/v1")
    if data.get("mode") not in {"lite", "full"}:
        errors.append("mode must be lite or full")
    if not is_str(data.get("run_id")) or not str(data.get("run_id")).startswith("EG-RUN-"):
        errors.append("run_id must start with EG-RUN-")

    idx = artifact_index(repo_root) if repo_root else {}
    scenario_refs = bdd_scenario_index(repo_root, idx) if repo_root else {}
    intent_id, intent_status = validate_artifact_ref(errors, data.get("intent"), "intent", idx, require_live=bool(repo_root))
    if intent_status in ARTIFACT_STATUSES and intent_status not in INTENT_OK:
        errors.append("intent.status must be review or approved")
    if intent_status == "review":
        errors.append("intent.status must be approved before freezing plan, writing tests, or emitting handoff")
    if repo_root and intent_id:
        live = idx.get(intent_id)
        if live and live.get("type") != "intent":
            errors.append(f"intent {intent_id} must have type: intent")

    bdd_refs = data.get("bdd")
    bdd_ids: set[str] = set()
    if not isinstance(bdd_refs, list) or not bdd_refs:
        errors.append("bdd must be non-empty before planning/final validation")
    else:
        for i, ref in enumerate(bdd_refs):
            bid, status = validate_artifact_ref(errors, ref, f"bdd[{i}]", idx, require_live=bool(repo_root))
            if bid:
                bdd_ids.add(bid)
                if status not in BDD_TESTABLE:
                    errors.append(f"{bid} must be approved before tests are derived")
                if repo_root:
                    validate_bdd_approval(errors, bid, idx)

    required_at_ids = validate_enforce_plan(errors, data, bdd_ids, scenario_refs)
    validate_frozen_plan_file(errors, data, ledger_path)
    validate_ci_facts_contract(errors, data, required_at_ids, final=final)
    validate_context(errors, data)
    validate_acceptance_tests(errors, data.get("acceptance_tests"), bdd_ids, scenario_refs, final=final)
    hypotheses = validate_hypotheses(errors, data.get("hypotheses"), bdd_ids, scenario_refs, idx, final=final)
    validate_adr_coverage(errors, data, idx, scenario_refs, final=final)

    if final:
        accepted = [h for h in hypotheses if h.get("decision") == "accepted"]
        if not accepted:
            errors.append("at least one accepted hypothesis is required in final phase")
        if not isinstance(data.get("touched_files"), list) or not data.get("touched_files"):
            errors.append("touched_files must be non-empty in final phase")

    return errors


def handoff_tests(data: dict[str, Any]) -> list[dict[str, Any]]:
    tests: list[dict[str, Any]] = []
    for test in data.get("acceptance_tests", []):
        if not isinstance(test, dict):
            continue
        tests.append({
            "id": test.get("id"),
            "name": test.get("name"),
            "derived_from": test.get("derived_from"),
            "artifact_status": test.get("artifact_status"),
            "status": test.get("status"),
        })
    for hyp in data.get("hypotheses", []):
        if not isinstance(hyp, dict):
            continue
        status = hyp.get("status")
        if status not in TEST_HANDOFF_STATUSES:
            continue
        item = {
            "id": hyp.get("id"),
            "name": hyp.get("name"),
            "derived_from": hyp.get("derived_from"),
            "artifact_status": hyp.get("artifact_status"),
            "status": status,
        }
        if hyp.get("derived_from") == "internal":
            item["source"] = hyp.get("source")
        tests.append(item)
    return tests


def handoff_manual_qa(data: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in data.get("manual_qa", []) or []:
        if isinstance(item, dict) and is_str(item.get("item")):
            out.append({"hypothesis": item.get("hypothesis", ""), "item": item["item"]})
    for hyp in data.get("hypotheses", []) or []:
        if not isinstance(hyp, dict) or hyp.get("status") != "manual":
            continue
        for item in hyp.get("manual_qa", []) or []:
            if is_str(item):
                out.append({"hypothesis": hyp.get("id", ""), "item": item})
    return out


def emit_handoff(data: dict[str, Any], ledger_path: Path, out_path: Path, *, force: bool = False) -> None:
    handoff = {
        "schema": "eg-handoff/v1",
        "run_id": data["run_id"],
        "stage": "tdd-complete",
        "repo": data["repo"],
        "agent": "codex",
        "intent": data["intent"],
        "bdd": data["bdd"],
        "enforce_plan": data["enforce_plan"],
        "ci_facts_contract": data["ci_facts_contract"],
        "related_adrs": data["related_adrs"],
        "adr_coverage": data["adr_coverage"],
        "tests": handoff_tests(data),
        "manual_qa": handoff_manual_qa(data),
        "tmp_run_dir": str(ledger_path.parent),
        "tmp_run_dir_authoritative": False,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and not force:
        print(f"ERROR: handoff already exists; pass --force-handoff to overwrite: {out_path}", file=sys.stderr)
        raise SystemExit(2)
    out_path.write_text(yaml.safe_dump(handoff, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate EG TDD ledger.")
    parser.add_argument("path", help="Path to /tmp/eg/<run-id>/ledger.json")
    parser.add_argument("--phase", choices=["planning", "final"], default="planning")
    parser.add_argument("--repo-root", help="Repo root to validate live ADR/BDD frontmatter.")
    parser.add_argument("--emit-handoff", help="On clean final validation, write .eg/handoff/<run-id>.yml")
    parser.add_argument("--force-handoff", action="store_true", help="Allow overwriting an existing handoff.")
    parser.add_argument("--emit-manifest", help="Deprecated; use --emit-handoff", default=None)
    args = parser.parse_args()

    if args.emit_manifest:
        print("ERROR: --emit-manifest is deprecated; use --emit-handoff", file=sys.stderr)
        return 2

    ledger_path = ensure_under_tmp_eg_run(Path(args.path))
    data = load_json(ledger_path)
    phase = "final" if args.emit_handoff else args.phase
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None

    errors = validate(data, phase, repo_root, ledger_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.emit_handoff:
        emit_handoff(data, ledger_path, Path(args.emit_handoff), force=args.force_handoff)
        print(f"OK: {ledger_path} (final); handoff -> {args.emit_handoff}")
    else:
        print(f"OK: {ledger_path} ({phase})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
