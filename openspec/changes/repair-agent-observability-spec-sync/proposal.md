# Proposal: Repair Agent Observability Main Spec Synchronization

## Why

Archiving establish-agent-observability-contract aborted main specification synchronization due to a requirement-header mismatch in agent-docs-sync-observability, leaving the canonical agent-observability-contract capability absent from the main specification catalog.

Following the archive of establish-agent-observability-contract, the main specification root retained previous baseline versions without incorporating the canonical cross-agent observability contract requirements (composition-root initialization, lifecycle completion, canonical correlation attributes, trace-log correlation, evaluation trace linkage, privacy defaults, and exporter topologies) or consumer observability conformance requirements. This corrective change repairs the delta specification headers and formally synchronizes the missing capabilities and requirements to main specs.

## What Changes

- Introduce the canonical `agent-observability-contract` specification as an ADDED capability covering composition root initialization, idempotency, lifecycle completion, correlation attributes, trace-log correlation, evaluation-to-trace linkage, privacy defaults, exporter topology, extensibility, and conformance evidence classifications.
- Repair the `agent-docs-sync-observability` delta specification by structuring both `Observability initialization at composition root` and `Consumer observability conformance` under `ADDED Requirements` rather than `MODIFIED Requirements` to eliminate the header mismatch.
- Enable successful downstream specification synchronization without hand-editing main specifications.

## Capabilities

### New Capabilities
- `agent-observability-contract`: Canonical cross-repo agent observability contract defining composition root initialization, idempotency, lifecycle flush, canonical correlation attributes, trace-log correlation, evaluation-to-trace linkage, privacy defaults, and exporter topology.

### Modified Capabilities
- `agent-docs-sync-observability`: Adds composition-root observability initialization and consumer observability conformance requirements.

## Non-Goals

- Recreating, resetting, or modifying the archived `openspec/changes/archive/2026-08-21-establish-agent-observability-contract/` directory.
- Directly hand-editing main specifications in `openspec/specs/` outside the supported OpenSpec workflow.
- Modifying runtime or test source code in `agent-core`, `agent-docs-sync`, or `agent-harness`.
- Performing immediate archive operations within this planning proposal.

## Impact

- **Affected Ownership Boundaries**:
  - `openspec/specs/agent-observability-contract/`: New canonical specification catalog entry.
  - `openspec/specs/agent-docs-sync-observability/`: Main specification synchronized with consumer observability requirements.
  - Agent ecosystem repos (`agent-core`, `agent-docs-sync`, `agent-harness`): Alignment between active implementation and repository specifications.
