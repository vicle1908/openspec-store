# Design: Modernize SHB Agent Frameworks

## 1. Context & Architectural Overview

The initial bootstrap of the SHB autonomous engineering platform created clean repository boundaries, isolated environment management (`~/.shb/.env`), and basic CLI commands. However, the runtime execution loops in `shb-agent-core` and workflow state management in `shb-agent-harness` were implemented as minimal mocks:
- `shb-agent-core` simulated ReAct reasoning using plain string substring matching (`if "balance" in user_prompt.lower():`) and string-formatted response generation, omitting real LLM connectivity and Pydantic AI contracts.
- `shb-agent-harness` implemented a procedural linear `for` loop over stage classes with in-memory string checkpointing, lacking graph DAG topology, conditional transitions, error recovery, and durable persistence.

This design transitions both repositories to production standards by integrating **Pydantic AI v2** (`pydantic-ai>=2.51.0`) into `shb-agent-core` and **LangGraph** (`langgraph>=1.2.12`) into `shb-agent-harness`.

```
+-----------------------------------------------------------------------------------+
|                                 SHB Agent Platform                                |
+-----------------------------------------------------------------------------------+
|  shb-agent-core                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | Pydantic AI Agent[ShbAgentDeps, ShbAgentOutput]                             |  |
|  |   - Model Gateway: OmniRoute / OpenAIModel (http://127.0.0.1:20128/v1)      |  |
|  |   - Fallback Chain: Primary -> Fallback via httpx resilience                |  |
|  |   - Typed Tool Registry: @agent.tool with Pydantic input models             |  |
|  |   - Zero-cost Testing: pydantic_ai.models.test.TestModel                    |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
|  shb-agent-harness                                                                |
|  +-----------------------------------------------------------------------------+  |
|  | LangGraph StateGraph[HarnessState]                                          |  |
|  |   - Nodes: 12 discrete planning stages                                      |  |
|  |   - Conditional Edges: Classification-based skip routing (e.g. API contract) |  |
|  |   - Checkpointer: MemorySaver (development) / PostgresSaver (production)   |  |
|  |   - Human-in-the-Loop: interrupt() at API_CONTRACT and PLAN_REVIEW          |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Detailed Technical Design

### 2.1 `shb-agent-core`: Pydantic AI v2 Agent Architecture

#### Model Resolution & Gateway Connectivity
`shb_agent.model` will resolve endpoints from `ShbSettings`:
- Primary Model: `settings.default_model` (e.g. `fable-5`) via `pydantic_ai.models.openai.OpenAIModel` pointing to `settings.model_gateway_url` (OmniRoute `http://127.0.0.1:20128/v1` or remote endpoints).
- Fallback Model: `settings.fallback_model` (e.g. `Advance`).
- Resilience: If the primary model raises an API/HTTP connection error, the resolver fails over to the fallback model within `FallbackModelChain`.

#### Typed Dependencies & Agent Initialization
```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from shb_core.config import ShbSettings, get_settings
from shb_core.clients.banking import BankingApiClient, BankingApiClientFactory

@dataclass
class ShbAgentDeps:
    settings: ShbSettings
    banking_client: BankingApiClient

class ShbAgentOutput(BaseModel):
    status: str = Field(description="Execution status, e.g. COMPLETED or FAILED")
    summary: str = Field(description="Synthesized natural language response")
    tool_calls_executed: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
```

The agent is defined as:
```python
agent: Agent[ShbAgentDeps, ShbAgentOutput] = Agent(
    model=primary_model,
    deps_type=ShbAgentDeps,
    result_type=ShbAgentOutput,
    system_prompt="You are the SHB Banking Autonomous Assistant...",
)
```

#### Typed Tool Registration
Tools are registered directly on the agent with explicit parameter types:
```python
class AccountBalanceQuery(BaseModel):
    account_number: str = Field(pattern=r"^\d{10,14}$", description="SHB Account Number")

@agent.tool
async def get_account_balance(
    ctx: RunContext[ShbAgentDeps],
    query: AccountBalanceQuery,
) -> dict[str, Any]:
    """Retrieve verified available and ledger balance for an SHB account."""
    # Invokes ctx.deps.banking_client with validation
    return ctx.deps.banking_client.get_balance(query.account_number)
```

#### Testing Strategy
Unit tests use `pydantic_ai.models.test.TestModel` with custom tool return mocks, verifying tool argument parsing, agent reasoning steps, and fallback behavior hermetically without network access.

---

### 2.2 `shb-agent-harness`: LangGraph State Graph & Durable Workflows

#### Graph Definition & State Reducer
`shb_harness.state.HarnessState` serves as the state schema. The workflow compiles a `StateGraph`:
```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

workflow = StateGraph(HarnessState)

# Register 12 stages as nodes
workflow.add_node("intake", intake_node)
workflow.add_node("classification", classification_node)
workflow.add_node("context", context_node)
workflow.add_node("impact", impact_node)
workflow.add_node("spec", spec_node)
workflow.add_node("api_contract", api_contract_node)
workflow.add_node("design", design_node)
workflow.add_node("test_plan", test_plan_node)
workflow.add_node("implementation_plan", implementation_plan_node)
workflow.add_node("coding_plan", coding_plan_node)
workflow.add_node("verification", verification_node)
workflow.add_node("plan_review", plan_review_node)
```

#### Conditional Routing
After `classification`, the workflow branches conditionally:
- If `ticket_category == "internal_refactor"` or no API impact is detected: route around `api_contract` directly to `design`.
- Otherwise: route through `spec` and `api_contract`.

#### Checkpointing & Resumption
The workflow uses `MemorySaver` for in-process memory and CLI execution, storing state snapshots at every stage transition:
```python
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```
Operators can query or resume workflows by `thread_id` (mapped to `ticket_id`).

#### Human-in-the-Loop Gating
At `plan_review`, the harness calls `interrupt({"action": "require_operator_approval", "ticket_id": state.ticket_id})`. The graph suspends execution until the operator explicitly resumes via CLI (`shb-harness approve --ticket-id <id>`).

---

## 3. Migration and Compatibility

- **CLI Compatibility**:
  - `shb-agent run "<prompt>"` retains the existing console output shape while executing a real Pydantic AI agent loop under the hood.
  - `shb-harness run --ticket-id <id>` executes through the compiled LangGraph workflow.
- **Dependency Isolation**:
  - All additions (`pydantic-ai`, `langgraph`, `httpx`) are declared strictly in `pyproject.toml` using Python `>=3.14` and synchronized via `uv`.
- **Zero Impact on Other Orgs**:
  - No changes to `tdt/`, `vds/`, or `platform/`. Configuration remains strictly isolated in `~/.shb/`.
