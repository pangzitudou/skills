"""Data-level validation for precipitation artifacts (ADR, CONTEXT).

Validates the structured data the agent authors in /tmp. `eg seal` additionally
runs the original validate-precipitation.py on the rendered .md so the repo
artifact stays byte-compatible with what eg-tdd / eg-enforce parse.
"""
from __future__ import annotations

import re
from typing import Any

from store import filled_str

TYPES = {"intent", "decision", "constraint"}
STATUSES = {"draft", "review", "approved", "deprecated"}
DOMAINS = {"security", "cost", "performance", "observability", "other"}
ADR_ID_RE = re.compile(r"^ADR-[0-9]{4}$")
# BDD must never appear in an ADR (it is a later derivation from intent).
BDD_RE = re.compile(r"(^|\n)\s*(##\s+Scenario:|Given\s+|When\s+|Then\s+)", re.IGNORECASE)


def _filled_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0 and all(filled_str(x) for x in value)


def _no_bdd(value: Any) -> bool:
    return not (isinstance(value, str) and BDD_RE.search(value))


def validate_adr(data: dict[str, Any], *, require_seed: bool = False) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "eg-adr/v1":
        errors.append("adr.schema must be eg-adr/v1")
    adr_id = data.get("id")
    if not isinstance(adr_id, str) or not ADR_ID_RE.match(adr_id):
        errors.append("adr.id must match ADR-NNNN")
    adr_type = data.get("type")
    status = data.get("status")
    if adr_type not in TYPES:
        errors.append(f"adr.type must be one of {sorted(TYPES)}")
    if status not in STATUSES:
        errors.append(f"adr.status must be one of {sorted(STATUSES)}")
    if not filled_str(data.get("title")):
        errors.append("adr.title is required")
    if not filled_str(data.get("slug")):
        errors.append("adr.slug is required")
    if adr_type == "constraint" and data.get("domain") not in DOMAINS:
        errors.append(f"constraint adr.domain must be one of {sorted(DOMAINS)}")
    for key in ("context", "decision"):
        if not filled_str(data.get(key)):
            errors.append(f"adr.{key} is required and non-empty")
    for key in ("context", "decision", "consequences"):
        if not _no_bdd(data.get(key)):
            errors.append(f"adr.{key} must not contain BDD scenarios or Given/When/Then")
    if adr_type == "intent":
        for key in ("in_scope", "out_of_scope", "non_goals"):
            if not _filled_list(data.get(key)):
                errors.append(f"intent adr.{key} must be a non-empty list of filled items")
        if require_seed and not _filled_list(data.get("acceptance_seed")):
            errors.append("intent adr ready for TDD requires a non-empty acceptance_seed")
    return errors


def validate_context(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "eg-context/v1":
        errors.append("context.schema must be eg-context/v1")
    if not filled_str(data.get("name")):
        errors.append("context.name is required")
    if not filled_str(data.get("description")):
        errors.append("context.description is required")
    terms = data.get("terms")
    if not isinstance(terms, list) or not terms:
        errors.append("context.terms must be a non-empty list")
        return errors
    seen: set[str] = set()
    for i, term in enumerate(terms):
        path = f"context.terms[{i}]"
        if not isinstance(term, dict):
            errors.append(f"{path} must be an object")
            continue
        name = term.get("term")
        if not filled_str(name):
            errors.append(f"{path}.term is required")
        elif name in seen:
            errors.append(f"{path}.term duplicates {name!r}")
        else:
            seen.add(str(name))
        if not filled_str(term.get("definition")):
            errors.append(f"{path}.definition is required")
        if not isinstance(term.get("avoid", []), list):
            errors.append(f"{path}.avoid must be a list")
    return errors
