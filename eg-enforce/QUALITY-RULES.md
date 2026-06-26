# Quality Rules

Layer A uses a small, stable taxonomy. Pick the closest risk domain; do not
invent finding types. Only report issues introduced or worsened by the diff.

## `design-depth-regression`

The diff adds or worsens a shallow module: an API/helper/module whose interface
is almost as complex as its implementation, so callers gain little complexity
reduction.

Strong signals:
- A new wrapper only forwards parameters without hiding meaningful complexity.
- A helper name promises abstraction but exposes the same branching/config
  choices to callers.
- Callers must know implementation details to use the abstraction correctly.
- One-use extraction increases indirection without reducing caller burden.
- Module splits create more coordination cost than hidden complexity.

Do not flag thin framework adapters, DTO/mapper bridges, simple private helpers
that improve local readability, generated code, or documented compatibility
shims.

Evidence must state:
- `Interface burden: ...`
- `Hidden complexity: ...`
- `Why net complexity increased: ...`

## `literal-configuration-risk`

The diff introduces magic values, hard-coded operational config, scattered
enum-like literals, duplicated thresholds, unlabelled time units, or hard-coded
external identifiers that should be named, documented, configured, or expressed
as domain constants.

Do not flag obvious local constants, test literals that clarify scenarios, or
one-off values whose meaning is already explicit in the surrounding API.

## `layer-boundary-risk`

The diff places logic in the wrong layer or leaks models across boundaries:
controller business flow, mapper business decisions, domain code depending on
HTTP/Spring MVC/database/external SDK concerns, API returning database entities,
or cross-module access to internals.

## `transaction-boundary-risk`

The diff creates unclear or unsafe transactional behavior: transaction boundary
in the wrong layer, external HTTP/RPC/MQ/file/model work inside a database
transaction, swallowed exceptions after writes, missing rollback semantics,
long transaction loops, transaction on read paths without reason, or missing
compensation state for post-commit side effects.

## `observability-risk`

The diff weakens production diagnosis or creates logging risk: missing key
state/failure logs, logs without request/tenant/user/resource context, sensitive
data exposure, noisy high-frequency info logs, trace/request/business IDs
conflated, swallowed exceptions that only log, or external calls without
duration/result/error context.

## `annotation-contract-risk`

The diff misuses annotations or comments as hidden behavior: annotation scope is
larger than necessary, transaction/async/cache/security/validation annotation
has no clear reason at that layer, custom annotation lacks semantics/limits,
`@SuppressWarnings`, `@Disabled`, or `@Ignore` has no reason and recovery
condition, TODO lacks owner/tracking item, or comments conflict with code.

## `side-effect-retry-risk`

The diff risks duplicate or inconsistent side effects: retryable writes without
business idempotency key, retry regenerates keys, trace ID used as idempotency
key, duplicate payload conflict not handled, terminal state can be rewritten,
first concurrent submission lacks uniqueness/lock/CAS protection, downstream
duplicate response is bypassed with a new ID, or half-success has no retry or
manual compensation path.

## `test-evidence-risk`

The diff changes risky behavior without credible test evidence: complex
business, state machine, idempotency, concurrency, permissions, amount,
database mapping/migration, external adapter, or bug fix lacks focused tests;
tests only cover happy path; tests assert implementation details instead of
behavior; mock-only tests are presented as E2E; or required manual QA is absent.
