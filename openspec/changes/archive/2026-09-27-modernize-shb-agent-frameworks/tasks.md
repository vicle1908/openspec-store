# Tasks

## 1. Dependency Modernization

- [x] 1.1 Add `pydantic-ai>=2.51.0` and `httpx>=0.28.1` to `shb/shb-agent-core/pyproject.toml`. Verification: run `uv sync` in `shb-agent-core` and assert clean resolution.
- [x] 1.2 Add `langgraph>=1.2.12` to `shb/shb-agent-harness/pyproject.toml`. Verification: run `uv sync` in `shb-agent-harness` and assert clean resolution.

## 2. Pydantic AI Agent Runtime Implementation (`shb-agent-core`)

- [x] 2.1 Implement `ShbAgentDeps` and `ShbAgentOutput` in `shb_agent/agent.py` defining typed dependency injection and structured agent responses. Verification: run type checks with `uv run mypy src/shb_agent/agent.py`.
- [x] 2.2 Implement `OpenAIModel` gateway resolution in `shb_agent/model.py` connecting to `SHB_MODEL_GATEWAY_URL` with automated failover in `FallbackModelChain`. Verification: unit tests in `tests/test_model.py` verifying fallback sequence under simulated connection error.
- [x] 2.3 Refactor `ShbAgent` in `shb_agent/agent.py` to initialize a native `pydantic_ai.Agent[ShbAgentDeps, ShbAgentOutput]` with dynamic system prompt and structured tool execution. Verification: unit test verifying agent execution via `TestModel`.

## 3. Typed Banking Tools & Hermetic Testing (`shb-agent-core`)

- [x] 3.1 Define typed Pydantic models `AccountBalanceQuery` and `TransactionStatusQuery` in `shb_agent/tools/banking.py` and bind them to `@agent.tool` definitions with `RunContext[ShbAgentDeps]`. Verification: test parameter schema generation and input validation failure on malformed account numbers.
- [x] 3.2 Update `tests/test_agent.py` to use `pydantic_ai.models.test.TestModel` for zero-cost, hermetic verification of ReAct reasoning loops and tool execution. Verification: run `uv run pytest tests/test_agent.py -v`.
- [x] 3.3 Verify CLI compatibility in `shb_agent/cli.py` for `shb-agent run`, `tools-list`, and `models-list`. Verification: execute `uv run shb-agent --help` and `uv run shb-agent tools-list`.

## 4. LangGraph Workflow & State Graph (`shb-agent-harness`)

- [x] 4.1 Refactor 12 stages into graph nodes in `shb_harness/workflow.py`, converting `StageResult` outputs into typed state updates on `HarnessState`. Verification: unit tests verifying individual node execution.
- [x] 4.2 Compile `StateGraph(HarnessState)` in `shb_harness/workflow.py` with conditional routing after `ClassificationStage` to bypass `ApiContractStage` for internal refactor tickets. Verification: test graph execution paths for feature vs refactor tickets.
- [x] 4.3 Integrate `MemorySaver` checkpointer into compiled graph, capturing state snapshots at each node boundary keyed by `ticket_id`. Verification: test workflow checkpoint inspection and resumption of interrupted state.
- [x] 4.4 Implement human-in-the-loop interruption via `interrupt()` at `StageName.PLAN_REVIEW`, supporting resume after operator approval. Verification: test graph suspension at review milestone.

## 5. Verification & Quality Gates

- [x] 5.1 Run full test suite across `shb-agent-core` (`uv run pytest tests/ -q`). Verification: all tests pass with zero warnings.
- [x] 5.2 Run full test suite across `shb-agent-harness` (`uv run pytest tests/ -q`). Verification: all tests pass with zero warnings.
- [x] 5.3 Run Ruff lint and format checks across both repositories (`uv run ruff check` and `uv run ruff format --check`). Verification: zero lint violations.
- [x] 5.4 Run strict Mypy type-checking across both repositories (`uv run mypy src/ --strict`). Verification: zero type errors.
