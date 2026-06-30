"""Render diagnosis-preview.md from diagnosis.yml (problem-by-problem).

Ported from eg-diagnose/scripts/render-diagnosis-preview.py; callable so
`eg render` and `eg seal` keep the preview in sync automatically.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: {path} must be a YAML object")
    return data


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any, fallback: str = "none") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _render_list(values: list[Any]) -> str:
    if not values:
        return "none"
    return ", ".join(str(item) for item in values)


def _render_evidence(evidence: list[Any]) -> list[str]:
    if not evidence:
        return ["  - none"]
    lines: list[str] = []
    for item in evidence:
        if not isinstance(item, dict):
            continue
        source_ref = _text(item.get("source_ref"))
        summary = _text(item.get("summary"))
        strength = _text(item.get("strength"))
        source_type = _text(item.get("source_type"))
        lines.append(f"  - [{strength}/{source_type}] {source_ref}: {summary}")
    return lines or ["  - none"]


def render(data: dict[str, Any]) -> str:
    run_id = _text(data.get("run_id"))
    status = _text(data.get("stage"))
    source_gap = _load_yaml(Path(str(data.get("source_gap")))) if data.get("source_gap") else {}
    lines = [
        "## 分析结果",
        "",
        f"- diagnosis: `{run_id}`",
        f"- status: `{status}`",
        f"- source_gap: `{_text(source_gap.get('status'))}`",
        "",
    ]
    problem_findings = _as_list(data.get("problem_findings"))
    if not problem_findings:
        lines.extend(["### P0: no problem findings", "- 根因: none", "- 依据:", "  - none", ""])
        return "\n".join(lines).rstrip() + "\n"
    for item in problem_findings:
        if not isinstance(item, dict):
            continue
        pid = _text(item.get("id"), "P?")
        problem = _text(item.get("problem"))
        lines.extend([
            f"### {pid}: {problem}",
            f"- 状态: `{_text(item.get('status'))}` / `{_text(item.get('finding_type'))}` / `{_text(item.get('confidence'))}`",
            f"- 根因: {_text(item.get('root_cause'))}",
            "- 依据:",
            *_render_evidence(_as_list(item.get("evidence"))),
            f"- 缺口: {_render_list(_as_list(item.get('missing_evidence')))}",
            f"- 修复方向: {_render_list(_as_list(item.get('fix_options')))}",
            "",
        ])
    fix_options = _as_list(data.get("fix_options"))
    if fix_options:
        lines.extend(["## 修复选项", ""])
        for item in fix_options:
            if not isinstance(item, dict):
                continue
            lines.append(f"- {_text(item.get('id'))}: {_text(item.get('summary'))}")
        lines.append("")
    gaps = _as_list(data.get("unexplained_symptoms"))
    if gaps:
        lines.extend(["## 未解释问题", ""])
        for item in gaps:
            if isinstance(item, dict):
                lines.append(f"- {_text(item.get('symptom'))}: {_render_list(_as_list(item.get('missing_evidence')))}")
            else:
                lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
