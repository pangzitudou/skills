# Finding Lifecycle

Use this when reporting a second or later eg-enforce round, or when generating a fix handoff.

## States

- `new`: fingerprint was not present in the previous ledger.
- `persisted`: fingerprint was open before and appears again with no closure evidence.
- `partial-fix`: fingerprint appears again after the fix agent submitted closure evidence.
- `regression`: fingerprint was closed before and appears again.
- `closed`: fingerprint was open before and is absent now, or was waived.
- `superseded`: reserved for an explicit future replacement relationship.

## Fingerprint Rule

`enforce.py` computes fingerprints from:

- finding type
- artifactRef
- ruleRef
- normalized location with line numbers stripped

Do not ask reviewers or fix agents to invent semantic keys. They may explain context, but scripts own identity.

## Class Rule

`enforce.py` also emits a `class_key` from finding type, artifact root, rule, and normalized domain/location.

Fix agents must sweep the whole `class_key`, not only the exact fingerprint. If the next round finds a different fingerprint in the same attempted class, `update-finding-ledger.py` reports `partial-fix`.

## Reporting Rule

Always report lifecycle buckets before ordinary findings:

1. `regression`
2. `partial-fix`
3. `persisted`
4. `new`
5. `closed`

If `regression`, `partial-fix`, or `persisted` is non-empty, lead with it. These mean a previous repair loop did not close.

## Fix Handoff Contract

Fix handoff must include every open agent-fixable ledger entry and its fingerprint.

The fix agent must produce `/tmp/eg/<run-id>/closure-evidence.json`:

```json
{
  "attempted": [
    {
      "fingerprint": "egf-...",
      "summary": "what changed",
      "code_change": "files/symbols changed",
      "class_sweep": "where the same class was searched and why it is closed",
      "tests": ["stable test ids or names"],
      "ci_facts": ["ci-facts result ids, if applicable"],
      "commit": "commit sha",
      "notes": "manual QA or blocker"
    }
  ]
}
```

Next enforce round treats a still-present fingerprint with closure evidence as `partial-fix`, not as a fresh issue.
