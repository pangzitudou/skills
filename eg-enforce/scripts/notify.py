#!/usr/bin/env python3
"""eg-enforce -> Feishu (via hermes), human-facing.

Turns feedback.json into a HUMAN digest (what was done / what you must decide /
what you should manually QA / links) and sends it through `hermes send`. The
agent-facing detail stays in feedback.json (linked, not inlined).

Best-effort: if hermes is missing or send fails, warn and exit 0. The gate
verdict is enforce.py's exit code; notification never changes it.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

# Plain-language templates for the "you must decide" bucket, keyed by type.
DECIDE_TEMPLATES = {
    "artifact-status-violation":
        "改动了已批准的 {ref}，Agent 无权自改 → 批准修改规则 / 退回让 Agent 改代码",
    "scope-violation":
        "实现超出 {ref} 的范围 → 批准扩范围 / 删除超范围实现",
}


def humanize_decision(r):
    ref = r.get("artifactRef") or "(无 artifact)"
    tmpl = DECIDE_TEMPLATES.get(r["type"])
    if tmpl:
        return tmpl.format(ref=ref)
    if r.get("enforcement_level") == 3:
        return f"{r['type']} @ {ref} → 需你豁免(soft-gate)或退回修复"
    return f"{r['type']} @ {ref} → {r.get('next_step', '需处理')}"


def load_ledger(path):
    if not path:
        return {}
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def build_digest(fb, args, ledger=None):
    blocked = fb.get("blocked")
    icon = "❌" if blocked else "✅"
    c = fb.get("counts", {})
    lines = [f"{icon} eg-enforce · {args.repo} PR #{args.pr_number} 「{args.pr_title}」", ""]
    lines.append("做了什么")
    lines.append("  并行评审了 PR：代码质量 (Layer A) + 治理一致性 (Layer B)。")
    lines.append("")

    lifecycle_counts = ((ledger or {}).get("summary", {}).get("counts", {}))
    lifecycle_parts = [
        ("regression", "回归"),
        ("partial-fix", "半修"),
        ("persisted", "未修净"),
        ("new", "新增"),
        ("closed", "已关闭"),
    ]
    if any(lifecycle_counts.get(key, 0) for key, _ in lifecycle_parts):
        lines.append("复修状态")
        for key, label in lifecycle_parts:
            count = lifecycle_counts.get(key, 0)
            if count:
                lines.append(f"  · {label}: {count}")
        lines.append("")

    decisions = fb.get("decisions_for_human", [])
    if decisions:
        lines.append(f"🔴 需要你定夺 ({len(decisions)})")
        for r in decisions:
            lines.append(f"  · {humanize_decision(r)}")
        lines.append("")

    qa = fb.get("human_qa", [])
    if qa:
        lines.append(f"🟡 建议你抽查 ({len(qa)})")
        for m in qa:
            lines.append(f"  · {m.get('item')}")
        lines.append("")

    af = fb.get("agent_fix", [])
    if af:
        lines.append(f"⚪ Agent 自修 ({len(af)}) — 已进修复清单，无需你处理")
        lines.append("")

    if not (decisions or qa):
        lines.append("无需你处理。")
        lines.append("")

    verdict = "🚫 合并被拦" if blocked else "✅ 可合并"
    lines.append(f"结论: {fb.get('gate')} — {verdict}  "
                 f"(hard:{c.get('hard-gate',0)} soft:{c.get('soft-gate',0)} "
                 f"explain:{c.get('required-explanation',0)} advisory:{c.get('advisory',0)})")

    links = [f"PR {args.pr_url}" if args.pr_url else None,
             f"CI {args.ci_url}" if args.ci_url else None,
             f"修复清单 {args.artifact_url}" if args.artifact_url else None]
    links = [x for x in links if x]
    if links:
        lines.append("🔗 " + "  |  ".join(links))
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Send eg-enforce human digest via hermes.")
    ap.add_argument("--feedback", required=True, help="feedback.json from enforce.py")
    ap.add_argument("--repo", default="")
    ap.add_argument("--pr-number", default="")
    ap.add_argument("--pr-title", default="")
    ap.add_argument("--pr-url", default="")
    ap.add_argument("--ci-url", default="")
    ap.add_argument("--artifact-url", default="")
    ap.add_argument("--ledger", help="finding-ledger.json from update-finding-ledger.py")
    ap.add_argument("--to", default="feishu", help="hermes target (default: feishu)")
    ap.add_argument("--dry-run", action="store_true", help="print digest, do not send")
    args = ap.parse_args()

    try:
        fb = json.loads(Path(args.feedback).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read feedback: {exc}", file=sys.stderr)
        return 2

    digest = build_digest(fb, args, load_ledger(args.ledger))
    if args.dry_run:
        print(digest)
        return 0

    subject = f"[eg-enforce] {args.repo} PR #{args.pr_number}"
    try:
        res = subprocess.run(
            ["hermes", "send", "--to", args.to, "--subject", subject, "--file", "-"],
            input=digest, text=True, capture_output=True,
        )
    except FileNotFoundError:
        print("WARN: hermes not found; skipped notification (gate verdict unaffected)", file=sys.stderr)
        return 0
    if res.returncode != 0:
        print(f"WARN: hermes send failed ({res.returncode}): {res.stderr.strip()}", file=sys.stderr)
        return 0
    print(f"notified {args.to}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
