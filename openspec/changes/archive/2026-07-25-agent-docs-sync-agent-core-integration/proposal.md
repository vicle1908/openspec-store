## Why

agent-docs-sync needs to properly leverage agent-core's new harness capabilities (planning, subagents, guardrails, dynamic_workflow) to avoid rework and overlap. Current implementation partially uses these features but doesn't fully integrate them.

## What Changes

- Add planning capability for LLM-based classification (improve classification accuracy)
- Add subagents for delegated validation tasks (separate concerns)
- Add guardrails for input validation (replace custom hooks)
- Upgrade to DynamicWorkflow for complex routing (better flexibility)
- Update config.yaml with full harness configuration
- Update specs to reflect agent-core integration requirements

## Capabilities

### New Capabilities

- `agent-core-harness-integration`: Proper integration with agent-core harness capabilities (planning, subagents, guardrails, dynamic_workflow)

### Modified Capabilities

- `hybrid-discovery`: Add agent-core integration requirements

## Impact

- **agent-docs-sync**: Main implementation target
- **agent-core**: Dependency (no changes needed, already has features)
- **LlmConfig**: Add planning_guidance field
- **DiscoveryAgent**: Add harness_config parameter
- **ValidationAgent**: Add harness_config parameter
- **config.yaml**: Add planning, subagents, guardrails configuration
