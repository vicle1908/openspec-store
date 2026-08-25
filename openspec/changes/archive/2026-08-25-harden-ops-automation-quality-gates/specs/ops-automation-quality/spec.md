## ADDED Requirements

### Requirement: Repository quality commands SHALL be documented

The operations automation repository README SHALL document reproducible setup, test, lint, formatting, and type-check commands using the repository's `uv` toolchain.

#### Scenario: A contributor follows the documented quality workflow

- **WHEN** a contributor reads `README.md`
- **THEN** the README SHALL provide `uv sync`
- **AND** it SHALL provide `uv run pytest -W error::DeprecationWarning`
- **AND** it SHALL provide `uv run ruff check src tests`
- **AND** it SHALL provide `uv run ruff format --check src tests`
- **AND** it SHALL provide `uv run mypy src`

### Requirement: Model timestamps SHALL be documented as timezone-aware UTC

The README SHALL state that model-generated creation timestamps are timezone-aware UTC values.

#### Scenario: Timestamp semantics are discoverable

- **WHEN** a contributor needs to interpret `created_at`
- **THEN** the README SHALL identify the value as timezone-aware UTC
- **AND** the statement SHALL agree with the implementation in `src/ops_automation/models.py`

### Requirement: Quality-gate documentation SHALL not modify runtime scheduling

This documentation change SHALL NOT modify Hermes cron definitions, generated graph artifacts, or unrelated worktree changes.

#### Scenario: Documentation commit is scoped

- **WHEN** the change is staged and committed
- **THEN** only README/OpenSpec quality-gate artifacts SHALL be included
- **AND** generated `graphify-out/` changes SHALL remain unstaged
- **AND** cron definitions SHALL remain unchanged

### Requirement: Existing quality gates SHALL remain passing

The completed change SHALL preserve the repository's passing test, lint, format, and type-check gates.

#### Scenario: Final verification is warning-clean

- **WHEN** the final verification commands run
- **THEN** `uv run pytest -W error::DeprecationWarning` SHALL pass
- **AND** `uv run ruff check src tests` SHALL pass
- **AND** `uv run ruff format --check src tests` SHALL pass
- **AND** `uv run mypy src` SHALL pass
