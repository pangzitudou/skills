#!/usr/bin/env python3
"""Write deterministic eg-enforce fix-agent handoff from finding ledger."""
import argparse
import json
import sys
from pathlib import Path

ORDER = ("regression", "partial-fix", "persisted", "new")


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"not found: {path}")
    except json.JSONDecodeError as exc:
        die(f"invalid json {path}: {exc}")


def ensure_under_tmp_eg_run(path):
    resolved = Path(path).expanduser().resolve()
    tmp_eg = Path("/tmp/eg").resolve()
    try:
        resolved.relative_to(tmp_eg)
    except ValueError:
        die(f"output path must be under /tmp/eg/<run-id>: {resolved}")
    if resolved == tmp_eg:
        die("output path must include /tmp/eg/<run-id>")
    return resolved


def run_id_from_path(path):
    parts = Path(path).parts
    if len(parts) >= 3 and parts[-2]:
        return parts[-2]
    return "<run-id>"


def selected_entries(ledger):
    entries = []
    for entry in ledger.get("findings", []) or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("status") != "open":
            continue
        if not entry.get("agent_fixable"):
            continue
        entries.append(entry)
    return sorted(entries, key=lambda e: (
        ORDER.index(e.get("lifecycle")) if e.get("lifecycle") in ORDER else len(ORDER),
        e.get("finding", {}).get("severity", ""),
        e.get("fingerprint", ""),
    ))


def bullet_list(values):
    return "\n".join(f"- `{value}`" for value in values)


def format_entry(entry):
    finding = entry.get("finding", {})
    required = entry.get("closure_required", {}).get("required_evidence", [])
    lines = [
        f"### `{entry.get('fingerprint')}`",
        "",
        f"- lifecycle: `{entry.get('lifecycle')}`",
        f"- class_key: `{entry.get('class_key')}`",
        f"- type: `{finding.get('type')}`",
        f"- severity: `{finding.get('severity')}`",
        f"- next_step: `{finding.get('next_step')}`",
        f"- artifactRef: `{finding.get('artifactRef')}`",
        f"- location: `{finding.get('location')}`",
        f"- ruleRef: `{finding.get('ruleRef')}`",
        f"- evidence: {finding.get('evidence')}",
        f"- impact: {finding.get('impact')}",
        "",
        "Closure required:",
        bullet_list(required),
    ]
    attempts = entry.get("closure_attempts", [])
    if attempts:
        lines.extend(["", "Previous closure attempts:"])
        for attempt in attempts:
            summary = attempt.get("summary") or attempt.get("code_change") or attempt.get("notes") or "(no summary)"
            lines.append(f"- round `{attempt.get('round', '?')}`: {summary}")
    return "\n".join(lines)


def closure_template(entries):
    return {
        "attempted": [
            {
                "fingerprint": entry.get("fingerprint"),
                "summary": "",
                "code_change": "",
                "class_sweep": "",
                "tests": [],
                "ci_facts": [],
                "commit": "",
                "notes": "",
            }
            for entry in entries
        ]
    }


def render(ledger_path, ledger, entries, args):
    run_id = run_id_from_path(ledger_path)
    closure_path = f"/tmp/eg/{run_id}/closure-evidence.json"
    lines = [
        "# EG Fix Handoff",
        "",
        f"Source ledger: `{ledger_path}`",
        f"Round: `{ledger.get('round')}`",
        "",
        "## Context",
        "",
        f"- repo_root: `{args.repo_root or '<repo>'}`",
        f"- pr_context: `{args.pr_context or ''}`",
        f"- diff: `{args.diff or ''}`",
        f"- selected_handoffs: `{args.handoffs or ''}`",
        f"- feedback: `{args.feedback or ledger.get('source_feedback', '')}`",
        f"- closure_evidence: `{closure_path}`",
        "",
        "## Scope",
        "",
        "- Fix only open agent-fixable findings listed below.",
        "- Do not change approved ADR/BDD substance. Stop and ask human if a fix requires artifact changes.",
        "- Do not include unrelated refactors.",
        "- Commit the verified fix-scope changes when done.",
        "- Allowed code-change files must be recorded in `code_change`; do not modify approved ADR/BDD substance.",
        "",
        "## Closure Contract",
        "",
        "- Every listed fingerprint must be absent in the next eg-enforce round, or you must stop with a concrete blocker.",
        "- Sweep the whole class_key area, not only the exact fingerprint location.",
        "- Add or update a regression test when the finding is testable; otherwise record manual QA.",
        "- Run relevant verification and preserve CI/test evidence.",
        "- After committing, run `python3 <eg-enforce-skill>/scripts/validate-fix-commit-scope.py --repo-root <repo> --closure-evidence " + closure_path + "`.",
        f"- Write closure evidence to `{closure_path}` using this shape:",
        "",
        "```json",
        json.dumps(closure_template(entries), indent=2, ensure_ascii=False),
        "```",
        "",
        "## Findings",
        "",
    ]
    for lifecycle in ORDER:
        group = [entry for entry in entries if entry.get("lifecycle") == lifecycle]
        if not group:
            continue
        lines.extend([f"## {lifecycle}", ""])
        for entry in group:
            lines.extend([format_entry(entry), ""])
    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Write eg-enforce fix handoff from finding ledger.")
    ap.add_argument("--ledger", required=True, help="finding-ledger.json")
    ap.add_argument("--out", required=True, help="fix-handoff.md output")
    ap.add_argument("--repo-root", help="Repo root for the fix agent.")
    ap.add_argument("--pr-context", help="PR context JSON used by enforce.")
    ap.add_argument("--diff", help="PR diff path used by enforce.")
    ap.add_argument("--handoffs", help="selected_handoffs.json used by enforce.")
    ap.add_argument("--feedback", help="feedback.json used to build the ledger.")
    args = ap.parse_args()

    ledger = load_json(args.ledger)
    entries = selected_entries(ledger)
    if not entries:
        die("no open agent-fixable findings in ledger")
    out = ensure_under_tmp_eg_run(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(args.ledger, ledger, entries, args), encoding="utf-8")
    print(f"fix-handoff findings={len(entries)} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
