"""Render precipitation data to the repo .md formats that downstream parses.

ADR -> docs/adr/NNNN-slug.md (frontmatter + sections, as eg-tdd/eg-enforce expect).
CONTEXT -> CONTEXT.md glossary.
"""
from __future__ import annotations

from typing import Any


def _bullets(items: Any) -> list[str]:
    out = [f"- {str(x).strip()}" for x in (items or []) if str(x).strip()]
    return out or ["- "]


def render_adr(data: dict[str, Any]) -> str:
    adr_type = data.get("type")
    fm = ["---", f"id: {data.get('id')}", f"type: {adr_type}", f"status: {data.get('status')}"]
    if adr_type == "constraint":
        fm.append(f"domain: {data.get('domain')}")
    fm.append("---")

    title_line = ["", f"# {str(data.get('title') or '').strip()}", ""]

    if "sections" in data:
        # imported model: title + preamble + verbatim ## sections
        out = title_line[:]
        preamble = str(data.get("preamble") or "").strip()
        if preamble:
            out += [preamble, ""]
        for s in data.get("sections") or []:
            if not isinstance(s, dict):
                continue
            out += [f"## {str(s.get('heading') or '').strip()}", "", str(s.get("body") or "").strip(), ""]
        return "\n".join(fm + out).rstrip() + "\n"

    body = [
        "",
        f"# {str(data.get('title') or '').strip()}",
        "",
        "## Context",
        str(data.get("context") or "").strip(),
        "",
        "## Decision",
        str(data.get("decision") or "").strip(),
    ]
    consequences = str(data.get("consequences") or "").strip()
    if consequences:
        body += ["", "## Consequences", consequences]
    if adr_type == "intent":
        body += ["", "## In Scope", *_bullets(data.get("in_scope"))]
        body += ["", "## Out of Scope", *_bullets(data.get("out_of_scope"))]
        body += ["", "## Non Goals", *_bullets(data.get("non_goals"))]
        seed = data.get("acceptance_seed") or []
        if seed:
            body += ["", "## Acceptance Criteria Seed", *_bullets(seed)]
    return "\n".join(fm + body).rstrip() + "\n"


def render_context(data: dict[str, Any]) -> str:
    lines = [
        f"# {str(data.get('name') or '').strip()}",
        "",
        str(data.get("description") or "").strip(),
        "",
        "## Language",
        "",
    ]
    for term in data.get("terms", []) or []:
        if not isinstance(term, dict):
            continue
        name = str(term.get("term") or "").strip()
        definition = str(term.get("definition") or "").strip()
        lines.append(f"**{name}**:")
        lines.append(definition)
        avoid = [str(a).strip() for a in (term.get("avoid") or []) if str(a).strip()]
        if avoid:
            lines.append(f"_Avoid_: {', '.join(avoid)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
