"""Import a legacy saler BDD .md into the eg .yml data model.

saler's BDD .md (frontmatter id/status/test_surface/derived_from + `# title` +
optional `> notes` + `### Scenario: ... {#anchor}` + Given/When/Then/And) maps
almost 1:1 onto eg-bdd/v1. The one thing saler lacks is per-scenario kind
(happy/edge); we infer it heuristically and let `eg check` flag whatever the
heuristic and the four-question ruler disagree on.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

import mirror

FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
TITLE_RE = re.compile(r"^#\s+(.*?)\s*$", re.MULTILINE)
SCENARIO_RE = re.compile(r"^###\s+Scenario:\s*(.*?)\s*\{#(scenario-[a-z0-9-]+)\}\s*$", re.MULTILINE)
STEP_RE = re.compile(r"^\s*-\s*\*\*(Given|When|Then|And)\*\*\s*(.*\S)\s*$")
ADR_RE = re.compile(r"ADR-(\d{4})")
ADR_PATH_RE = re.compile(r"adr/(\d{4})")

# STRONG signals that a scenario is a negative / boundary / failure / retry path.
# Deliberately NOT bare negation ("not"/"不") — happy scenarios routinely assert
# "does not reveal X", so generic negation over-classifies to edge.
EDGE_SIGNALS = [
    "cannot", "can't", "without", "unable", "unavailable", "not available",
    "no usable", "fail", "error", "invalid", "missing", "reject", "block",
    "skip", "zero", "exhaust", "idempotent", "terminal", "duplicate", "no-op",
    "noop", "expire", "timeout", "overflow", " full", "unauthor", "forbidden",
    "拒", "失败", "异常", "错误", "终态", "幂等", "重复", "越权", "禁止", "兜底",
    "超时", "满", "非法", "缺", "无法", "过期", "再次", "告警", "不报错", "不改变",
]


def _normalize_adr(value: Any) -> str:
    if isinstance(value, list):
        value = value[0] if value else ""
    text = str(value or "")
    m = ADR_RE.search(text) or ADR_PATH_RE.search(text)
    return f"ADR-{m.group(1)}" if m else text.strip()


def _infer_kind(title: str, then_steps: list[str]) -> str:
    blob = (title + " " + " ".join(then_steps)).lower()
    return "edge" if any(sig in blob for sig in EDGE_SIGNALS) else "happy"


def _parse_steps(block: str) -> dict[str, list[str]]:
    steps = {"given": [], "when": [], "then": []}
    section = "given"
    keyword = {"Given": "given", "When": "when", "Then": "then"}
    for line in block.splitlines():
        m = STEP_RE.match(line)
        if not m:
            continue
        kw, text = m.group(1), m.group(2).strip()
        if kw != "And":
            section = keyword[kw]
        steps[section].append(text)
    return steps


def parse_saler_md(text: str, filename: str) -> tuple[dict, list[str]]:
    """Return (eg-bdd data, warnings)."""
    warnings: list[str] = []
    fm_match = FM_RE.match(text)
    if not fm_match:
        raise SystemExit(f"{filename}: no frontmatter")
    fm = yaml.safe_load(fm_match.group(1))
    body = fm_match.group(2)
    fm = fm if isinstance(fm, dict) else {}

    fname_m = re.match(r"^(?:BDD-)?(\d{4})-(.*)\.md$", os.path.basename(filename))
    if not fname_m:
        raise SystemExit(f"{filename}: name must be [BDD-]NNNN-slug.md")
    number, file_slug = int(fname_m.group(1)), fname_m.group(2)

    bdd_id = str(fm.get("id") or f"BDD-{number:04d}")
    title_m = TITLE_RE.search(body)
    title = title_m.group(1).strip() if title_m else file_slug

    # notes = blockquote lines between the title and the first scenario
    first_sc = SCENARIO_RE.search(body)
    head = body[title_m.end():first_sc.start()] if (title_m and first_sc) else ""
    notes = "\n".join(ln[1:].strip() for ln in head.splitlines() if ln.lstrip().startswith(">")).strip()

    test_surface = fm.get("test_surface")
    if not test_surface:
        warnings.append(f"{filename}: no test_surface (left null; fill it)")

    scenarios = []
    matches = list(SCENARIO_RE.finditer(body))
    for i, m in enumerate(matches):
        sc_title, anchor = m.group(1).strip(), m.group(2)
        block = body[m.end():matches[i + 1].start()] if i + 1 < len(matches) else body[m.end():]
        steps = _parse_steps(block)
        kind = _infer_kind(sc_title, steps["then"])
        scenarios.append({"anchor": anchor, "title": sc_title, "kind": kind, **steps})
    if not scenarios:
        warnings.append(f"{filename}: no scenarios parsed")

    data = {
        "schema": "eg-bdd/v1",
        "id": bdd_id,
        "status": str(fm.get("status") or "approved"),
        "test_surface": test_surface,
        "derived_from": _normalize_adr(fm.get("derived_from")),
        "title": title,
        "slug": file_slug,
        "notes": notes,
        "scenarios": scenarios,
    }
    # preserve real approval metadata if the source carried it (don't fabricate)
    for k in ("approved_by", "approved_at", "approval_source"):
        if fm.get(k):
            data[k] = fm.get(k)
    if data.get("status") == "approved" and not data.get("approved_at"):
        warnings.append(f"{filename}: approved but no approval metadata (downstream wants approved_by/at/source)")
    return data, warnings


def import_md(repo_root: Path, md_path: Path, remove_source: bool = False) -> tuple[dict, list[str]]:
    data, warnings = parse_saler_md(md_path.read_text(encoding="utf-8"), md_path.name)
    number = int(re.match(r"^(?:BDD-)?(\d{4})", md_path.name).group(1))
    yml_path, _ = mirror.commit_doc(repo_root, "docs/bdd", f"{number:04d}-{data['slug']}", data)
    if remove_source and md_path.resolve() != yml_path.with_suffix(".md").resolve():
        md_path.unlink()
        warnings.append(f"removed source {md_path.name} (run git add -A)")
    return {"id": data["id"], "yml": str(yml_path),
            "kinds": {s["anchor"]: s["kind"] for s in data["scenarios"]}}, warnings
