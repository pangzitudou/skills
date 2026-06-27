# Source Taxonomy

Use these categories in every `/tmp/eg/<run-id>/source-matrix.yml`. Do not drop a category. Mark it `needed: false` with a reason when irrelevant.

## Categories

- `code`: frontend, backend, shared libraries, generated clients, tests, migrations.
- `runtime_data`: MySQL, PostgreSQL, Redis, Milvus, ES data, object storage, MQ, cache, feature flags.
- `runtime_behavior`: logs, traces, metrics, job status, queue state, API responses, browser network HAR.
- `configuration`: env vars, YAML/properties, Nacos/Apollo, gateway routes, permission config, tenant config, provider config, frontend build config.
- `domain_state`: tenant/account/user/member rows, roles, bindings, quotas, workflow state, external account state.
- `comparative_baseline`: customer counterpart, old version, production/staging, another tenant/user, expected spec/ADR/BDD.
- `external_dependency`: SMS/email provider, third-party API, webhook sender/receiver, OAuth, payment, IM, search/vector service.
- `user_reproduction_context`: account, tenant, timestamp, operation path, input, browser, environment, screenshot/video, request id.
- `change_history`: git diff, recent commits, deployment version, migration history, config change, release notes.
- `existing_governance`: CONTEXT, ADR, BDD, previous handoff, ci-facts, finding ledger.
- `other`: any task-specific source not covered above.

## Source Matrix Rule

Each category entry must include:

```yaml
- category: code
  needed: true
  reason: identify saler and customer account-center paths
  available:
    - repo:saler
  missing: []
  impact_if_missing: code-only diagnosis may miss runtime state
  access_mode: read-only
```

When `needed: true`, explain which hypothesis or symptom the source can prove or rule out.

When `needed: false`, explain why the category is not relevant.
