# NFR Checklist

Used during the **NFR prompting checkpoint**: just before closing an `intent`-type ADR, ask once what non-functional requirements align with that capability. This is the proactive precipitation trigger for `type: constraint` ADRs.

## How to prompt

Ask the user a single question with this checklist as the menu — do **not** ask an open-ended "any NFRs?" (that gets "no" reflexively). Frame it as a check-off:

> "Before we close this intent — does this capability touch any of these? Check off what applies, or say 'none':
> - [ ] Security (data protection, auth, abuse)
> - [ ] Cost (budget, per-unit limits)
> - [ ] Performance (latency, throughput, response time)
> - [ ] Observability (logging, tracing, metrics)
> - [ ] Other: ______"

Each checked item becomes a `constraint`-type ADR (or is appended to a related existing one), tagged with `domain`.

## Rules

- **Ask once, at intent-ADR close.** Not on every In Scope line. This is a checkpoint, not a tax — NFR prompting must not fragment the grill.
- **Accept "none" or "not now" without friction.** Do not push. Forgetting to press is better than pressing until the user disengages.
- **Only surface, do not invent.** The user must confirm each NFR; do not hallucinate constraints they didn't acknowledge.
- **Record the domain.** Each constraint ADR carries a `domain` from the checklist (security/cost/performance/observability) or the user's "other."

## Domain vocabulary (minimum, expandable)

| domain | typical form | example |
|---|---|---|
| security | policy (often needs human review) | learner PII must be redacted in logs |
| cost | quantifiable (budget/threshold) | per-learner monthly token budget < X |
| performance | quantifiable (latency/throughput) | first token < 800ms p95 |
| observability | structural (instrumentation must exist) | every LLM call must be traced |

The checklist is deliberately short. If a project accumulates dense NFRs in one domain, consider splitting `constraint` by enforcement form (quantifiable / policy / structural) — never by domain label. See [ADR-FORMAT.md](./ADR-FORMAT.md).

## Worked example

A grill reaches the close of an intent-type ADR for "Learner Progress & Unlock":

> **Skill:** Before we close ADR-0001 (intent: Learner Progress & Unlock) — does this capability touch any of these? Check off what applies, or say "none":
> - [ ] Security (data protection, auth, abuse)
> - [ ] Cost (budget, per-unit limits)
> - [ ] Performance (latency, throughput, response time)
> - [ ] Observability (logging, tracing, metrics)
> - [ ] Other: ______

**User:** Security — learner progress is PII-adjacent, and completion data shouldn't leak between learners. Cost too — each unlock check hits the DB. The rest, not for now.

**Skill:** Got it. Two constraint ADRs to precipitate:
> - ADR-0003 `type: constraint` `domain: security` — learner progress must not leak across learners.
> - ADR-0004 `type: constraint` `domain: cost` — unlock-check query budget per session.
> Shall I draft them now, or carry them into the close summary?

**User:** Draft them.

Note what happened: the checkpoint surfaced two NFRs the user hadn't raised unprompted, each became a `constraint` ADR with a `domain`, and the skill did **not** push on the unchecked items (Performance, Observability). One ask, real signal, no friction.
