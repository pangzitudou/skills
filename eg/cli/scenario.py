"""saler-cli scenario lifecycle helper (cli test surface).

Scenario JSON stays the executable source — its full schema (setup/steps/expect
keys) is owned by the Java harness `ScenarioKeys.java` and validated by
`ScenarioRunnerTest`. eg only handles the lifecycle pain: allocate a free number,
scaffold a /tmp draft header, structure-check it, and print the promote command
for a human to run (the scenarios/ dir is agent-denied on purpose).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import store

TMP = Path("/tmp")
SCENARIO_DIR = "saler-cli/scenarios"
NAME_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
ADR_NUM_RE = re.compile(r"(\d{4})")


def _scenarios_dir(repo_root: Path) -> Path:
    return repo_root / SCENARIO_DIR


def next_number(repo_root: Path) -> int:
    highest = 0
    d = _scenarios_dir(repo_root)
    if d.is_dir():
        for p in d.glob("*.json"):
            m = re.match(r"^(\d+)_", p.name)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1


def _resolve_adr(repo_root: Path, ref: str) -> tuple[str, bool]:
    """Return (path-or-id, exists). Accepts ADR-NNNN or a docs/adr path."""
    m = ADR_NUM_RE.search(ref)
    if not m:
        return ref, False
    num = m.group(1)
    adr_dir = repo_root / "docs/adr"
    hits = sorted(adr_dir.glob(f"{num}-*.yml")) + sorted(adr_dir.glob(f"{num}-*.md"))
    if hits:
        return f"docs/adr/{hits[0].name}", True
    return ref, False


def scaffold(name: str, derived_from: list[str], number: int) -> dict:
    return {
        "_draft_note": "DRAFT — 待人工评审。禁止 AI 写入 saler-cli/scenarios/（deny 规则）。"
                       "过审后由人 promote。setup/steps/expect 参考一个相近的已批准 scenario。",
        "name": name,
        "description": None,
        "behavior": {"given": None, "when": None, "then": None},
        "derived_from": derived_from,
        "harness_notes": [],
        "setup": {},
        "steps": [],
        "expect": {},
    }


def new_draft(repo_root: Path, name: str, derived_from_refs: list[str]) -> tuple[Path, list[str]]:
    warnings: list[str] = []
    if not NAME_RE.match(name):
        warnings.append(f"name {name!r} is not snake_case (a-z0-9_)")
    number = next_number(repo_root)
    derived: list[str] = []
    for ref in derived_from_refs:
        path, ok = _resolve_adr(repo_root, ref)
        derived.append(path)
        if not ok:
            warnings.append(f"derived_from {ref!r} does not resolve to an ADR in docs/adr")
    data = scaffold(name, derived, number)
    out = TMP / f"scenario-draft-{number:02d}_{name}.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out, warnings


def validate_scenario(data: Any, repo_root: Path | None = None) -> list[str]:
    """Structure-only: header + non-empty steps/expect. The setup/steps/expect
    KEY schema is the Java harness's job (ScenarioKeys / ScenarioRunnerTest)."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["scenario must be a JSON object"]
    if not store.filled_str(data.get("name")):
        errors.append("name is required")
    elif not NAME_RE.match(str(data.get("name"))):
        errors.append("name must be snake_case (a-z0-9_)")
    if not store.filled_str(data.get("description")):
        errors.append("description is required")
    behavior = data.get("behavior")
    if not isinstance(behavior, dict):
        errors.append("behavior must be an object with given/when/then")
    else:
        for k in ("given", "when", "then"):
            if not store.filled_str(behavior.get(k)):
                errors.append(f"behavior.{k} is required")
    derived = data.get("derived_from")
    if not isinstance(derived, list) or not derived:
        errors.append("derived_from must be a non-empty list (the constraining ADRs)")
    elif repo_root is not None:
        for ref in derived:
            if not _resolve_adr(repo_root, str(ref))[1]:
                errors.append(f"derived_from {ref!r} does not exist in docs/adr")
    if not isinstance(data.get("steps"), list) or not data.get("steps"):
        errors.append("steps must be a non-empty list")
    if not isinstance(data.get("expect"), dict) or not data.get("expect"):
        errors.append("expect must be a non-empty object")
    return errors


def promote(draft_path: Path, repo_root: Path) -> tuple[Path | None, list[str]]:
    """Validate + write a cleaned (draft markers stripped) copy to /tmp, and
    return (cleaned_path, errors). The final move into scenarios/ is left to a
    human (agent-deny)."""
    data = json.loads(draft_path.read_text(encoding="utf-8"))
    errors = validate_scenario(data, repo_root)
    if errors:
        return None, errors
    m = re.search(r"(\d+)_", draft_path.name)
    if not m:
        return None, [f"draft name must contain NN_ number: {draft_path.name}"]
    number = int(m.group(1))
    name = data["name"]
    for marker in ("_draft_note", "_reconstruction_gap"):
        data.pop(marker, None)
    cleaned = TMP / f"scenario-promote-{number:02d}_{name}.json"
    cleaned.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return cleaned, []
