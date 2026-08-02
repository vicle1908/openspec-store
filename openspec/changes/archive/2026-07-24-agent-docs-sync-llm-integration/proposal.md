## Why

agent-docs-sync currently runs deterministic workflows without LLM assistance. While effective for git diff parsing and link validation, it cannot generate intelligent documentation from code changes. Adding LLM integration enables:

1. **Intelligent doc generation** — Understand code changes and generate accurate documentation
2. **Code-doc consistency** — Verify documentation matches actual API signatures
3. **Agent-core alignment** — Use BaseAgent with pydantic-ai and WorkflowBuilder with LangGraph as intended

## What Changes

- **New GenerationAgent** — LLM-powered agent for doc generation (sh/claude-opus-4.8.6)
- **Hybrid workflow** — Deterministic steps (detect, analyze, validate) + agent step (generate)
- **Per-app configuration** — agent-docs-sync/config.yaml overrides global ~/.tdt/config.yaml
- **LangGraph orchestration** — WorkflowBuilder with PostgresSaver for durable execution
- **Graceful degradation** — Fail-safe when LLM unavailable

## Capabilities

### New Capabilities

- `agent-docs-sync-llm`: LLM-powered documentation generation with agent-core integration

### Modified Capabilities

- `agent-docs-sync`: Add GenerationAgent and LangGraph workflow orchestration

## Impact

- **Code changes:** agent-docs-sync/src/agent_docs_sync/ (new agents/ module, updated workflow)
- **Dependencies:** agent-core (BaseAgent, WorkflowBuilder, LiteLLMGateway)
- **Configuration:** New agent-docs-sync/config.yaml, ~/.tdt/.env (LITELLM_* vars)
- **Infrastructure:** PostgreSQL for PostgresSaver checkpointing (already available)
- **Breaking changes:** None — LLM integration is optional, deterministic fallback preserved
