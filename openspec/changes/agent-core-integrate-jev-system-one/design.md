# Design: Jev System One Decision Architecture

## Context

`agent-core` hosts the shared agent runtime across the TDT ecosystem. Currently, discrete decisions (such as tool pre-flight risk checks, edge routing in LangGraph workflows, skill candidate matching, and evaluation scoring) either rely on static regex pattern matching (`_DANGEROUS_PATTERNS` in `ShellTool`) or full generative LLM execution (`pydantic-ai` models). Full generative calls add 1.5–5 seconds of latency and token generation costs, while regex patterns are brittle against command obfuscation or variable semantics.

## Goals / Non-Goals

**Goals:**
- Provide a non-generative System One decision evaluation layer (`JevDecisionClient`) in `agent-core`.
- Implement `JevSettings` (`JEV_` prefix) adhering to the foundation settings pattern with strict secret isolation.
- Implement `JevToolGuardrail` for sub-200ms semantic safety evaluation prior to shell or filesystem operations.
- Introduce `JevConditionalRouter` for deterministic, low-latency edge dispatch in `WorkflowEngine` graphs.
- Implement `JevEvaluator` for `pydantic-evals` dataset evaluation to enable high-throughput test assertions without generative LLM overhead.
- Provide clean degradation/fallback when `TYPESAFE_API_KEY` is not present, failing closed for security-critical checks and failing over to lexical/vector logic for skills and evaluations.

**Non-Goals:**
- Do not modify `tdt-core.provider_model_profile.ProviderProtocol` (which remains dedicated to streaming chat/responses generative backends).
- Do not replace human-in-the-loop approval requirements (`ApprovalMode.AUTHENTICATED_SUBJECT`); Jev acts as an early risk classifier, never as a bypass for high-authority tools.
- Do not generate free-form text or explainability paragraphs.

## Architecture & Data Flow

```
                      +-----------------------------+
                      |   Task / User Instruction   |
                      +-----------------------------+
                                     |
                                     v
                       +---------------------------+
                       |    System 2 Agent Loop    |
                       | (Claude 3.7 / GPT-5 / OMP)|
                       +---------------------------+
                                     |
                       Proposes Tool Call / Transition
                                     |
                                     v
                      +-------------------------------+
                      | Jev System One Decision Model |
                      |    (TypeSafe AI: 80-200ms)    |
                      +-------------------------------+
                        /        |          \         \
                       /         |           \         \
             [Tool Guard]  [Graph Route]  [Skill Pick] [Eval Scorer]
                  |              |             |             |
                  v              v             v             v
           is_destructive?   next_node?    best_match?   correct?
            (bool / score)    (choice)      (choice)      (score)
                  |              |             |             |
        +---------+---------+    |             |             v
        |                   |    |             |        Record Metric
     [True]              [False] v             v        in EvalRecord
        |                   | Dispatch     Bind Skill   (Langfuse/
        v                   v to Node       to Deps      MLflow)
 [Require Approval]   [Authority Policy
 [or Block Exec]       & Approval Check]
                           |
                    +------+------+
                    |             |
                [Approved]    [Denied]
                    |             |
                    v             v
                [Execute]     [Halt / Error]
```

## Decisions

### D1: Decoupled Decision Client vs. Generative Model Provider
- **Decision:** Implement Jev via a standalone `JevDecisionClient` (leveraging `TypeSafeClient` or direct HTTP post to `https://api.typesafe.ai/v1/systemone`) and optional `TypeSafeModel` from `pydantic-ai-slim[typesafe]`, rather than shoehorning Jev into `tdt-core`'s `ProviderProtocol`.
- **Rationale:** `ProviderProtocol` strictly models token-streaming generative chat APIs (`messages`, `openai_chat`, `responses`). Jev does not speak SSE chat completions or emit tokens. Decoupling preserves `tdt-core` type invariants.

### D2: Fail-Closed Security Policy in `JevToolGuardrail`
- **Decision:** If `JevToolGuardrail` encounters a network error, timeout, or missing API key when evaluating high-authority tools (such as shell commands or unconstrained writes), it fails closed by falling back to `AuthorityClass` mandatory approval and regex blocking.
- **Rationale:** Tool execution security must never degrade to open execution when an external classifier fails.

### D3: LangGraph Edge Router Integration via EdgeDescriptor
- **Decision:** Implement `JevConditionalRouter` as a routing handler integrated through `WorkflowEngine`'s edge compilation and routing metadata (`_build_route_map` and conditional edge wiring), rather than calling non-existent public graph methods.
- **Rationale:** `WorkflowEngine` declares nodes and edges using `NodeDescriptor` and `EdgeDescriptor`. Adding decision-driven routing extends edge definitions cleanly while remaining fully compatible with LangGraph's underlying conditional edges.

### D4: Layered Configuration via JevSettings
- **Decision:** Implement `JevSettings` as a subclass of `pydantic_settings.BaseSettings` with `SettingsConfigDict(env_prefix="JEV_")` registered in `agent_core.foundation.settings`.
- **Rationale:** Follows `agent-core`'s standard pattern (`AgentSettings`, `MemorySettings`, `ToolsSettings`, `ObservabilitySettings`). API keys are never read from YAML, enforcing secret isolation.

### D5: Fast Non-Generative Evaluation Scorers
- **Decision:** Implement `JevEvaluator` conforming to the `pydantic_evals.evaluators.Evaluator` interface, compatible with `run_evaluation()` in `agent_core.observability.scorers.runner`.
- **Rationale:** Datasets like `jira_triage` (priority, category, team) and `code_review` (severity, bug detection) can be evaluated in parallel batches without spending tokens on frontier generative LLMs.

## Transaction Boundaries

- **Stateless Evaluator Boundary:** `JevDecisionClient` is strictly stateless. Each call to evaluate a state against questions does not initiate, join, or commit database transactions.
- **Orchestration State Persistence:** In `agent_core.orchestration.graph`, routing decisions returned by `JevConditionalRouter` are pure functions of the node's returned state dictionary. Checkpointing and durable state commits occur only within the configured LangGraph checkpointer (e.g., PostgreSQL or SQLite checkpointers in `pydantic_ai_harness.step_persistence` / `langgraph-checkpoint-postgres`) before and after node execution.
- **Authority Nonce & Approval Lifecycle:** Jev operates strictly prior to approval request construction and does not mint, commit, or consume approval nonces. When Jev flags an operation as high risk, it triggers the standard `ApprovalRequired` exception. Approval nonces are generated and stored exclusively during the authenticated subject approval workflow, and are consumed atomically by `authorize_operation()` only when final authorized execution begins.

## Risks / Trade-offs

- **External Dependency Latency:** Network roundtrip to `api.typesafe.ai` adds ~80–200ms. *Mitigation:* Apply strict 500ms timeout with circuit breaker.
- **Lack of Explanations:** Jev returns calibrated probabilities without rationale text. *Mitigation:* For auditing, log the question prompt, decision, and confidence score; if human approval is triggered, the human inspects the raw command arguments.
- **API Key Requirement:** Requires `TYPESAFE_API_KEY`. *Mitigation:* Graceful opt-in; when disabled or unconfigured, agents default to legacy regex and rule-based behavior.
