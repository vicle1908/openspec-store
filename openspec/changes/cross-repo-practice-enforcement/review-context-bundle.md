# Review Context Bundle: cross-repo-practice-enforcement

## Actual Workspace State (Verified Aug 5, 2026)

### Locked Tool Versions
- ruff: 0.15.14 (6 repos), 0.15.15 (5 repos), 0.15.16 (1), 0.15.20 (1), 0.16.0 (3 repos)
- mypy: 2.1.0 (13 repos), 2.3.0 (3 repos: agent-docs-sync, agent-harness, ai-harness-skills)
- pytest: 9.0.3 (13 repos), 9.1.1 (3 repos: agent-docs-sync, agent-harness, tdt-observability)

### Latest Stable (from GitHub API)
- ruff: 0.16.1
- mypy: 2.3.0
- pytest: 9.1.1
- pytest-asyncio: 1.4.0
- gitleaks: v8.30.1
- ruff-pre-commit: v0.16.1
- pre-commit-hooks: v6.0.0
- pre-commit: v4.6.1

### Pre-Commit Patterns
Pattern A (agent-core, docs-sync, harness): gitleaks v8.30.1 + ruff-pre-commit v0.15.15 + local mypy/pytest (uv run --frozen)
Pattern B (ai-review, tdt-core, webhook-receiver): gitleaks v8.30.0 + ruff-pre-commit v0.16.0 + pre-commit-hooks v6.0.0
Pattern C (jira-*, browser-cli, ops-auto): gitleaks v8.30.0 + shellcheck + shfmt + ruff-pre-commit v0.16.0 + actionlint

Missing pre-commit: ai-harness-skills, code-daily-scan, tdt-observability, tdt-sheets

### Ruff Rule Counts
agent-core: 19, agent-docs-sync: 25, agent-harness: 14, ai-harness-skills: 7, ai-review: 12,
browser-cli: 8, code-daily-scan: 12, jira-daily-reports: 12, jira-epic-report: 12,
jira-kanban: 12, jira-skill: 12, ops-automation: 12, tdt-core: 12, tdt-observability: 9,
tdt-sheets: 13, webhook-receiver: 12

### Cross-Repo Dependencies
Hub: tdt-core (12 consumers via path sources)
Well-pinned: agent-core (>=0.3,<0.4), agent-docs-sync (>=0.3,<0.4), jira-daily-reports (>=0.1.0)
Missing pins: jira-skill (tdt-core[all], tdt-sheets), code-daily-scan (tdt-core), webhook-receiver (tdt-core)

### All repos mypy strict = true: YES (all 16)
### All repos target Python 3.14: YES (except tdt-observability which has no target-version set)
### All repos line-length 100: YES (except tdt-observability which uses default 88)


## Change Artifacts

### proposal.md
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


### design.md
# Design: Cross-Repo Practice Enforcement

## Architecture Overview

The workspace has **16 independent Python repositories** sharing a common workspace root (`~/Developer/`). Each repo has its own git history, lockfile, and CI pipeline. Enforcement must work across this distributed model without creating coupling.

### Current State: Dependency Graph

```
                    tdt-core (hub — 12 consumers)
                   /    |    \        \
          tdt-sheets   ...   ...     ...
         /    |    \
  jira-daily  jira-epic  jira-kanban  jira-skill
                                      |
                              webhook-receiver

  agent-core → agent-docs-sync, agent-harness, code-daily-scan

  Independent: browser-cli, ops-automation-suite, ai-harness-skills
```

**Hub dependency**: `tdt-core` is consumed by 12 of 16 repos via editable path sources.

### Current Pre-Commit Patterns

**Pattern A — Agent ecosystem (strongest):**
- gitleaks v8.30.1 + ruff-pre-commit v0.15.15 + local mypy (uv run --frozen) + local pytest (uv run --frozen)
- Used by: agent-core, agent-docs-sync, agent-harness

**Pattern B — Standard:**
- gitleaks v8.30.0 + ruff-pre-commit v0.16.0 + pre-commit-hooks v6.0.0
- Used by: ai-review, tdt-core, webhook-receiver

**Pattern C — Full linters:**
- gitleaks v8.30.0 + shellcheck + shfmt + ruff-pre-commit v0.16.0 + actionlint
- Used by: jira-\*, browser-cli, ops-automation-suite

## Design Decisions

### 1. Build on Pattern A, Don't Replace It

Pattern A already has the strongest hooks (local mypy + pytest with `uv run --frozen`). The canonical template extends Pattern A with:
- Updated rev versions to latest stable
- `uv-pre-commit` hook for lockfile sync
- `pre-commit-hooks` for hygiene checks
- shellcheck/shfmt as optional addons (Pattern C repos keep theirs)

### 2. Canonical Tool Versions (Latest Stable — Verified Aug 5, 2026)

```toml
[dependency-groups]
dev = [
    "ruff>=0.16.1",
    "mypy>=2.3.0",
    "pytest>=9.1.1",
    "pytest-asyncio>=1.4.0",
    "pytest-cov>=7.1.0",
    "pre-commit>=4.6.1",
]
```

### 3. Canonical Ruff Config

```toml
[tool.ruff]
target-version = "py314"
line-length = 100

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "N",     # pep8-naming
    "UP",    # pyupgrade
    "B",     # flake8-bugbear
    "A",     # flake8-builtins
    "C4",    # flake8-comprehensions
    "SIM",   # flake8-simplify
    "TCH",   # flake8-type-checking
    "TC",    # type-checking imports
    "RUF",   # ruff-specific
    "S",     # flake8-bandit (security)
    "PTH",   # flake8-use-pathlib
    "PIE",   # misc lints
    "PT",    # pytest style
    "ARG",   # unused arguments (in tests)
    "SLF",   # private member access (in tests)
]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*.py" = ["F841", "B007", "E402", "S101", "S108", "ARG001", "ARG002", "SLF001"]
```

**Per-repo override pattern** (repos add to the canonical base):
```toml
# Agent repos — pydantic-ai runtime type hints
"src/agent_core/_ai/*" = ["TC001", "TC002"]

# tdt-sheets — intentional shadowing
"src/tdt_sheets/exceptions.py" = ["A001"]

# jira-epic-report — typographic characters in reporter output
"epic_report/reporters/**/*.py" = ["RUF001", "RUF002", "RUF003"]
```

### 4. Canonical Mypy Config

```toml
[tool.mypy]
python_version = "3.14"
strict = true
warn_unused_configs = true
```

Note: `strict = true` already enables 8 of 10 commonly listed flags. Only `warn_unused_configs` is NOT in strict mode.

### 5. Canonical Pre-Commit Config

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.1
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.12.0
    hooks:
      - id: uv-lock

  - repo: local
    hooks:
      - id: mypy
        name: mypy (strict)
        entry: uv run --frozen mypy .
        language: system
        types: [python]
      - id: pytest
        name: pytest
        entry: uv run --frozen pytest -q --tb=short
        language: system
        types: [python]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
      - id: detect-private-key
```

**Key design decisions:**
- Uses `uv run --frozen` — prevents lockfile drift during commits
- Adds `uv-pre-commit` with `uv-lock` hook — keeps lockfile in sync with pyproject.toml
- Local mypy/pytest hooks use the project's venv via `uv run`
- Pattern C repos keep shellcheck/shfmt/actionlint as additional local hooks

### 6. Cross-Repo Dependency Contracts

```toml
# Consumer pyproject.toml — proper pinning pattern:
[project]
dependencies = [
    "tdt-core[jira,scheduler]>=0.3,<0.4",   # explicit extras + range
]

[tool.uv.sources]
tdt-core = { path = "../tdt-core", editable = true }
```

**Contract**: Each consumer pins `>=X.Y,<X.(Y+1)` for cross-repo deps. The hub repo (`tdt-core`) maintains backward compatibility within a minor version.

### 7. Enforcement Script

`~/Developer/scripts/check-enforcement.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

REPOS=(agent-core agent-docs-sync agent-harness ai-harness-skills ai-review
       browser-cli code-daily-scan jira-daily-reports jira-epic-report
       jira-kanban-from-spreadsheet jira-skill ops-automation-suite
       tdt-core tdt-observability tdt-sheets webhook-receiver)

CANONICAL_RUFF="0.16.1"
CANONICAL_MYPY="2.3.0"
CANONICAL_PYTEST="9.1.1"

DRIFT=0
for repo in "${REPOS[@]}"; do
    cd ~/Developer/$repo
    echo "=== $repo ==="

    # Check tool version floors in pyproject.toml
    for tool_var in "ruff>=$CANONICAL_RUFF" "mypy>=$CANONICAL_MYPY" "pytest>=$CANONICAL_PYTEST"; do
        tool=$(echo "$tool_var" | cut -d> -f1)
        ver=$(echo "$tool_var" | cut -d= -f2)
        if ! grep -q "\"$tool>=$ver\"" pyproject.toml 2>/dev/null; then
            echo "  DRIFT: $tool version floor below $ver"
            DRIFT=1
        fi
    done

    # Check ruff config has select rules
    if ! grep -q '\[tool.ruff.lint\]' pyproject.toml 2>/dev/null; then
        echo "  DRIFT: missing [tool.ruff.lint] section"
        DRIFT=1
    fi

    # Check mypy strict
    if ! grep -q 'strict = true' pyproject.toml 2>/dev/null; then
        echo "  DRIFT: mypy strict = true not set"
        DRIFT=1
    fi

    # Check pre-commit exists
    if [ ! -f .pre-commit-config.yaml ]; then
        echo "  DRIFT: missing .pre-commit-config.yaml"
        DRIFT=1
    fi

    # Check pre-commit has required repos
    if [ -f .pre-commit-config.yaml ]; then
        for required_repo in "gitleaks/gitleaks" "astral-sh/ruff-pre-commit"; do
            if ! grep -q "$required_repo" .pre-commit-config.yaml; then
                echo "  DRIFT: pre-commit missing $required_repo"
                DRIFT=1
            fi
        done
    fi

    echo ""
done

exit $DRIFT
```

## Trade-offs

| Decision | Chosen | Alternative | Rationale |
|----------|--------|-------------|-----------|
| Individual lockfiles | ✓ Keep | uv workspace with shared lockfile | Repos are independent git repos; shared lockfile would couple CI/CD |
| Editable path sources | ✓ Keep | Published packages | Development velocity; path sources work with individual lockfiles |
| Template-based config | ✓ Template | Centralized config package | Avoids coupling repos; simpler adoption; no new dependency |
| Build on Pattern A | ✓ Pattern A | Single canonical template | Pattern A already has the strongest hooks; avoids regressions |
| `uv run --frozen` in hooks | ✓ --frozen | bare uv run | Prevents accidental lockfile modifications during commits |
| uv-pre-commit for lock sync | ✓ Add | Manual | Automates pyproject.toml ↔ uv.lock synchronization |
| Ruff S (bandit) enabled | ✓ Yes | Skip security rules | Catches eval/exec/shell injection; low false-positive rate |
| Ruff TCH+TC enabled | ✓ Yes | Skip | Enforces TYPE_CHECKING boundary; reduces cross-module coupling |
| pre-commit (not prek) | ✓ pre-commit | prek | pre-commit more widely installed; prek migration is a separate change |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| mypy 2.1→2.3 surfaces new errors | 13 repos need updating | Pilot on 3 repos first; `[[tool.mypy.overrides]]` for third-party gaps |
| Ruff 0.15→0.16 surfaces new violations | Low — most repos already at 0.15.x | Per-file-ignores for pre-existing violations; `--fix` first pass |
| pre-commit hook format change | Touching 12 repos | One-at-a-time commits; template ensures consistency |
| Cross-repo breaking changes | tdt-core changes break consumers | `>=X.Y,<X.(Y+1)` contract; consumer CI catches breaks |
| uv-pre-commit rev drift | Hook version falls behind | Enforcement script checks pre-commit revs |


### tasks.md
# Tasks: Cross-Repo Practice Enforcement

## Phase 0: Pilot on 3 Repos (4 tasks)

- [ ] 0.1 Apply full enforcement to **agent-core** (69 tests, GitHub Actions, Pattern A)
  - Update dependency-group versions: ruff>=0.16.1, mypy>=2.3.0, pytest>=9.1.1
  - Update pre-commit revs: ruff-pre-commit v0.15.15→v0.16.1, gitleaks v8.30.1
  - Add uv-pre-commit hook for lockfile sync
  - Run `uv lock` to regenerate lockfile
  - Verify: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy .`, `uv run pytest -q`
- [ ] 0.2 Apply full enforcement to **tdt-core** (20 tests, GitLab CI, hub dependency)
  - Same gates as 0.1
  - Critical: any break here cascades to 12 consumers
  - Update pre-commit revs to match canonical
- [ ] 0.3 Apply full enforcement to **jira-skill** (90 tests, GitLab CI, most cross-deps)
  - Same gates as 0.1
  - Fix missing version pins on tdt-core[all] and tdt-sheets (HIGH finding from review)
  - Update pre-commit revs: gitleaks v8.30.0→v8.30.1, ruff-pre-commit v0.16.0→v0.16.1
  - Keep shellcheck/shfmt/actionlint (Pattern C)
- [ ] 0.4 Evaluate pilot results
  - Document violations found per repo
  - Document time to fix
  - Document any rule adjustments needed for the canonical set
  - If mypy 2.3.0 surfaces many new errors, add `[[tool.mypy.overrides]]` for third-party gaps

## Phase 1: Create Template and Scripts (3 tasks)

- [ ] 1.1 Create `~/Developer/workspace-python-template/` with:
  - `pyproject.toml` — canonical [tool.ruff], [tool.mypy], [tool.pytest.ini_options], [dependency-groups]
  - `.pre-commit-config.yaml` — canonical hook layout (gitleaks v8.30.1, ruff v0.16.1, uv-pre-commit, mypy, pytest, pre-commit-hooks v6.0.0)
  - `scripts/check-enforcement.sh` — workspace-level drift checker
  - `README.md` — usage instructions and adoption checklist with override documentation
- [ ] 1.2 Verify template passes all gates: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy .`
- [ ] 1.3 Commit template

## Phase 2: Standardize Tool Versions (4 tasks)

- [ ] 2.1 Update ruff version floor to `>=0.16.1` in all 16 repos' `[dependency-groups]`
  - Run `uv lock` in each repo to regenerate lockfiles
  - Verify `uv run ruff check .` passes in each repo
- [ ] 2.2 Update mypy version floor to `>=2.3.0` in all 16 repos' `[dependency-groups]`
  - Run `uv lock` in each repo
  - Verify `uv run mypy .` passes (or add overrides for third-party gaps)
- [ ] 2.3 Update pytest version floor to `>=9.1.1` (and pytest-asyncio>=1.4.0) in all 16 repos
  - Run `uv lock` in each repo
  - Verify `uv run pytest -q` passes
- [ ] 2.4 Run `uv run --frozen` in all repos to verify lockfile sync

## Phase 3: Standardize Ruff Config (3 tasks)

- [ ] 3.1 Update ruff lint select rules to canonical 19-rule set in repos with drift:
  - agent-core: already 19 rules — verify alignment with canonical
  - agent-docs-sync: 25 rules → 19 canonical + repo-specific extras
  - browser-cli: 8 rules → 19 canonical
  - tdt-observability: 9 rules → 19 canonical
  - ai-harness-skills: 7 rules → 19 canonical
  - agent-harness: 14 rules → 19 canonical (add ARG, SLF)
  - tdt-sheets: 13 rules → 19 canonical + keep repo-specific per-file-ignores
  - code-daily-scan: 12 rules → 19 canonical + keep repo-specific per-file-ignores
- [ ] 3.2 Add canonical per-file-ignores to all repos:
  - `"__init__.py" = ["F401"]`
  - `"tests/**/*.py" = ["F841", "B007", "E402", "S101", "S108", "ARG001", "ARG002", "SLF001"]`
  - Keep existing repo-specific overrides (document in template README)
- [ ] 3.3 Run `uv run ruff check . --fix` then `uv run ruff check .` in all 16 repos

## Phase 4: Add Pre-Commit to Missing Repos (2 tasks)

- [ ] 4.1 Create `.pre-commit-config.yaml` from canonical template in: ai-harness-skills, code-daily-scan, tdt-observability, tdt-sheets
- [ ] 4.2 Install and verify: `uv run pre-commit install && uv run pre-commit run --all-files`

## Phase 5: Standardize Existing Pre-Commit Configs (3 tasks)

- [ ] 5.1 Update Pattern A repos (agent-core, docs-sync, harness) — update revs to canonical:
  - ruff-pre-commit v0.15.15 → v0.16.1
  - Add uv-pre-commit hook
  - Add pre-commit-hooks v6.0.0
  - Keep local mypy/pytest hooks with `uv run --frozen`
- [ ] 5.2 Update Pattern B repos (ai-review, tdt-core, webhook-receiver) — add local mypy/pytest hooks:
  - Add uv run --frozen mypy + pytest local hooks
  - Add uv-pre-commit hook
  - Update ruff-pre-commit to v0.16.1
- [ ] 5.3 Update Pattern C repos (jira-\*, browser-cli, ops-auto) — update revs:
  - Update gitleaks v8.30.0 → v8.30.1
  - Update ruff-pre-commit v0.16.0 → v0.16.1
  - Add uv-pre-commit hook
  - Keep shellcheck/shfmt/actionlint

## Phase 6: Cross-Repo Dependency Contracts (2 tasks)

- [ ] 6.1 Audit and fix missing version pins across all cross-repo dependencies:
  - jira-skill: add `>=0.3,<0.4` to tdt-core[all] and `>=0.1,<0.2` to tdt-sheets
  - code-daily-scan: add `>=0.3,<0.4` to tdt-core[gitlab] and `>=0.1,<0.2` to tdt-sheets
  - webhook-receiver: add `>=0.3,<0.4` to tdt-core[gitlab,scheduler] and `>=0.3,<0.4` to jira-skill
  - jira-daily-reports: add `>=0.3,<0.4` to jira-skill (currently only `>=0.1.0` on tdt-sheets)
  - agent-docs-sync: verify agent-core pin uses proper range
  - Ensure `>=X.Y,<X.(Y+1)` pattern for ALL cross-repo deps
- [ ] 6.2 Verify `uv run --frozen` works in all repos (lockfile sync check)

## Phase 7: Validation and Documentation (3 tasks)

- [ ] 7.1 Run `check-enforcement.sh` across all 16 repos — verify zero drift
- [ ] 7.2 Update workspace documentation (AGENTS.md if needed)
- [ ] 7.3 Commit all changes per-repo, then archive openspec change:
  ```
  cd ~/Developer/openspec-store
  openspec archive cross-repo-practice-enforcement --store openspec-store --yes
  git add openspec/
  git commit -m "archive: cross-repo-practice-enforcement"
  ```

