# Design: Cross-Repo Practice Enforcement

## Architecture Overview

The workspace has **16 independent Python repositories** sharing a common workspace root (`~/Developer/`). Unlike a monorepo, these repos have individual git histories, lockfiles, and CI pipelines. Enforcement must work across this distributed model.

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

### Enforcement Layers

#### Layer 1: Canonical pyproject.toml Tooling Config (Template)

A single source-of-truth template that all repos inherit. Located at `~/Developer/workspace-python-template/`.

**Canonical versions (latest stable as of Aug 2026):**
```
ruff   >= 0.16.0
mypy   >= 2.3.0
pytest >= 9.1.1
```

**Canonical ruff rule set:**
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
    "TCH",   # flake8-type-checking (enforces TYPE_CHECKING boundary)
    "TC",    # type-checking imports (companion to TCH)
    "RUF",   # ruff-specific
    "S",     # flake8-bandit (security — catches eval, exec, shell injection)
    "PTH",   # flake8-use-pathlib
    "PIE",   # misc lints
    "PT",    # pytest style
]
ignore = ["E501"]  # line length handled by formatter

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*.py" = ["F841", "B007", "E402", "S101"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Canonical mypy config:**
```toml
[tool.mypy]
python_version = "3.14"
strict = true
warn_unused_configs = true
# strict = true already enables: warn_return_any, disallow_untyped_defs,
# disallow_any_generics, check_untyped_defs, no_implicit_reexport,
# warn_redundant_casts, warn_unused_ignores
# Only warn_unused_configs is NOT in strict mode
```

**Canonical pytest config:**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short"
```

**Canonical dependency-group versions:**
```toml
[dependency-groups]
dev = [
    "pytest>=9.1.1",
    "pytest-cov>=7.1.0",
    "pytest-asyncio>=1.3.0",
    "ruff>=0.16.0",
    "mypy>=2.3.0",
    "pre-commit>=4.6.0",
]
```

#### Layer 2: Standardized Pre-Commit Hooks

All repos get the same `.pre-commit-config.yaml` pattern:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.0
    hooks:
      - id: gitleaks
  
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.0
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format
  
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

**Key design decisions (updated per review):**
- Uses `uv run --frozen` in hooks — prevents lockfile drift during commits
- Removes ad-hoc shellcheck/shfmt/actionlint hooks (CI concern, not commit hook)
- Uses `uv run` consistently (not bare `ruff` or `mypy`)
- Adds mypy+pytest hooks to the 4 repos missing pre-commit entirely
- Hook IDs use canonical names (`ruff` not `ruff-check`)
- Ruff S rules with per-file-ignores for tests (S101 assert)
- Shellcheck added to canonical template for repos with bash scripts

**Future consideration: prek** — Rust-based drop-in replacement for pre-commit. Used by Apache Airflow, CPython, FastAPI. Workspace-aware hooks (per-module), faster execution. Can migrate later without config changes.

#### Layer 3: Cross-Repo Dependency Contracts

For the hub-and-spoke model where `tdt-core` feeds 12 consumers:

```toml
# In consumer pyproject.toml dependencies:
[project]
dependencies = [
    "tdt-core[jira,scheduler]>=0.3,<0.4",  # explicit extras
]

# In [tool.uv.sources]:
[tool.uv.sources]
tdt-core = { path = "../tdt-core", editable = true }
```

**Contract**: Each consumer pins `>=X.Y,<X.(Y+1)` for cross-repo deps. The hub repo (`tdt-core`) maintains backward compatibility within a minor version.

**Import boundary enforcement** (gap in uv — no runtime isolation):
- Ruff `TCH` + `TC` rules enforce TYPE_CHECKING imports reduce coupling
- CI builds Docker images per member (only declared deps) to catch undeclared imports
- Custom AST-based pytest tests can verify imports match declared dependencies

#### Layer 4: Workspace Enforcement Script

`~/Developer/scripts/check-enforcement.sh` — runs across all 16 repos:

```bash
#!/usr/bin/env bash
# Cross-repo practice enforcement checker
# Checks: tool versions, ruff config, pre-commit hooks, test passage

set -euo pipefail
REPOS=(agent-core agent-docs-sync agent-harness ai-harness-skills ai-review
       browser-cli code-daily-scan jira-daily-reports jira-epic-report
       jira-kanban-from-spreadsheet jira-skill ops-automation-suite
       tdt-core tdt-observability tdt-sheets webhook-receiver)

# Canonical minimum versions
CANONICAL_RUFF="0.16.0"
CANONICAL_MYPY="2.3.0"
CANONICAL_PYTEST="9.1.1"

DRIFT=0
for repo in "${REPOS[@]}"; do
    cd ~/Developer/$repo
    echo "=== $repo ==="
    
    # Check tool versions
    # Check ruff config has select rules
    # Check pre-commit exists
    # Run ruff check
    # Run mypy
done

exit $DRIFT
```

**What it checks:**
1. `pyproject.toml` has `[tool.ruff.lint]` with canonical select rules
2. `pyproject.toml` has `[tool.mypy]` with `strict = true`
3. Tool version minimums in `[dependency-groups]`
4. `.pre-commit-config.yaml` exists and has required hooks
5. `uv run ruff check .` passes
6. `uv run mypy .` passes (or at least runs)

## Trade-offs

| Decision | Chosen | Alternative | Rationale |
|----------|--------|-------------|-----------|
| Individual lockfiles | ✓ Keep | uv workspace with shared lockfile | Repos are independent git repos; shared lockfile would couple CI/CD |
| Editable path sources | ✓ Keep | Published packages | Development velocity; path sources work with individual lockfiles |
| Template-based config | ✓ Template | Centralized config package | Avoids coupling repos; simpler adoption; no new dependency |
| pre-commit (not prek) | ✓ pre-commit | prek | pre-commit more widely installed; prek migration is a separate change |
| `uv run --frozen` in hooks | ✓ --frozen | bare uv run | Prevents accidental lockfile modifications during commits |
| Ruff S (bandit) enabled | ✓ Yes | Skip security rules | Catches eval/exec/shell injection; low false-positive rate |
| Ruff TCH+TC enabled | ✓ Yes | Skip | Enforces TYPE_CHECKING boundary; reduces cross-module coupling |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Version bump coordination | All 16 repos need updating | Enforcement script detects drift; batch PR possible |
| Ruff rule additions surface violations | Repos that previously passed may fail | Incremental rule adoption; ignore lists for pre-existing violations |
| mypy 2.x strict surfaces new errors | Type errors not caught by 1.x | Pilot on 2-3 repos first; add [[tool.mypy.overrides]] for third-party gaps |
| pre-commit hook format change | Touching 12 repos | One-at-a-time commits; template ensures consistency |
| mypy strict + new version | New strict checks may surface errors | Run per-repo; fix incrementally; some repos may need mypy overrides |
| Cross-repo breaking changes | tdt-core changes break consumers | >=X.Y,<X.(Y+1) contract; consumer CI catches breaks |
