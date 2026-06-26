#!/usr/bin/env python3
"""Select active EG handoff manifests for an eg-enforce round.

This automates the standard pre-review steps:

1. Read a PR diff, or a pr-context.json produced by pr-context.sh.
2. Find changed repo handoffs under .eg/handoff/*.yml.
3. Keep only active stages, defaulting to tdd-complete.
4. Validate the handoff's touched commit and referenced artifacts.
5. Emit a bounded JSON selection for the later enforce workflow.

The script does not judge enforcement level and does not mutate the repo.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


DEFAULT_ACTIVE_STAGES = ("tdd-complete",)
HANDOFF_PREFIX = ".eg/handoff/"
HANDOFF_SUFFIXES = (".yml", ".yaml")
TEST_STATUSES = {"green", "manual", "deferred", "merged"}
ADR_STATUSES = {"draft", "review", "approved", "deprecated"}
ADR_TYPES = {"intent", "decision", "constraint"}
COVERAGE_STATES = {"covered", "not-applicable", "deferred"}


def die(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


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


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"not found: {path}")
    except yaml.YAMLError as exc:
        die(f"invalid yaml {path}: {exc}")
    if not isinstance(data, dict):
        die(f"{path} must contain a YAML object")
    return data


def load_diff(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        die(f"not found: {path}")


def is_handoff_path(path: str) -> bool:
    return path.startswith(HANDOFF_PREFIX) and path.endswith(HANDOFF_SUFFIXES)


def extract_changed_handoffs(diff_text: str) -> list[str]:
    """Return non-deleted handoff paths from a unified git diff."""
    paths: list[str] = []
    current: str | None = None
    deleted = False

    def flush() -> None:
        if current and not deleted and is_handoff_path(current) and current not in paths:
            paths.append(current)

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            flush()
            deleted = False
            parts = line.split()
            current = None
            if len(parts) >= 4:
                b_path = parts[3]
                current = b_path[2:] if b_path.startswith("b/") else b_path
            continue
        if current and line.startswith("deleted file mode"):
            deleted = True
        elif current and line.startswith("+++ /dev/null"):
            deleted = True

    flush()
    return sorted(paths)


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


def build_artifact_index(repo_root: Path) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for subdir in ("docs/adr", "docs/bdd"):
        root = repo_root / subdir
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.md")):
            fm = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
            artifact_id = fm.get("id")
            if not artifact_id:
                continue
            index[str(artifact_id)] = {
                "path": str(path.relative_to(repo_root)),
                "status": fm.get("status"),
                "type": fm.get("type") or ("bdd" if subdir.endswith("bdd") else "adr"),
            }
    return index


def artifact_root(ref: str) -> str:
    return ref.split("#", 1)[0]


def check_artifact(
    *,
    artifact_id: str,
    expected_status: str | None,
    artifact_index: dict[str, dict[str, Any]],
    label: str,
    errors: list[str],
) -> dict[str, Any] | None:
    live = artifact_index.get(artifact_id)
    if not live:
        errors.append(f"{label} {artifact_id} does not exist in docs/adr or docs/bdd")
        return None
    live_status = live.get("status")
    if live_status == "deprecated":
        errors.append(f"{label} {artifact_id} is deprecated")
    if expected_status and live_status and expected_status != live_status:
        errors.append(
            f"{label} {artifact_id} status mismatch: handoff={expected_status}, live={live_status}"
        )
    return live


def run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def verify_commit_in_range(repo_root: Path, commit: str, base_ref: str | None, head_ref: str | None) -> tuple[bool, str]:
    if not base_ref or not head_ref:
        return True, "not_checked: missing base/head ref"

    for ref in (commit, base_ref, head_ref):
        res = run_git(repo_root, ["rev-parse", "--verify", "-q", f"{ref}^{{commit}}"])
        if res.returncode != 0:
            return False, f"ref not found: {ref}"

    in_head = run_git(repo_root, ["merge-base", "--is-ancestor", commit, head_ref])
    if in_head.returncode != 0:
        return False, f"{commit} is not reachable from {head_ref}"

    in_base = run_git(repo_root, ["merge-base", "--is-ancestor", commit, base_ref])
    if in_base.returncode == 0:
        return False, f"{commit} is already reachable from {base_ref}"

    return True, f"{commit} is in {base_ref}..{head_ref}"


def derive_touched_commit(repo_root: Path, rel_path: str, head_ref: str | None) -> tuple[str, str]:
    """Return the newest commit touching rel_path on head_ref.

    A committed handoff cannot contain the hash of the same commit that contains
    it: changing the file to fill the hash changes the hash. So commit is
    optional in the handoff, and this script derives the touched commit from git.
    """
    if not head_ref:
        return "", "not_checked: missing head ref"
    res = run_git(repo_root, ["log", "-1", "--format=%H", head_ref, "--", rel_path])
    commit = res.stdout.strip()
    if res.returncode != 0 or not commit:
        return "", f"could not derive touched commit for {rel_path} on {head_ref}"
    return commit, "derived_from_git_log"


def optional_str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def validate_handoff(
    *,
    repo_root: Path,
    path: str,
    data: dict[str, Any],
    artifact_index: dict[str, dict[str, Any]],
    base_ref: str | None,
    head_ref: str | None,
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    run_id = optional_str(data.get("run_id"))
    stage = optional_str(data.get("stage"))
    declared_commit = optional_str(data.get("commit"))
    derived_commit, commit_source = derive_touched_commit(repo_root, path, head_ref)
    commit = declared_commit or derived_commit

    if data.get("schema") != "eg-handoff/v1":
        errors.append("schema must be eg-handoff/v1")
    if not run_id:
        errors.append("run_id is required")
    if not commit:
        errors.append("could not determine touched commit for enforce handoff selection")
    else:
        ok, message = verify_commit_in_range(repo_root, commit, base_ref, head_ref)
        if ok and message.startswith("not_checked"):
            warnings.append(message)
        elif not ok:
            errors.append(message)
        if declared_commit and derived_commit and declared_commit != derived_commit:
            warnings.append(
                f"handoff commit {declared_commit} differs from git-derived touched commit {derived_commit}"
            )
        if commit_source.startswith("not_checked"):
            warnings.append(commit_source)

    intent = data.get("intent")
    if not isinstance(intent, dict) or not optional_str(intent.get("id")):
        errors.append("intent.id is required")
        intent_out: dict[str, Any] = {}
    else:
        intent_id = optional_str(intent.get("id"))
        live = check_artifact(
            artifact_id=intent_id,
            expected_status=optional_str(intent.get("status")) or None,
            artifact_index=artifact_index,
            label="intent",
            errors=errors,
        )
        intent_out = {
            "id": intent_id,
            "status": intent.get("status"),
            "path": live.get("path") if live else None,
            "live_status": live.get("status") if live else None,
        }

    bdd_items = data.get("bdd")
    bdd_ids: set[str] = set()
    bdd_out: list[dict[str, Any]] = []
    if not isinstance(bdd_items, list) or not bdd_items:
        errors.append("bdd must be a non-empty list")
    else:
        for index, item in enumerate(bdd_items):
            if not isinstance(item, dict) or not optional_str(item.get("id")):
                errors.append(f"bdd[{index}].id is required")
                continue
            bdd_id = optional_str(item.get("id"))
            bdd_ids.add(bdd_id)
            live = check_artifact(
                artifact_id=bdd_id,
                expected_status=optional_str(item.get("status")) or None,
                artifact_index=artifact_index,
                label="bdd",
                errors=errors,
            )
            bdd_out.append({
                "id": bdd_id,
                "status": item.get("status"),
                "path": live.get("path") if live else None,
                "live_status": live.get("status") if live else None,
            })

    related = data.get("related_adrs")
    related_ids: set[str] = set()
    related_out: list[dict[str, Any]] = []
    if not isinstance(related, list) or not related:
        errors.append("related_adrs must be a non-empty list")
    else:
        for index, item in enumerate(related):
            if not isinstance(item, dict):
                errors.append(f"related_adrs[{index}] must be an object")
                continue
            aid = optional_str(item.get("id"))
            atype = optional_str(item.get("type"))
            status = optional_str(item.get("status"))
            if not aid:
                errors.append(f"related_adrs[{index}].id is required")
                continue
            related_ids.add(aid)
            if atype not in ADR_TYPES:
                errors.append(f"related_adrs[{index}].type must be one of {sorted(ADR_TYPES)}")
            if status not in ADR_STATUSES:
                errors.append(f"related_adrs[{index}].status must be an artifact status")
            live = check_artifact(
                artifact_id=aid,
                expected_status=status or None,
                artifact_index=artifact_index,
                label=f"related_adrs[{index}]",
                errors=errors,
            )
            related_out.append({
                "id": aid,
                "type": atype,
                "status": status,
                "path": live.get("path") if live else None,
                "live_status": live.get("status") if live else None,
            })

    coverage = data.get("adr_coverage")
    coverage_out: list[dict[str, Any]] = []
    covered_ids: set[str] = set()
    if not isinstance(coverage, list) or not coverage:
        errors.append("adr_coverage must be a non-empty list")
    else:
        for index, item in enumerate(coverage):
            if not isinstance(item, dict):
                errors.append(f"adr_coverage[{index}] must be an object")
                continue
            aid = optional_str(item.get("adr"))
            state = optional_str(item.get("coverage"))
            refs = item.get("covered_by")
            reason = optional_str(item.get("reason"))
            if not aid:
                errors.append(f"adr_coverage[{index}].adr is required")
                continue
            covered_ids.add(aid)
            if aid not in related_ids:
                errors.append(f"adr_coverage[{index}].adr {aid} is absent from related_adrs")
            if state not in COVERAGE_STATES:
                errors.append(f"adr_coverage[{index}].coverage must be one of {sorted(COVERAGE_STATES)}")
            if not isinstance(refs, list):
                errors.append(f"adr_coverage[{index}].covered_by must be a list")
                refs = []
            if not reason:
                errors.append(f"adr_coverage[{index}].reason is required")
            coverage_out.append({
                "adr": aid,
                "coverage": state,
                "covered_by": refs,
                "reason": reason,
            })
    for aid in related_ids - covered_ids:
        errors.append(f"adr_coverage missing for {aid}")

    tests = data.get("tests")
    tests_out: list[dict[str, Any]] = []
    if not isinstance(tests, list) or not tests:
        errors.append("tests must be a non-empty list")
    else:
        for index, item in enumerate(tests):
            if not isinstance(item, dict):
                errors.append(f"tests[{index}] must be an object")
                continue
            test_id = optional_str(item.get("id"))
            derived_from = optional_str(item.get("derived_from"))
            status = optional_str(item.get("status"))
            artifact_status = optional_str(item.get("artifact_status"))
            if not test_id:
                errors.append(f"tests[{index}].id is required")
            if not optional_str(item.get("name")):
                errors.append(f"tests[{index}].name is required")
            if not derived_from:
                errors.append(f"tests[{index}].derived_from is required")
            elif derived_from != "internal":
                root = artifact_root(derived_from)
                if root not in bdd_ids:
                    errors.append(f"tests[{index}].derived_from references {root}, absent from bdd[]")
            else:
                source = optional_str(item.get("source"))
                if not source:
                    errors.append(f"tests[{index}].source is required when derived_from is internal")
                else:
                    check_artifact(
                        artifact_id=artifact_root(source),
                        expected_status=None,
                        artifact_index=artifact_index,
                        label=f"tests[{index}].source",
                        errors=errors,
                    )
            if status not in TEST_STATUSES:
                errors.append(f"tests[{index}].status must be one of {sorted(TEST_STATUSES)}")
            if artifact_status not in {"draft", "review", "approved", "deprecated"}:
                errors.append(f"tests[{index}].artifact_status must be an artifact status")
            tests_out.append({
                "id": test_id,
                "name": item.get("name"),
                "derived_from": derived_from,
                "source": item.get("source"),
                "artifact_status": artifact_status,
                "status": status,
            })

    manual_qa = data.get("manual_qa") or []
    if not isinstance(manual_qa, list):
        errors.append("manual_qa must be a list when present")
        manual_qa = []

    selected = {
        "path": path,
        "run_id": run_id,
        "stage": stage,
        "commit": commit,
        "commit_source": "handoff" if declared_commit else commit_source,
        "intent": intent_out,
        "bdd": bdd_out,
        "related_adrs": related_out,
        "adr_coverage": coverage_out,
        "tests": tests_out,
        "test_count": len(tests_out),
        "manual_qa": manual_qa,
        "manual_qa_count": len(manual_qa),
        "tmp_run_dir": data.get("tmp_run_dir"),
        "tmp_run_dir_authoritative": bool(data.get("tmp_run_dir_authoritative", False)),
        "warnings": warnings,
    }
    return selected, errors


def resolve_inputs(args: argparse.Namespace) -> tuple[Path, str | None, str | None, Path]:
    context: dict[str, Any] = {}
    if args.pr_context:
        context = load_json(Path(args.pr_context))

    diff_path = Path(args.diff or context.get("diffPath", ""))
    if not str(diff_path):
        die("pass --diff or --pr-context with diffPath")

    base_ref = args.base_ref
    head_ref = args.head_ref
    if context:
        target = optional_str(context.get("target"))
        source = optional_str(context.get("source"))
        base_ref = base_ref or (f"origin/{target}" if target else None)
        head_ref = head_ref or (source if source else None)

    repo_root = Path(args.repo_root).resolve()
    return repo_root, base_ref, head_ref, diff_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Select active EG handoffs from a PR diff.")
    parser.add_argument("--repo-root", default=".", help="Repository root containing .eg/, docs/adr, and docs/bdd.")
    parser.add_argument("--diff", help="Unified git diff patch file.")
    parser.add_argument("--pr-context", help="JSON produced by eg-enforce/scripts/pr-context.sh.")
    parser.add_argument("--base-ref", help="Base ref for commit range validation.")
    parser.add_argument("--head-ref", help="Head ref for commit range validation.")
    parser.add_argument(
        "--active-stage",
        action="append",
        choices=["tdd-complete", "enforce-ready"],
        help="Stage to select. Defaults to tdd-complete. Repeatable.",
    )
    parser.add_argument("--out", required=True, help="Output selected_handoffs.json.")
    args = parser.parse_args()

    repo_root, base_ref, head_ref, diff_path = resolve_inputs(args)
    if not repo_root.is_dir():
        die(f"repo root not found: {repo_root}")

    active_stages = set(args.active_stage or DEFAULT_ACTIVE_STAGES)
    diff_text = load_diff(diff_path)
    changed_handoffs = extract_changed_handoffs(diff_text)
    artifact_index = build_artifact_index(repo_root)

    selected: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    errors: list[str] = []

    for rel_path in changed_handoffs:
        full_path = repo_root / rel_path
        data = load_yaml(full_path)
        stage = optional_str(data.get("stage"))
        if stage not in active_stages:
            skipped.append({"path": rel_path, "reason": f"stage {stage or '<missing>'} is not active"})
            continue
        handoff, handoff_errors = validate_handoff(
            repo_root=repo_root,
            path=rel_path,
            data=data,
            artifact_index=artifact_index,
            base_ref=base_ref,
            head_ref=head_ref,
        )
        if handoff_errors:
            errors.extend(f"{rel_path}: {error}" for error in handoff_errors)
        else:
            selected.append(handoff)

    output = {
        "schema": "eg-enforce-handoff-selection/v1",
        "repo_root": str(repo_root),
        "diff": str(diff_path),
        "base_ref": base_ref,
        "head_ref": head_ref,
        "active_stages": sorted(active_stages),
        "changed_handoffs": changed_handoffs,
        "selected": selected,
        "skipped": skipped,
        "errors": errors,
    }
    Path(args.out).write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"wrote {args.out}")
        return 2
    if not selected:
        print(f"no active handoffs selected -> {args.out}")
        return 1
    print(f"selected {len(selected)} active handoff(s) -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
