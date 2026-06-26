# BDD .md Format

BDD scenarios are a **cross-role behaviour protocol**, not a test script (07 §5).
They must be readable by product, business, test, dev, and the agent alike. So
eg-tdd writes them as `.md` (same family as the ADRs, Obsidian-friendly), never
as JSON and never as runnable Gherkin glue.

## Location & naming

```text
docs/bdd/BDD-0001-reset-password.md
docs/bdd/BDD-0002-invite-team-member.md
```

One `.md` file per BDD Feature. A Feature is one stable business capability or
user flow — not one button, not "User Management" (07 §4).

## Skeleton

```md
---
id: BDD-0001
status: draft        # draft -> approved. Human approval is required before tests.
derived_from: ADR-0001
---

# Reset Password

### Scenario: unregistered email requests reset {#scenario-unregistered-email}
- **Given** the email x@y.com is not registered
- **When** the user submits a reset request
- **Then** the system returns a neutral message
- **And** it does not reveal whether the email exists

### Scenario: use an expired reset link {#scenario-expired-link}
- **Given** a reset link has expired
- **When** the user opens the link
- **Then** the user cannot set a new password
```

The `{#scenario-slug}` anchor IS the scenario id: `BDD-0001#scenario-unregistered-email`
(13 §5). Acceptance tests reference exactly this string in `derived_from`.

## Approval metadata

Draft BDD may be written directly by `eg-tdd`. Approved BDD requires human preview and explicit approval. After approval, the agent updates frontmatter:

```yaml
status: approved
approved_by: human
approved_at: 2026-06-26T11:30:00+08:00
approval_source: chat-confirmation
```

The approval covers only the BDD content shown in the preview. If content changes after preview, keep or return to `draft` and preview again.

## Derivation rule

For **each** Acceptance Criterion in the intent-ADR's Seed, derive **at least one
happy AND at least one edge/negative** scenario. A Feature with only success
paths fails the ruler below. Each constraint-ADR (NFR) that touches the capability
should also surface as a negative scenario or a high-risk hypothesis.

## The four-question ruler (run before handing to review)

Any one failing → rewrite, do not hand off.

| # | Question | Fail signal |
|---|---|---|
| ① | Is **Then** an observable behaviour, not an implementation/API/UI detail? | `POST /api/...`, `state = submitting`, `navigate to /x`, a loading spinner |
| ② | Can business and product read and discuss it? | Only a coder understands it; it is a list of test steps |
| ③ | Is there an edge/negative beyond happy? | Only one "success" scenario |
| ④ | Would this behaviour still be right under a different implementation? | The scenario describes how the implementation should look |

(Sources: Fowler GivenWhenThen ①②; Cucumber Gherkin Reference ②③; Dan North Introducing BDD ②③④.)

## What a BDD scenario is NOT (07 §6)

Implementation lives elsewhere:

| Do not put in BDD | Belongs in |
|---|---|
| why the feature exists | ADR `type: intent` |
| why this tech / design | ADR `type: decision` |
| DB schema, Redis keys, token storage | ADR / implementation |
| mock setup, framework calls | Test |
| component loading/empty/error states | Story |
| file naming | Code standard |

Wrong (implementation disguised as behaviour):

```md
### Scenario: store reset token in Redis {#scenario-store-token}
- **Given** Redis is available
- **Then** it is stored with key reset:token:{id}
```

Right (observable behaviour):

```md
### Scenario: use an expired reset link {#scenario-expired-link}
- **Then** the user cannot set a new password
```
