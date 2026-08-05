# Proposal: Cross-Repo Practice Enforcement Standardization

## Why

The workspace contains 16 Python repositories with moderate tool version drift and inconsistent enforcement patterns. While the drift is less severe than initially assessed, it creates two real problems: (1) new repos have no template to follow, and (2) there's no single mechanism to detect drift across repos.

### Actual Tool Version Drift (verified Aug 5, 2026)

| Tool | Locked Versions | Spread |
|------|----------------|--------|
| **Ruff** | 0.15.14 (6), 0.15.15 (5), 0.15.16 (1), 0.15.20 (1), **0.16.0** (3) | 0.15.14 → 0.16.0 |
| **mypy** | **2.1.0** (13), **2.3.0** (3) | 2.1.0 → 2.3.0 |
| **pytest** | **9.0.3** (13), **9.1.1** (3) | 9.0.3 → 9.1.1 |

Latest stable versions: ruff **0.16.1**, mypy **2.3.0**, pytest **9.1.1**.

### Pre-Commit Status

**4 repos missing pre-commit**: ai-harness-skills, code-daily-scan, tdt-observability, tdt-sheets.

**3 distinct established patterns** across the 12 repos that have pre-commit:

| Pattern | Repos | Hooks |
|---------|-------|-------|
| **A: Agent + local hooks** | agent-core, docs-sync, harness | gitleaks + ruff-pre-commit + **local mypy + pytest (uv run --frozen)** |
| **B: Standard** | ai-review, tdt-core, webhook-receiver | gitleaks + ruff-pre-commit + pre-commit-hooks |
| **C: Full linters** | jira-\*, browser-cli, ops-auto | gitleaks + shellcheck + shfmt + ruff-pre-commit + actionlint |

### Ruff Lint Rule Drift

All 16 repos have ruff rules configured. Rule counts range from 7 (ai-harness-skills) to 25 (agent-docs-sync), with the majority at 12 rules. Per-file-ignores vary significantly — tdt-sheets and code-daily-scan have 15+ per-file ignores for source-specific patterns.

### Cross-Repo Dependency Risks

- **tdt-core** is a hub dependency (12 of 16 repos depend on it via path sources)
- **Mixed pin quality**: some have proper `>=X.Y,<X.(Y+1)` ranges, some have only lower bounds, some have no pins at all
- **Repos missing version pins**: jira-skill (tdt-core[all], tdt-sheets), code-daily-scan (tdt-core), webhook-receiver (tdt-core)

### Business Impact

- New repos have no template to follow (must copy from existing repos)
- No mechanism to detect drift after initial setup
- Developers can't trust that quality checks are equivalent across repos

## What Changes

### 1. Canonical Template Repository

Create `~/Developer/workspace-python-template/` with:

- **pyproject.toml** — canonical tool config (ruff 19-rule set with per-file-ignores, mypy strict, pytest options, dependency-group versions)
- **.pre-commit-config.yaml** — builds on Pattern A (agent-core pattern) as the strongest existing baseline, adds uv-pre-commit for lockfile sync
- **check-enforcement.sh** — workspace-level drift detection script
- **README.md** — adoption checklist and override documentation

### 2. Standardize Tool Versions

Bump all 16 repos to latest stable:

- **ruff** >= 0.16.1 (from 0.15.14-0.16.0)
- **mypy** >= 2.3.0 (from 2.1.0-2.3.0)
- **pytest** >= 9.1.1 (from 9.0.3-9.1.1)
- **pytest-asyncio** >= 1.4.0, **pytest-cov** >= 7.1.0

### 3. Standardize Ruff Config

Adopt canonical 19-rule set across all repos. Per-file-ignores use the union of existing repo-specific patterns plus the canonical test ignores. Each repo may add repo-specific overrides documented in the template.

### 4. Standardize Pre-Commit Hooks

Three-tier approach:
- **All repos get**: gitleaks + ruff-pre-commit + pre-commit-hooks + uv-pre-commit (lockfile sync)
- **Agent repos keep**: local mypy/pytest hooks with `uv run --frozen`
- **Shell repos keep**: shellcheck/shfmt/actionlint (jira-\*, browser-cli, ops-auto)

### 5. Cross-Repo Dependency Contracts

Audit and fix version pins to use `>=X.Y,<X.(Y+1)` for all cross-repo dependencies.

### 6. Enforcement Script

`check-enforcement.sh` that detects drift across all 16 repos.

### Not Changing

- No uv workspace conversion (repos remain independent git repos with individual lockfiles)
- No shared uv.lock (each repo keeps its own lockfile)
- No structural changes to repo layout
- Existing OpenSpec specs are unaffected (`skip_specs: true`)
- No CI workflow changes (local enforcement only)
