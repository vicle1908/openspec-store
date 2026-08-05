# Proposal: Cross-Repo Practice Enforcement Standardization

## Why

The workspace contains 16 Python repositories with significant drift in code quality enforcement:

### Tool Version Drift
| Tool | Versions Found | Count |
|------|---------------|-------|
| Ruff | 0.5.0, 0.8.4, 0.15.0, 0.15.20, 0.16.0 | **5 different versions** |
| mypy | 1.10.0, 1.11, 1.14.0, 2.1.0, 2.3.0 | **5 different versions** |
| pytest | 8.3.0, 8.3.4, 9.0.0, 9.1.1 | **4 different versions** |

### Enforcement Gap Drift
- **4 repos missing pre-commit hooks entirely**: ai-harness-skills, code-daily-scan, tdt-observability, tdt-sheets
- **3 different pre-commit hook patterns** across the 12 repos that have them (varying hook IDs, sources, and scope)
- **Ruff lint rules vary widely**: from 0 rule sets (tdt-sheets, agent-core) to 12 rule sets (majority), with inconsistent ignore lists ranging from 0 to 11 entries
- **mypy strictness**: All have `strict = true`, but version drift means different strict behaviors

### Cross-Repo Dependency Risks
- **tdt-core** is a hub dependency (12 of 16 repos depend on it via `path = "../tdt-core"`)
- **tdt-sheets** (5 consumers), **jira-skill** (3 consumers), **agent-core** (3 consumers)
- No dependency version contracts or minimum-version enforcement between repos
- A breaking change in tdt-core can silently break 12 downstream repos
- **Missing version pins**: jira-skill (`tdt-core[all]`, `tdt-sheets`), jira-daily-reports (`jira-skill`), jira-epic-report (`jira-skill`), jira-kanban (`tdt-core`, `tdt-sheets`) have NO version constraints

### Business Impact
- Developers can't trust that passing quality checks in one repo means equivalent quality in another
- Cross-repo contributions require understanding per-repo tooling nuances
- CI/CD pipelines can't apply uniform quality gates
- New repos have no template to follow

## What Changes

### 1. Shared Tooling Config Template
Create a canonical `pyproject.toml` tooling configuration template that all 16 Python repos adopt. Based on 5-provider review findings, this includes:
- **Ruff**: Target rule set (17 rules including S for security), line length, target version, ignore rules, per-file-ignores for tests
- **mypy**: `strict = true` + `warn_unused_configs` (strict already enables 8 of 10 flags)
- **pytest**: Coverage thresholds, async mode, markers
- **dependency-group versions**: Pinned minimum versions for ruff, mypy, pytest across all repos

### 2a. Pilot Phase (NEW — from review H3)
Apply enforcement to 3 representative repos first (agent-core, tdt-core, jira-skill) to validate
the canonical config doesn't surface overwhelming violations before rolling out to all 16 repos.

### 2. Standardized Pre-Commit Hooks
All 16 repos get identical pre-commit enforcement:
- gitleaks (secret scanning)
- ruff-check + ruff-format (using `uv run` for version consistency)
- mypy with `--strict` flag
- Standard pre-commit-hooks (trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, check-added-large-files)
- Optional shellcheck/shfmt for repos with bash scripts

### 3. Cross-Repo Dependency Contracts
For the hub-and-spoke dependency graph (tdt-core → consumers), establish:
- Minimum version pins for cross-repo dependencies
- A `uv.lock`-compatible source override pattern that works across repos
- CI verification that cross-repo imports match declared dependencies

### 4. Workspace-Level Enforcement Script
A single script (`scripts/check-enforcement.sh`) that:
- Runs ruff, mypy, pytest across all 16 repos
- Reports drift from the canonical config
- Can be used in CI or as a periodic audit

### Not Changing
- No uv workspace conversion (repos remain independent git repos with individual lockfiles)
- No shared `uv.lock` (each repo keeps its own lockfile)
- No structural changes to repo layout
- Existing OpenSpec specs are unaffected (`skip_specs: true`)
