"""Data-level validation for BDD artifacts.

Validates the structured BDD data the agent authors in /tmp. `eg seal` renders to
docs/bdd/NNNN-slug.md (the format validate-governance.py / enforce.py parse) and
the downstream governance scripts re-validate approval + scenario anchors in
ledger context.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from store import filled_str

STATUS = {"draft", "approved", "deprecated"}
KIND = {"happy", "edge"}
TEST_SURFACE = {"cli", "mockmvc", "backend", "cross-service", "frontend", "manual"}
BDD_ID_RE = re.compile(r"^BDD-[0-9]{4}$")
ADR_ID_RE = re.compile(r"^ADR-[0-9]{4}$")
ANCHOR_RE = re.compile(r"^scenario-[a-z0-9-]+$")


def _filled_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0 and all(filled_str(x) for x in value)


def _adr_exists(repo_root: Path, adr_id: str) -> bool:
    """True if an ADR with this number exists in docs/adr (.md or .yml, any type).
    The intent-linkage is enforced downstream by validate-governance; here we only
    guard against a dangling reference."""
    adr_dir = repo_root / "docs/adr"
    if not adr_dir.is_dir():
        return False
    num = adr_id.split("-")[1]
    return bool(list(adr_dir.glob(f"{num}-*.md")) + list(adr_dir.glob(f"{num}-*.yml"))
                + list(adr_dir.glob(f"ADR-{num}-*.md")))


def validate_bdd(data: dict[str, Any], repo_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "eg-bdd/v1":
        errors.append("bdd.schema must be eg-bdd/v1")
    if not (isinstance(data.get("id"), str) and BDD_ID_RE.match(data["id"])):
        errors.append("bdd.id must match BDD-NNNN")
    derived = data.get("derived_from")
    if not (isinstance(derived, str) and ADR_ID_RE.match(derived)):
        errors.append("bdd.derived_from must be an ADR id (ADR-NNNN)")
    elif repo_root is not None and not _adr_exists(repo_root, derived):
        errors.append(f"bdd.derived_from {derived} does not exist in docs/adr")
    if data.get("status") not in STATUS:
        errors.append(f"bdd.status must be one of {sorted(STATUS)}")
    if not filled_str(data.get("title")):
        errors.append("bdd.title is required")
    if not filled_str(data.get("slug")):
        errors.append("bdd.slug is required")
    # test_surface is optional, but if present must be a known surface.
    ts = data.get("test_surface")
    if ts is not None and ts not in TEST_SURFACE:
        errors.append(f"bdd.test_surface must be one of {sorted(TEST_SURFACE)}")

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("bdd.scenarios must be a non-empty list")
        return errors
    kinds: set[str] = set()
    seen: set[str] = set()
    for i, sc in enumerate(scenarios):
        path = f"bdd.scenarios[{i}]"
        if not isinstance(sc, dict):
            errors.append(f"{path} must be an object")
            continue
        anchor = sc.get("anchor")
        if not (isinstance(anchor, str) and ANCHOR_RE.match(anchor)):
            errors.append(f"{path}.anchor must match scenario-[a-z0-9-]+")
        elif anchor in seen:
            errors.append(f"{path}.anchor duplicates {anchor!r}")
        else:
            seen.add(anchor)
        if not filled_str(sc.get("title")):
            errors.append(f"{path}.title is required")
        kind = sc.get("kind")
        if kind not in KIND:
            errors.append(f"{path}.kind must be one of {sorted(KIND)}")
        else:
            kinds.add(kind)
        # Given + Then are required; When is optional (observability/state
        # scenarios legitimately have no action), but if present must be filled.
        for step in ("given", "then"):
            if not _filled_list(sc.get(step)):
                errors.append(f"{path}.{step} must be a non-empty list of filled steps")
        if sc.get("when") and not _filled_list(sc.get("when")):
            errors.append(f"{path}.when, if present, must be filled steps")
    # Four-question ruler #3: a feature needs more than a happy path.
    if "happy" not in kinds:
        errors.append("bdd must include at least one happy scenario (kind: happy)")
    if "edge" not in kinds:
        errors.append("bdd must include at least one edge/negative scenario (kind: edge)")
    return errors
