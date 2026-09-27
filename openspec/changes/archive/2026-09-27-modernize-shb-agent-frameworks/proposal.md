# Proposal: Modernize SHB Agent Frameworks

## Why

The initial bootstrap of the Saigon - Hanoi Bank (SHB) autonomous agent ecosystem (`shb-agent-core` and `shb-agent-harness`) established foundational interfaces, models, and CLI commands. However, an architectural audit reveals that the underlying implementations rely on simulated abstractions rather than production-grade agentic frameworks:
1. **`shb-agent-core`**: Operates via naive string substring parsing (`if "balance" in user_prompt.lower():`) and simulated string generation (`f"[Model: {self.model_name}] Response to: {prompt}"`) rather than a real autonomous ReAct execution loop. `pydantic-ai` is missing from `pyproject.toml`, and tools lack JSON Schema validation and type-safe injection.
2. **`shb-agent-harness`**: Executes 12 planning stages through a procedural Python `for stage in STAGES_SEQUENCE:` loop. State checkpointing is simulated via an in-memory string list (`self.state.checkpoints.append(...)`). `langgraph` is missing from `pyproject.toml`, preventing DAG branching, state reduction, error recovery, conditional stage routing, or human-in-the-loop review.

Modernizing both packages to upstream standards (`pydantic-ai>=2.51.0` and `langgraph>=1.2.12`, consistent with `tdt/agent-core` and `tdt/agent-harness`) transitions the SHB agent platform from a simulated placeholder into a resilient, production-ready banking autonomous agent runtime.

## What Changes

- **Adopt Pydantic AI v2 in `shb-agent-core`**:
  - Add `pydantic-ai>=2.51.0` and `httpx>=0.28.1` to dependencies.
  - Implement real model endpoint resolution targeting `SHB_MODEL_GATEWAY_URL` (OmniRoute `http://127.0.0.1:20128/v1` or direct OpenAI-compatible gateways) with automatic provider fallback.
  - Re-architect `ShbAgent` using `pydantic_ai.Agent` with typed dependencies (`RunContext[ShbAgentDeps]`), dynamic system prompts, and structured output models.
  - Convert `banking_tools` to `@agent.tool` decorators with typed Pydantic parameters, automatic JSON Schema generation, and parameter validation.
  - Add hermetic offline testing using `pydantic_ai.models.test.TestModel` for zero-cost, deterministic test execution.

- **Adopt LangGraph in `shb-agent-harness`**:
  - Add `langgraph>=1.2.12` to dependencies.
  - Refactor the 12-stage sequential lifecycle into a compiled `StateGraph[HarnessState]`.
  - Implement conditional routing after `ClassificationStage` (e.g., bypass `ApiContractStage` for non-API changes).
  - Integrate durable state persistence using `MemorySaver` (development/testing) with an upgrade path to `PostgresSaver`.
  - Support human-in-the-loop approval gating via `interrupt()` at `API_CONTRACT` and `PLAN_REVIEW` milestones.

## Capabilities

### Modified Capabilities
- `shb-agent-runtime`: Upgrades ReAct loop from simulated substring checks to production Pydantic AI v2 agent with live gateway connectivity, fallback routing, and type-safe tool validation.
- `shb-planning-harness`: Upgrades 12-stage ticket execution from linear procedural loops to a stateful LangGraph `StateGraph` with durable checkpointing and human-in-the-loop interrupts.

## Non-Goals

- Modifying existing `shb-core` client factories (`JiraClientFactory`, `GitlabClientFactory`, `BankingApiClientFactory`).
- Introducing legacy Java dependencies or Spring Boot code into the SHB ecosystem.
- Breaking existing CLI commands (`shb-agent run`, `shb-harness run`, `shb-harness status`); CLI options and output shapes remain backward-compatible.
- Migrating `shb-observability` or `shb-mcp-servers` in this change; these will be addressed in a follow-up telemetry standardization change.
