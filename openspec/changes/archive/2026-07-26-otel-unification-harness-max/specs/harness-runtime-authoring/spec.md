## ADDED Requirements

### Requirement: RuntimeAuthoring capability SHALL be wired via harness_config
`AgentRuntime._build_harness_capabilities()` SHALL support a `runtime_authoring` key in the `harness_config` dict. When present, it SHALL instantiate `pydantic_ai_harness.runtime_authoring.RuntimeAuthoring` with the configured `directory` parameter.

**Verified API:**
```python
from pydantic_ai_harness.runtime_authoring import RuntimeAuthoring
from pathlib import Path

cap = RuntimeAuthoring(
    directory=Path(".agent-capabilities"),  # REQUIRED - where authored capabilities are stored
    guidance="Optional guidance text for the agent",
)
```

**Constructor params:**
- `directory: Path` — REQUIRED — directory for storing authored capabilities
- `guidance: str | None = None` — optional guidance text
- `id: str | None = None` — capability ID
- `description: str | None = None` — capability description
- `defer_loading: bool = False` — whether to defer loading

**It IS an AbstractCapability** (verified: `issubclass(RuntimeAuthoring, AbstractCapability) == True`)

#### Scenario: RuntimeAuthoring enabled
- **WHEN** `harness_config={"runtime_authoring": {"directory": ".agent-capabilities"}}` is passed to AgentRuntime
- **THEN** the RuntimeAuthoring capability SHALL be added to the agent's capabilities list

#### Scenario: RuntimeAuthoring not configured
- **WHEN** `harness_config` does not contain a `runtime_authoring` key
- **THEN** no RuntimeAuthoring capability SHALL be added

#### Scenario: RuntimeAuthoring without directory
- **WHEN** `harness_config={"runtime_authoring": {}}` is passed without a `directory` key
- **THEN** a default directory SHALL be used (e.g., `.agent-capabilities` relative to workspace root)

### Requirement: Agent SHALL be able to author capabilities at runtime
When RuntimeAuthoring is active, the agent SHALL be able to define, validate, and load new capabilities from natural language instructions during a run, without code changes or restarts.

#### Scenario: Agent authors a new tool capability
- **WHEN** the agent is asked to create a new capability and RuntimeAuthoring is active
- **THEN** the agent SHALL be able to define instructions, tools, and load them into the current run

### Requirement: RuntimeAuthoringSettings SHALL be configurable and gate capability wiring
`RuntimeAuthoringSettings` SHALL be added to `foundation/settings.py` with env prefix `RUNTIME_AUTHORING_` and field `enabled: bool = False`. When `enabled=True` and `harness_config` does not already contain a `runtime_authoring` key, `AgentRuntime.__init__()` SHALL automatically add `runtime_authoring={}` to the merged config, enabling the capability without requiring explicit `harness_config` wiring.

#### Scenario: RuntimeAuthoring configured via environment
- **WHEN** `RUNTIME_AUTHORING_ENABLED=true` is set
- **THEN** `Settings.runtime_authoring.enabled` SHALL be `True`

#### Scenario: Settings-based gating enables capability
- **WHEN** `RUNTIME_AUTHORING_ENABLED=true` is set and `harness_config` does not contain `runtime_authoring`
- **THEN** `AgentRuntime.__init__()` SHALL merge `runtime_authoring={}` into the config, causing the capability to be wired

#### Scenario: harness_config takes precedence
- **WHEN** `harness_config={"runtime_authoring": {"directory": "/custom"}}` is provided
- **THEN** the explicit config SHALL be used and the settings-based default SHALL NOT override it

### Requirement: Import SHALL be graceful
The `pydantic_ai_harness.runtime_authoring` import SHALL be wrapped in `try/except ImportError` following the existing harness capability wiring pattern.

#### Scenario: Harness not installed
- **WHEN** `pydantic-ai-harness` is not installed
- **THEN** the RuntimeAuthoring capability SHALL be skipped with a debug log and no error SHALL propagate
