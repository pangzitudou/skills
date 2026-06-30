"""Render BDD data to docs/bdd/NNNN-slug.md (the format downstream parses)."""
from __future__ import annotations

from typing import Any


def _steps(keyword: str, items: Any) -> list[str]:
    out: list[str] = []
    for j, step in enumerate([s for s in (items or []) if str(s).strip()]):
        kw = keyword if j == 0 else "And"
        out.append(f"- **{kw}** {str(step).strip()}")
    return out


def render_bdd(data: dict[str, Any]) -> str:
    fm = [
        "---",
        f"id: {data.get('id')}",
        f"status: {data.get('status')}",
    ]
    if data.get("test_surface"):
        fm.append(f"test_surface: {data.get('test_surface')}")
    fm.append(f"derived_from: {data.get('derived_from')}")
    if data.get("status") == "approved":
        for k in ("approved_by", "approved_at", "approval_source"):
            if data.get(k):
                fm.append(f"{k}: {data[k]}")
    fm.append("---")

    lines = fm + ["", f"# {str(data.get('title') or '').strip()}", ""]
    notes = str(data.get("notes") or "").strip()
    if notes:
        lines += [f"> {ln}" if ln.strip() else ">" for ln in notes.splitlines()] + [""]
    for sc in data.get("scenarios", []) or []:
        if not isinstance(sc, dict):
            continue
        title = str(sc.get("title") or "").strip()
        anchor = str(sc.get("anchor") or "").strip()
        lines.append(f"### Scenario: {title} {{#{anchor}}}")
        lines += _steps("Given", sc.get("given"))
        lines += _steps("When", sc.get("when"))
        lines += _steps("Then", sc.get("then"))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
