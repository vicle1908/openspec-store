## Why

Recent Pydantic AI changes were moved into the archive with incomplete tasks and were marked complete in later commits, even though existing specs already prohibit unsupported completion claims. The store needs executable enforcement so archive readiness is checked at the mutation boundary rather than reconstructed after the fact.

## What Changes

- Add a repository-owned archive-readiness validator that checks task completion, required artifact presence, authoritative delta-spec paths, exact source/evidence identities, required gate results, and rollback evidence before a change can be reported ready.
- Add a minimal uv-managed `pyproject.toml`/`uv.lock` for reproducible store validator tests; the existing untracked local `.venv` SHALL not be treated as CI evidence.
- Add deterministic checks for archived changes that still contain incomplete tasks or whose completion-only task edits occurred after the archive move.
- Produce a corrective ledger for the four reviewed dependency/capability archives and cross-reference the owning active corrective change instead of rewriting archived artifacts.
- Integrate the validator into a tracked GitHub Actions store gate and the store-owned standard/Claude single and bulk archive workflows so incomplete readiness is blocked before agent-driven mutation and raw-CLI violations are caught before integration.
- Require archive evidence to bind source HEADs, raw dirty inventories, content-diff fingerprints, imported dependency origins, prerequisite-aware passes/skips, spec-sync results, and final store identity.
- Add tests covering no-delta changes, skipped specs, missing evidence, incomplete tasks, source drift, failed or unavailable gates, post-archive mutation detection, and clean successful archive readiness.

## Non-goals

- No modification of the external OpenSpec CLI package or user-global authentication/configuration.
- No rewriting, deleting, moving, or retroactively checking tasks in existing archives.
- No implementation of Pydantic AI runtime behavior or repair of Python Ruff/mypy findings.
- No mutation of the current untracked observability change or unrelated active JTI change.

## Capabilities

### New Capabilities

None. This change enforces existing archive, readiness-evidence, and framework-verification requirements and sets `skip_specs: true`.

### Modified Capabilities

None. Existing normative requirements already cover corrective ledgers, evidence-gated completion, inline spec sync, and pre-archive revalidation.

## Impact

- **openspec-store owner:** `pyproject.toml`, `uv.lock`, `scripts/validate-archive-readiness.py`, focused pytest fixtures/tests, `.github/workflows/validate-openspec-store.yml`, the corrective ledger, and store-owned archive surfaces under `.agents/skills`, `.claude/skills`, and `.claude/commands/opsx`.
- **workspace skill exposure:** `scripts/sync-workspace-agent-skills.py --check` verifies symlink exposure after the store-owned surfaces are updated; `.codex/skills` remains untouched.
- **code repository owners:** read-only evidence providers; this change does not edit agent-core, agent-harness, or agent-docs-sync.
- The validator must remain fail-closed for required evidence while distinguishing an intentional `skip_specs: true` no-op from a missing delta spec.
- This change is independent of the Python quality prerequisite but is executed after it and before capability-contract implementation so every later lifecycle uses the enforced gate.
