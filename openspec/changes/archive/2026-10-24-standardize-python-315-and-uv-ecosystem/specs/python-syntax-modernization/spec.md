# Spec Delta: python-syntax-modernization

## MODIFIED Requirements

### Requirement: Ruff `UP` rules SHALL be enabled in every Python repo's `[tool.ruff.lint] select`
Every workspace Python repository's `pyproject.toml` SHALL set `target-version = "py315"` in `[tool.ruff]` and `python_version = "3.15"` in `[tool.mypy]`, and SHALL include `UP` alongside the full canonical 19-rule set in `[tool.ruff.lint] select`.

#### Scenario: Ruff flags legacy except syntax
- **GIVEN** a developer writes `except TypeError, ValueError:` in any TDT Python repo
- **WHEN** `ruff check .` is run
- **THEN** ruff SHALL report `UP024` (syntax error on legacy except alias) or the equivalent `C`/`B`/`SIM` rule
- **AND** the command SHALL exit non-zero.

#### Scenario: Ruff pre-fix rewriters handle whitespace correctly
- **WHEN** `ruff check . --fix` rewrites `except X, Y:` to `except (X, Y) as e:`
- **THEN** the line length SHALL not regress beyond the repo's `line-length`
- **AND** `ruff format .` SHALL be a no-op afterwards.

#### Scenario: Target version py315 configured across ecosystem
- **WHEN** inspecting `[tool.ruff]` and `[tool.mypy]` across all workspace `pyproject.toml` files
- **THEN** `[tool.ruff].target-version` SHALL equal `"py315"`
- **AND** `[tool.mypy].python_version` SHALL equal `"3.15"`.

## ADDED Requirements

### Requirement: Python 3.15 builtin sentinel variable shadowing prohibited
Python source code and test files SHALL NOT use `sentinel` as a variable, parameter, or module-level alias in violation of Ruff rule `A001` / `A002`, because `sentinel` is a Python 3.15 builtin constructor.

#### Scenario: Sentinel variables renamed to domain-specific names
- **WHEN** running `ruff check .` with rule `A` enabled across all workspace Python repositories
- **THEN** zero occurrences of `A001` or `A002` shadowing `sentinel` SHALL exist
- **AND** occurrences in scheduler, harness, and test fixtures SHALL use domain names such as `reload_sentinel`, `mock_sentinel`, or `_MISSING`.

### Requirement: Modern StrEnum and PEP 695 type parameter syntax
Python string enum definitions SHALL use `enum.StrEnum` rather than `(str, Enum)`, and generic classes and functions SHALL use PEP 695 `class C[T]:` and `def f[T]():` syntax rather than legacy `typing.TypeVar` and `typing.Generic`.

#### Scenario: StrEnum migration passes UP042
- **WHEN** inspecting string enum definitions in `agent-harness` and `code-daily-scan`
- **THEN** classes inheriting from `(str, Enum)` SHALL be refactored to `StrEnum`
- **AND** `ruff check .` SHALL report zero `UP042` violations.

#### Scenario: PEP 695 type parameters pass UP046
- **WHEN** inspecting generic classes and type aliases in `tdt-core`, `agent-core`, and `shb/*`
- **THEN** generic declarations SHALL use bracketed type parameters (`[T]`) without `Generic[T]` inheritance or explicit `TypeVar` allocations
- **AND** type aliases SHALL use `type X = ...` declarations.

### Requirement: Native PEP 649 annotation evaluation without future imports
Source code in modernized Python 3.15 packages SHALL rely on standard library PEP 649 deferred annotation evaluation and SHALL NOT require boilerplate `from __future__ import annotations` statements.

#### Scenario: Tests execute cleanly without future annotations import
- **WHEN** `from __future__ import annotations` is omitted from modernized package modules
- **THEN** runtime type reflection and Pydantic validation SHALL execute successfully under Python 3.15
- **AND** `pytest` suites SHALL pass without forward-reference NameErrors.
