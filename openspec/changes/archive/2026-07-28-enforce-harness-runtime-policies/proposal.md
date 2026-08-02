## Why

Several configured runtime controls are currently advisory or unimplemented: model-authored usage can satisfy budget checks, cost and token accounting are not cumulative across a run, and concurrency and retention settings do not drive runtime behavior. The product contract must match controls that the CLI can authoritatively enforce.

## What Changes

- Separate provider-authoritative usage from untrusted model-authored stage content.
- Aggregate requests, tokens, and cost transactionally across each run and expose the authoritative totals in status/report output.
- Pass only the remaining enforceable budget into a provider invocation and fail before starting work when no budget remains.
- Make automated support conditional on the provider guarantees required by configured hard limits; downgrade unsupported hard-cost configurations rather than claiming enforcement.
- Enforce a single combined provider output limit and reconcile the runtime-policy result with provider execution hardening.
- Remove, reserve, or truthfully implement concurrency and retention settings; documentation must not claim active cleanup or fan-out limits without a corresponding runtime mechanism.
- **BREAKING**: Provider-reported usage inside the structured planning document will no longer be authoritative, and configurations requesting unenforceable hard limits may be rejected or downgraded.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `harness-workflow`: Tighten authoritative usage, cumulative budgets, capability-dependent enforcement, concurrency, retention, and reporting requirements.

## Non-Goals

- Estimating provider prices from an unversioned external price table.
- Adding distributed orchestration, PostgreSQL, or a daemon.
- Automatically deleting immutable artifact revisions.
- Making live-provider tests mandatory for deterministic pull-request CI.

## Impact

- Repository: `ai-harness-skills`.
- Primary modules: provider result parsing, adapter event/envelope parsing, workflow begin/complete paths, ledger usage metadata/schema, configuration, doctor/report output, and security/reference documentation.
- GitNexus reports CRITICAL upstream impact for `parse_structured_result` (17 symbols and 12 execution processes) and HIGH impact for `WorkflowEngine._begin` (26 symbols and 3 execution processes).
- This change depends conceptually on the provider isolation contract from `harden-harness-provider-execution`; overlapping process-limit work must land once, not be duplicated.
- No new external dependency is required.
