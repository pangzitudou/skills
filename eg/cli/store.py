"""Shared IO, fill predicates, dotted-path set, and the keyed merge engine.

Single source of truth for "what counts as filled" so scaffold, merge/set,
and the validators never drift (the TBD-passes-validation bug came from three
copies disagreeing).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

# Deceptive placeholders: look filled but are not. Empty string is NOT here —
# "" is merely unfilled (is_filled handles it); only typed placeholders that
# slip past a non-empty check belong here. Stripped + lower-cased before compare.
SENTINELS = {"tbd", "tba", "todo", "fixme", "xxx", "placeholder", "...", "<fill>", "fillme", "fill me"}
DEFER_RE = re.compile(r"^\s*defer\s*:\s*\S+", re.I)


def is_sentinel(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() in SENTINELS


def is_deferred(value: Any) -> bool:
    """A conscious deferral: the string 'defer: <reason>' with a real reason."""
    return isinstance(value, str) and bool(DEFER_RE.match(value))


def is_filled(value: Any) -> bool:
    """True when a value is a real answer (a deferral counts as a real answer)."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and not is_sentinel(value)
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True  # bool/int/float: False and 0 are real answers


def filled_str(value: Any) -> bool:
    """Replacement for the validators' is_str: a string that is actually filled."""
    return isinstance(value, str) and bool(value.strip()) and not is_sentinel(value)


# ---- IO -------------------------------------------------------------------

def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def dump(path: Path, data: Any) -> None:
    if path.suffix == ".json":
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    else:
        text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    path.write_text(text, encoding="utf-8")


# ---- merge engine ---------------------------------------------------------
# Keyed lists, addressed by full path "<artifact>:<field>[.<field>...]".
# A keyed list accepts either a list of objects or a map {key_value: {...}}.
KEYED: dict[str, str] = {
    "source-matrix:categories": "category",
    "diagnosis:symptoms": "id",
    "diagnosis:problem_findings": "id",
    "diagnosis:problem_findings.evidence": "id",
    "diagnosis:root_causes": "id",
    "diagnosis:root_causes.evidence": "id",
    "diagnosis:fix_options": "id",
    "diagnosis:handoff_to_precipitate.proposed_intents": "id",
    "query-plan:queries": "id",
    "context:terms": "term",
    "bdd:scenarios": "anchor",
}


def _expand_map(value: Any, key_field: str) -> list:
    """{code: {...}} -> [{category: code, ...}]; a list passes through."""
    if isinstance(value, dict):
        items = []
        for k, v in value.items():
            item = {key_field: k}
            if isinstance(v, dict):
                item.update(v)
            else:
                raise ValueError(f"keyed-list entry {k!r} must be a mapping")
            items.append(item)
        return items
    if isinstance(value, list):
        return value
    raise ValueError("keyed list must be a map or a list")


def merge(base: Any, frag: Any, path: str) -> Any:
    """Deep-merge frag into base. Keyed lists upsert by key; other lists and
    scalars overwrite; objects recurse."""
    if isinstance(frag, dict) and isinstance(base, dict):
        for k, v in frag.items():
            child_path = _join(path, k)
            if child_path in KEYED:
                base[k] = _merge_keyed(base.get(k), v, child_path)
            elif isinstance(v, dict) and isinstance(base.get(k), dict):
                base[k] = merge(base[k], v, child_path)
            else:
                base[k] = v
        return base
    return frag


def _join(path: str, key: str) -> str:
    # path is "<artifact>" or "<artifact>:field" or "<artifact>:field.sub"
    if ":" in path:
        return f"{path}.{key}"
    return f"{path}:{key}"


def _merge_keyed(base_list: Any, frag_value: Any, path: str) -> list:
    key_field = KEYED[path]
    base_list = base_list if isinstance(base_list, list) else []
    incoming = _expand_map(frag_value, key_field)
    index = {item.get(key_field): item for item in base_list if isinstance(item, dict)}
    for item in incoming:
        if not isinstance(item, dict):
            raise ValueError(f"{path} entry must be a mapping")
        key = item.get(key_field)
        existing = index.get(key)
        if existing is None:
            new_item: dict = {key_field: key}
            base_list.append(merge(new_item, item, path))
            index[key] = new_item
        else:
            merge(existing, item, path)
    return base_list


# ---- dotted-path set ------------------------------------------------------
_SEG_RE = re.compile(r"^([^\[\].]+)(?:\[([^\]]+)\])?$")


def set_path(artifact_name: str, root: dict, dotted: str, value: Any) -> None:
    """Set a leaf at e.g. 'categories[code].reason' or 'status'.
    '[key]' selects an existing item in a keyed list by its key value."""
    segs = dotted.split(".")
    node: Any = root
    path = artifact_name
    for i, seg in enumerate(segs):
        m = _SEG_RE.match(seg)
        if not m:
            raise ValueError(f"bad path segment: {seg!r}")
        name, key = m.group(1), m.group(2)
        last = i == len(segs) - 1
        field_path = _join(path, name)
        if key is None:
            if last:
                node[name] = value
                return
            node = node.setdefault(name, {})
            path = field_path
        else:
            if field_path not in KEYED:
                raise ValueError(f"{field_path} is not a keyed list; '[{key}]' invalid")
            key_field = KEYED[field_path]
            lst = node.setdefault(name, [])
            target = next((it for it in lst if isinstance(it, dict) and it.get(key_field) == key), None)
            if target is None:
                raise ValueError(f"no {name} item with {key_field}={key!r}; use 'eg merge' to add it")
            if last:
                raise ValueError(f"path ends on a keyed list item; address a field, e.g. {seg}.<field>")
            node = target
            path = field_path
