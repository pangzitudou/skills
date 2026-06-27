# CI Facts Format

`ci-facts.json` is produced by CI or by the agent from reviewed CI output. It must match the handoff `ci_facts_contract.path`.

Minimum shape:

```json
{
  "results": [
    {
      "id": "AT-001",
      "status": "passed",
      "test": "AT-001 rejects invalid scope",
      "evidence": {
        "command": "mvn test",
        "summary": "passed in CI"
      }
    }
  ]
}
```

Rules:

- `id` is the stable `AT-*` or `H*` id from `.eg/handoff/<run-id>.yml`.
- `status` must be one of `passed`, `success`, `green`, `failed`, `failure`, `error`, `timeout`, `cancelled`, `canceled`, or `skipped`.
- Every handoff test with `status: green` or `merged` must have exactly one passing CI fact: `passed`, `success`, or `green`.
- `skipped`, `error`, `timeout`, and cancelled statuses are contract blockers for required tests.
- `test` should contain the real CI test name.
- `evidence` should include command/job/log summary when available.
