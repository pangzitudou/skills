#!/usr/bin/env python3
"""Create a sequential EG ADR skeleton after write preview approval."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


TYPES = {"intent", "decision", "constraint"}
STATUSES = {"draft", "review", "approved"}
DOMAINS = {"security", "cost", "performance", "observability", "other"}


def die(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower())
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "adr"


def next_number(adr_dir: Path) -> int:
    highest = 0
    if adr_dir.is_dir():
        for path in adr_dir.glob("*.md"):
            match = re.match(r"^([0-9]{4})-", path.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return highest + 1


def frontmatter(adr_id: str, adr_type: str, status: str, domain: str) -> str:
    lines = ["---", f"id: {adr_id}", f"type: {adr_type}", f"status: {status}"]
    if adr_type == "constraint":
        lines.append(f"domain: {domain}")
    lines.append("---")
    return "\n".join(lines)


def skeleton(title: str, adr_type: str) -> str:
    sections = [
        f"# {title}",
        "",
        "## Context",
        "",
        "## Decision",
        "",
        "## Consequences",
        "",
    ]
    if adr_type == "intent":
        sections.extend([
            "## In Scope",
            "- ",
            "",
            "## Out of Scope",
            "- ",
            "",
            "## Non Goals",
            "- ",
            "",
            "## Acceptance Criteria Seed",
            "- ",
            "",
        ])
    return "\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a sequential EG ADR skeleton.")
    parser.add_argument("--repo-root", default=".", help="Repo root containing docs/adr.")
    parser.add_argument("--title", required=True, help="ADR title.")
    parser.add_argument("--type", required=True, choices=sorted(TYPES), help="ADR type.")
    parser.add_argument("--status", default="review", choices=sorted(STATUSES), help="Initial ADR status.")
    parser.add_argument("--domain", default="", help="Constraint domain.")
    args = parser.parse_args()

    if args.type == "constraint" and args.domain not in DOMAINS:
        die(f"--domain must be one of {sorted(DOMAINS)} for constraint ADRs")
    repo_root = Path(args.repo_root).resolve()
    adr_dir = repo_root / "docs/adr"
    adr_dir.mkdir(parents=True, exist_ok=True)
    number = next_number(adr_dir)
    adr_id = f"ADR-{number:04d}"
    path = adr_dir / f"{number:04d}-{slug(args.title)}.md"
    if path.exists():
        die(f"ADR already exists: {path}")
    content = frontmatter(adr_id, args.type, args.status, args.domain) + "\n\n" + skeleton(args.title, args.type)
    path.write_text(content, encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
