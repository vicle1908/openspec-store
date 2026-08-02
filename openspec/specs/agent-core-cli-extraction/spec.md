## Purpose

Define the modular CLI architecture for agent-core: extracting monolithic app.py into thin wiring plus sub-modules (utils, schedules, skills, init, agent) while preserving all existing commands and test compatibility.

## Requirements

### Requirement: CLI modular architecture
`cli/app.py` SHALL be reduced to a thin wiring file that imports and registers sub-modules.

#### Scenario: Sub-modules exist
- **WHEN** the extraction is complete
- **THEN** these files SHALL exist: `cli/utils.py`, `cli/schedules.py`, `cli/skills.py`, `cli/init_cmd.py`, `cli/agent_cmd.py`

#### Scenario: app.py is thin wiring
- **WHEN** a developer reads `cli/app.py`
- **THEN** it SHALL contain only imports, app construction, command registration, and re-exports for test compatibility
- **AND** it SHALL be under 120 lines (including re-exports)

#### Scenario: All commands preserved
- **WHEN** `agent-core --help` is run
- **THEN** all existing commands SHALL be available: config, health, review, propose, explore, repl, init, skills, schedules

### Requirement: Shared utilities module
Global CLI state and shared helpers SHALL live in `cli/utils.py`.

#### Scenario: Global state accessible
- **WHEN** `_verbose`, `_quiet`, `_json_output` are set in the callback
- **THEN** sub-modules SHALL access them via `from agent_core.cli.utils import ...`

#### Scenario: Profile helpers shared
- **WHEN** `health` command (in app.py) and `skills` commands (in skills.py) need profile helpers
- **THEN** `_profile_config`, `_resolve_cli_profile`, `_load_profile_skills` SHALL live in `utils.py`
- **AND** both modules SHALL import from `utils.py`

### Requirement: Orphaned eval.py wired in
The existing `cli/eval.py` SHALL be renamed to `cli/eval_cmd.py` and registered as a sub-app.

#### Scenario: eval command available
- **WHEN** `agent-core eval --help` is run
- **THEN** the eval sub-app SHALL be available

### Requirement: Test compatibility via re-exports
Existing CLI tests SHALL pass without modification.

#### Scenario: Test monkeypatch compatibility
- **WHEN** tests do `monkeypatch.setattr(cli_app, "_run_agent_prompt", fake)`
- **THEN** `cli_app` (which is `agent_core.cli.app`) SHALL still have `_run_agent_prompt` in its namespace
- **AND** the thin `app.py` SHALL re-export all private helpers that tests monkeypatch

#### Scenario: Test suite passes
- **WHEN** `pytest tests/cli/` is run after extraction
- **THEN** all tests SHALL pass without modification
