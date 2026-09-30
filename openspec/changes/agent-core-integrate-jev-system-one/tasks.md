# Tasks

## 1. Core Jev Decision Client & Settings

- [ ] 1.1 Add optional `typesafe` dependency support to `agent-core/pyproject.toml` (`typesafe-sdk` or `pydantic-ai-slim[typesafe]`). Verification: run `uv sync` and verify successful dependency resolution.
- [ ] 1.2 Implement `JevSettings` in `agent_core/foundation/settings.py` with `JEV_` environment variable prefix and secret isolation. Verification: unit tests in `tests/test_settings.py` checking defaults and environment variable overrides.
- [ ] 1.3 Implement `JevDecisionClient` in `agent_core/foundation/jev.py` handling `bool`, `choice`, and `score` questions with timeout (500ms), circuit breaking, and mock capabilities for hermetic unit testing. Verification: unit tests in `tests/test_jev_client.py` covering success and timeout fallback.

## 2. Pre-Flight Tool Guardrail Integration

- [ ] 2.1 Implement `JevToolGuardrail` in `agent_core/tool_registry/guardrails.py` wrapping sensitive tools (e.g. `ShellTool`, file mutators) to evaluate `is_destructive` and risk levels before execution, enforcing that high-authority tools still progress to mandatory approval checks. Verification: unit tests verifying dangerous command interception vs benign command authority progression.
- [ ] 2.2 Wire `JevToolGuardrail` into `AgentRuntime` tool execution path in `agent_core/_ai/tools.py` with fail-closed fallback to standard authority checks when the service is unreachable. Verification: test fail-closed behavior when `TYPESAFE_API_KEY` is unset or times out.

## 3. Workflow Engine LangGraph Decision Routing

- [ ] 3.1 Implement `JevConditionalRouter` in `agent_core/orchestration/graph.py` translating state attributes into discrete target edge selections with fallback to default edges on unrecognized outputs. Verification: test state routing across multiple targets in a test LangGraph workflow.
- [ ] 3.2 Update `WorkflowEngine._wire_edges` to support direct `JevConditionalRouter` specifications alongside existing static `EdgeCondition` rules. Verification: integration test running an end-to-end graph transition.

## 4. Skill Matcher Second-Stage Reranking

- [ ] 4.1 Extend `SkillMatcher` in `agent_core/skill_system/matcher.py` with an optional `a_match_jev()` method to disambiguate top-K retrieved candidates using Jev's `choice` question, falling back to initial ranks on error. Verification: unit tests verifying candidate reranking when lexical/semantic scores are closely tied.

## 5. Non-Generative Evaluation Scorers

- [ ] 5.1 Implement `JevEvaluator` in `agent_core/observability/scorers/jev_scorer.py` conforming to `pydantic-evals.evaluators.Evaluator` interface. Verification: unit tests verifying rubric evaluation against sample outputs.
- [ ] 5.2 Integrate `JevEvaluator` with `agent_core/observability/scorers/runner.py` and benchmark on `agent_core/evaluation/datasets/jira_triage.py`. Verification: run evaluation runner and confirm score extraction without LLM generation tokens.

## 6. End-to-End Verification & Observability

- [ ] 6.1 Add OpenTelemetry tracing and span attributes for Jev decision queries (latency, question type, confidence scores) in `agent_core/foundation/tracing.py`. Verification: check OTel spans emitted during a guarded agent step.
- [ ] 6.2 Run full `pytest` regression suite across `agent-core` to ensure zero breaking changes in standard generative agent paths. Verification: run `uv run pytest tests/` with all existing tests passing.
