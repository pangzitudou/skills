# NFR Checklist

Use this once before closing an intent ADR.

Ask a single check-off question. Do not ask open-ended "any NFRs?"

```md
Before we close this intent, does this capability touch any of these?

- [ ] Security: data protection, auth, abuse, privacy
- [ ] Cost: budget, per-unit limits, provider spend
- [ ] Performance: latency, throughput, response time
- [ ] Observability: logging, tracing, metrics, auditability
- [ ] Other: ______

Say "none" if none apply.
```

Rules:

- Ask once at intent ADR close.
- Accept "none" or "not now" without pressure.
- Surface, do not invent.
- Each confirmed item becomes or updates a `type: constraint` ADR.
- Each constraint ADR must carry `domain`.

Domain vocabulary:

| domain | typical form | example |
|---|---|---|
| security | policy | logs must redact PII before persistence |
| cost | quantifiable | token spend must stay below a monthly cap |
| performance | quantifiable | first token p95 under a threshold |
| observability | structural | every provider call must be traced |

If a domain grows too dense, split by enforcement form, not by domain label.
