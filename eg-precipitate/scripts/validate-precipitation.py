#!/usr/bin/env python3
"""Validate EG precipitation ADR artifacts."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


TYPES = {"intent", "decision", "constraint"}
STATUSES = {"draft", "review", "approved", "deprecated"}
DOMAINS = {"security", "cost", "performance", "observability", "other"}
BDD_RE = re.compile(r"(^##\s+Scenario:|^\s*Given\s+|^\s*When\s+|^\s*Then\s+)", re.MULTILINE)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return {}, text[end + 4 :]
    return (data if isinstance(data, dict) else {}), text[end + 4 :]


def non_empty_section(body: str, heading: str) -> bool:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", body, re.MULTILINE)
    if not match:
        return False
    rest = body[match.end() :]
    next_heading = re.search(r"^##\s+", rest, re.MULTILINE)
    section = rest[: next_heading.start()] if next_heading else rest
    stripped = section.strip()
    return bool(stripped and stripped != "-")


def validate(path: Path, *, require_seed: bool) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(text)
    number_match = re.match(r"^([0-9]{4})-", path.name)
    if not number_match:
        errors.append("ADR filename must start with 0001- style numbering")
    expected_id = f"ADR-{number_match.group(1)}" if number_match else ""
    adr_id = fm.get("id")
    adr_type = fm.get("type")
    status = fm.get("status")
    if adr_id != expected_id:
        errors.append(f"frontmatter id must be {expected_id}")
    if adr_type not in TYPES:
        errors.append(f"type must be one of {sorted(TYPES)}")
    if status not in STATUSES:
        errors.append(f"status must be one of {sorted(STATUSES)}")
    if adr_type == "constraint" and fm.get("domain") not in DOMAINS:
        errors.append(f"constraint domain must be one of {sorted(DOMAINS)}")
    if BDD_RE.search(body):
        errors.append("precipitation ADR must not contain BDD scenarios or Given/When/Then")
    for heading in ("Context", "Decision"):
        if not non_empty_section(body, heading):
            errors.append(f"## {heading} must be present and non-empty")
    if adr_type == "intent":
        for heading in ("In Scope", "Out of Scope", "Non Goals"):
            if not non_empty_section(body, heading):
                errors.append(f"intent ADR requires non-empty ## {heading}")
        if require_seed and not non_empty_section(body, "Acceptance Criteria Seed"):
            errors.append("intent ADR ready for TDD requires non-empty ## Acceptance Criteria Seed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate EG precipitation ADR artifacts.")
    parser.add_argument("paths", nargs="+", help="ADR markdown files to validate.")
    parser.add_argument("--require-seed", action="store_true", help="Require Acceptance Criteria Seed for intent ADRs.")
    args = parser.parse_args()
    errors: list[str] = []
    for raw in args.paths:
        path = Path(raw)
        if not path.is_file():
            errors.append(f"{path}: not found")
            continue
        for error in validate(path, require_seed=args.require_seed):
            errors.append(f"{path}: {error}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(args.paths)} ADR artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
