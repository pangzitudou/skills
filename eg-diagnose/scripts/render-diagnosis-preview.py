#!/usr/bin/env python3
"""Render human-readable EG diagnosis preview by problem."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: {path} must be a YAML object")
    return data


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def text(value: Any, fallback: str = "none") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def render_list(values: list[Any]) -> str:
    if not values:
        return "none"
    return ", ".join(str(item) for item in values)


def render_evidence(evidence: list[Any]) -> list[str]:
    if not evidence:
        return ["  - none"]
    lines: list[str] = []
    for item in evidence:
        if not isinstance(item, dict):
            continue
        source_ref = text(item.get("source_ref"))
        summary = text(item.get("summary"))
        strength = text(item.get("strength"))
        source_type = text(item.get("source_type"))
        lines.append(f"  - [{strength}/{source_type}] {source_ref}: {summary}")
    return lines or ["  - none"]


def render(data: dict[str, Any]) -> str:
    run_id = text(data.get("run_id"))
    status = text(data.get("stage"))
    source_gap = load_yaml(Path(str(data.get("source_gap")))) if data.get("source_gap") else {}
    lines = [
        "## 分析结果",
        "",
        f"- diagnosis: `{run_id}`",
        f"- status: `{status}`",
        f"- source_gap: `{text(source_gap.get('status'))}`",
        "",
    ]
    problem_findings = as_list(data.get("problem_findings"))
    if not problem_findings:
        lines.extend(["### P0: no problem findings", "- 根因: none", "- 依据:", "  - none", ""])
        return "\n".join(lines).rstrip() + "\n"
    for item in problem_findings:
        if not isinstance(item, dict):
            continue
        pid = text(item.get("id"), "P?")
        problem = text(item.get("problem"))
        lines.extend([
            f"### {pid}: {problem}",
            f"- 状态: `{text(item.get('status'))}` / `{text(item.get('finding_type'))}` / `{text(item.get('confidence'))}`",
            f"- 根因: {text(item.get('root_cause'))}",
            "- 依据:",
            *render_evidence(as_list(item.get("evidence"))),
            f"- 缺口: {render_list(as_list(item.get('missing_evidence')))}",
            f"- 修复方向: {render_list(as_list(item.get('fix_options')))}",
            "",
        ])
    fix_options = as_list(data.get("fix_options"))
    if fix_options:
        lines.extend(["## 修复选项", ""])
        for item in fix_options:
            if not isinstance(item, dict):
                continue
            lines.append(f"- {text(item.get('id'))}: {text(item.get('summary'))}")
        lines.append("")
    gaps = as_list(data.get("unexplained_symptoms"))
    if gaps:
        lines.extend(["## 未解释问题", ""])
        for item in gaps:
            if isinstance(item, dict):
                lines.append(f"- {text(item.get('symptom'))}: {render_list(as_list(item.get('missing_evidence')))}")
            else:
                lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render diagnosis-preview.md from diagnosis.yml.")
    parser.add_argument("diagnosis", help="/tmp/eg/<run-id>/diagnosis.yml")
    parser.add_argument("--out", help="Defaults to sibling diagnosis-preview.md")
    args = parser.parse_args()

    diagnosis_path = Path(args.diagnosis)
    data = load_yaml(diagnosis_path)
    out = Path(args.out) if args.out else diagnosis_path.with_name("diagnosis-preview.md")
    out.write_text(render(data), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
