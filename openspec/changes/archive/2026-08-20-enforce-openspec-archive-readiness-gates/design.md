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

- **Store-owned validator:** implement `scripts/validate-archive-readiness.py` with focused fixtures/tests in `tests/`, then invoke it from `.github/workflows/validate-openspec-store.yml` and the reviewed archive workflows. A repository-owned validator is auditable and reversible; direct mutation of the external CLI is not.
- **Active preflight is fail-closed:** an active change cannot be reported archive-ready when tasks are incomplete, required artifacts are absent, required evidence is missing, or source identity changed after the last gate.
- **Post-archive audit is scoped to the archive delta:** compare newly moved archive paths and subsequent task-only mutations relative to a supplied base ref. Do not fail the entire legacy store because historical debt already exists; emit a corrective ledger row for known debt.
- **Authoritative spec paths:** consume `artifactPaths.specs.existingOutputPaths` from status/instructions rather than inferring specs from proposal, design, or tasks.
- **Evidence schema:** store redacted JSON/Markdown records containing repository, SHA, dirty inventory, content fingerprint, command/exit status, environment classification, source origins, spec-sync result, rollback result, and owner.
- **Reproducible tool environment:** add a minimal uv project for store scripts/tests, commit its lockfile, and use `uv run --frozen` in local and GitHub Actions gates. CI installs the reviewed OpenSpec CLI `1.10.0`; the local untracked `.venv` is never an input to readiness.

## Risks / Trade-offs

- [Legacy archives already violate the gate] → scope blocking checks to newly touched archives and maintain an explicit historical corrective ledger.
- [Archive workflow bypassed] → the tracked GitHub Actions gate compares the PR/base range and detects newly introduced incomplete archives or post-archive completion edits even when a user runs the raw CLI.
- [Evidence file drift] → hash the evidence manifest externally or exclude its self-referential line and record the final fingerprint separately.
- [False failure for skip-spec changes] → require `.openspec.yaml` to declare `skip_specs: true` and verify that no delta spec files exist.
- [CI environment diverges from local `.venv`] → build only from committed `pyproject.toml`/`uv.lock`, print tool versions, and fail `uv run --frozen` or OpenSpec version mismatches.

## Migration Plan

1. Add the uv-managed store tooling environment, validator, and unit fixtures.
2. Run the validator against the five reviewed archived changes to produce a corrective baseline without modifying them.
3. Add the GitHub Actions invocation and update `.agents/skills/openspec-{archive,bulk-archive}-change`, the matching `.claude/skills` surfaces, and `opsx/{archive,bulk-archive}.md` without touching `.codex/skills`.
4. Verify clean success, each failure class, rollback of the validator itself, and no mutation of unrelated active changes.
