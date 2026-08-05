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
