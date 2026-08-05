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

**Canonical versions:**
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
    "TCH",   # flake8-type-checking
    "RUF",   # ruff-specific
    "TC",    # type-checking imports
    "S",     # flake8-bandit (security)
    "PTH",   # flake8-use-pathlib
    "PIE",   # misc lints
    "PT",    # pytest style
]
ignore = ["E501"]  # line length handled by formatter

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Canonical mypy config:**
```toml
[tool.mypy]
python_version = "3.14"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_reexport = true
warn_redundant_casts = true
warn_unused_ignores = true
```

**Canonical pytest config:**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short"
```

#### Layer 2: Standardized Pre-Commit Hooks

All repos get the same `.pre-commit-config.yaml` pattern:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.x.x
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
        entry: uv run mypy .
        language: system
        types: [python]
      - id: pytest
        name: pytest
        entry: uv run pytest -q --tb=short
        language: system
        types: [python]
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.x.x
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
      - id: detect-private-key
```

**Difference from current state:** 
- Removes ad-hoc shellcheck/shfmt/actionlint hooks (CI concern, not commit hook concern)
- Uses `uv run` consistently (not bare `ruff` or `mypy`)
- Adds mypy+pytest hooks to the 4 repos missing pre-commit entirely

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

**New contract**: Each consumer pins `>=X.Y,<X.(Y+1)` for cross-repo deps. The hub repo (`tdt-core`) is responsible for not breaking within a minor version.

#### Layer 4: Workspace Enforcement Script

`~/Developer/scripts/check-enforcement.sh` — runs across all 16 repos:
- Checks pyproject.toml has canonical tool config sections
- Checks pre-commit hooks exist and match template
- Runs ruff check, mypy, pytest per repo
- Reports version drift vs canonical versions
- Exit code non-zero on any drift

## Trade-offs

| Decision | Chosen | Alternative | Rationale |
|----------|--------|-------------|-----------|
| Individual lockfiles | ✓ Keep | uv workspace with shared lockfile | Repos are independent git repos; shared lockfile would couple CI/CD |
| Editable path sources | ✓ Keep | Published packages | Development velocity; path sources work with individual lockfiles |
| Template-based config | ✓ Template | Centralized tool | Avoids coupling repos to a shared config package; simpler adoption |
| Pre-commit over prek | ✓ pre-commit | prek | pre-commit is more widely installed; prek adoption is premature for 16 repos |
| `uv run` in hooks | ✓ Yes | Bare tool invocation | Guarantees version consistency with lockfile |

## Risks

1. **Version bump coordination**: When upgrading canonical versions, all 16 repos need updating. Mitigated by the enforcement script.
2. **Ruff rule additions**: New rules may surface violations in repos that previously passed. Mitigated by incremental rule adoption.
3. **Edit lock on pre-commit hooks**: Standardizing hook format requires touching 12 repos. One-at-a-time commits.
