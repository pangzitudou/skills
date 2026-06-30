"""Standalone artifact lint: validate committed *.yml data files against their
schema rules, with no run/ledger context. Routes by the `schema` field.

`eg check` validates a run's completeness; `eg lint` validates already-committed
artifacts (a file or a whole docs/bdd dir).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import bdd_rules
import precip_rules
import store

SKIP_DIRS = {".git", "target", "node_modules", ".tmp", "build", "dist", "__pycache__"}


def _repo_root(path: Path) -> Path:
    """Walk up to the ancestor that holds a docs/ dir (for ADR-existence checks)."""
    for parent in [path] + list(path.parents):
        if (parent / "docs").is_dir():
            return parent
    return path.parent


def _validate(data: dict, file: Path) -> list[str] | None:
    schema = data.get("schema") if isinstance(data, dict) else None
    root = _repo_root(file)
    if schema == "eg-bdd/v1":
        return bdd_rules.validate_bdd(data, root)
    if schema == "eg-adr/v1":
        require_seed = data.get("type") == "intent" and data.get("status") == "approved"
        return precip_rules.validate_adr(data, require_seed=require_seed)
    if schema == "eg-context/v1":
        return precip_rules.validate_context(data)
    return None  # not an eg artifact; skip


def _collect_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for y in sorted(p.rglob("*.yml")):
                if not any(part in SKIP_DIRS for part in y.parts):
                    files.append(y)
        elif p.is_file():
            files.append(p)
        else:
            files.append(p)  # let load() raise a clear error
    return files


def lint(paths: list[str]) -> tuple[int, int, int, list[tuple[Path, list[str]]]]:
    """Return (checked, skipped, failed, [(file, errors)])."""
    checked = skipped = 0
    failures: list[tuple[Path, list[str]]] = []
    for file in _collect_files(paths):
        try:
            data = store.load(file)
        except Exception as exc:
            failures.append((file, [f"could not read: {exc}"]))
            continue
        errors = _validate(data, file)
        if errors is None:
            skipped += 1
            continue
        checked += 1
        if errors:
            failures.append((file, errors))
    return checked, skipped, len(failures), failures
