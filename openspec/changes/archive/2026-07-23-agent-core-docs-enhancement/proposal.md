## Why

agent-core has 10+ implemented features with zero or incomplete documentation:
- Harness integration (10 capabilities wired, no docs)
- Subgraphs, Command API, per-node features (implemented, no docs)
- Streaming (outdated API docs)
- YAML agent loading (no guide)
- ToolSearch/Thinking (no docs)

Developers cannot use these features without reading source code.

## What Changes

- **Orchestration docs**: Add subgraphs, Command API, per-node features
- **Configuration docs**: Add harness_config section with all 10 capabilities
- **Streaming docs**: Fix to match actual `run_stream()` API
- **New: harness-integration.md**: Dedicated guide for harness capabilities
- **New: agent-config.md**: YAML/JSON agent loading guide
- **Extending docs**: Add ToolSearch/Thinking examples

## Capabilities

### New Capabilities

- `agent-docs-harness`: Documentation for pydantic-ai-harness integration
- `agent-docs-orchestration-enhanced`: Documentation for subgraphs, command API, per-node features
- `agent-docs-agent-config`: Documentation for YAML/JSON agent loading

### Modified Capabilities

- `agent-core-orchestration`: Add subgraph, command API, per-node sections
- `agent-core-streaming`: Fix to match actual `run_stream()` API
- `agent-core-configuration`: Add harness_config section
- `agent-core-extending`: Add ToolSearch/Thinking examples

## Impact

- **Files modified**: 4 (orchestration.md, streaming.md, configuration.md, extending.md)
- **Files created**: 2 (harness-integration.md, agent-config.md)
- **Dependencies**: None
- **Breaking changes**: None — docs only
