# vendor-isolation Specification

## Purpose
Confines pydantic-ai imports to `src/agent_core/_ai/` via ruff TC002 enforcement, composition over inheritance, and a defined package structure.
## Requirements
### Requirement: VI-1: pydantic-ai Import Confinement

pydantic-ai v2.9 types SHALL be imported only inside `src/agent_core/_ai/`.

All runtime imports of `pydantic_ai` outside `src/agent_core/_ai/` SHALL cause a lint failure.

`TYPE_CHECKING` blocks are exempt from this requirement.

#### Scenario: Import outside _ai/ triggers lint

- **GIVEN** a developer writes `from pydantic_ai import Agent` in `agent_base/agent.py`
- **WHEN** `ruff check src/agent_core/agent_base/agent.py` runs
- **THEN** a TC002 lint error is raised

#### Scenario: Import inside _ai/ is allowed

- **GIVEN** a developer writes `from pydantic_ai import Agent` in `src/agent_core/_ai/agent.py`
- **WHEN** `ruff check src/agent_core/` runs
- **THEN** no TC002 error is raised

### Requirement: VI-2: TC002 Ruff Enforcement

A ruff `TC002` configuration SHALL be added to `pyproject.toml` under `[tool.ruff.lint.per-file-ignores]`.

`src/agent_core/_ai/*` SHALL be listed in `per-file-ignores` for TC002.

Note: `agent-core` has no separate `ruff.toml`; all ruff configuration lives in `pyproject.toml`.

#### Scenario: TC002 configuration exists

- **GIVEN** `agent-core/pyproject.toml` is read
- **WHEN** the `[tool.ruff.lint.per-file-ignores]` section is checked
- **THEN** `"src/agent_core/_ai/*": ["TC002"]` is present

### Requirement: VI-3: Composition over Inheritance

No class in `src/agent_core/_ai/` SHALL subclass `pydantic_ai.Agent` or any other pydantic-ai class.

All pydantic-ai primitives SHALL be held as private instance attributes.

#### Scenario: AgentRuntime uses composition

- **GIVEN** `AgentRuntime` is instantiated
- **WHEN** `type(agent_runtime)._agent` is accessed
- **THEN** the value is a `pydantic_ai.Agent` instance
- **AND** `AgentRuntime` does not inherit from `pydantic_ai.Agent`

### Requirement: VI-4: _ai/ Package Structure

The `_ai/` package SHALL be located at `src/agent_core/_ai/` and SHALL contain at minimum:

```
_ai/
    __init__.py   # Re-exports all _ai public types
    models.py     # Model backend factory functions
    agent.py      # AgentRuntime class
    tools.py      # Builtin tools as @agent.tool()
    hooks.py      # HookAdapter class
    deps.py       # AgentRuntimeDeps dataclass
    types.py      # Internal type aliases
```

#### Scenario: Package imports succeed

- **GIVEN** the `_ai/` package is created with the required files
- **WHEN** each module is imported in isolation
- **THEN** no import errors occur

