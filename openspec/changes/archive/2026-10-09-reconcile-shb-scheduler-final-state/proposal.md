# Proposal

## Why

The archived `2026-10-09-containerize-shb-scheduler-postgres18` change is implemented, but its immutable evidence and review artifacts predate later runtime hardening and do not reconcile the final implementation identity, test-count claims, or canonical-spec strict-validation result. The scheduler implementation and operator wiki also need a final-state consistency pass without reopening or editing the archive.

## What Changes

- Create a corrective, active OpenSpec change that reconciles final-state claims against live repository commits and command evidence.
- Preserve `openspec/changes/archive/2026-10-09-containerize-shb-scheduler-postgres18/` byte-for-byte; no archive edits or moves.
- Record value-blind evidence for the final scheduler and skills commits, validated task count, live verification commands, and known historical-artifact discrepancies.
- Reconcile the canonical `shb-schedule-engine` specification so strict validation no longer fails on an overlong requirement while preserving its behavior and scenarios.
- Update stale curated wiki entities to describe Docker Compose/PostgreSQL/advisory-lock operation while retaining the documented local SQLite fallback.
- **BREAKING**: Remove the obsolete user LaunchAgent plist `~/Library/LaunchAgents/com.shb.schedule.plist` after verifying the exact path and that no active scheduler process depends on it.
- Remove only the residual scheduler `__pycache__` directory after verifying it contains no source files.

## Capabilities

### New Capabilities

- `shb-schedule-final-state-reconciliation`: Immutable archive claim reconciliation, canonical specification conformance, and bounded documentation/runtime cleanup for the completed scheduler containerization.

### Modified Capabilities

- `shb-schedule-engine`: Split the overlong canonical requirement without changing observable behavior or scenario coverage.
- `shb-ecosystem-tooling`: Reconcile curated SHB scheduler descriptions with the final containerized architecture.

## Non-Goals

- Do not edit, rewrite, move, or re-archive the completed scheduler archive.
- Do not change scheduler runtime behavior, database schema, workflow semantics, or Docker image versions.
- Do not modify unrelated active OpenSpec changes or generated Graphify outputs.
- Do not remove arbitrary LaunchAgents, caches, repositories, or user files; cleanup is limited to the exact approved paths above.
- Do not push commits to any remote.

## Impact

- Makes final-state OpenSpec evidence auditable and distinct from historical review-plan claims.
- Restores strict validation for the canonical scheduler specification.
- Prevents operators and knowledge consumers from receiving stale host-service guidance.
- Removes one obsolete scheduler host artifact and one residual bytecode-only directory.

## Affected Ownership Boundaries

- Central planning/specification: `/Users/androidteam/Developer/platform/openspec-store`.
- Scheduler implementation evidence: `/Users/androidteam/Developer/shb/shb-schedule`.
- Scheduler skill documentation: `/Users/androidteam/Developer/shb/shb-agent-skills`.
- Curated wiki documentation: `/Users/androidteam/Developer/wiki/entities`.
- Exact approved host cleanup target: `/Users/androidteam/Library/LaunchAgents/com.shb.schedule.plist`.
