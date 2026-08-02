# precommit-config — Delta

## MODIFIED Requirements

### Requirement: Pre-commit hooks use frozen uv run

The agent-core pre-commit hooks MUST invoke `uv run --frozen` (not bare `uv run`) for any `uv` invocations.

#### Scenario: mypy hook does not modify uv.lock

- **WHEN** `git commit` is invoked against `agent-core/` with at least one Python file staged
- **AND** `mypy` pre-commit hook runs
- **THEN** the hook's `uv run --frozen mypy src/agent_core/` command MUST complete
- **AND** the working-tree `uv.lock` MUST be unchanged after the hook

#### Scenario: pytest hook does not modify uv.lock

- **WHEN** `git commit` is invoked against `agent-core/` with at least one Python file staged
- **AND** `pytest` pre-commit hook runs
- **THEN** the hook's `uv run --frozen pytest tests/ -q --tb=short` command MUST complete
- **AND** the working-tree `uv.lock` MUST be unchanged after the hook
