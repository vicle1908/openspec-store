# Spec Delta: shb-ecosystem-tooling

## MODIFIED Requirements

### Requirement: Python Packaging and Quality Standardization
All Python repositories in the `shb` ecosystem SHALL use `uv` for dependency management with Python version requirements `>=3.14`, Ruff for linting and formatting (line length 100), strict Mypy type checking, and modern Python clean-break syntax including PEP 585 builtin generic types (`list`, `dict`, `set`, `tuple`), PEP 604 union types (`T | None`, `A | B`), timezone-aware UTC datetimes (`datetime.now(timezone.utc)`), and Pydantic v2 validation contracts.

#### Scenario: Dependency synchronization and test execution
- **WHEN** an engineer executes `uv sync` followed by `uv run pytest` in any SHB repository
- **THEN** virtual environments are provisioned with pinned dependencies and the test suite executes successfully without root cache pollution

#### Scenario: Clean-break typing and syntax validation
- **WHEN** static analysis via Ruff (`UP006`, `UP007`, `UP035`) is executed across any SHB repository
- **THEN** zero violations SHALL be reported for deprecated `typing.List`, `typing.Dict`, `typing.Optional`, or `typing.Union` constructs

#### Scenario: Line length and CLI parameter formatting
- **WHEN** static analysis checks line length compliance across all CLI entrypoints
- **THEN** zero violations of Ruff `E501` (>100 characters) SHALL exist
- **AND** Typer CLI options SHALL be structured using wrapped parameters or `Annotated` definitions

## ADDED Requirements

### Requirement: Codebase Deprecation and Anti-Pattern Elimination
All Python source files and operational test fixtures across the SHB organization SHALL eliminate deprecated Python standard library calls, legacy Pydantic v1 methods, and unchained exception raises within `except` blocks.

#### Scenario: Timezone-aware UTC datetime enforcement
- **WHEN** inspecting datetime instantiations across SHB source and compliant test entity definitions
- **THEN** zero occurrences of deprecated `datetime.utcnow()` or `datetime.utcfromtimestamp()` SHALL exist
- **AND** all UTC timestamps SHALL be generated via `datetime.now(timezone.utc)`

#### Scenario: Explicit exception chaining
- **WHEN** an exception is raised within an `except` handler in any SHB application or CLI entrypoint
- **THEN** the exception SHALL explicitly chain the root cause using `from err` or `from None` per Python `B904` standards

#### Scenario: Pydantic v2 decorator and model method compliance
- **WHEN** Pydantic models and validation logic are defined in SHB repositories
- **THEN** field and model validations SHALL use `@field_validator` or `@model_validator`
- **AND** model serialization and copying SHALL use `.model_dump()`, `.model_dump_json()`, or `.model_copy()` rather than deprecated v1 methods
