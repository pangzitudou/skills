#!/usr/bin/env python3
"""Validate a fix-agent commit against closure evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def die(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def ensure_under_tmp_eg_run(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    tmp_eg = Path("/tmp/eg").resolve()
    try:
        resolved.relative_to(tmp_eg)
    except ValueError:
        die(f"closure evidence must be under /tmp/eg/<run-id>: {resolved}")
    if resolved == tmp_eg:
        die("closure evidence must include /tmp/eg/<run-id>")
    return resolved


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"not found: {path}")
    except json.JSONDecodeError as exc:
        die(f"invalid json {path}: {exc}")
    if not isinstance(data, dict):
        die(f"{path} must contain a JSON object")
    return data


def run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def changed_files(repo_root: Path, commit: str) -> set[str]:
    res = run_git(repo_root, ["show", "--name-only", "--format=", "--diff-filter=ACMRD", commit])
    if res.returncode != 0:
        die(res.stderr.strip() or f"git show failed for {commit}")
    return {line.strip() for line in res.stdout.splitlines() if line.strip()}


def paths_from_code_change(value: Any) -> set[str]:
    if isinstance(value, list):
        raw = value
    else:
        raw = str(value or "").replace(",", " ").split()
    paths = set()
    for item in raw:
        text = str(item).strip()
        if not text:
            continue
        if "/" in text or "." in Path(text).name:
            paths.add(text)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate fix-agent commit scope.")
    parser.add_argument("--repo-root", required=True, help="Git repo root.")
    parser.add_argument("--closure-evidence", required=True, help="/tmp/eg/<run-id>/closure-evidence.json")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    evidence = load_json(ensure_under_tmp_eg_run(Path(args.closure_evidence)))
    attempted = evidence.get("attempted")
    if not isinstance(attempted, list) or not attempted:
        die("closure evidence must contain non-empty attempted[]")

    by_commit: dict[str, set[str]] = {}
    for index, item in enumerate(attempted):
        if not isinstance(item, dict):
            die(f"attempted[{index}] must be an object")
        commit = str(item.get("commit") or "").strip()
        if not commit:
            die(f"attempted[{index}].commit is required")
        allowed = paths_from_code_change(item.get("code_change"))
        if not allowed:
            die(f"attempted[{index}].code_change must list changed file paths")
        by_commit.setdefault(commit, set()).update(allowed)

    for commit, allowed in by_commit.items():
        changed = changed_files(repo_root, commit)
        extra = sorted(changed - allowed)
        if extra:
            die(f"commit {commit} changed files outside closure evidence: {', '.join(extra)}")
    print(f"OK: {len(by_commit)} fix commit(s) match closure evidence scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
