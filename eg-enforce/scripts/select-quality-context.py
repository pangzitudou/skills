#!/usr/bin/env python3
"""Select Layer A quality rule packs from a PR diff.

This script is deterministic context selection only. It does not assign
findings, enforcement levels, or gates.
"""
import argparse
import fnmatch
import json
import sys
from pathlib import Path

import yaml


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def ensure_under_tmp_eg_run(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    tmp_eg = Path("/tmp/eg").resolve()
    try:
        resolved.relative_to(tmp_eg)
    except ValueError:
        die(f"output path must be under /tmp/eg/<run-id>: {resolved}")
    if resolved == tmp_eg:
        die("output path must include /tmp/eg/<run-id>")
    return resolved


def load_yaml(path: Path):
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"not found: {path}")
    except yaml.YAMLError as exc:
        die(f"invalid yaml {path}: {exc}")
    return doc or {}


def load_diff(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        die(f"not found: {path}")


def extract_paths(diff_text: str) -> list[str]:
    paths = set()
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            for raw in parts[2:4]:
                if raw.startswith(("a/", "b/")):
                    paths.add(raw[2:])
        elif line.startswith(("+++ b/", "--- a/")):
            paths.add(line[6:])
    return sorted(p for p in paths if p and p != "/dev/null")


def changed_text(diff_text: str) -> str:
    lines = []
    for line in diff_text.splitlines():
        if line.startswith(("+++", "---", "diff --git", "index ", "@@ ")):
            continue
        if line.startswith(("+", "-")):
            lines.append(line[1:])
    return "\n".join(lines)


def matches_paths(paths: list[str], patterns: list[str]) -> list[str]:
    out = []
    for path in paths:
        if any(fnmatch.fnmatch(path, pattern) for pattern in patterns):
            out.append(path)
    return out


def matches_tokens(text: str, tokens: list[str]) -> list[str]:
    lowered = text.lower()
    out = []
    for token in tokens:
        if token in text or token.lower() in lowered:
            out.append(token)
    return out


def rule_matches(matched_paths: list[str], matched_tokens: list[str], path_patterns: list[str], token_patterns: list[str]) -> bool:
    if path_patterns and token_patterns:
        return bool(matched_paths and matched_tokens)
    if path_patterns:
        return bool(matched_paths)
    if token_patterns:
        return bool(matched_tokens)
    return False


def append_unique(items: list[str], values: list[str]) -> None:
    seen = set(items)
    for value in values:
        if value not in seen:
            items.append(value)
            seen.add(value)


def resolve_config(repo_root: Path, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    repo_config = repo_root / "quality-context.yml"
    if repo_config.exists():
        return repo_config
    return Path(__file__).resolve().parents[1] / "quality-context.default.yml"


def main() -> int:
    ap = argparse.ArgumentParser(description="Select eg-enforce Layer A rule packs.")
    ap.add_argument("--diff", required=True, help="PR diff patch file")
    ap.add_argument("--repo-root", default=".", help="repository root")
    ap.add_argument("--config", help="quality-context.yml override")
    ap.add_argument("--out", required=True, help="quality-context.json output")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    config_path = resolve_config(repo_root, args.config)
    config = load_yaml(config_path)
    diff = load_diff(Path(args.diff))
    paths = extract_paths(diff)
    text = changed_text(diff)

    selected: list[str] = []
    triggers = []
    append_unique(selected, config.get("default_rule_packs", []) or [])

    rules = config.get("rules", {}) or {}
    if not isinstance(rules, dict):
        die("quality context config `rules` must be a mapping")

    for rule_name, rule in rules.items():
        if not isinstance(rule, dict):
            continue
        include = rule.get("include_when", {}) or {}
        path_patterns = include.get("paths", []) or []
        token_patterns = include.get("tokens", []) or []
        matched_paths = matches_paths(paths, path_patterns)
        matched_tokens = matches_tokens(text, token_patterns)
        if not rule_matches(matched_paths, matched_tokens, path_patterns, token_patterns):
            continue
        append_unique(selected, rule.get("rule_packs", []) or [])
        evidence = []
        if matched_paths:
            evidence.append("paths=" + ",".join(matched_paths[:8]))
        if matched_tokens:
            evidence.append("tokens=" + ",".join(matched_tokens[:8]))
        triggers.append({"rule": rule_name, "evidence": "; ".join(evidence)})

    missing = [path for path in selected if not (repo_root / path).exists()]
    output = {
        "config": str(config_path),
        "diff_paths": paths,
        "rule_packs": selected,
        "missing_rule_packs": missing,
        "triggers": triggers,
    }
    out_path = ensure_under_tmp_eg_run(Path(args.out))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"selected {len(selected)} rule packs from {len(triggers)} triggers -> {args.out}")
    if missing:
        print(f"WARN: missing rule packs: {', '.join(missing)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
