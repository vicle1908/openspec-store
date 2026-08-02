# python-syntax-modernization Specification

## Purpose
TBD - created by archiving change tdt-workspace-cleanup-2026-06-29. Update Purpose after archive.
## Requirements
### Requirement: `except` clauses SHALL use the parenthesized tuple form

Every `except` clause in TDT Python source code SHALL use `except (<Type1>, <Type2>, ...) as <name>:`. The Python 2 form `except <Type1>, <Type2>:` is prohibited because, in Python 3, it silently binds the second identifier as a local name rather than catching it as an exception type.

#### Scenario: A workspace-wide search returns zero violations

- **WHEN** `rg 'except\s+[A-Za-z_][A-Za-z0-9_\.]*\s*,\s*[A-Za-z_][A-Za-z0-9_\.]*\s*:' --type py` is run across `~/Developer/tdt/`
- **AND** the result is filtered to exclude `.venv/`, `deployments/`, and `deps/` directories
- **THEN** zero matching lines SHALL remain

#### Scenario: A caught exception is bound to a local variable

- **GIVEN** code that needs to inspect the exception value, e.g. `except (TypeError, ValueError) as e:`
- **WHEN** the `except` clause executes and raises
- **THEN** the local variable `e` SHALL be available in the body
- **AND** `e` SHALL be an instance of either `TypeError` or `ValueError`

#### Scenario: A bare exception type list uses a tuple

- **GIVEN** code needs to catch two unrelated types
- **WHEN** the developer writes the clause
- **THEN** they SHALL write `except (TypeError, ValueError) as e:`
- **AND** they SHALL NOT write `except TypeError, ValueError:` (the legacy form)

### Requirement: A regression test SHALL guard against reintroduction

A regression test SHALL exist in `jira-skill/tests/analysis/test_rca.py` (or a successor test) that scans the workspace for legacy `except` syntax and fails the test suite when any match is found outside the documented exception paths.

#### Scenario: Existing `test_analyzer_uses_python3_except_syntax` extends to the workspace

- **GIVEN** the existing test at `jira-skill/tests/analysis/test_rca.py` enforces modern syntax for `analyzer.py`
- **WHEN** the test is extended
- **THEN** the assertion SHALL scan every Python file in the workspace inventory (per `agent-core-quality-gate`)
- **AND** the test SHALL fail if any file contains `except <Type1>, <Type2>:` outside the documented exclusion list

#### Scenario: Test passes after the cleanup

- **WHEN** the workspace-wide cleanup is applied
- **THEN** the regression test SHALL pass
- **AND** it SHALL continue to pass if any future commit reintroduces a violation

### Requirement: Ruff `UP` rules SHALL be enabled in every Python repo's `[tool.ruff.lint] select`

Every TDT Python repo's `pyproject.toml` SHALL include `UP` (pyupgrade) in `[tool.ruff.lint] select` so ruff catches legacy syntax automatically. `UP` SHALL be present alongside `E`, `W`, `F`, `I`, `N`, `B`, `A`, `C4`, `SIM`, `TCH`, and `RUF` (per `lint-config-baseline`).

#### Scenario: Ruff flags legacy except syntax

- **GIVEN** a developer writes `except TypeError, ValueError:` in any TDT Python repo
- **WHEN** `ruff check .` is run
- **THEN** ruff SHALL report `UP024` (syntax error on legacy except alias) or the equivalent `C`/`B`/`SIM` rule
- **AND** the command SHALL exit non-zero

#### Scenario: Ruff pre-fix rewriters handle whitespace correctly

- **WHEN** `ruff check . --fix` rewrites `except X, Y:` to `except (X, Y) as e:`
- **THEN** the line length SHALL not regress beyond the repo's `line-length`
- **AND** `ruff format .` SHALL be a no-op afterwards

### Requirement: Vendored and generated code SHALL be excluded from the search

The workspace-wide search for legacy except syntax SHALL explicitly exclude `.venv/`, `deployments/`, and `deps/` directories because they contain snapshot copies of source from the host's prior Python 3.14 environment.

#### Scenario: Excluded paths are documented

- **WHEN** the regression test enumerates directories to scan
- **THEN** it SHALL skip any path matching `.venv`, `deployments`, or `deps` segments
- **AND** the exclusion list SHALL be present in a constant near the test entry point with a comment explaining why

#### Scenario: Vendored copies do not block the gate

- **GIVEN** a vendored copy under `deployments/ai-review/deps/tdt-core/src/...` contains a legacy `except`
- **WHEN** the regression test runs
- **THEN** that line SHALL be ignored
- **AND** the live source under `tdt-core/src/...` SHALL still be scanned

### Requirement: Test files SHALL be modernized alongside source files

Test files in the workspace SHALL be modernized in the same change set because they exercise the same code paths. A Py2-style except in a test file is as much of a regression risk as in a production module.

#### Scenario: Test files are scanned and fixed

- **WHEN** the cleanup runs
- **THEN** files under `*/tests/` (e.g. `jira-skill/tests/test_setup_evidence.py`, `tests/analysis/test_cli.py`, `tests/analysis/test_dashboard.py`) SHALL be updated in addition to `*/src/`

#### Scenario: Pytest continues to pass after modernization

- **GIVEN** a repo with modernized except clauses in both source and tests
- **WHEN** `uv run pytest -x` runs in that repo
- **THEN** the test suite SHALL exit 0
- **AND** the regression test in `jira-skill/tests/analysis/test_rca.py` SHALL continue to pass

