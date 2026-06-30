"""Deep validation for EG diagnosis artifacts.

Adapted from eg-diagnose/scripts/validate-diagnosis.py. The only behavioural
change: `is_str` now means "filled string" (store.filled_str), so placeholders
like TBD no longer pass, and `defer: <reason>` counts as a real answer. The
`sealed` flag toggles the stage==diagnosis-complete requirement so `eg check`
can run before sealing. This module is the single source of the enum sets.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

from store import filled_str as is_str  # filled-aware; kills the TBD blind spot

REQUIRED_CATEGORIES = {
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
}
FINDING_TYPES = {"root_cause", "probable_root_cause", "hypothesis"}
CONFIDENCE = {"high", "medium", "low"}
EVIDENCE_STRENGTH = {"direct", "supporting", "contradicting"}
SOURCE_GAP_STATUS = {"complete", "blocked", "degraded"}
PROBLEM_STATUS = {"explained", "probable", "hypothesis", "blocked"}
QUERY_OPERATIONS = {"SELECT", "SHOW", "DESCRIBE", "EXPLAIN", "ES_SEARCH", "LOG_SEARCH", "HTTP_GET", "LOCAL_READ"}
SAFE_SECRET_VALUES = {"", "redacted", "<redacted>", "***", "****", "none", "null"}
SECRET_KEY_RE = re.compile(r"(password|passwd|pwd|token|secret|private[_-]?key|access[_-]?key)", re.I)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
INLINE_SECRET_RE = re.compile(r"(password|passwd|pwd|token|secret)\s*[:=]\s*([^\\s,;]+)", re.I)


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    except yaml.YAMLError as exc:
        print(f"ERROR: invalid yaml {path}: {exc}", file=sys.stderr)
        raise SystemExit(2)


def under_tmp_eg(path: Path) -> bool:
    resolved = path.resolve()
    root = Path("/tmp/eg")
    return resolved == root or root in resolved.parents


def same_run(path: str, run_id: str) -> bool:
    if not path:
        return False
    p = Path(path)
    return under_tmp_eg(p) and run_id in p.parts


def raw_source_path(path: str, run_id: str) -> bool:
    if not same_run(path, run_id):
        return False
    parts = Path(path).parts
    try:
        idx = parts.index(run_id)
    except ValueError:
        return False
    return len(parts) > idx + 1 and parts[idx + 1] == "sources"


def collect_secret_errors(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if SECRET_KEY_RE.search(key_text):
                text = str(child).strip().lower() if child is not None else ""
                if text not in SAFE_SECRET_VALUES and not text.startswith("<"):
                    errors.append(f"{child_path} contains unredacted secret-like value")
            collect_secret_errors(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            collect_secret_errors(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        for match in INLINE_SECRET_RE.finditer(value):
            secret_value = match.group(2).strip().lower()
            if secret_value not in SAFE_SECRET_VALUES and not secret_value.startswith("<"):
                errors.append(f"{path} contains inline unredacted secret-like value")
        if EMAIL_RE.search(value):
            errors.append(f"{path} contains full email address; derived artifacts must redact it")


def validate_source_matrix(path: Path, run_id: str, errors: list[str]) -> dict[str, Any]:
    if not under_tmp_eg(path):
        errors.append("source_matrix must be under /tmp/eg")
        return {}
    data = load_yaml(path)
    if not isinstance(data, dict):
        errors.append("source_matrix must be an object")
        return {}
    if data.get("schema") != "eg-source-matrix/v1":
        errors.append("source_matrix.schema must be eg-source-matrix/v1")
    if data.get("run_id") != run_id:
        errors.append("source_matrix.run_id must match diagnosis.run_id")
    categories = data.get("categories")
    if not isinstance(categories, list):
        errors.append("source_matrix.categories must be a list")
        return data
    seen: set[str] = set()
    for index, item in enumerate(categories):
        item_path = f"source_matrix.categories[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_path} must be an object")
            continue
        category = item.get("category")
        if category not in REQUIRED_CATEGORIES:
            errors.append(f"{item_path}.category must be one of required taxonomy categories")
        elif category in seen:
            errors.append(f"{item_path}.category duplicates {category}")
        else:
            seen.add(category)
        if not isinstance(item.get("needed"), bool):
            errors.append(f"{item_path}.needed must be boolean")
        for key in ("reason", "impact_if_missing", "access_mode"):
            if not is_str(item.get(key)):
                errors.append(f"{item_path}.{key} is required")
        for key in ("available", "missing"):
            if not isinstance(item.get(key), list):
                errors.append(f"{item_path}.{key} must be a list")
    missing_categories = REQUIRED_CATEGORIES - seen
    if missing_categories:
        errors.append(f"source_matrix missing categories: {', '.join(sorted(missing_categories))}")
    collect_secret_errors(data, "source_matrix", errors)
    return data


def validate_source_gap(path: Path, run_id: str, errors: list[str]) -> dict[str, Any]:
    if not under_tmp_eg(path):
        errors.append("source_gap must be under /tmp/eg")
        return {}
    data = load_yaml(path)
    if not isinstance(data, dict):
        errors.append("source_gap must be an object")
        return {}
    if data.get("schema") != "eg-source-gap/v1":
        errors.append("source_gap.schema must be eg-source-gap/v1")
    if data.get("run_id") != run_id:
        errors.append("source_gap.run_id must match diagnosis.run_id")
    if data.get("status") not in SOURCE_GAP_STATUS:
        errors.append(f"source_gap.status must be one of {sorted(SOURCE_GAP_STATUS)}")
    for key in ("available", "missing", "questions_for_user"):
        if not isinstance(data.get(key), list):
            errors.append(f"source_gap.{key} must be a list")
    if data.get("status") == "blocked" and not data.get("questions_for_user"):
        errors.append("source_gap.questions_for_user is required when status is blocked")
    if data.get("status") == "degraded" and not is_str(data.get("degraded_reason")):
        errors.append("source_gap.degraded_reason is required when status is degraded")
    collect_secret_errors(data, "source_gap", errors)
    return data


def validate_query_plan(path: Path, run_id: str, errors: list[str]) -> None:
    if not path.exists():
        return
    if not under_tmp_eg(path):
        errors.append("query_plan must be under /tmp/eg")
        return
    data = load_yaml(path)
    if not isinstance(data, dict):
        errors.append("query_plan must be an object")
        return
    if data.get("schema") != "eg-query-plan/v1":
        errors.append("query_plan.schema must be eg-query-plan/v1")
    if data.get("run_id") != run_id:
        errors.append("query_plan.run_id must match diagnosis.run_id")
    queries = data.get("queries")
    if not isinstance(queries, list):
        errors.append("query_plan.queries must be a list")
        return
    for index, query in enumerate(queries):
        qpath = f"query_plan.queries[{index}]"
        if not isinstance(query, dict):
            errors.append(f"{qpath} must be an object")
            continue
        for key in ("id", "source", "purpose", "operation", "risk", "expected_evidence"):
            if not is_str(query.get(key)):
                errors.append(f"{qpath}.{key} is required")
        operation = str(query.get("operation", "")).upper()
        if operation not in QUERY_OPERATIONS:
            errors.append(f"{qpath}.operation is not read-only; explicit user confirmation required")
    side_effects = data.get("side_effecting_operations", [])
    if side_effects:
        errors.append("query_plan.side_effecting_operations must be empty unless user explicitly approved and diagnosis stops before mutation")


def validate_symptoms(data: dict[str, Any], errors: list[str]) -> set[str]:
    symptoms = data.get("symptoms")
    if not isinstance(symptoms, list) or not symptoms:
        errors.append("symptoms must be a non-empty list")
        return set()
    seen: set[str] = set()
    for index, item in enumerate(symptoms):
        path = f"symptoms[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        sid = item.get("id")
        if not is_str(sid):
            errors.append(f"{path}.id is required")
        elif sid in seen:
            errors.append(f"{path}.id duplicates {sid}")
        else:
            seen.add(str(sid))
        if not is_str(item.get("description")):
            errors.append(f"{path}.description is required")
    return seen


def validate_findings(data: dict[str, Any], symptom_ids: set[str], source_gap: dict[str, Any], errors: list[str]) -> set[str]:
    findings = data.get("root_causes")
    if not isinstance(findings, list):
        errors.append("root_causes must be a list")
        return set()
    ids: set[str] = set()
    for index, item in enumerate(findings):
        path = f"root_causes[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        fid = item.get("id")
        if not is_str(fid):
            errors.append(f"{path}.id is required")
        elif fid in ids:
            errors.append(f"{path}.id duplicates {fid}")
        else:
            ids.add(str(fid))
        finding_type = item.get("finding_type")
        confidence = item.get("confidence")
        if finding_type not in FINDING_TYPES:
            errors.append(f"{path}.finding_type must be one of {sorted(FINDING_TYPES)}")
        if confidence not in CONFIDENCE:
            errors.append(f"{path}.confidence must be one of {sorted(CONFIDENCE)}")
        if finding_type == "hypothesis" and confidence == "high":
            errors.append(f"{path} hypothesis cannot have high confidence")
        if finding_type == "probable_root_cause" and confidence == "high":
            errors.append(f"{path} probable_root_cause cannot have high confidence")
        explains = item.get("explains")
        if not isinstance(explains, list) or not explains:
            errors.append(f"{path}.explains must be a non-empty list")
            explains = []
        for symptom in explains:
            if symptom not in symptom_ids:
                errors.append(f"{path}.explains references unknown symptom {symptom!r}")
        if not is_str(item.get("summary")):
            errors.append(f"{path}.summary is required")
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{path}.evidence must be non-empty")
            evidence = []
        direct = 0
        supporting_types: set[str] = set()
        for ev_index, ev in enumerate(evidence):
            ev_path = f"{path}.evidence[{ev_index}]"
            if not isinstance(ev, dict):
                errors.append(f"{ev_path} must be an object")
                continue
            for key in ("id", "source_type", "source_ref", "strength", "summary"):
                if not is_str(ev.get(key)):
                    errors.append(f"{ev_path}.{key} is required")
            if ev.get("strength") not in EVIDENCE_STRENGTH:
                errors.append(f"{ev_path}.strength must be one of {sorted(EVIDENCE_STRENGTH)}")
            if ev.get("strength") == "direct":
                direct += 1
            if ev.get("strength") in {"direct", "supporting"} and is_str(ev.get("source_type")):
                supporting_types.add(str(ev["source_type"]))
            source_ref = str(ev.get("source_ref") or "")
            if source_ref.startswith("/tmp/eg/") and not same_run(source_ref, str(data["run_id"])):
                errors.append(f"{ev_path}.source_ref must stay within this run")
        if finding_type == "root_cause":
            if source_gap.get("status") != "complete" and confidence == "high":
                errors.append(f"{path} high-confidence root_cause requires complete source_gap")
            if confidence == "high" and direct == 0 and len(supporting_types) < 2:
                errors.append(f"{path} high-confidence root_cause requires direct evidence or two independent source types")
    return ids


def validate_problem_findings(
    data: dict[str, Any],
    symptom_ids: set[str],
    finding_ids: set[str],
    option_ids: set[str],
    errors: list[str],
) -> set[str]:
    items = data.get("problem_findings")
    if not isinstance(items, list) or not items:
        errors.append("problem_findings must be a non-empty list with one item per symptom")
        return set()
    seen_ids: set[str] = set()
    seen_symptoms: set[str] = set()
    for index, item in enumerate(items):
        path = f"problem_findings[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        pid = item.get("id")
        if not is_str(pid):
            errors.append(f"{path}.id is required")
        elif pid in seen_ids:
            errors.append(f"{path}.id duplicates {pid}")
        else:
            seen_ids.add(str(pid))
        symptom = item.get("symptom")
        if symptom not in symptom_ids:
            errors.append(f"{path}.symptom references unknown symptom {symptom!r}")
        elif symptom in seen_symptoms:
            errors.append(f"{path}.symptom duplicates {symptom}")
        else:
            seen_symptoms.add(str(symptom))
        for key in ("problem", "root_cause"):
            if not is_str(item.get(key)):
                errors.append(f"{path}.{key} is required")
        status = item.get("status")
        finding_type = item.get("finding_type")
        confidence = item.get("confidence")
        if status not in PROBLEM_STATUS:
            errors.append(f"{path}.status must be one of {sorted(PROBLEM_STATUS)}")
        if finding_type not in FINDING_TYPES:
            errors.append(f"{path}.finding_type must be one of {sorted(FINDING_TYPES)}")
        if confidence not in CONFIDENCE:
            errors.append(f"{path}.confidence must be one of {sorted(CONFIDENCE)}")
        if status == "explained" and finding_type != "root_cause":
            errors.append(f"{path}.finding_type must be root_cause when status is explained")
        if status == "probable" and finding_type != "probable_root_cause":
            errors.append(f"{path}.finding_type must be probable_root_cause when status is probable")
        if status == "hypothesis" and finding_type != "hypothesis":
            errors.append(f"{path}.finding_type must be hypothesis when status is hypothesis")
        cause_refs = item.get("cause_refs")
        if not isinstance(cause_refs, list):
            errors.append(f"{path}.cause_refs must be a list")
            cause_refs = []
        if status != "blocked" and not cause_refs:
            errors.append(f"{path}.cause_refs must be non-empty unless status is blocked")
        for ref in cause_refs:
            if ref not in finding_ids:
                errors.append(f"{path}.cause_refs references unknown finding {ref!r}")
                continue
            for finding in data.get("root_causes", []) or []:
                if isinstance(finding, dict) and finding.get("id") == ref:
                    if symptom not in (finding.get("explains") or []):
                        errors.append(f"{path}.cause_refs {ref!r} does not explain symptom {symptom!r}")
                    break
        evidence = item.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{path}.evidence must be a list")
            evidence = []
        if status != "blocked" and not evidence:
            errors.append(f"{path}.evidence must be non-empty unless status is blocked")
        direct = 0
        supporting_types: set[str] = set()
        for ev_index, ev in enumerate(evidence):
            ev_path = f"{path}.evidence[{ev_index}]"
            if not isinstance(ev, dict):
                errors.append(f"{ev_path} must be an object")
                continue
            for key in ("id", "source_type", "source_ref", "strength", "summary"):
                if not is_str(ev.get(key)):
                    errors.append(f"{ev_path}.{key} is required")
            if ev.get("strength") not in EVIDENCE_STRENGTH:
                errors.append(f"{ev_path}.strength must be one of {sorted(EVIDENCE_STRENGTH)}")
            if ev.get("strength") == "direct":
                direct += 1
            if ev.get("strength") in {"direct", "supporting"} and is_str(ev.get("source_type")):
                supporting_types.add(str(ev["source_type"]))
            source_ref = str(ev.get("source_ref") or "")
            if source_ref.startswith("/tmp/eg/") and not same_run(source_ref, str(data["run_id"])):
                errors.append(f"{ev_path}.source_ref must stay within this run")
        if finding_type == "root_cause" and confidence == "high" and direct == 0 and len(supporting_types) < 2:
            errors.append(f"{path} high-confidence root_cause requires direct evidence or two independent source types")
        missing_evidence = item.get("missing_evidence")
        if not isinstance(missing_evidence, list):
            errors.append(f"{path}.missing_evidence must be a list")
        elif status == "blocked" and not missing_evidence:
            errors.append(f"{path}.missing_evidence is required when status is blocked")
        fix_options = item.get("fix_options")
        if not isinstance(fix_options, list):
            errors.append(f"{path}.fix_options must be a list")
            fix_options = []
        if status != "blocked" and not fix_options:
            errors.append(f"{path}.fix_options must be non-empty unless status is blocked")
        for ref in fix_options:
            if ref not in option_ids:
                errors.append(f"{path}.fix_options references unknown fix option {ref!r}")
    missing = symptom_ids - seen_symptoms
    if missing:
        errors.append(f"problem_findings missing symptoms: {', '.join(sorted(missing))}")
    extra = seen_symptoms - symptom_ids
    if extra:
        errors.append(f"problem_findings has unknown symptoms: {', '.join(sorted(extra))}")
    return seen_symptoms


def validate_unexplained(data: dict[str, Any], symptom_ids: set[str], explained: set[str], errors: list[str]) -> None:
    unexplained = data.get("unexplained_symptoms")
    if not isinstance(unexplained, list):
        errors.append("unexplained_symptoms must be a list")
        return
    listed: set[str] = set()
    for index, item in enumerate(unexplained):
        path = f"unexplained_symptoms[{index}]"
        if isinstance(item, str):
            sid = item
        elif isinstance(item, dict):
            sid = item.get("symptom")
            if not item.get("missing_evidence"):
                errors.append(f"{path}.missing_evidence is required")
        else:
            errors.append(f"{path} must be a string or object")
            continue
        if sid not in symptom_ids:
            errors.append(f"{path} references unknown symptom {sid!r}")
        else:
            listed.add(str(sid))
    missing = symptom_ids - explained - listed
    if missing:
        errors.append(f"symptoms neither explained nor listed as unexplained: {', '.join(sorted(missing))}")


def validate_fix_options(data: dict[str, Any], finding_ids: set[str], errors: list[str]) -> set[str]:
    options = data.get("fix_options")
    if not isinstance(options, list):
        errors.append("fix_options must be a list")
        return set()
    ids: set[str] = set()
    for index, item in enumerate(options):
        path = f"fix_options[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        fid = item.get("id")
        if not is_str(fid):
            errors.append(f"{path}.id is required")
        elif fid in ids:
            errors.append(f"{path}.id duplicates {fid}")
        else:
            ids.add(str(fid))
        addresses = item.get("addresses")
        if not isinstance(addresses, list) or not addresses:
            errors.append(f"{path}.addresses must be non-empty")
            addresses = []
        for ref in addresses:
            if ref not in finding_ids:
                errors.append(f"{path}.addresses references unknown finding {ref!r}")
        for key in ("summary", "expected_effect", "risks", "required_validation"):
            if key == "summary":
                if not is_str(item.get(key)):
                    errors.append(f"{path}.{key} is required")
            elif not isinstance(item.get(key), list):
                errors.append(f"{path}.{key} must be a list")
        if item.get("needs_precipitation") is not True:
            errors.append(f"{path}.needs_precipitation must be true")
    return ids


def validate_handoff(data: dict[str, Any], finding_ids: set[str], option_ids: set[str], errors: list[str]) -> None:
    handoff = data.get("handoff_to_precipitate")
    if not isinstance(handoff, dict):
        errors.append("handoff_to_precipitate must be an object")
        return
    intents = handoff.get("proposed_intents")
    if not isinstance(intents, list):
        errors.append("handoff_to_precipitate.proposed_intents must be a list")
        return
    for index, item in enumerate(intents):
        path = f"handoff_to_precipitate.proposed_intents[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        if not is_str(item.get("id")):
            errors.append(f"{path}.id is required")
        if not is_str(item.get("summary")):
            errors.append(f"{path}.summary is required")
        based_on = item.get("based_on")
        if not isinstance(based_on, dict):
            errors.append(f"{path}.based_on must be an object")
            continue
        for ref in based_on.get("root_causes", []) or []:
            if ref not in finding_ids:
                errors.append(f"{path}.based_on.root_causes references unknown finding {ref!r}")
        for ref in based_on.get("fix_options", []) or []:
            if ref not in option_ids:
                errors.append(f"{path}.based_on.fix_options references unknown fix option {ref!r}")
        for key in ("acceptance_seed_candidates", "decisions_needed", "constraints_to_check"):
            if not isinstance(item.get(key), list):
                errors.append(f"{path}.{key} must be a list")


def validate_sensitive_material(data: dict[str, Any], run_id: str, errors: list[str]) -> None:
    sensitive = data.get("sensitive_material")
    if not isinstance(sensitive, dict):
        errors.append("sensitive_material must be an object")
        return
    if sensitive.get("do_not_copy_to_repo") is not True:
        errors.append("sensitive_material.do_not_copy_to_repo must be true")
    paths = sensitive.get("paths")
    if not isinstance(paths, list):
        errors.append("sensitive_material.paths must be a list")
        return
    for index, path in enumerate(paths):
        if not isinstance(path, str) or not raw_source_path(path, run_id):
            errors.append(f"sensitive_material.paths[{index}] must be under /tmp/eg/{run_id}/sources")


def validate_preview(diagnosis_path: Path, data: dict[str, Any], errors: list[str]) -> None:
    preview_path = diagnosis_path.with_name("diagnosis-preview.md")
    if not preview_path.exists():
        errors.append("diagnosis-preview.md must exist next to diagnosis.yml")
        return
    if not under_tmp_eg(preview_path):
        errors.append("diagnosis-preview.md must be under /tmp/eg")
        return
    preview = preview_path.read_text(encoding="utf-8")
    if "## 分析结果" not in preview:
        errors.append("diagnosis-preview.md must contain '## 分析结果'")
    for index, item in enumerate(data.get("problem_findings", []) or []):
        if not isinstance(item, dict):
            continue
        pid = item.get("id")
        if is_str(pid) and f"### {pid}:" not in preview:
            errors.append(f"diagnosis-preview.md missing heading for problem_findings[{index}] {pid}")
    if "\n## 根因" in preview and "\n## 依据" in preview:
        errors.append("diagnosis-preview.md must not use separated global root-cause/evidence sections")


def validate(data: dict[str, Any], diagnosis_path: Path, sealed: bool = True) -> list[str]:
    """Full diagnosis validation. With sealed=False the stage==diagnosis-complete
    requirement is skipped so `eg check` can run before sealing."""
    errors: list[str] = []
    if data.get("schema") != "eg-diagnosis/v1":
        errors.append("schema must be eg-diagnosis/v1")
    run_id = data.get("run_id")
    if not is_str(run_id) or not str(run_id).startswith("EG-RUN-"):
        errors.append("run_id must start with EG-RUN-")
        run_id = ""
    if not under_tmp_eg(diagnosis_path):
        errors.append("diagnosis.yml must be under /tmp/eg")
    if diagnosis_path.name != "diagnosis.yml":
        errors.append("diagnosis file must be named diagnosis.yml")
    for key in ("stage", "repo", "task", "created_at"):
        if not is_str(data.get(key)):
            errors.append(f"{key} is required")
    if sealed and data.get("stage") != "diagnosis-complete":
        errors.append("stage must be diagnosis-complete before declaring completion")
    if errors:
        return errors

    source_matrix_path = Path(str(data.get("source_matrix") or ""))
    source_gap_path = Path(str(data.get("source_gap") or ""))
    query_plan_path = Path(str(data.get("query_plan") or ""))
    validate_source_matrix(source_matrix_path, str(run_id), errors)
    source_gap = validate_source_gap(source_gap_path, str(run_id), errors)
    validate_query_plan(query_plan_path, str(run_id), errors)
    validate_sensitive_material(data, str(run_id), errors)

    symptom_ids = validate_symptoms(data, errors)
    finding_ids = validate_findings(data, symptom_ids, source_gap, errors)
    option_ids = validate_fix_options(data, finding_ids, errors)
    validate_problem_findings(data, symptom_ids, finding_ids, option_ids, errors)
    explained = set()
    for finding in data.get("root_causes", []) or []:
        if isinstance(finding, dict):
            for sid in finding.get("explains", []) or []:
                if isinstance(sid, str):
                    explained.add(sid)
    validate_unexplained(data, symptom_ids, explained, errors)
    validate_handoff(data, finding_ids, option_ids, errors)
    if sealed:
        validate_preview(diagnosis_path, data, errors)

    collect_secret_errors(data, "diagnosis", errors)
    return errors
