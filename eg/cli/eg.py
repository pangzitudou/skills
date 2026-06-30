#!/usr/bin/env python3
"""eg — Executable Governance CLI.

One entrypoint; every subcommand derives from the single schema registry, so
scaffold / merge / set / check / render never drift. Stages: diagnose, precipitate.

Usage:
  eg new diagnosis  --repo R --task T [--run-id ID]
  eg new precipitate --repo-root . --task T [--run-id ID]
  eg adr-new <run> --type intent|decision|constraint --title "..." [--status ...] [--domain ...]
  eg merge  <run> <artifact>            # YAML fragment on stdin
  eg set    <run> <artifact> <path> <value>
  eg check  <run> [artifact]
  eg seal   <run> [artifact]            # hard gate
  eg render <run> [artifact]
  eg schema <artifact>

<run> is a run-id (EG-RUN-...) or a /tmp/eg/<run-id> path.
diagnose artifacts: source-matrix source-gap query-plan diagnosis
precipitate artifacts: context  adr-NNNN   (schema kinds: adr-intent adr-decision adr-constraint)
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402

import adr_import  # noqa: E402
import bdd_import  # noqa: E402
import lint as lint_mod  # noqa: E402
import mirror  # noqa: E402
import registry  # noqa: E402
import scenario as scenario_mod  # noqa: E402
import stage_enforce  # noqa: E402
import stage_precipitate  # noqa: E402
import stage_tdd  # noqa: E402
import store  # noqa: E402


def _err(msg: str) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return 1


def _coerce(value: str):
    low = value.strip().lower()
    if value.startswith("defer:") or value.startswith("defer :"):
        return value
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~", "none"):
        return None
    if re.fullmatch(r"-?\d+", value.strip()):
        return int(value.strip())
    return value


def _module_for(run_dir):
    meta_path = run_dir / "run.json"
    if meta_path.exists():
        stage = store.load(meta_path).get("stage")
        if stage == "precipitate":
            return stage_precipitate
        if stage == "tdd":
            return stage_tdd
        if stage == "enforce":
            return stage_enforce
    return registry


# ---- commands -------------------------------------------------------------

def cmd_new(args) -> int:
    if args.stage in ("diagnosis", "diagnose", "precipitate", "tdd") and not args.task:
        return _err(f"eg new {args.stage} needs --task")
    if args.stage in ("diagnosis", "diagnose"):
        if not args.repo:
            return _err("eg new diagnosis needs --repo and --task")
        run_dir = registry.new_run(args.repo, args.task, args.run_id)
        print(run_dir)
        print("next: eg merge <run> source-matrix; source-gap; diagnosis; eg check; eg seal")
        return 0
    if args.stage == "precipitate":
        run_dir = stage_precipitate.new_run(args.repo_root, args.task, args.run_id)
        print(run_dir)
        print("next: eg adr-new <run> --type intent --title '...'; merge fields; eg check; eg seal <run> adr-NNNN")
        return 0
    if args.stage == "tdd":
        if not args.intent_adr:
            return _err("eg new tdd needs --intent-adr ADR-NNNN")
        run_dir = stage_tdd.new_run(args.repo_root, args.task, args.intent_adr, args.mode, args.run_id)
        print(run_dir)
        print("next: eg bdd-new <run> --title '...' --derived-from ADR-NNNN; merge scenarios; eg check; eg seal <run> bdd-NNNN")
        return 0
    if args.stage == "enforce":
        if not args.repo or not args.target:
            return _err("eg new enforce needs --repo NAME and --target BRANCH")
        run_dir = stage_enforce.new_run(args.repo_root, args.repo, args.target, args.source, args.run_id)
        print(run_dir)
        print("next: eg pr-context <run>; eg select <run>; write findings; eg check <run>; eg enforce <run> [--facts ...]")
        return 0
    return _err("stage must be 'diagnosis', 'precipitate', 'tdd', or 'enforce'")


def _enforce_only(run_dir):
    if _module_for(run_dir) is not stage_enforce:
        raise SystemExit("ERROR: this command is only valid in an enforce run")


def _wrap(args, fn, *fn_args) -> int:
    run_dir = registry.resolve_run_dir(args.run)
    _enforce_only(run_dir)
    rc, out, err = fn(run_dir, *fn_args)
    sys.stdout.write(out)
    sys.stderr.write(err)
    return rc


def cmd_pr_context(args) -> int:
    return _wrap(args, stage_enforce.pr_context)


def cmd_select(args) -> int:
    return _wrap(args, stage_enforce.select)


def cmd_enforce(args) -> int:
    return _wrap(args, stage_enforce.enforce, args.facts)


def cmd_notify(args) -> int:
    return _wrap(args, stage_enforce.notify, not args.send)


def cmd_fix_handoff(args) -> int:
    return _wrap(args, stage_enforce.fix_handoff)


def cmd_render_all(args) -> int:
    from pathlib import Path
    out = mirror.render_all(Path(args.repo_root).resolve())
    for p in out:
        print(p)
    print(f"rendered {len(out)} doc(s) from committed *.yml")
    return 0


def cmd_lint(args) -> int:
    checked, skipped, failed, failures = lint_mod.lint(args.paths)
    for file, errors in failures:
        print(f"{file}:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
    print(f"lint: {checked} checked, {failed} with issues, {skipped} skipped (no eg schema)")
    return 1 if failed else 0


def cmd_bdd_import(args) -> int:
    from pathlib import Path
    repo_root = Path(args.repo_root).resolve()
    seen: dict[int, str] = {}
    warned = 0
    for f in args.files:
        md = Path(f)
        result, warnings = bdd_import.import_md(repo_root, md, args.remove_source)
        num = int(result["yml"].rsplit("/", 1)[-1][:4])
        if num in seen:
            print(f"WARNING: id collision {num:04d}: {result['yml']} vs {seen[num]} — renumber one", file=sys.stderr)
        seen[num] = result["yml"]
        edges = sum(1 for k in result["kinds"].values() if k == "edge")
        happies = sum(1 for k in result["kinds"].values() if k == "happy")
        print(f"{result['id']} -> {result['yml']}  (happy:{happies} edge:{edges})")
        for w in warnings:
            print(f"  ! {w}", file=sys.stderr)
            warned += 1
    print(f"imported {len(args.files)} file(s); {warned} warning(s). Run: eg check <run> per file or review the .yml.")
    return 0


def cmd_scenario_new(args) -> int:
    from pathlib import Path
    out, warnings = scenario_mod.new_draft(Path(args.repo_root).resolve(), args.name, args.derived_from)
    print(out)
    for w in warnings:
        print(f"  ! {w}", file=sys.stderr)
    print("fill description/behavior/setup/steps/expect (参考一个相近的已批准 scenario), then: eg scenario-check")
    return 0


def cmd_scenario_check(args) -> int:
    from pathlib import Path
    import json
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    rc = 0
    for f in args.files:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        errors = scenario_mod.validate_scenario(data, repo_root)
        if errors:
            print(f"{f}:", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            rc = 1
        else:
            print(f"{f}: OK (header + structure; harness schema validated by ScenarioRunnerTest)")
    return rc


def cmd_scenario_promote(args) -> int:
    from pathlib import Path
    repo_root = Path(args.repo_root).resolve()
    cleaned, errors = scenario_mod.promote(Path(args.draft), repo_root)
    if errors:
        print("not ready to promote:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    m = __import__("re").search(r"(\d+)_(.+)\.json$", cleaned.name)
    target = repo_root / scenario_mod.SCENARIO_DIR / f"{m.group(1)}_{m.group(2)}.json"
    print(f"validated + cleaned -> {cleaned}")
    print("agent 被 deny 拦，由人执行最后一步：")
    print(f"  mv {cleaned} {target}")
    return 0


def cmd_adr_import(args) -> int:
    from pathlib import Path
    repo_root = Path(args.repo_root).resolve()
    warned = 0
    for f in args.files:
        result, warnings = adr_import.import_md(repo_root, Path(f), args.remove_source)
        print(f"{result['id']} ({result['type']}) -> {result['yml']}  ({result['sections']} sections)")
        for w in warnings:
            print(f"  ! {w}", file=sys.stderr)
            warned += 1
    print(f"imported {len(args.files)} ADR(s); {warned} warning(s). Then: eg lint docs/adr")
    return 0


def cmd_bdd_new(args) -> int:
    run_dir = registry.resolve_run_dir(args.run)
    if _module_for(run_dir) is not stage_tdd:
        return _err("bdd-new is only valid in a tdd run")
    bdd_id, path = stage_tdd.bdd_new(run_dir, args.title, args.derived_from, args.test_surface)
    print(f"{bdd_id}  {path}")
    print(f"next: eg merge {args.run} bdd-{int(bdd_id.split('-')[1]):04d}  (scenarios: >=1 happy + >=1 edge)")
    return 0


def _tdd_only(run_dir):
    if _module_for(run_dir) is not stage_tdd:
        raise SystemExit("ERROR: this command is only valid in a tdd run")


def cmd_freeze(args) -> int:
    run_dir = registry.resolve_run_dir(args.run)
    _tdd_only(run_dir)
    rc, out, err = stage_tdd.freeze(run_dir)
    sys.stdout.write(out)
    sys.stderr.write(err)
    return rc


def cmd_govern(args) -> int:
    run_dir = registry.resolve_run_dir(args.run)
    _tdd_only(run_dir)
    rc, out, err = stage_tdd.govern(run_dir, args.phase, args.emit_handoff)
    sys.stdout.write(out)
    sys.stderr.write(err)
    return rc


def cmd_commit_check(args) -> int:
    run_dir = registry.resolve_run_dir(args.run)
    _tdd_only(run_dir)
    rc, out, err = stage_tdd.commit_check(run_dir, args.handoff)
    sys.stdout.write(out)
    sys.stderr.write(err)
    return rc


def cmd_adr_new(args) -> int:
    run_dir = registry.resolve_run_dir(args.run)
    if _module_for(run_dir) is not stage_precipitate:
        return _err("adr-new is only valid in a precipitate run")
    adr_id, path = stage_precipitate.adr_new(run_dir, args.type, args.title, args.status, args.domain)
    print(f"{adr_id}  {path}")
    print(f"next: eg merge {args.run} adr-{int(adr_id.split('-')[1]):04d}  (context/decision + scope)")
    return 0


def cmd_merge(args) -> int:
    run_dir = registry.resolve_run_dir(args.run)
    mod = _module_for(run_dir)
    path = mod.artifact_path(run_dir, args.artifact)
    if not path.exists():
        return _err(f"missing artifact: {path}")
    fragment_text = sys.stdin.read()
    if not fragment_text.strip():
        return _err("empty fragment on stdin")
    try:
        fragment = yaml.safe_load(fragment_text)
    except yaml.YAMLError as exc:
        return _err(f"invalid YAML fragment: {exc}")
    if not isinstance(fragment, dict):
        return _err("fragment must be a mapping of artifact fields")
    base = store.load(path)
    try:
        merged = store.merge(base, fragment, mod.merge_key(args.artifact))
    except ValueError as exc:
        return _err(str(exc))
    problems = mod.validate_written(args.artifact, merged)
    if problems:
        for p in problems:
            print(f"ERROR: {p}", file=sys.stderr)
        print("not written; fix the fragment and retry", file=sys.stderr)
        return 1
    store.dump(path, merged)
    print(f"merged into {args.artifact}: {', '.join(fragment.keys())}")
    return 0


def cmd_set(args) -> int:
    run_dir = registry.resolve_run_dir(args.run)
    mod = _module_for(run_dir)
    path = mod.artifact_path(run_dir, args.artifact)
    if not path.exists():
        return _err(f"missing artifact: {path}")
    data = store.load(path)
    value = _coerce(args.value)
    try:
        store.set_path(mod.merge_key(args.artifact), data, args.path, value)
    except ValueError as exc:
        return _err(str(exc))
    problems = mod.validate_written(args.artifact, data)
    if problems:
        for p in problems:
            print(f"ERROR: {p}", file=sys.stderr)
        print("not written; fix the value and retry", file=sys.stderr)
        return 1
    store.dump(path, data)
    print(f"set {args.artifact}.{args.path} = {value!r}")
    return 0


def cmd_check(args) -> int:
    run_dir = registry.resolve_run_dir(args.run)
    mod = _module_for(run_dir)
    errors, deferrals = mod.check_run(run_dir, args.artifact)
    if deferrals:
        print(f"Deferred ({len(deferrals)}):")
        for d in deferrals:
            print(f"  - {d}")
    if errors:
        print(f"GAPS ({len(errors)}) — not ready to seal:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK: consistent; ready to seal")
    return 0


def cmd_seal(args) -> int:
    run_dir = registry.resolve_run_dir(args.run)
    mod = _module_for(run_dir)
    errors = mod.seal_run(run_dir, args.artifact)
    if errors:
        print(f"SEAL REFUSED ({len(errors)}):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    if mod is registry:
        print(f"sealed: {registry.artifact_path(run_dir, 'diagnosis')} (stage=diagnosis-complete)")
        print(f"preview: {run_dir / 'diagnosis-preview.md'}")
    else:
        print(f"sealed {args.artifact} -> repo")
    return 0


def cmd_render(args) -> int:
    run_dir = registry.resolve_run_dir(args.run)
    mod = _module_for(run_dir)
    out = mod.render_run(run_dir, args.artifact)
    print(out)
    return 0


def cmd_schema(args) -> int:
    name = args.artifact
    if name in registry.FILENAMES:
        example = registry.example(name)
        enum_hints = {f"{a}.{f}": sorted(v) for (a, f), v in registry.ENUMS.items() if a == name}
        filename = registry.FILENAMES[name]
    elif name == "bdd":
        example = stage_tdd.example(name)
        enum_hints = {f"{a}.{f}": sorted(v) for (a, f), v in stage_tdd.ENUMS.items()}
        filename = "bdd-NNNN.yml"
    elif name == "findings":
        example = stage_enforce.example(name)
        enum_hints = {}
        filename = "layer-{a,b}-findings.json"
    else:
        example = stage_precipitate.example(name)
        key = stage_precipitate.merge_key("context" if name == "context" else "adr")
        enum_hints = {f"{a}.{f}": sorted(v) for (a, f), v in stage_precipitate.ENUMS.items() if a == key}
        filename = f"{name}.yml"
    print(f"# {name} ({filename})")
    print("# null leaves are required; fill them or 'defer: <reason>'. Empty required lists must fill before seal.")
    print(yaml.safe_dump(example, sort_keys=False, allow_unicode=True))
    if enum_hints:
        print("# enums:")
        for k, v in enum_hints.items():
            print(f"#   {k}: {v}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eg", description="Executable Governance CLI.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="scaffold a new run")
    p_new.add_argument("stage", help="diagnosis | precipitate | tdd | enforce")
    p_new.add_argument("--repo", help="diagnose/enforce: repo/project name")
    p_new.add_argument("--repo-root", default=".", help="precipitate/tdd/enforce: repo root")
    p_new.add_argument("--task", help="diagnose/precipitate/tdd: task slug")
    p_new.add_argument("--intent-adr", help="tdd: governing intent ADR id (ADR-NNNN)")
    p_new.add_argument("--mode", default="lite", choices=["lite", "full"], help="tdd: risk mode")
    p_new.add_argument("--target", help="enforce: PR target branch")
    p_new.add_argument("--source", help="enforce: PR source branch (default current)")
    p_new.add_argument("--run-id")
    p_new.set_defaults(func=cmd_new)

    p_adr = sub.add_parser("adr-new", help="reserve and scaffold a new ADR (precipitate)")
    p_adr.add_argument("run")
    p_adr.add_argument("--type", required=True, choices=sorted(stage_precipitate.precip_rules.TYPES))
    p_adr.add_argument("--title", required=True)
    p_adr.add_argument("--status", default="review", choices=sorted(stage_precipitate.precip_rules.STATUSES))
    p_adr.add_argument("--domain", default=None)
    p_adr.set_defaults(func=cmd_adr_new)

    p_bdd = sub.add_parser("bdd-new", help="reserve and scaffold a new BDD (tdd)")
    p_bdd.add_argument("run")
    p_bdd.add_argument("--title", required=True)
    p_bdd.add_argument("--derived-from", required=True, help="governing intent ADR id (ADR-NNNN)")
    p_bdd.add_argument("--test-surface", default=None,
                       choices=sorted(stage_tdd.bdd_rules.TEST_SURFACE),
                       help="saler test surface (optional)")
    p_bdd.set_defaults(func=cmd_bdd_new)

    p_freeze = sub.add_parser("freeze", help="freeze enforce plan + ci-facts contract (tdd)")
    p_freeze.add_argument("run")
    p_freeze.set_defaults(func=cmd_freeze)

    p_govern = sub.add_parser("govern", help="validate ledger; emit handoff on final (tdd)")
    p_govern.add_argument("run")
    p_govern.add_argument("--phase", choices=["planning", "final"], default="planning")
    p_govern.add_argument("--emit-handoff", action="store_true")
    p_govern.set_defaults(func=cmd_govern)

    p_commit = sub.add_parser("commit-check", help="validate staged files are scoped to the run (tdd)")
    p_commit.add_argument("run")
    p_commit.add_argument("--handoff", required=True)
    p_commit.set_defaults(func=cmd_commit_check)

    p_prctx = sub.add_parser("pr-context", help="gather PR diff + context (enforce)")
    p_prctx.add_argument("run")
    p_prctx.set_defaults(func=cmd_pr_context)

    p_sel = sub.add_parser("select", help="select active handoffs + quality context (enforce)")
    p_sel.add_argument("run")
    p_sel.set_defaults(func=cmd_select)

    p_enf = sub.add_parser("enforce", help="run the gate: enforce.py + finding ledger (enforce)")
    p_enf.add_argument("run")
    p_enf.add_argument("--facts", help="CI test facts JSON")
    p_enf.set_defaults(func=cmd_enforce)

    p_notify = sub.add_parser("notify", help="send/preview the gate digest (enforce)")
    p_notify.add_argument("run")
    p_notify.add_argument("--send", action="store_true", help="actually send (default: dry-run)")
    p_notify.set_defaults(func=cmd_notify)

    p_fix = sub.add_parser("fix-handoff", help="generate fix-handoff.md from the finding ledger (enforce)")
    p_fix.add_argument("run")
    p_fix.set_defaults(func=cmd_fix_handoff)

    p_ra = sub.add_parser("render-all", help="regenerate docs/adr|bdd/*.md + CONTEXT.md from committed *.yml")
    p_ra.add_argument("repo_root")
    p_ra.set_defaults(func=cmd_render_all)

    p_lint = sub.add_parser("lint", help="validate committed *.yml artifacts standalone (file or dir)")
    p_lint.add_argument("paths", nargs="+", help="*.yml file(s) or a dir (e.g. docs/bdd)")
    p_lint.set_defaults(func=cmd_lint)

    p_bi = sub.add_parser("bdd-import", help="convert legacy saler BDD .md into eg .yml data")
    p_bi.add_argument("--repo-root", required=True)
    p_bi.add_argument("--remove-source", action="store_true", help="delete the old .md after import")
    p_bi.add_argument("files", nargs="+", help="legacy BDD .md file(s)")
    p_bi.set_defaults(func=cmd_bdd_import)

    p_sn = sub.add_parser("scenario-new", help="scaffold a /tmp scenario draft with the next free number")
    p_sn.add_argument("--repo-root", required=True)
    p_sn.add_argument("--name", required=True, help="snake_case scenario name")
    p_sn.add_argument("--derived-from", nargs="+", default=[], help="constraining ADR id(s), e.g. ADR-0012")
    p_sn.set_defaults(func=cmd_scenario_new)

    p_sc = sub.add_parser("scenario-check", help="structure-check a scenario draft (header + steps/expect present)")
    p_sc.add_argument("--repo-root", help="repo root for derived_from ADR resolution")
    p_sc.add_argument("files", nargs="+", help="scenario draft .json")
    p_sc.set_defaults(func=cmd_scenario_check)

    p_sp = sub.add_parser("scenario-promote", help="validate + clean a draft; print the human move command")
    p_sp.add_argument("--repo-root", required=True)
    p_sp.add_argument("draft", help="/tmp scenario draft .json")
    p_sp.set_defaults(func=cmd_scenario_promote)

    p_ai = sub.add_parser("adr-import", help="convert legacy ADR .md into eg .yml (sections form)")
    p_ai.add_argument("--repo-root", required=True)
    p_ai.add_argument("--remove-source", action="store_true", help="delete the old .md after import")
    p_ai.add_argument("files", nargs="+", help="legacy ADR .md file(s)")
    p_ai.set_defaults(func=cmd_adr_import)

    p_merge = sub.add_parser("merge", help="merge a YAML fragment (stdin) into an artifact")
    p_merge.add_argument("run")
    p_merge.add_argument("artifact")
    p_merge.set_defaults(func=cmd_merge)

    p_set = sub.add_parser("set", help="set a single leaf value")
    p_set.add_argument("run")
    p_set.add_argument("artifact")
    p_set.add_argument("path")
    p_set.add_argument("value")
    p_set.set_defaults(func=cmd_set)

    p_check = sub.add_parser("check", help="report gaps and deferrals")
    p_check.add_argument("run")
    p_check.add_argument("artifact", nargs="?")
    p_check.set_defaults(func=cmd_check)

    p_seal = sub.add_parser("seal", help="hard gate: finalize if check passes")
    p_seal.add_argument("run")
    p_seal.add_argument("artifact", nargs="?")
    p_seal.set_defaults(func=cmd_seal)

    p_render = sub.add_parser("render", help="render a human preview")
    p_render.add_argument("run")
    p_render.add_argument("artifact", nargs="?")
    p_render.set_defaults(func=cmd_render)

    p_schema = sub.add_parser("schema", help="show an artifact's fields and enums")
    p_schema.add_argument("artifact")
    p_schema.set_defaults(func=cmd_schema)

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
