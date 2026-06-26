#!/usr/bin/env python3
"""Update eg-enforce finding lifecycle ledger.

Reads feedback.json from enforce.py and writes /tmp/eg/<run-id>/finding-ledger.json.
The ledger lets later enforce rounds distinguish new findings from persisted,
partially fixed, regressed, and closed findings.
"""
import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

LIFECYCLES = ("new", "persisted", "partial-fix", "regression", "closed", "superseded")
OPEN_LIFECYCLES = {"new", "persisted", "partial-fix", "regression"}


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path, required=True):
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        if required:
            die(f"not found: {path}")
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"invalid json {path}: {exc}")


def normalize_part(value):
    text = str(value or "").strip()
    return re.sub(r"\s+", " ", text).lower()


def normalize_location(value):
    text = normalize_part(value)
    return re.sub(r"(?<=\S):\d+(?::\d+)?\b", "", text)


def fingerprint_basis(finding):
    return {
        "type": normalize_part(finding.get("type")),
        "artifactRef": normalize_part(finding.get("artifactRef")),
        "ruleRef": normalize_part(finding.get("ruleRef")),
        "location": normalize_location(finding.get("location")),
    }


def fingerprint(finding):
    if finding.get("fingerprint"):
        return str(finding["fingerprint"])
    basis = fingerprint_basis(finding)
    raw = "\n".join(basis[key] for key in ("type", "artifactRef", "ruleRef", "location"))
    return "egf-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def compact_finding(finding):
    keys = (
        "fingerprint", "type", "section", "artifactRef", "ruleRef", "evidence",
        "impact", "location", "source", "severity", "next_step",
        "enforcement_level", "human_review_required", "humanVerify", "waived",
    )
    return {key: finding.get(key) for key in keys if key in finding}


def load_closure_attempts(path):
    doc = load_json(path, required=False)
    attempts = {}
    if not doc:
        return attempts
    raw = doc.get("attempted", doc.get("findings", []))
    if isinstance(raw, dict):
        raw = [{"fingerprint": key, **value} for key, value in raw.items() if isinstance(value, dict)]
    if not isinstance(raw, list):
        die("closure evidence must contain attempted[] or findings[]")
    for item in raw:
        if not isinstance(item, dict):
            die("closure evidence entries must be objects")
        fp = item.get("fingerprint")
        if not fp:
            die("closure evidence entry missing fingerprint")
        attempts[str(fp)] = item
    return attempts


def build_current_findings(feedback):
    agent_fixable = {fingerprint(item) for item in feedback.get("agent_fix", [])}
    by_fp = {}
    for raw in feedback.get("findings", []):
        if not isinstance(raw, dict):
            die("feedback findings[] entries must be objects")
        item = dict(raw)
        fp = fingerprint(item)
        item["fingerprint"] = fp
        item.setdefault("fingerprint_basis", fingerprint_basis(item))
        item["agent_fixable"] = fp in agent_fixable
        if fp in by_fp:
            by_fp[fp].setdefault("_duplicates", []).append(compact_finding(item))
            continue
        by_fp[fp] = item
    return by_fp


def previous_entries(previous):
    entries = {}
    for item in previous.get("findings", []) or []:
        if not isinstance(item, dict) or not item.get("fingerprint"):
            continue
        entries[str(item["fingerprint"])] = item
    return entries


def closure_required(finding):
    next_step = finding.get("next_step")
    required = ["finding_absent_in_next_enforce"]
    if next_step == "fix-code":
        required.insert(0, "code_change")
        required.insert(1, "regression_test_or_manual_qa")
    elif next_step == "fix-test":
        required.insert(0, "test_change")
        required.insert(1, "test_id_in_ci_facts_or_handoff")
    elif next_step == "update-handoff":
        required.insert(0, "handoff_change")
    else:
        required.insert(0, "human_decision_or_scope_change")
    if finding.get("source") == "ci-facts" or finding.get("ruleRef") == "ci-facts":
        required.append("ci_fact_passed")
    return {
        "required_evidence": required,
        "must_reference_fingerprint": finding["fingerprint"],
        "must_commit_fix_scope": True,
    }


def history_event(round_no, lifecycle, status, finding=None, closure_attempt=None, close_reason=None):
    event = {"round": round_no, "lifecycle": lifecycle, "status": status}
    if finding is not None:
        event["finding"] = compact_finding(finding)
    if closure_attempt is not None:
        event["closure_attempt"] = closure_attempt
    if close_reason:
        event["close_reason"] = close_reason
    return event


def clone_history(entry):
    history = entry.get("history", [])
    return history if isinstance(history, list) else []


def update_seen_entry(prev, finding, round_no, attempt):
    was_closed = prev and prev.get("status") == "closed"
    was_open = prev and prev.get("status") == "open"
    if finding.get("waived"):
        lifecycle, status, close_reason = "closed", "closed", "waived"
    elif was_closed:
        lifecycle, status, close_reason = "regression", "open", None
    elif was_open and attempt:
        lifecycle, status, close_reason = "partial-fix", "open", None
    elif was_open:
        lifecycle, status, close_reason = "persisted", "open", None
    else:
        lifecycle, status, close_reason = "new", "open", None

    first_seen = prev.get("first_seen_round") if prev else None
    entry = {
        "fingerprint": finding["fingerprint"],
        "status": status,
        "lifecycle": lifecycle,
        "first_seen_round": first_seen or round_no,
        "last_seen_round": round_no,
        "closed_round": round_no if status == "closed" else None,
        "close_reason": close_reason,
        "agent_fixable": bool(finding.get("agent_fixable")),
        "finding": compact_finding(finding),
        "fingerprint_basis": finding.get("fingerprint_basis", fingerprint_basis(finding)),
        "closure_required": closure_required(finding),
        "closure_attempts": list((prev or {}).get("closure_attempts", [])),
        "history": clone_history(prev or {}),
    }
    if attempt:
        attempt = dict(attempt)
        attempt.setdefault("round", round_no)
        entry["closure_attempts"].append(attempt)
    entry["history"].append(history_event(round_no, lifecycle, status, finding, attempt, close_reason))
    if finding.get("_duplicates"):
        entry["current_duplicate_count"] = len(finding["_duplicates"]) + 1
        entry["current_duplicates"] = finding["_duplicates"]
    return entry


def update_absent_entry(prev, round_no):
    entry = dict(prev)
    if prev.get("status") == "open":
        entry["status"] = "closed"
        entry["lifecycle"] = "closed"
        entry["closed_round"] = round_no
        entry["close_reason"] = "absent-in-current-enforce"
        entry["history"] = clone_history(prev)
        entry["history"].append(history_event(
            round_no, "closed", "closed", close_reason="absent-in-current-enforce"))
    return entry


def summary_item(entry):
    finding = entry.get("finding", {})
    return {
        "fingerprint": entry.get("fingerprint"),
        "type": finding.get("type"),
        "artifactRef": finding.get("artifactRef"),
        "location": finding.get("location"),
        "severity": finding.get("severity"),
        "next_step": finding.get("next_step"),
        "agent_fixable": entry.get("agent_fixable", False),
    }


def build_summary(entries, round_no):
    buckets = {name: [] for name in LIFECYCLES}
    for entry in entries:
        if entry.get("last_seen_round") == round_no or entry.get("closed_round") == round_no:
            lifecycle = entry.get("lifecycle")
            if lifecycle in buckets:
                buckets[lifecycle].append(summary_item(entry))
    counts = {name: len(items) for name, items in buckets.items()}
    counts["open"] = sum(1 for entry in entries if entry.get("status") == "open")
    counts["agent_fixable_open"] = sum(
        1 for entry in entries
        if entry.get("status") == "open" and entry.get("agent_fixable")
    )
    return {"counts": counts, "buckets": buckets}


def main():
    ap = argparse.ArgumentParser(description="Update eg-enforce finding lifecycle ledger.")
    ap.add_argument("--previous", help="previous finding-ledger.json; defaults to --out if it exists")
    ap.add_argument("--feedback", required=True, help="feedback.json from enforce.py")
    ap.add_argument("--closure-evidence", help="optional fix-agent closure evidence JSON")
    ap.add_argument("--round", required=True, type=int, help="enforce round number")
    ap.add_argument("--out", required=True, help="finding-ledger.json output")
    args = ap.parse_args()

    if args.round < 1:
        die("--round must be >= 1")

    feedback = load_json(args.feedback)
    previous_path = args.previous or args.out
    previous = load_json(previous_path, required=False)
    previous_by_fp = previous_entries(previous)
    current_by_fp = build_current_findings(feedback)
    attempts = load_closure_attempts(args.closure_evidence)

    entries = []
    all_fps = sorted(set(previous_by_fp) | set(current_by_fp))
    for fp in all_fps:
        prev = previous_by_fp.get(fp)
        finding = current_by_fp.get(fp)
        if finding:
            entries.append(update_seen_entry(prev, finding, args.round, attempts.get(fp)))
        elif prev:
            entries.append(update_absent_entry(prev, args.round))

    out = {
        "schema_version": 1,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "round": args.round,
        "source_feedback": str(Path(args.feedback)),
        "source_previous": str(Path(previous_path)) if Path(previous_path).exists() else None,
        "source_closure_evidence": str(Path(args.closure_evidence)) if args.closure_evidence else None,
        "summary": build_summary(entries, args.round),
        "findings": entries,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    c = out["summary"]["counts"]
    print(
        f"finding-ledger round={args.round} open={c['open']} "
        f"new={c['new']} persisted={c['persisted']} partial={c['partial-fix']} "
        f"regression={c['regression']} closed={c['closed']} -> {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
