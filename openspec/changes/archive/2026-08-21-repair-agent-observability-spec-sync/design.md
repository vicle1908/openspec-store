# Design: Repair Agent Observability Main Spec Synchronization

## Context

See proposal.md - Why.
During the archiving of `establish-agent-observability-contract`, the archive command halted main specification synchronization because `agent-docs-sync-observability` used a `MODIFIED` section header for requirements that were previously undeclared in the main spec. As a result, `agent-observability-contract` remained unmerged into `openspec/specs/` and consumer observability requirements remained unsynchronized in `openspec/specs/agent-docs-sync-observability/spec.md`.

## Goals / Non-Goals

**Goals:**
- Provide a clean OpenSpec change definition that resolves delta header mismatches.
- Ensure `agent-observability-contract` and `agent-docs-sync-observability` can be cleanly synced to main specs without aborting.
- Comply with all OpenSpec validation constraints (`openspec validate --strict`).

**Non-Goals:**
- Modifying product source code in `agent-core`, `agent-docs-sync`, or `agent-harness`.
- Altering the archived change record `2026-08-21-establish-agent-observability-contract`.
- Manual out-of-band editing of files in `openspec/specs/`.

## Decisions

### Decision 1: Declare all new requirements under ADDED Requirements
- **Rationale**: When syncing delta specs into existing main specs, OpenSpec requires any requirement not currently present in the target main spec to be declared under `## ADDED Requirements`. For new capabilities (like `agent-observability-contract`), all requirements are `ADDED`. For existing capabilities (`agent-docs-sync-observability`), newly introduced requirements (`Observability initialization at composition root`, `Consumer observability conformance`) must also be `ADDED`.
- **Alternatives Considered**: Modifying main specs manually was rejected because OpenSpec governance requires specs to evolve through validated changes.

### Decision 2: Preserve exact canonical contract terminology and scenarios
- **Rationale**: The contract established in the archived change is already implemented in `agent-core` and consumer repositories. The specification text must match the exact normative definitions (`SHALL`, `MUST`, correlation attributes, lifecycle flush, privacy defaults, exporter routing).
- **Alternatives Considered**: Simplifying or reducing requirement text was rejected as it would diverge from implemented behavior.

## Risks / Trade-offs

- [Risk] Main spec sync conflicts if main specs were edited out-of-band → Mitigation: Strict validation against current main specs ensures zero conflicts.
- [Risk] Re-archiving confusion → Mitigation: The change is scoped strictly to corrective planning artifacts without re-archiving.

## Migration Plan

1. Create and validate planning artifacts (`proposal.md`, `specs/`, `design.md`, `tasks.md`).
2. Run strict validation via `openspec validate repair-agent-observability-spec-sync --strict --store openspec-store`.
3. When ready for spec sync, standard OpenSpec tooling (`openspec sync-specs` or `openspec archive`) will apply the deltas cleanly.

## Transaction Boundaries

The OpenSpec store is a git repository. Transaction boundaries are defined at the commit level for planning artifacts. No code repositories or runtime databases are mutated.
