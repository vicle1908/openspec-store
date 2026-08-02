# TDT Ecosystem - Toolchain Standardization

**Date:** 2026-05-21  
**Status:** 📋 Final Draft  
**Relates to:** [spec.md](spec.md), [design.md](design.md), [docs/UV-BEST-PRACTICES.md](../../docs/UV-BEST-PRACTICES.md)

---

## Current State (Audit)

| Setting | jira-skill | jira-epic-report | webhook-receiver | ops-automation |
|---------|-----------|-----------------|-----------------|----------------|
| uv version | >=0.11.15 | >=0.11.15 | >=0.11.9,<0.12 | (none) |
| Python | 3.14 | 3.14 | 3.14 | 3.12 |
| line-length | 88 | 100 | 100 | 100 |
| ruff rules | E,W,F,I,N,B,C4,UP | E,F,W,I,N,UP,B,A,C4,SIM | E,W,F,I,N,B,C4,UP | E,F,I,N,W,UP,B,C4,SIM |
| mypy | relaxed (12 disabled) | relaxed (10 disabled) | relaxed (11 disabled) | strict |
| formatter | black (pre-commit) | (none) | (none) | (none) |
| build backend | hatchling | hatchling | hatchling | hatchling |
| src layout | ✅ src/jira_skill/ | ❌ epic_report/ | ✅ src/webhook_receiver/ | ✅ src/ops_automation/ |
| dev deps | PEP 735 | PEP 735 | PEP 735 | PEP 735 |

**Key inconsistencies:** line-length, ruff rule sets, formatter (black vs none), mypy strictness, uv version pin.

---

## Standardized Toolchain (Target)

### 1. uv Configuration

```toml
[tool.uv]
default-groups = ["dev"]
required-version = ">=0.11.15"
python-preference = "only-managed"
```

**Decisions:**
- `required-version = ">=0.11.15"` — minimum for all projects (current stable)
- `python-preference = "only-managed"` — never use system Python
- `default-groups = ["dev"]` — dev deps installed by default in development
- **No uv workspace** — projects stay independent (per UV-BEST-PRACTICES.md recommendation)
- Path deps for tdt-core: `tdt-core = {path = "../tdt-core", editable = true}`

### 2. Python Version

```
# .python-version (in each project root)
3.14.5
```

All projects target Python 3.14. ops-automation-suite will be upgraded from 3.12 → 3.14.

### 3. Ruff (Linting + Formatting)

```toml
[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "A",    # flake8-builtins
    "C4",   # flake8-comprehensions
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking (move imports to TYPE_CHECKING blocks)
    "RUF",  # ruff-specific rules
]
ignore = [
    "E501",   # line too long (handled by formatter)
    "SIM108", # ternary operator (readability preference)
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # unused imports OK in __init__
"tests/**/*.py" = ["F841", "B007", "E402", "B905"]  # test flexibility

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
docstring-code-format = true
```

**Decisions:**
- `line-length = 100` — majority wins (3/4 projects already use 100)
- `ruff format` replaces black — faster, same output, one less dependency
- Added `A` (builtins shadowing), `SIM` (simplify), `TCH` (type-checking imports), `RUF` (ruff-specific)
- `isort` handled by ruff `I` rule — no separate isort config needed
- jira-skill migrates from 88 → 100 (one-time `ruff format` run)

### 4. mypy (Gradual Typing)

```toml
[tool.mypy]
python_version = "3.14"
# Gradual strictness — tighten over time
warn_return_any = true
warn_no_return = true
warn_unused_ignores = true
no_implicit_optional = true
strict_equality = true
check_untyped_defs = true
disallow_untyped_defs = false          # Phase 2: enable
disallow_incomplete_defs = false       # Phase 2: enable
disallow_untyped_decorators = false    # Phase 3: enable
ignore_missing_imports = true          # until all stubs available

# Per-module overrides for new code (strict)
[[tool.mypy.overrides]]
module = "tdt_core.*"
disallow_untyped_defs = true
disallow_incomplete_defs = true
warn_return_any = true
```

**Decisions:**
- Start pragmatic (matches current state), tighten over time
- New code (tdt-core) starts strict from day 1
- Remove `disable_error_code` lists gradually — each removed code = progress
- `ignore_missing_imports = true` until third-party stubs are available
- Per-module overrides allow strict typing for new packages without breaking old code

**Typing roadmap:**
1. **Now:** Baseline passes, no regressions
2. **Phase 2:** Enable `disallow_untyped_defs` for public APIs
3. **Phase 3:** Enable `disallow_untyped_decorators`, remove `ignore_missing_imports`
4. **Phase 4:** Full `strict = true` (target: when all `disable_error_code` entries removed)

### 5. pytest

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --tb=short --strict-markers"
markers = [
    "integration: marks tests requiring real API access",
    "slow: marks tests that take > 5s",
]
```

**Decisions:**
- `--strict-markers` prevents typos in marker names
- `integration` marker for tests that hit real APIs (skipped in CI by default)
- Coverage target: 80% minimum (enforced in CI)

### 6. Build System

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/<package_name>"]
```

**Decisions:**
- hatchling everywhere (already adopted)
- `src/` layout for all projects (jira-epic-report migrates from flat → src layout)
- Explicit `packages` declaration prevents accidental inclusion

### 7. Pre-commit (Standardized)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
        args: [--maxkb=500]
      - id: check-merge-conflict
      - id: detect-private-key
      - id: debug-statements

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic>=2.5]
        args: [--ignore-missing-imports]
```

**Decisions:**
- `ruff` replaces both black and isort hooks
- `ruff-format` replaces black formatter
- mypy in pre-commit for type checking on commit
- jira-skill migrates from black+isort → ruff+ruff-format

### 8. Dependency Configuration Pattern

```toml
[project]
name = "project-name"
version = "1.0.0"
requires-python = ">=3.14,<3.15"
dependencies = [
    # Core deps — pinned to compatible release
    "pydantic>=2.5.0,<3.0.0",
    "python-dotenv>=1.0.0,<2.0.0",
    # Internal deps — path reference
    "tdt-core @ file:///${PROJECT_ROOT}/../tdt-core",
]

[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-cov>=5.0.0",
    "pytest-mock>=3.12.0",
    "ruff>=0.15.0",
    "mypy>=1.14.0",
    "pre-commit>=4.6.0",
]

[project.optional-dependencies]
# Feature extras (for consumers)
gitlab = ["python-gitlab>=8.3.0,<9.0.0"]
```

**Decisions:**
- `requires-python = ">=3.14,<3.15"` — pin to minor version
- External deps: `>=X.Y.Z,<NEXT_MAJOR` (compatible release range)
- Internal deps: path reference with `editable = true` in dev
- Dev deps in `[dependency-groups]` (PEP 735), NOT `[project.optional-dependencies]`
- Feature extras in `[project.optional-dependencies]` (for consumers to opt-in)

---

## Migration Checklist (Per Project)

### tdt-core (new — start correct)
- [ ] Use all standardized configs from day 1
- [ ] `strict = true` in mypy (new code, no legacy)
- [ ] 100% test coverage target

### jira-skill
- [ ] Change line-length 88 → 100
- [ ] Run `uv run ruff format .` (one-time reformat)
- [ ] Replace `.pre-commit-config.yaml` black+isort → ruff+ruff-format
- [ ] Add ruff rules: A, SIM, TCH, RUF
- [ ] Add path dep to tdt-core
- [ ] Remove `disable_error_code` entries one at a time

### jira-epic-report
- [ ] Migrate to src layout: `epic_report/` → `src/epic_report/`
- [ ] Add ruff rules: TCH, RUF
- [ ] Add pre-commit config (currently none)
- [ ] Add path dep to tdt-core (Phase 3)

### webhook-receiver
- [ ] Update uv required-version: `>=0.11.9,<0.12` → `>=0.11.15`
- [ ] Add ruff rules: A, SIM, TCH, RUF
- [ ] Add pre-commit config with ruff (replace any black usage)
- [ ] Add path dep to tdt-core (Phase 4)

### ops-automation-suite
- [ ] Upgrade Python 3.12 → 3.14
- [ ] Align ruff config with standard
- [ ] Add uv required-version
- [ ] Add path dep to tdt-core (Phase 5)

---

## uv Workspace: Decision

**Decision: NOT now. Revisit at 6+ projects.**

| Factor | Workspace | Independent |
|--------|-----------|-------------|
| Shared lockfile | 🟢 One lockfile for all | 🟡 Per-project lockfiles |
| Dependency conflicts | 🔴 All projects must agree | 🟢 Each project independent |
| CI complexity | 🟡 Single install | 🟢 Per-project CI |
| Path deps | 🟢 Automatic resolution | 🟡 Manual `file://` paths |
| Project mobility | 🔴 Tied to workspace | 🟢 Can be moved/cloned independently |
| Current state | Requires migration | ✅ Already working |

**Rationale:** With 4-5 projects and different dependency profiles (FastAPI vs typer vs pure library), a shared lockfile would create conflicts. Path deps with `file://` work fine for tdt-core sharing. Revisit when ecosystem reaches 6+ projects with aligned dependency profiles.

---

## Template: New Project Scaffold

```bash
# Create new project in ecosystem
mkdir tdt/new-project && cd tdt/new-project
uv init --lib --name new-project
# Then apply standardized configs from this document
```

Complete `pyproject.toml` template:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "new-project"
version = "0.1.0"
description = "Description here"
readme = "README.md"
requires-python = ">=3.14,<3.15"
license = {text = "MIT"}
authors = [{name = "lekhanhvinh"}]
dependencies = [
    "tdt-core[all] @ file:///${PROJECT_ROOT}/../tdt-core",
]

[project.scripts]
new-project = "new_project.cli:app"

[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-cov>=5.0.0",
    "pytest-mock>=3.12.0",
    "ruff>=0.15.0",
    "mypy>=1.14.0",
    "pre-commit>=4.6.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/new_project"]

[tool.uv]
default-groups = ["dev"]
required-version = ">=0.11.15"
python-preference = "only-managed"

[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH", "RUF"]
ignore = ["E501", "SIM108"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*.py" = ["F841", "B007", "E402", "B905"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
docstring-code-format = true

[tool.mypy]
python_version = "3.14"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --tb=short --strict-markers"
```

---

## Commands Reference

```bash
# Development workflow
uv sync                          # Install all deps (dev included)
uv run ruff check .              # Lint
uv run ruff format .             # Format
uv run mypy src/                 # Type check
uv run pytest                    # Test
uv run pytest --cov --cov-fail-under=80  # Test with coverage

# Dependency management
uv add <package>                 # Add production dep
uv add --group dev <package>     # Add dev dep
uv lock --upgrade-package <pkg>  # Upgrade single package
uv sync --locked                 # CI: verify lockfile is fresh

# Pre-commit
uv run pre-commit install        # Install hooks
uv run pre-commit run --all-files  # Run all hooks
```
