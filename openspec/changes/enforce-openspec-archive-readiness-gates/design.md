## Context

See proposal.md for the incident. Existing `agent-framework-verification`, `readiness-evidence`, and `openspec-runtime-governance` specs already define corrective ledgers, source identity, inline spec synchronization, and pre-archive revalidation; the gap is executable enforcement at the store boundary.

## Goals / Non-Goals

**Goals:**

- Add a deterministic store-owned readiness check that can run before and after archive operations.
- Keep historical archives immutable while recording corrective ownership and evidence separately.
- Make no-delta changes, intentional `skip_specs: true`, and required delta specs distinguishable.

**Non-Goals:**

- Do not replace or patch the external OpenSpec CLI package.
- Do not retroactively rewrite existing archives or claim to repair their historical evidence.

## Decisions

- **Store-owned validator:** implement the check under `openspec-store/scripts/` and invoke it from store verification/CI and the reviewed archive guidance. A wrapper is auditable and reversible; direct mutation of the external CLI is not.
- **Active preflight is fail-closed:** an active change cannot be reported archive-ready when tasks are incomplete, required artifacts are absent, required evidence is missing, or source identity changed after the last gate.
- **Post-archive audit is scoped to the archive delta:** compare newly moved archive paths and subsequent task-only mutations relative to a supplied base ref. Do not fail the entire legacy store because historical debt already exists; emit a corrective ledger row for known debt.
- **Authoritative spec paths:** consume `artifactPaths.specs.existingOutputPaths` from status/instructions rather than inferring specs from proposal, design, or tasks.
- **Evidence schema:** store redacted JSON/Markdown records containing repository, SHA, dirty inventory, content fingerprint, command/exit status, environment classification, source origins, spec-sync result, rollback result, and owner.

## Risks / Trade-offs

- [Legacy archives already violate the gate] → scope blocking checks to newly touched archives and maintain an explicit historical corrective ledger.
- [Archive wrapper bypassed] → add CI/store verification that detects newly introduced incomplete archives even when a user runs the raw CLI.
- [Evidence file drift] → hash the evidence manifest externally or exclude its self-referential line and record the final fingerprint separately.
- [False failure for skip-spec changes] → require `.openspec.yaml` to declare `skip_specs: true` and verify that no delta spec files exist.

## Migration Plan

1. Implement the validator and unit fixtures in openspec-store.
2. Run it against the four reviewed archived changes to produce a corrective baseline without modifying them.
3. Add the pre-archive/CI invocation and update the owned archive guidance.
4. Verify clean success, each failure class, rollback of the validator itself, and no mutation of unrelated active changes.
