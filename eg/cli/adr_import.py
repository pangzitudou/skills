"""Import a legacy saler ADR .md into the eg .yml data model (sections form).

saler ADRs are free-form prose with arbitrary, mixed-language sections (Context /
决策 / numbered `1. ...` / Enforcement / 修订记录 ...). We preserve every section
verbatim as an ordered `sections: [{heading, body}]` list plus a `preamble` (prose
between the title and the first `##`), so the .yml round-trips back to the exact
.md. Only the frontmatter is structured/validated.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

import mirror

FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$")
H2_RE = re.compile(r"^##\s+(.+?)\s*$")
TITLE_NUM_RE = re.compile(r"^\d{3,4}\s+")
TYPES = {"intent", "decision", "constraint"}


def _normalize_adr_id(value: Any, number: int) -> str:
    text = str(value or "")
    m = re.search(r"ADR-(\d+)", text)
    return f"ADR-{int(m.group(1)):04d}" if m else f"ADR-{number:04d}"


def parse_adr_md(text: str, filename: str) -> tuple[dict, list[str]]:
    warnings: list[str] = []
    fm_match = FM_RE.match(text)
    if not fm_match:
        raise SystemExit(f"{filename}: no frontmatter")
    fm = yaml.safe_load(fm_match.group(1))
    fm = fm if isinstance(fm, dict) else {}
    body = fm_match.group(2)

    fname_m = re.match(r"^(\d{4})-(.*)\.md$", os.path.basename(filename))
    if not fname_m:
        raise SystemExit(f"{filename}: name must be NNNN-slug.md")
    number, file_slug = int(fname_m.group(1)), fname_m.group(2)

    adr_type = fm.get("type")
    if adr_type not in TYPES:
        warnings.append(f"{filename}: type {adr_type!r} is not one of {sorted(TYPES)} — fix it")

    title = file_slug
    preamble: list[str] = []
    sections: list[dict] = []
    cur: dict | None = None
    seen_title = False
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and not seen_title and H1_RE.match(line):
            title = TITLE_NUM_RE.sub("", H1_RE.match(line).group(1)).strip()
            seen_title = True
            continue
        if not in_fence and H2_RE.match(line):
            cur = {"heading": H2_RE.match(line).group(1).strip(), "body": []}
            sections.append(cur)
            continue
        (cur["body"] if cur is not None else preamble).append(line)

    for s in sections:
        s["body"] = "\n".join(s["body"]).strip()
    if not sections:
        warnings.append(f"{filename}: no ## sections parsed (all prose went to preamble)")

    data = {
        "schema": "eg-adr/v1",
        "id": _normalize_adr_id(fm.get("id"), number),
        "type": adr_type,
        "status": str(fm.get("status") or "approved"),
        "title": title or file_slug,
        "slug": file_slug,
        "preamble": "\n".join(preamble).strip(),
        "sections": sections,
    }
    if adr_type == "constraint" or fm.get("domain"):
        data["domain"] = fm.get("domain")
        if adr_type == "constraint" and not fm.get("domain"):
            warnings.append(f"{filename}: constraint without domain")
    return data, warnings


def import_md(repo_root: Path, md_path: Path, remove_source: bool = False) -> tuple[dict, list[str]]:
    data, warnings = parse_adr_md(md_path.read_text(encoding="utf-8"), md_path.name)
    number = int(re.match(r"^(\d{4})-", md_path.name).group(1))
    yml_path, _ = mirror.commit_doc(repo_root, "docs/adr", f"{number:04d}-{data['slug']}", data)
    if remove_source and md_path.resolve() != yml_path.with_suffix(".md").resolve():
        md_path.unlink()
        warnings.append(f"removed source {md_path.name} (run git add -A)")
    return {"id": data["id"], "type": data["type"], "yml": str(yml_path),
            "sections": len(data["sections"])}, warnings
