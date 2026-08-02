## MODIFIED Requirements

### Requirement: Agent construction helper

agent-core SHALL provide `build_agent()` that constructs a `BaseAgent` from consumer config, gateway, and tools. The helper SHALL accept optional `hooks`, `harness_config`, and `flavors` parameters. When `hooks` is provided but empty, the helper SHALL auto-register Tier 0 hook packs (`otel_metrics`, `structured_audit`). When `flavors` is provided, the helper SHALL use the pre-built flavors instead of creating a Flavor from config.

#### Scenario: build_agent with pre-built flavors
- **WHEN** `build_agent(gateway=gw, tools=registry, flavors=[my_flavor])` is called
- **THEN** the agent SHALL use the provided flavors
- **AND** no Flavor SHALL be created from config

#### Scenario: build_agent without config or flavors raises error
- **WHEN** `build_agent(gateway=gw)` is called with both `config=None` and `flavors=None`
- **THEN** a `ValueError` SHALL be raised

#### Scenario: build_agent with config and flavors uses flavors
- **WHEN** `build_agent(config=my_config, gateway=gw, flavors=[my_flavor])` is called
- **THEN** the agent SHALL use the provided flavors
- **AND** config SHALL still be used for model, tools_allowed, etc.

### Requirement: Consumer imports SHALL use SDK surface

All consumer code SHALL import from `agent_core.sdk` rather than internal modules (`agent_core.agent_base`, `agent_core.llm_gateway`, `agent_core.tool_registry`, etc.). The SDK re-exports all consumer-facing symbols.

#### Scenario: Consumer imports BaseAgent from SDK
- **WHEN** a consumer runs `from agent_core.sdk import BaseAgent`
- **THEN** the import SHALL resolve correctly

#### Scenario: Consumer imports HookPhase, HookPoint from SDK
- **WHEN** a consumer runs `from agent_core.sdk import HookPhase, HookPoint`
- **THEN** the import SHALL resolve correctly

#### Scenario: Consumer imports LLMGateway from SDK
- **WHEN** a consumer runs `from agent_core.sdk import LLMGateway`
- **THEN** the import SHALL resolve correctly
