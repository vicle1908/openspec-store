# tdt-artifact-hygiene Specification

## Purpose
TBD - created by archiving change tdt-workspace-cleanup-2026-06-29. Update Purpose after archive.
## Requirements
### Requirement: GitNexus / Graphify output directories SHALL NOT be tracked in git

Every TDT ecosystem repository's `.gitignore` SHALL list `.graphify/` (or `.graphify/cache/`) so that the GitNexus toolchain never has a chance to commit a generated artifact. A file under `*/.graphify/` SHALL NOT appear in `git ls-files` for any repo in the workspace.

#### Scenario: Generated `.graphify_root` is not tracked

- **GIVEN** a developer runs `npx gitnexus analyze` against `tdt-core` or `webhook-receiver`
- **WHEN** the command writes files into `<repo>/.graphify/`
- **THEN** `git -C <repo> ls-files .graphify/` SHALL return an empty list
- **AND** `<repo>/.gitignore` SHALL contain the line `.graphify/`

#### Scenario: A repo that runs Graphify SHALL have a .gitignore entry before regeneration

- **GIVEN** a repo's `.gitignore` is missing `.graphify/`
- **WHEN** Graphify is invoked against the repo
- **THEN** the operator SHALL add `.graphify/` to `.gitignore` BEFORE running the analyzer
- **AND** this rule SHALL be enforced by the GitNexus pre-edit hook `config/codex/scripts/pre-edit-check.sh`

#### Scenario: Cross-repo audit finds zero tracked .graphify files

- **WHEN** `openspec validate --strict tdt-artifact-hygiene` is run
- **THEN** a sweep across `~/Developer/tdt/*/.graphify/` SHALL report 0 paths from `git ls-files` for every Python and TypeScript repo in the workspace inventory

### Requirement: Lockfile backups SHALL NOT be committed

`*.lock.bak`, `*.lock.orig`, and `*.lock~` files SHALL NOT appear in `git ls-files` for any repo in the workspace. `uv` operations that produce such files SHALL redirect them to the developer's local stash or `/tmp`, never inside the repo root.

#### Scenario: `uv lock` does not leave a backup in the repo

- **GIVEN** a developer runs `uv lock` in `tdt-core`
- **WHEN** the command completes
- **THEN** no `uv.lock.bak`, `uv.lock.orig`, or `uv.lock~` SHALL exist under `tdt-core/`
- **AND** `git -C tdt-core ls-files | grep -E 'uv\.lock\.(bak|orig|~)'` SHALL return empty

#### Scenario: A historical `.lock.bak` is purged

- **GIVEN** a `*.lock.bak` file exists at `<repo>/uv.lock.bak`
- **WHEN** the cleanup is applied
- **THEN** the file SHALL be deleted (or `git rm --cached` if tracked) without affecting the live `uv.lock`
- **AND** the post-cleanup SHA-256 of `<repo>/uv.lock` SHALL equal the pre-cleanup SHA-256

### Requirement: Generated caches SHALL live in canonical runtime directories only

Generated caches such as `.graphify/`, `reports-out/`, `htmlcov/`, `.pytest_cache/`, `.ruff_cache/`, and `.mypy_cache/` SHALL be referenced through canonical `$TDT_HOME/state/` paths when their lifetime exceeds one session. In-repo `.graphify/` directories are session-scoped regeneration artifacts, not durable state.

#### Scenario: Cross-session state is delegated to `~/.tdt/state/`

- **GIVEN** a tool needs to persist output across sessions (e.g., a graph or coverage report)
- **WHEN** the tool writes its output
- **THEN** it SHALL write under `$TDT_HOME/state/<tool>/` (e.g., `$TDT_HOME/state/gitnexus/`)
- **AND** the in-repo path `.graphify/` SHALL be treated as transient and re-creatable on demand

### Requirement: A repo's `.gitignore` SHALL list every generated artifact pattern the repo's tooling can emit

Each Python repo's `.gitignore` SHALL include at least: `.graphify/`, `reports-out/`, `htmlcov/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.venv/`, `__pycache__/`, `*.egg-info/`, `dist/`, `build/`, `.coverage`. A repo SHALL be considered compliant only when every pattern above is present.

#### Scenario: Repo audit verifies all standard patterns

- **WHEN** the lint-config-baseline check runs against a repo
- **THEN** it SHALL verify every required pattern is present in `.gitignore`
- **AND** the check SHALL exit non-zero if any pattern is missing

### Requirement: Cleanup MUST be reversible through git history

`.graphify/` deletion and lockfile backup deletion MUST keep the prior state reachable via `git log --diff-filter=D -- .graphify/` for at least 30 days after the change is archived, so a future contributor can recover a generated report from the historical tree if the underlying index is needed.

#### Scenario: Historical `GRAPH_REPORT.md` remains recoverable

- **GIVEN** `agent-core/.graphify/GRAPH_REPORT.md` was tracked at SHA `abc123`
- **WHEN** the cleanup is archived
- **THEN** `git -C agent-core log --diff-filter=D -- .graphify/GRAPH_REPORT.md` SHALL still list a deletion commit referencing the prior tree
- **AND** `git -C agent-core show <sha>:.graphify/GRAPH_REPORT.md` SHALL return the prior report content

