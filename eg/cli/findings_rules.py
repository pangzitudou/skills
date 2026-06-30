"""Guard for reviewer findings JSON (Layer A / Layer B).

Validates the shape declared in eg-enforce/findings.schema.json plus a sentinel
scan, so a malformed or placeholder finding is caught before enforce.py runs
(enforce.py rejects unknown finding TYPES against enforcement.yml; type vocab
stays its job). Reviewers stay isolated; this only checks structure.
"""
from __future__ import annotations

from typing import Any

import store

LAYERS = {"A", "B"}
REQUIRED_STR = ("type", "ruleRef", "evidence", "impact", "location")  # non-empty strings


def validate_findings(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["findings doc must be a JSON object with layer + findings"]
    if data.get("layer") not in LAYERS:
        errors.append(f"layer must be one of {sorted(LAYERS)}")
    findings = data.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be a list")
        return errors
    for i, f in enumerate(findings):
        path = f"findings[{i}]"
        if not isinstance(f, dict):
            errors.append(f"{path} must be an object")
            continue
        for key in REQUIRED_STR:
            v = f.get(key)
            if not (isinstance(v, str) and v.strip()):
                errors.append(f"{path}.{key} is required and non-empty")
            elif store.is_sentinel(v):
                errors.append(f"{path}.{key} is a placeholder ({v!r}); a reviewer finding must be concrete")
        # artifactRef: string or null (null for quality findings).
        if "artifactRef" not in f:
            errors.append(f"{path}.artifactRef is required (string or null)")
        elif f["artifactRef"] is not None and not (isinstance(f["artifactRef"], str) and f["artifactRef"].strip()):
            errors.append(f"{path}.artifactRef must be a non-empty string or null")
        if not isinstance(f.get("humanVerify"), bool):
            errors.append(f"{path}.humanVerify must be a boolean")
    return errors
