# Capability: lint-config-baseline

## Purpose

Establish a single, canonical ruff and mypy configuration that every TDT Python repository MUST inherit. Today, ruff rule sets diverge across repos (some miss `A`, `SIM`, `TCH`, `RUF`) and mypy `strict = true` is suppressed in `jira-skill` and `jira-epic-report`. This spec pins the bar so a developer moving from one repo to another gets the same lint signals.

## ADDED Requirements

### Requirement: Every Python repo's `[tool.ruff.lint] select` SHALL be a fixed canonical set

The `[tool.ruff.lint] select` array in every Python repo's `pyproject.toml` SHALL equal `["E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH", "RUF"]`. The set is closed: any rule addition SHALL be made through a new OpenSpec change that revises this requirement.

#### Scenario: A repo's ruff select matches the canonical set

- **GIVEN** a Python repo in the workspace inventory defined in `agent-core-quality-gate`
- **WHEN** `python -c 'import tomllib; print(sorted(tomllib.load(open("pyproject.toml", "rb"))["tool"]["ruff"]["lint"]["select"]))' | jq . == "<sorted canonical array>"`
- **THEN** the comparison SHALL return true
- **AND** the lint-config-baseline check SHALL exit 0

#### Scenario: A repo is missing `RUF` and `TCH`

- **GIVEN** `tdt-sheets/pyproject.toml` lacks `RUF` and `TCH` in its select list
- **WHEN** the cleanup runs
- **THEN** `tdt-sheets/pyproject.toml` SHALL be updated to include `"RUF"` and `"TCH"` in `select`
- **AND** `ruff check .` SHALL pass against the new baseline

#### Scenario: A repo is missing all canonical rules

- **GIVEN** `jira-epic-report/pyproject.toml` lacks `TCH` and `RUF`
- **WHEN** the cleanup runs
- **THEN** the file SHALL be edited to include the missing rules
- **AND** any new violations surfaced by the added rules SHALL be fixed inline

### Requirement: Mypy SHALL run with `strict = true` and `disallow_untyped_defs = true`

Every Python repo's `pyproject.toml` `[tool.mypy]` section SHALL set `strict = true` and `disallow_untyped_defs = true`. A repo SHALL NOT use a blanket `disable_error_code` list as a substitute for fixing real type errors; selective per-line overrides are acceptable, blanket suppressions are not.

#### Scenario: `jira-skill` enables strict mode

- **GIVEN** `jira-skill/pyproject.toml` currently disables `disable_error_code` blanket-wide
- **WHEN** the cleanup runs
- **THEN** the blanket `disable_error_code` entry SHALL be removed
- **AND** `strict = true` and `disallow_untyped_defs = true` SHALL be present
- **AND** `uv run mypy . --strict` SHALL exit 0

#### Scenario: `jira-epic-report` enables strict mode

- **GIVEN** `jira-epic-report/pyproject.toml` currently suppresses `disallow_untyped_defs`
- **WHEN** the cleanup runs
- **THEN** `strict = true` SHALL be set
- **AND** the blanket suppression SHALL be removed
- **AND** any actual type errors surfaced SHALL be fixed or annotated inline

#### Scenario: Blanket `disable_error_code` is forbidden

- **WHEN** the lint-config-baseline validator inspects any repo's `pyproject.toml`
- **THEN** it SHALL fail if it finds a `disable_error_code` line that lists more than 2 error codes
- **AND** it SHALL allow per-line overrides (e.g. `# type: ignore[arg-type]`)

### Requirement: Ruff check and ruff format check SHALL pass on every repo

For every Python repo in the workspace inventory, `ruff check . --fix && ruff format . --check` SHALL exit 0 after applying the canonical rule set. Pre-existing violations surfaced by adding rules SHALL be fixed as part of the change.

#### Scenario: Format check is clean

- **WHEN** `ruff format . --check` runs in a repo
- **THEN** no diff SHALL be reported
- **AND** the command SHALL exit 0

#### Scenario: Lint check is clean

- **WHEN** `ruff check .` runs in a repo
- **THEN** no violations SHALL be reported
- **AND** the command SHALL exit 0

### Requirement: The lint-config-baseline validator SHALL be a single script

A single validator script at `tdt-meta/scripts/lint-config-baseline-check.sh` (or equivalent) SHALL exist and SHALL be invokable by name to verify every repo's `pyproject.toml` against the canonical set.

#### Scenario: Validator finds a non-compliant repo

- **WHEN** `bash tdt-meta/scripts/lint-config-baseline-check.sh` runs
- **THEN** the script SHALL list every repo that does not match the canonical config
- **AND** it SHALL exit non-zero if any repo fails

#### Scenario: Validator passes after cleanup

- **GIVEN** every repo has been updated to the canonical baseline
- **WHEN** the validator runs
- **THEN** it SHALL exit 0
- **AND** it SHALL print a per-repo summary showing each repo's matched rule set

### Requirement: Ruff `lint.per-file-ignores` MAY be used for tests

A repo MAY use `[tool.ruff.lint.per-file-ignores]` to relax rule N802, N803, or N806 inside `tests/` directories. Such per-file ignores SHALL NOT be used to relax rules in production source (`src/`, `*/__init__.py`, etc.).

#### Scenario: Tests relax naming rules

- **GIVEN** test files commonly use snake_case locals that trip N802-style rules
- **WHEN** a repo declares `[tool.ruff.lint.per-file-ignores]`
- **THEN** it SHALL only target `"tests/**/*.py"` or `"test_*.py"` globs
- **AND** it SHALL NOT relax rules for production code

### Requirement: Pre-existing violations SHALL be fixed within the change

When adding rules to a repo's `[tool.ruff.lint] select` exposes pre-existing violations, those violations SHALL be fixed within the same OpenSpec change. They SHALL NOT be silenced via `# noqa` comments without justification.

#### Scenario: Adding `RUF` exposes a violation

- **GIVEN** `tdt-sheets` is missing `RUF`
- **WHEN** `RUF` is added to its `select`
- **THEN** `ruff check .` MAY surface new violations
- **AND** those violations SHALL be fixed inline in the same change
- **AND** a `# noqa: RUFxxx` comment SHALL NOT be used unless accompanied by a `# reason:` comment explaining why