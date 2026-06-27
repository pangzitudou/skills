#!/usr/bin/env python3
"""Validate that staged git changes are scoped to one EG TDD run."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


def die(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def ensure_under_tmp_eg_run(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    tmp_eg = Path("/tmp/eg").resolve()
    try:
        resolved.relative_to(tmp_eg)
    except ValueError:
        die(f"ledger must be under /tmp/eg/<run-id>: {resolved}")
    if resolved == tmp_eg:
        die("ledger must include /tmp/eg/<run-id>")
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


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def artifact_paths(repo_root: Path, ids: set[str]) -> set[str]:
    paths: set[str] = set()
    for subdir in ("docs/adr", "docs/bdd"):
        root = repo_root / subdir
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.md")):
            fm = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
            if str(fm.get("id") or "") in ids:
                paths.add(str(path.relative_to(repo_root)))
    return paths


def run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def staged_files(repo_root: Path) -> set[str]:
    res = run_git(repo_root, ["diff", "--cached", "--name-only", "--diff-filter=ACMRD"])
    if res.returncode != 0:
        die(res.stderr.strip() or "git diff --cached failed")
    return {line.strip() for line in res.stdout.splitlines() if line.strip()}


def collect_artifact_ids(data: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    intent = data.get("intent")
    if isinstance(intent, dict) and intent.get("id"):
        ids.add(str(intent["id"]))
    for key in ("bdd", "related_adrs"):
        for item in data.get(key, []) or []:
            if isinstance(item, dict) and item.get("id"):
                ids.add(str(item["id"]))
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate staged git changes for one EG run.")
    parser.add_argument("--repo-root", required=True, help="Git repo root.")
    parser.add_argument("--ledger", required=True, help="/tmp/eg/<run-id>/ledger.json")
    parser.add_argument("--handoff", required=True, help="Repo handoff path, e.g. .eg/handoff/<run-id>.yml")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    ledger_path = ensure_under_tmp_eg_run(Path(args.ledger))
    data = load_json(ledger_path)
    run_id = str(data.get("run_id") or "")
    if not run_id or not run_id.startswith("EG-RUN-"):
        die("ledger.run_id must start with EG-RUN-")

    touched = data.get("touched_files")
    if not isinstance(touched, list) or not touched:
        die("ledger.touched_files must be non-empty before commit")
    allowed = {str(path) for path in touched if isinstance(path, str) and path.strip()}
    allowed |= artifact_paths(repo_root, collect_artifact_ids(data))

    handoff = Path(args.handoff)
    handoff_rel = str(handoff if not handoff.is_absolute() else handoff.resolve().relative_to(repo_root))
    if not handoff_rel.startswith(".eg/handoff/"):
        die("handoff must be under .eg/handoff/")
    if run_id not in Path(handoff_rel).name:
        die("handoff filename must include ledger.run_id")
    allowed.add(handoff_rel)

    staged = staged_files(repo_root)
    if not staged:
        die("no staged files")
    extra = sorted(staged - allowed)
    if extra:
        die("staged files outside EG run scope: " + ", ".join(extra))
    print(f"OK: staged files are scoped to {run_id} ({len(staged)} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
