# Design: Clean-Break Full Workspace Python Dependency Upgrade

## Context

See `proposal.md` for motivation. The workspace contains 22 Python repositories across 4 namespaces (`tdt/`, `platform/`, `vds/`, and `ai-tooling/`). All repos use PEP 517/621 packaging (`pyproject.toml`) and `uv`. Multiple services depend on shared sibling libraries via `[tool.uv.sources]` editable paths (`../tdt-core`, `../tdt-sheets`, `../jira-skill`, `../agent-core`). Pinned upper bounds (`<`) and legacy polyfills prevent adopting latest major upstream capabilities (DBOS v3.1, Anthropic SDK v1.8, Pydantic AI 2.51, Pandas 3.0 Copy-on-Write).

Surrounding deployment and automation surfaces include:
- 5 repositories with Dockerfiles (`jira-skill`, `agent-core`, `tdt-observability`, `claude-code-provider-adapter`, `hermes-webui`), all standardizing on Python 3.14 runtime containers.
- 16 repositories maintaining `.pre-commit-config.yaml` hooks (`ruff-pre-commit`, `uv-pre-commit`, `gitleaks`).
- 6 system LaunchAgents under `~/Library/LaunchAgents/` executing Python jobs (`com.developer.index-refresh`, `com.tdt.ai-review`, `com.workspace.claude-code-provider-adapter`, etc.).

## Goals / Non-Goals

**Goals:**
- Strip all `<` upper bound specifiers from direct and dev dependencies across all 22 repositories.
- Perform a clean-break upgrade to the latest available releases on PyPI for all dependencies.
- Remove all legacy compatibility shims, deprecated event hooks (`@app.on_event`), `datetime.utcnow()`, and legacy typing.
- Upgrade core upstream frameworks to their latest major APIs:
  - DBOS v2 → v3.1.0 in `tdt-core` and scheduler consumers.
  - Anthropic v0.x → v1.8.0 in `agent-core` and AI review/sync agents.
  - Pydantic AI 2.32 → 2.51.0 and Harness 0.23 → 0.36.0 in `agent-core`.
  - Pandas 2.3 → 3.0.6 (pure Copy-on-Write) in `viettel-excel-updater`.
- Coordinate internal SemVer increments (`tdt-core` 0.4.0, `tdt-sheets` 0.2.0, `jira-skill` 0.4.0, `agent-core` 0.3.0) and update all 12 consumer manifests synchronously.
- Update `.pre-commit-config.yaml` hook revisions (`ruff-pre-commit` to v0.16.9, `uv-pre-commit` to 0.12.19) across all 16 repos.
- Fully regenerate `uv.lock` across all 21 lockfile-managed repos and verify all pytest test suites and strict type checks pass.

**Non-Goals:**
- Preserving backwards compatibility with Python < 3.14 (all projects target Python 3.14+).
- Retaining fallback imports or compatibility wrappers for older library major versions.
- Modifying database schemas outside of DBOS scheduler table migrations.

## Decisions

### 1. Zero Legacy Shims Policy (Clean Break over Dual-Version Polyfills)
- **Decision:** Eliminate all fallback branches, conditional version checks (`if sys.version_info < ...`), and legacy wrappers. Upgrade callers directly to modern APIs.
- **Rationale:** The workspace has full source ownership and single-operator control. Maintaining compatibility shims increases cyclomatic complexity, hides deprecation warnings, and delays necessary technical debt remediation.
- **Alternatives Considered:**
  - *Dual-mode compatibility wrappers:* Rejected because it preserves technical debt and complicates test suites.

### 2. Tiered Topological Migration Sequence
- **Decision:** Upgrade dependencies and lockfiles strictly in dependency order:
  - Tier 0: `tdt-core`
  - Tier 1: `tdt-sheets`, `jira-skill`
  - Tier 2: `agent-core`, `ai-harness-skills`, `tdt-observability`, `jira-kanban-from-spreadsheet`
  - Tier 3: `agent-docs-sync`, `agent-harness`, `code-daily-scan`, `jira-daily-reports`, `jira-epic-report`, `webhook-receiver`, `ai-review`
  - Standalone: `claude-code-provider-adapter`, `hermes-webui`, `openspec-store`, `browser-cli`, `ops-automation-suite`, `viettel-excel-updater`, `wiki-mcp-server`
- **Rationale:** Inter-package path dependencies (`path = "../<sibling>"`) require upstream libraries to be upgraded, locked, and versioned first before downstream solvers can resolve.
- **Alternatives Considered:**
  - *All-at-once concurrent lockfile update:* Failed solver validation due to unsatisfied internal version floor constraints.

### 3. Native DBOS v3 Client Migration
- **Decision:** Migrate `src/tdt_core/scheduler/` from internal private imports (`_dbos`, `_queue`) to DBOS v3 public client abstractions (`DBOS`, `DBOSConfig`, `Queue`, `Debouncer`). Update system table queries from `dbos.application_versions` to DBOS v3 `system.workflow_status`.
- **Rationale:** DBOS v3 reorganizes internal modules and schema. Using public client contracts prevents future private import breakage.

### 4. Pydantic AI & Harness Sandboxing Alignment
- **Decision:** Upgrade `pydantic-ai` to 2.51.0 and `pydantic-ai-harness` to 0.36.0, unpinning Monty from v0.0.18. Dynamic workflows will use Harness 0.36's native execution environment.
- **Rationale:** Harness 0.36 dropped `MontyRepl` in favor of standard pydantic-ai-slim execution. Keeping Monty 0.0.18 blocked upgrading the agent framework.

### 5. Pure Copy-on-Write (CoW) in Pandas 3.0
- **Decision:** Audit all dataframe manipulations in `viettel-excel-updater` and `tdt-observability`. Replace chained indexing mutations with `.loc[mask, col] = val` or explicit `.copy()`.
- **Rationale:** Pandas 3.0 removes silent in-place mutating views. Strict CoW prevents subtle data corruption bugs.

### 6. Pre-Commit Hook Revision Alignment
- **Decision:** Synchronize `.pre-commit-config.yaml` across all 16 repositories:
  - `ruff-pre-commit`: v0.16.1/v0.16.3 → v0.16.9
  - `uv-pre-commit`: 0.12.0/0.12.5 → 0.12.19
- **Rationale:** Mismatched pre-commit linter versions cause developer friction where CLI `uv run ruff` passes but pre-commit git hooks fail on different formatting heuristics.

## Risks / Trade-offs

- **[DBOS v3 System Migration]** Stale workflows in SQLite/PostgreSQL might not match DBOS v3 schema.  
  → *Mitigation:* Run DBOS migration scripts during container boot and test state reconciliation with `test_state_reconciliation.py`.
- **[Anthropic v1 Client Changes]** Streaming event shapes differ between v0 and v1.  
  → *Mitigation:* Focus test verification on `agent_core/llm/model.py` streaming tests and inspect live SSE outputs.
- **[Pandas 3.0 Copy-on-Write Exceptions]** Chained assignments in Excel transforms could raise runtime exceptions.  
  → *Mitigation:* Exercise `viettel-excel-updater` batch processing scripts against test spreadsheets before committing.
- **[Lockfile Cascade Divergence]** Sibling repos resolving inconsistent transitive pins.  
  → *Mitigation:* Run a final workspace-wide verification script ensuring all shared dependencies match resolved lockfile versions.
- **[LaunchAgent Path Desynchronization]** Background daemons referencing stale python binary paths.  
  → *Mitigation:* Validate each LaunchAgent's command execution after `uv sync` to ensure subpath persistence.

## Migration Plan

1. **Pre-flight Baseline:** Verify Git status across all 22 repos; create clean feature branches (`feature/python-deps-clean-break`).
2. **Phase 1 (Tier 0 Base):** Upgrade `tdt-core` manifest to unpinned latest + DBOS v3. Lock, sync, test, and bump version to `0.4.0`.
3. **Phase 2 (Tier 1 Subsystems):** Update `tdt-sheets` and `jira-skill` to `tdt-core>=0.4.0`. Lift bounds, lock, sync, and test (1,903 tests in `jira-skill`). Remediate 7 `datetime.utcnow()` calls in `jira-skill`. Bump versions.
4. **Phase 3 (Tier 2 Frameworks):** Update `agent-core` to `tdt-core>=0.4.0`. Lift bounds to `pydantic-ai>=2.51`, `harness>=0.36`, `anthropic>=1.8`. Adapt model calls. Lock, sync, and run 852 tests + strict mypy. Bump version to `0.3.0`.
5. **Phase 4 (Tier 3 Consumers):** Update downstream services to new SDK versions floors. Remediate `datetime.utcnow()` in `webhook-receiver`. Lift bounds, lock, sync, and run test suites per repo.
6. **Phase 5 (Standalone & Tooling):** Upgrade `viettel-excel-updater`, `claude-code-provider-adapter`, `browser-cli`, etc. Enforce Pandas CoW and Pyupgrade cleanups.
7. **Phase 6 (Tooling, Hooks & Daemons):** Update `.pre-commit-config.yaml` across 16 repos; verify Dockerfiles and LaunchAgent services.
8. **Phase 7 (Workspace Gates):** Execute `uv run ruff check` and `uv run pytest` across all 22 repositories. Verify 0 errors.
9. **Rollback Strategy:** Atomic Git commits per repository allow targeted rollbacks via `git checkout main` or branch reset if an unresolvable runtime issue occurs.
