#!/usr/bin/env python3
"""eg-enforce deterministic judgment engine.

Inputs (facts + reviewer findings + config) -> effective levels + gate + feedback.

The review subagents (Layer A quality, Layer B artifact-conformance) only
IDENTIFY findings. This script alone resolves enforcement_level, next_step,
override consumption, and the gate verdict. That is the "level does not cross
the river" boundary: LLM names facts, the script sentences them.

Reads:
  --findings PATH        reviewer findings JSON (repeatable; Layer A and/or B)
  --facts PATH           CI test facts JSON (optional; failed tests -> findings)
  --profile PATH         enforcement.yml
  --artifacts-root DIR   scanned for docs/adr + docs/bdd frontmatter (status, level)
  --overrides PATH       overrides.yml (optional)
  --handoffs PATH        selected_handoffs.json from select-handoffs.py (optional)
  --manifest PATH        deprecated; rejected. Use --handoffs.
  --today YYYY-MM-DD     override-expiry reference date (default: system date)
  --out PATH             write feedback.json here

Exit: 0 = mergeable (pass / advisory / required-explanation),
      1 = blocked (soft-gate or hard-gate), 2 = usage / contract error.
"""
import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

SEVERITY = {0: "documentation", 1: "advisory", 2: "required-explanation",
            3: "soft-gate", 4: "hard-gate"}
ARTIFACT_PREFIX_RE = None  # not needed; we strip '#'
FACT_PASS_STATUSES = {"passed", "success", "green"}
FACT_KNOWN_STATUSES = FACT_PASS_STATUSES | {"failed", "failure", "error", "timeout", "cancelled", "canceled", "skipped"}


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def ensure_under_tmp_eg_run(path):
    resolved = Path(path).expanduser().resolve()
    tmp_eg = Path("/tmp/eg").resolve()
    try:
        resolved.relative_to(tmp_eg)
    except ValueError:
        die(f"output path must be under /tmp/eg/<run-id>: {resolved}")
    if resolved == tmp_eg:
        die("output path must include /tmp/eg/<run-id>")
    return resolved


def load_yaml(path: str):
    try:
        return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"not found: {path}")
    except yaml.YAMLError as exc:
        die(f"invalid yaml {path}: {exc}")


def load_json(path: str):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"not found: {path}")
    except json.JSONDecodeError as exc:
        die(f"invalid json {path}: {exc}")


def artifact_id(ref):
    """BDD-0001#scenario-x -> BDD-0001 ; ADR-0001 -> ADR-0001."""
    if not ref:
        return None
    return ref.split("#", 1)[0]


def normalize_fingerprint_part(value):
    text = str(value or "").strip()
    return re.sub(r"\s+", " ", text).lower()


def normalize_fingerprint_location(value):
    text = normalize_fingerprint_part(value)
    # Keep the file/symbol anchor stable across small edits that shift line numbers.
    return re.sub(r"(?<=\S):\d+(?::\d+)?\b", "", text)


def normalize_class_domain(finding):
    explicit = finding.get("domain") or finding.get("component")
    if explicit:
        return normalize_fingerprint_location(explicit)
    text = normalize_fingerprint_location(finding.get("location"))
    return re.split(r"[#\s]", text, maxsplit=1)[0]


def finding_fingerprint_basis(finding):
    return {
        "type": normalize_fingerprint_part(finding.get("type")),
        "artifactRef": normalize_fingerprint_part(finding.get("artifactRef")),
        "ruleRef": normalize_fingerprint_part(finding.get("ruleRef")),
        "location": normalize_fingerprint_location(finding.get("location")),
    }


def finding_fingerprint(finding):
    basis = finding_fingerprint_basis(finding)
    raw = "\n".join(basis[key] for key in ("type", "artifactRef", "ruleRef", "location"))
    return "egf-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def finding_class_basis(finding):
    artifact = normalize_fingerprint_part(artifact_id(finding.get("artifactRef")) or finding.get("artifactRef"))
    domain = normalize_class_domain(finding)
    return {
        "type": normalize_fingerprint_part(finding.get("type")),
        "artifactRoot": artifact,
        "ruleRef": normalize_fingerprint_part(finding.get("ruleRef")),
        "domain": domain,
    }


def finding_class_key(finding):
    basis = finding_class_basis(finding)
    raw = "\n".join(basis[key] for key in ("type", "artifactRoot", "ruleRef", "domain"))
    return "egc-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    try:
        data = yaml.safe_load(block)
        return data if isinstance(data, dict) else {}
    except yaml.YAMLError:
        return {}


def build_artifact_index(root: str):
    index = {}
    base = Path(root)
    for sub in ("docs/adr", "docs/bdd"):
        d = base / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):
            fm = parse_frontmatter(f.read_text(encoding="utf-8"))
            aid = fm.get("id")
            if aid:
                index[aid] = {
                    "status": fm.get("status"),
                    "enforcement_level": fm.get("enforcement_level"),
                }
    return index


def fact_id(result):
    for key in ("id", "test_id", "testId"):
        value = result.get(key)
        if value:
            return str(value)
    name = str(result.get("test") or result.get("name") or "")
    for token in name.replace("_", " ").split():
        if token.startswith("AT-") or (token.startswith("H") and token[1:].isdigit()):
            return token
    return ""


def collect_findings(args, handoff_tests):
    findings = []
    for fpath in args.findings or []:
        doc = load_json(fpath)
        layer = doc.get("layer", "?")
        for item in doc.get("findings", []):
            if not isinstance(item, dict):
                die(f"{fpath}: each finding must be an object")
            for key in ("type", "artifactRef", "ruleRef", "evidence", "impact", "location", "humanVerify"):
                if key not in item:
                    die(f"{fpath}: finding missing '{key}'")
            for key in ("type", "ruleRef", "evidence", "impact", "location"):
                if not item.get(key):
                    die(f"{fpath}: finding missing '{key}'")
            if layer == "A" and item.get("artifactRef") is not None:
                die(f"{fpath}: Layer A quality findings must use artifactRef=null")
            if layer == "B" and not item.get("artifactRef"):
                die(f"{fpath}: Layer B governance findings require artifactRef")
            findings.append({
                "type": item["type"],
                "artifactRef": item.get("artifactRef"),
                "ruleRef": item["ruleRef"],
                "evidence": item["evidence"],
                "impact": item["impact"],
                "location": item.get("location", ""),
                "humanVerify": bool(item.get("humanVerify", False)),
                "source": f"layer-{layer}",
            })
    # CI test facts -> findings. When handoff tests are available, join by the
    # stable id emitted in the runner report and committed in .eg/handoff.
    if args.facts:
        facts = load_json(args.facts)
        for r in facts.get("results", []):
            tid = fact_id(r)
            htest = handoff_tests.get(tid, {}) if tid else {}
            artifact_ref = r.get("artifact_ref") or htest.get("artifactRef")
            artifact_status = r.get("artifact_status") or htest.get("artifact_status")
            status = str(r.get("status") or "").lower()
            if status not in FACT_KNOWN_STATUSES:
                die(f"ci facts result {tid or '<unknown>'} has unknown status {r.get('status')!r}")
            if status in FACT_PASS_STATUSES:
                continue
            if tid and tid not in handoff_tests and args.handoffs:
                findings.append({
                    "type": "traceability-missing",
                    "artifactRef": tid,
                    "ruleRef": "eg-handoff",
                    "evidence": f"CI result id {tid} is absent from selected EG handoffs.",
                    "impact": "eg-enforce cannot trace this test result to BDD/ADR-backed intent.",
                    "location": r.get("test") or r.get("name") or tid,
                    "humanVerify": False,
                    "source": "ci-facts",
                })
                continue
            if tid in handoff_tests:
                findings.append({
                    "type": "behavior-violation",
                    "artifactRef": artifact_ref,
                    "ruleRef": "ci-facts",
                    "evidence": json.dumps(r.get("evidence", {}), ensure_ascii=False),
                    "impact": f"A traced CI test status is {status}; changed behavior may violate artifact-backed expectations.",
                    "location": r.get("test", ""),
                    "humanVerify": False,
                    "source": "ci-facts",
                    "_fact_status": artifact_status,
                })
    return findings


def load_selected_handoffs(path):
    if not path:
        return {}, [], [], []
    doc = load_json(path)
    tests, manual_qa, decisions, errors = {}, [], [], []
    for handoff in doc.get("selected", []) or []:
        if not isinstance(handoff, dict):
            continue
        intent = handoff.get("intent", {}) if isinstance(handoff.get("intent"), dict) else {}
        ci_contract = handoff.get("ci_facts_contract", {}) if isinstance(handoff.get("ci_facts_contract"), dict) else {}
        for item in handoff.get("manual_qa", []) or []:
            if isinstance(item, dict) and item.get("item"):
                manual_qa.append({
                    "item": item["item"],
                    "hypothesis": item.get("hypothesis", ""),
                    "run_id": handoff.get("run_id", ""),
                })
        for test in handoff.get("tests", []) or []:
            if not isinstance(test, dict) or not test.get("id"):
                continue
            derived = test.get("derived_from")
            artifact_ref = derived
            if derived == "internal":
                artifact_ref = test.get("source") or intent.get("id")
            tid = str(test["id"])
            if tid in tests and tests[tid].get("run_id") != handoff.get("run_id", ""):
                errors.append(
                    f"duplicate bare test id {tid} across handoffs "
                    f"{tests[tid].get('run_id')} and {handoff.get('run_id', '')}"
                )
                continue
            tests[tid] = {
                "artifactRef": artifact_ref,
                "artifact_status": test.get("artifact_status"),
                "derived_from": derived,
                "source": test.get("source"),
                "run_id": handoff.get("run_id", ""),
                "handoff": handoff.get("path", ""),
                "ci_facts_path": ci_contract.get("path", ""),
                "ci_facts_producer": ci_contract.get("producer", ""),
                "status": test.get("status"),
                "name": test.get("name"),
            }
            if test.get("status") == "deferred":
                decisions.append({
                    "type": "deferred-test",
                    "section": "governance",
                    "artifactRef": test.get("id"),
                    "ruleRef": handoff.get("path", ""),
                    "evidence": f"Deferred EG test/risk {test.get('id')}: {test.get('name', '')}",
                    "impact": "A known EG risk was not verified in this run; human decision is required.",
                    "location": handoff.get("path", ""),
                    "source": "eg-handoff",
                    "artifact_status": test.get("artifact_status"),
                    "base_level": 0,
                    "frontmatter_level": None,
                    "status_ceiling": None,
                    "enforcement_level": 0,
                    "severity": "documentation",
                    "next_step": "request-human-review",
                    "override_allowed": False,
                    "waived": False,
                    "human_review_required": True,
                    "humanVerify": False,
                })
        for cov in handoff.get("adr_coverage", []) or []:
            if isinstance(cov, dict) and cov.get("coverage") == "deferred":
                decisions.append({
                    "type": "deferred-adr-coverage",
                    "section": "governance",
                    "artifactRef": cov.get("adr"),
                    "ruleRef": handoff.get("path", ""),
                    "evidence": cov.get("reason", "Deferred ADR coverage"),
                    "impact": "A related ADR was not covered in this run; human decision is required.",
                    "location": handoff.get("path", ""),
                    "source": "eg-handoff",
                    "artifact_status": None,
                    "base_level": 0,
                    "frontmatter_level": None,
                    "status_ceiling": None,
                    "enforcement_level": 0,
                    "severity": "documentation",
                    "next_step": "request-human-review",
                    "override_allowed": False,
                    "waived": False,
                    "human_review_required": True,
                    "humanVerify": False,
                })
    for error in doc.get("errors", []) or []:
        errors.append(str(error))
    return tests, manual_qa, decisions, errors


def load_ci_facts(path):
    if not path:
        return None
    doc = load_json(path)
    results = doc.get("results")
    if not isinstance(results, list):
        die("ci facts must contain results[]")
    by_id = {}
    for index, result in enumerate(results):
        if not isinstance(result, dict):
            die(f"ci facts results[{index}] must be an object")
        tid = fact_id(result)
        if not tid:
            die(f"ci facts results[{index}] has no id/test_id/name containing AT/H id")
        status = str(result.get("status") or "").lower()
        if status not in FACT_KNOWN_STATUSES:
            die(f"ci facts results[{index}] status must be one of {sorted(FACT_KNOWN_STATUSES)}")
        if tid in by_id:
            die(f"ci facts duplicate result id {tid}")
        by_id[tid] = result
    return by_id


def facts_path_matches_contract(actual_path, expected_path):
    if not expected_path:
        return True
    actual = Path(actual_path)
    expected = Path(str(expected_path))
    if str(actual_path) == str(expected_path):
        return True
    if actual.name == expected.name:
        return True
    return str(actual).endswith(str(expected))


def validate_facts_coverage(args, handoff_tests):
    required = sorted(
        tid for tid, test in handoff_tests.items()
        if test.get("status") in ("green", "merged")
    )
    if not required:
        return
    facts = load_ci_facts(args.facts)
    if facts is None:
        paths = sorted({
            str(test.get("ci_facts_path"))
            for test in handoff_tests.values()
            if test.get("ci_facts_path")
        })
        suffix = f" (contract path: {', '.join(paths)})" if paths else ""
        die(f"ci-facts.json is required because selected handoffs contain green/merged tests{suffix}")
    expected_paths = sorted({
        str(test.get("ci_facts_path"))
        for test in handoff_tests.values()
        if test.get("status") in ("green", "merged") and test.get("ci_facts_path")
    })
    mismatched = [path for path in expected_paths if not facts_path_matches_contract(args.facts, path)]
    if mismatched:
        die(f"--facts {args.facts} does not match ci_facts_contract.path: {', '.join(mismatched)}")
    missing = [tid for tid in required if tid not in facts]
    if missing:
        die(f"ci facts missing results for handoff tests: {', '.join(missing)}")
    not_passed = [
        tid for tid in required
        if str(facts[tid].get("status") or "").lower() not in FACT_PASS_STATUSES
    ]
    if not_passed:
        die(f"ci facts required results are not passing: {', '.join(not_passed)}")


def resolve_status(finding, artifact_index, manifest_status):
    """Status precedence: live frontmatter -> manifest snapshot -> fact -> unknown."""
    aid = artifact_id(finding.get("artifactRef"))
    if aid and aid in artifact_index and artifact_index[aid].get("status"):
        return artifact_index[aid]["status"]
    ref = finding.get("artifactRef")
    if ref and ref in manifest_status:
        return manifest_status[ref]
    if aid and aid in manifest_status:
        return manifest_status[aid]
    if finding.get("_fact_status"):
        return finding["_fact_status"]
    return "unknown" if finding.get("artifactRef") else None


def load_overrides(path, today):
    if not path:
        return []
    doc = load_yaml(path) or {}
    out = []
    for ov in doc.get("overrides", []) or []:
        if not isinstance(ov, dict):
            continue
        exp = ov.get("expires_at")
        active = False
        if exp:
            try:
                active = datetime.date.fromisoformat(str(exp)) >= today
            except ValueError:
                active = False
        ov["_active"] = active
        out.append(ov)
    return out


def match_override(finding, overrides):
    ref = finding.get("artifactRef")
    for ov in overrides:
        if not ov.get("_active"):
            continue
        target = ov.get("artifactRef") or ov.get("violation")
        if target and ref and (target == ref or target == artifact_id(ref)):
            return ov
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="eg-enforce judgment engine.")
    ap.add_argument("--findings", action="append", help="reviewer findings JSON (repeatable)")
    ap.add_argument("--facts", help="CI test facts JSON")
    ap.add_argument("--profile", required=True, help="enforcement.yml")
    ap.add_argument("--artifacts-root", default=".", help="repo root for docs/adr + docs/bdd")
    ap.add_argument("--overrides", help="overrides.yml")
    ap.add_argument("--handoffs", help="selected_handoffs.json from select-handoffs.py")
    ap.add_argument("--manifest", help="Deprecated; use --handoffs")
    ap.add_argument("--today", help="YYYY-MM-DD for override expiry (default: system date)")
    ap.add_argument("--out", required=True, help="feedback.json output")
    args = ap.parse_args()

    profile = load_yaml(args.profile) or {}
    mode = profile.get("mode", "strict")
    governance = profile.get("governance", {})
    quality = profile.get("quality", {})
    ceilings = profile.get("status_ceiling", {})
    human_review_types = set(profile.get("human_review_types", []))
    status_exempt = set(profile.get("status_exempt_types", []))

    if args.today:
        try:
            today = datetime.date.fromisoformat(args.today)
        except ValueError:
            die("--today must be YYYY-MM-DD")
    else:
        today = datetime.date.today()

    artifact_index = build_artifact_index(args.artifacts_root)
    if args.manifest:
        die("--manifest is deprecated; use --handoffs selected_handoffs.json")

    manifest_status, manual_qa = {}, []
    handoff_tests, handoff_manual_qa, handoff_decisions, handoff_errors = load_selected_handoffs(args.handoffs)
    manual_qa.extend(handoff_manual_qa)
    for err in handoff_errors:
        die(f"handoff selection error: {err}")
    validate_facts_coverage(args, handoff_tests)

    overrides = load_overrides(args.overrides, today)
    findings = collect_findings(args, handoff_tests)

    resolved, blocking_levels = [], []
    for f in findings:
        ftype = f["type"]
        if ftype in governance:
            section, rule = "governance", governance[ftype]
        elif ftype in quality:
            section, rule = "quality", quality[ftype]
        else:
            die(f"unknown finding type '{ftype}' (not in enforcement.yml governance/quality)")

        base = int(rule.get(mode, rule.get("strict", 0)))
        next_step = rule.get("next_step", "fix-code")
        status, ceiling, fm_level = None, None, None

        if section == "governance" and f.get("artifactRef"):
            aid = artifact_id(f["artifactRef"])
            if aid in artifact_index and artifact_index[aid].get("enforcement_level") is not None:
                try:
                    fm_level = int(artifact_index[aid]["enforcement_level"])
                except (TypeError, ValueError):
                    fm_level = None
            raw = max(base, fm_level or 0)            # frontmatter may only RAISE
            if ftype in status_exempt:
                # artifactRef is a test/check, not a status-bearing artifact
                effective = raw
            else:
                status = resolve_status(f, artifact_index, manifest_status)
                ceiling = int(ceilings.get(status, 4)) if status else 4
                effective = min(raw, ceiling)         # status ceiling wins
        else:
            effective = base

        override = match_override(f, overrides) if effective == 3 else None
        waived = override is not None
        human_review = (ftype in human_review_types) or (
            next_step in ("update-artifact-proposal", "request-human-review", "request-override"))

        entry = {
            "fingerprint": finding_fingerprint(f),
            "fingerprint_basis": finding_fingerprint_basis(f),
            "class_key": finding_class_key(f),
            "class_key_basis": finding_class_basis(f),
            "type": ftype, "section": section, "artifactRef": f.get("artifactRef"),
            "ruleRef": f["ruleRef"], "evidence": f["evidence"], "impact": f["impact"],
            "location": f["location"], "source": f["source"],
            "artifact_status": status, "base_level": base, "frontmatter_level": fm_level,
            "status_ceiling": ceiling, "enforcement_level": effective,
            "severity": SEVERITY.get(effective, "?"), "next_step": next_step,
            "override_allowed": effective == 3, "waived": waived,
            "human_review_required": human_review, "humanVerify": f["humanVerify"],
        }
        if waived:
            entry["override"] = {k: override.get(k) for k in
                                 ("reason", "approved_by", "expires_at", "compensation")}
        resolved.append(entry)
        if not waived:
            blocking_levels.append(effective)

    top = max(blocking_levels) if blocking_levels else 0
    if top == 4:
        gate, blocked = "hard-gate", True
    elif top == 3:
        gate, blocked = "soft-gate", True
    elif top == 2:
        gate, blocked = "pass-required-explanation", False
    elif top == 1:
        gate, blocked = "pass-advisory", False
    else:
        gate, blocked = "pass", False

    decisions = [r for r in resolved if not r["waived"] and r["human_review_required"]]
    decisions.extend(handoff_decisions)
    qa = [{"item": m["item"], "hypothesis": m["hypothesis"]} for m in manual_qa] + \
         [{"item": r["evidence"], "location": r["location"]} for r in resolved if r["humanVerify"]]
    agent_fix = [r for r in resolved if not r["waived"] and not r["human_review_required"] and
                 r["next_step"] in ("fix-code", "fix-test", "update-handoff")]

    counts = {name: sum(1 for r in resolved if r["severity"] == name) for name in SEVERITY.values()}
    feedback = {
        "gate": gate, "blocked": blocked, "mode": mode,
        "counts": counts,
        "findings": resolved,
        "human_qa": qa,
        "decisions_for_human": decisions,
        "agent_fix": agent_fix,
        "waived": [r for r in resolved if r["waived"]],
    }
    out_path = ensure_under_tmp_eg_run(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(feedback, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"gate={gate} blocked={blocked} "
          f"(hard:{counts['hard-gate']} soft:{counts['soft-gate']} "
          f"explain:{counts['required-explanation']} advisory:{counts['advisory']}) "
          f"-> {args.out}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
