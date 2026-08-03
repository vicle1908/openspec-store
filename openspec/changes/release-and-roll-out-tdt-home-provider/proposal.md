## Why

The provider artifact is locally verified, but release and deployment readiness
must be demonstrated separately from source implementation and before any
consumer or live `~/.tdt` cutover is authorized.

## What Changes

- Define a reproducible provider release-candidate gate using a locked local
  wheelhouse and a checkout-free installation.
- Define staged provider deployment ownership, compatibility checks, approval
  records, and an explicit rollback artifact.
- Require evidence that provider-only diagnostics and packaged contracts work in
  the target runtime before consumer adoption is opened.
- Keep live root cutover and consumer source migration in their own changes.

## Capabilities

### New Capabilities

- `tdt-home-provider-rollout`: provider release qualification, staged rollout,
  approval gates, and rollback evidence.

### Modified Capabilities

- None. The provider API contract and consumer conformance contracts remain
  separate capabilities.

## Ownership Boundaries

- `tdt-core` owns the artifact, package metadata, and provider-only smoke tests.
- Release operators own staging deployment, approval, and rollback decisions.
- Consumer repositories own adoption verification after provider rollout.
- `openspec-store` records evidence and gates; it does not publish packages or
  restart services automatically.
- The real `~/.tdt` and external deployment systems remain untouched until the
  later cutover change is explicitly approved.

## Impact

- Affects the provider build/release procedure and staging operator runbook.
- Requires a locked dependency closure, a disposable install target, and a
  retained rollback artifact.
- No application dependency or live database schema change is introduced.

## Explicit Non-Goals

- No Nexus publication, credential rotation, consumer migration, or live-root
  repair.
- No Docker restart or deployment mutation in this planning change.
- No claim that consumer compatibility is proven by provider-only tests.
