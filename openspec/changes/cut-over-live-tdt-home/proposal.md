## Why

The real `~/.tdt` tree contains operator-owned configuration, links, runtime
state, schedules, and logs; a cutover therefore needs an explicit, reversible
runbook after provider, conformance, synthetic migration, and rollout gates
have passed.

## What Changes

- Define preflight evidence and approval gates for a concrete live-root plan.
- Define quiescence, descriptor-relative execution, journal checkpoints,
  recovery, rollback, and post-cutover verification.
- Require value-free snapshots and redacted operator evidence.
- Keep the change dormant until an authorized operator supplies a specific
  plan, maintenance window, principals, and rollback decision.

## Capabilities

### New Capabilities

- `tdt-home-live-cutover`: approval-gated planning and execution contract for
  the real operator `~/.tdt` root.

### Modified Capabilities

- None. Provider, source-conformance, migration-engine, and rollout contracts
  are prerequisites and remain independently verifiable.

## Ownership Boundaries

- The operator owns the live root, maintenance window, principal approvals, and
  final cutover decision.
- `tdt-core` owns only the approved migration engine and verification tools.
- Consumer/deployment owners own quiescence, restart, and post-cutover smoke
  evidence for their repositories.
- `openspec-store` records the plan/evidence but never authorizes execution.

## Impact

- Potentially affects the live `~/.tdt` filesystem and services that read it,
  but this planning artifact performs no such operation.
- Requires a retained backup/snapshot, concrete mapping, maintenance window,
  and tested rollback path before execution.

## Explicit Non-Goals

- No live filesystem mutation, permission repair, symlink replacement, secret
  rotation, database change, service restart, or schedule trigger in this turn.
- No guessed mapping for duplicate config sources or broken credentials.
- No automatic approval based on local tests or a clean provider wheelhouse.
