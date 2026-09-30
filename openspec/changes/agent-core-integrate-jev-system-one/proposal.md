# Proposal

## Why

Discrete decision-making in multi-agent workflows currently incurs excessive latency and cost by forcing full autoregressive LLM generations or relying on brittle regex patterns for split-second choices.

In `agent-core`, tool authorization guards, LangGraph conditional branching, skill dispatch, and evaluation scoring repeatedly either pay 1.5–5 seconds of token generation overhead or fall back to rigid regex pattern matching that misses obfuscated commands. TypeSafe AI's Jev introduces a specialized "System One" decision model that evaluates typed probabilistic questions (`bool`, `choice`, `score`) in sub-200ms with calibrated confidence and zero output token cost. Adopting Jev equips `agent-core` with high-speed semantic pre-flight guardrails, deterministic graph routing, candidate skill refinement, and fast evaluation judges while maintaining full decoupling from streaming chat protocols.

## What Changes

- **Add Jev System One Client & Settings to `agent-core`**: Implement `JevSettings` (`JEV_` prefix) in `agent_core.foundation.settings` and provide a dedicated `JevDecisionClient` for evaluating typed probabilistic questions (`bool`, `choice`, `score`) with timeout, circuit breaking, and mock capabilities.
- **Semantic Pre-Flight Tool Guardrail (`JevToolGuardrail`)**: Introduce a high-speed pre-flight authorization guard in `agent_core.tool_registry.guardrails` that intercepts potentially destructive shell/write tool calls before execution or human approval deferral, catching obfuscated commands that bypass regex without LLM generation latency.
- **Probabilistic LangGraph Routing Nodes**: Enhance `WorkflowEngine` in `agent_core.orchestration.graph` with a `JevConditionalRouter` that evaluates state dictionaries against defined choice targets in ~80ms instead of requiring heavy LLM routing steps or brittle key-presence flags.
- **Two-Stage Skill Matcher Refinement**: Update `SkillMatcher` in `agent_core.skill_system.matcher` with an optional Jev reranking stage (`a_match_jev()`) that selects the best matching skill candidate from vector retrieval top-K results.
- **Fast Evaluation Scorers (`JevEvaluator`)**: Provide non-generative evaluators compatible with `pydantic-evals` and `agent_core.observability.scorers.runner` to score correctness, relevance, and severity across traces without LLM-as-a-judge token costs.
- **Fail-Closed Fallback & Protocol Decoupling**: Isolate Jev as a dedicated System One decision provider without mutating `tdt-core`'s strict generative `ProviderProtocol` enum, ensuring fallback to default rule-based gates when `TYPESAFE_API_KEY` is absent or unreachable.

## Capabilities

### New Capabilities
- `jev-decision-runtime`: Fast System One decision evaluation, pre-flight tool guardrails, LangGraph routing, candidate skill refinement, and evaluation scorers for agent-core.

### Modified Capabilities
- None. (Existing `agent-core` authority policies and `WorkflowEngine` public interfaces remain backward-compatible).

## Non-Goals

- **Replacing Generative Models ("System Two")**: Jev cannot generate conversational prose, write code diffs, or synthesize plans. Main reasoning agents will continue using Claude, GPT, or Gemini.
- **Mutating `tdt-core` ProviderProtocol**: Jev does not implement `messages`, `openai_chat`, or `responses` streaming wire protocols; it is decoupled from generative model route chains.
- **Bypassing Human Approval**: Jev serves as an early filter and risk-scorer, never as an escalation bypass for operations requiring authenticated subject approval.

## Impact

- **Affected Ownership Boundaries**:
  - `agent-core`: Runtime settings (`foundation/settings.py`), dependency additions (`pydantic-ai-slim[typesafe]` or `typesafe-sdk`), tool registry guardrails (`tool_registry/guardrails.py`), orchestration routers (`orchestration/graph.py`), skill matching (`skill_system/matcher.py`), and evaluation scorers (`observability/scorers/jev_scorer.py`).
  - `openspec-store`: Change specs, designs, and task tracking under `agent-core-integrate-jev-system-one`.
