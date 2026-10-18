# Spec Delta: Jev Decision Runtime

## Purpose
Provides sub-second, deterministic System One decision primitives — Noul yes/no probabilities, Choice routing, and ordinal Score — for agent-core tool guardrails, graph branching, skill reranking, and trace evaluation, without generative token latency or output-token cost.

## ADDED Requirements

### Requirement: System One Decision Client

The agent runtime SHALL provide a dedicated System One decision client that evaluates a `state` against a map of typed questions using TypeSafe's three primitives — `Noul` (yes/no), `Choice`, and `Score` — and returns typed answers. The client SHALL use the official `typesafe-sdk` client rather than a hand-rolled HTTP call, and SHALL read answers through the SDK's typed accessors or the `answers` map.

#### Scenario: Successful decision evaluation
- **WHEN** the client evaluates a state against a question map with a configured `TYPESAFE_API_KEY`
- **THEN** it MUST return typed answers keyed by the question IDs supplied
- **AND** a `Noul` answer MUST expose the yes-probability on a 0-to-1 scale
- **AND** a `Choice` or `Score` answer MUST expose both the selected value and its `confidence`
- **AND** no generative text SHALL be returned or parsed

#### Scenario: Multiple atomic questions evaluated in one request
- **WHEN** a caller supplies several independent questions for the same state
- **THEN** the client MUST send them in a single `system_one` request so they are evaluated in parallel
- **AND** code SHALL combine the answers, rather than asking one question per request

#### Scenario: Answer provenance is recorded
- **WHEN** the client completes a request
- **THEN** it MUST surface the response's `model` identifier and `request_id`
- **AND** because `SystemOneResponse.request_id` in `typesafe-sdk` 0.7.2 (`typesafe_sdk/_core/schemas/base.py:67-73`) raises `TypeSafeError("The response did not include a request ID.")` when the `x-typesafe-request-id` response header is absent, `JevDecisionClient` MUST safely extract `request_id` (catching `TypeSafeError` or reading `raw_http_response.headers.get("x-typesafe-request-id")` with a `None` or empty string fallback when absent)
- **AND** SHALL NOT assume the answering model version, because an alias such as `jev-latest` moves between releases
### Requirement: Configuration Management for Jev System One

The foundation settings module SHALL expose a typed `JevSettings` model bound to the `JEV_` environment variable prefix and `~/.tdt/config.yaml` layered configuration. Settings SHALL configure the model identifier, request timeout, and retry policy, and SHALL NOT be the source of the API credential.

#### Scenario: Default configuration loading
- **WHEN** the agent runtime initializes without custom environment variables
- **THEN** `JevSettings` SHALL default to `enabled=False`, a pinned model identifier, a request timeout, and `fail_closed=True`

#### Scenario: Environment variable override
- **WHEN** `JEV_ENABLED=true` and `JEV_TIMEOUT_SECONDS=1.0` are set in the execution environment
- **THEN** `JevSettings` SHALL reflect the overridden values with precedence over file-based configuration

#### Scenario: Secret isolation in configuration
- **WHEN** configuration is loaded from `~/.tdt/config.yaml` containing a top-level or nested `jev` `typesafe_api_key` or `pydantic_ai_gateway_api_key` key
- **THEN** the loader SHALL strip the secret field, emit a `UserWarning`, and require the credential through `TYPESAFE_API_KEY` (or `PYDANTIC_AI_GATEWAY_API_KEY`) or an `.env` file
- **AND** the SDK's own environment variables (`TYPESAFE_API_KEY`, `TYPESAFE_BASE_URL`, `TYPESAFE_DEFAULT_MODEL`) SHALL remain authoritative for transport concerns

#### Scenario: Model identifier may be pinned
- **WHEN** decision thresholds have been calibrated against a specific release
- **THEN** the configuration SHALL allow pinning that versioned model identifier instead of a moving alias

### Requirement: Credential and transport handling

The client SHALL obtain its credential from `TYPESAFE_API_KEY`, SHALL fail fast on an invalid key, and SHALL bound every request with a timeout and a retry policy that respects the service's rate-limit signalling.

#### Scenario: Missing credential
- **WHEN** no credential is configured and the guard is enabled
- **THEN** the client SHALL report an explicit configuration error rather than attempting a request
- **AND** the caller's fallback path SHALL run without hanging

#### Scenario: Invalid credential fails before any request
- **WHEN** a malformed or empty credential is supplied, or an unauthorized credential is rejected by the service
- **THEN** a malformed or empty key SHALL raise `TypeSafeError` during client construction before any request, and an unauthorized key SHALL raise `TypeSafeAuthenticationError` on the first call without retries
- **AND** the runtime SHALL treat this as a configuration/authentication error and trigger the caller's fallback or fail-closed path

#### Scenario: Timeout and rate-limit handling
- **WHEN** a request exceeds its configured timeout, or the service returns a rate-limit or overloaded status
- **THEN** the client SHALL abort or back off according to its retry policy
- **AND** SHALL NOT retry indefinitely within a tool-authorization path

### Requirement: Pre-Flight Tool Guardrail

The tool registry SHALL support an optional pre-flight semantic safety guardrail that intercepts tool invocations before execution or authority approval. The guardrail SHALL evaluate destructive conditions independently, combine probabilities in code, and apply risk-scaled thresholds. The guardrail SHALL NOT downgrade or bypass AuthorityClass requirements, and high-authority tools SHALL NEVER bypass human approval.

#### Scenario: Atomic conditions are judged independently
- **WHEN** the guardrail evaluates a tool invocation
- **THEN** it MUST ask one `Noul` per destructive condition rather than combining conditions into a single question
- **AND** it MUST combine the returned probabilities in code with weights the code controls

#### Scenario: High-risk command interception
- **WHEN** the combined risk for an invocation exceeds the threshold for its risk class
- **THEN** the guardrail SHALL require approval or block execution before the subprocess is spawned

#### Scenario: Genuinely uncertain judgment escalates instead of guessing
- **WHEN** a condition's probability is close to its decision boundary, or a `Choice`/`Score` answer's `confidence` is below the threshold for the action
- **THEN** the guardrail SHALL escalate to human review rather than resolving the invocation either way

#### Scenario: Safe command progression to authority checks
- **WHEN** an invocation's combined risk is below its risk-class threshold
- **THEN** the guardrail SHALL pass the invocation to standard authority and approval gating without bypassing mandatory policy checks

#### Scenario: Guardrail timeout or service failure fail-closed
- **WHEN** the guardrail encounters a network error, service timeout, or unavailable credential while evaluating a high-authority invocation
- **THEN** the guardrail SHALL fail closed by enforcing the standard AuthorityClass approval requirement and existing blocklists
- **AND** SHALL NOT permit tool execution without review

### Requirement: State-Driven Graph Routing

The orchestration engine SHALL support decision-based edge routing in workflow graphs using `Choice` evaluations over the active state dictionary, and SHALL treat the answer's confidence as a second decision axis rather than acting on the selected option alone.

#### Scenario: Deterministic workflow branching
- **WHEN** a graph execution node reaches a conditional branch governed by a decision router
- **THEN** the router SHALL select one of the designated target node IDs from the `Choice` criteria and transition execution without invoking a generative LLM node

#### Scenario: Low-confidence routing does not silently pick a branch
- **WHEN** the router's `Choice` answer falls below the configured confidence threshold for automatic routing
- **THEN** the router SHALL route to the configured review or fallback edge rather than treating the highest-probability option as settled

#### Scenario: Unrecognized decision target fallback
- **WHEN** a router returns a target identifier not defined in the configured route map
- **THEN** the router SHALL transition to the configured default or fallback edge without raising an unhandled exception

#### Scenario: State routing error handling
- **WHEN** evaluation of state routing fails due to a network error or timeout
- **THEN** the routing engine SHALL route execution to the error edge descriptor (`EdgeCondition.ON_FAILURE`)

#### Scenario: Async-safe conditional routing in workflow engine
- **WHEN** `WorkflowEngine.run()` or `resume()` executes a workflow graph via `await compiled.ainvoke(...)` in `src/agent_core/orchestration/graph.py:312-405`
- **THEN** the decision router wired via `add_conditional_edges` in `WorkflowEngine._wire_edges` MUST execute as an `async def` routing function directly awaiting `AsyncTypeSafeClient` / `a_evaluate`
- **AND** SHALL NOT invoke `asyncio.run()` or block the active asyncio event loop

### Requirement: Two-Stage Skill Candidate Selection

The skill matcher SHALL rerank a retrieved candidate shortlist by scoring each candidate against the task description independently and ordering by that score, rather than asking for a single best choice across the list.

#### Scenario: Independent per-candidate scoring
- **WHEN** the matcher reranks a shortlist of skill candidates
- **THEN** it MUST ask one `Noul` per query-candidate pair, keyed by a code-generated question ID
- **AND** it MUST order candidates by the returned yes-probability, highest first
- **AND** candidates MUST NOT be forced to compete inside one question

#### Scenario: The shortlist bounds what reranking can select
- **WHEN** reranking completes
- **THEN** the matcher SHALL only reorder candidates already present in the retrieved shortlist
- **AND** SHALL NOT introduce a candidate the first-stage retrieval did not return

#### Scenario: Reranking failure preserves baseline order
- **WHEN** candidate reranking encounters a decision timeout or service error
- **THEN** the skill matcher SHALL fall back to the initial blended lexical and semantic ranking order

### Requirement: Non-Generative Evaluation Scorer

The evaluation and observability subsystem SHALL provide a `JevEvaluator` compatible with `pydantic-evals` that assesses trace outputs by scoring independent rubric dimensions and combining them in code.

#### Scenario: Fast rubric evaluation
- **WHEN** `JevEvaluator` evaluates an agent output against a rubric
- **THEN** it SHALL score each rubric dimension independently using a `Score` or `Noul` question
- **AND** it SHALL return a numeric result without invoking autoregressive LLM completion
- **AND** the per-dimension answers SHALL remain available so the composition is inspectable

#### Scenario: Evaluator error handling during dataset run
- **WHEN** the evaluation service encounters a network error or timeout during a test case evaluation
- **THEN** the evaluator SHALL record a failed assertion with an error indicator and allow the remainder of the dataset run to complete

### Requirement: Centralized Question and Threshold Definitions

All TypeSafe questions, criteria, weights, and confidence thresholds SHALL be defined in one reviewable module, so that a reviewer can inspect and adjust the judgments without reading the code that consumes them.

#### Scenario: Questions and thresholds are reviewable in one place
- **WHEN** a reviewer inspects the decision configuration
- **THEN** every question, criterion, weight, and threshold SHALL be visible in a single module
- **AND** changing a weight or threshold SHALL NOT require editing the logic that combines the answers

#### Scenario: Questions remain atomic
- **WHEN** a judgment depends on several independent factors
- **THEN** each factor SHALL be asked as its own question
- **AND** the factors SHALL be combined by code rather than by asking one compound question

### Requirement: Decision Observability

Jev decisions SHALL be observable through OpenTelemetry spans carrying decision metadata sufficient to explain and tune a decision after the fact.

#### Scenario: Decision spans are emitted
- **WHEN** a Jev decision completes
- **THEN** a span SHALL be emitted carrying the model identifier that answered, the question identifiers, the returned probabilities or confidences, and the observed latency
- **AND** logging at debug level SHALL NOT emit state bodies containing credentials or secrets
- **AND** because `typesafe_sdk._core.transport.RequestState._log_wire` logs unredacted `request.content` when `"typesafe_sdk"` logger is at `DEBUG`, the runtime MUST clamp `logging.getLogger("typesafe_sdk")` to `>= logging.INFO` (or attach a body-redacting filter) and apply `_redact_secret_value` from `agent_core.foundation.tracing` when projecting bounded tool invocation state (<32k tokens)
### Requirement: HTTP/2 Transport Multiplexing

The client transport SHALL support HTTP/2 multiplexing via `typesafe-sdk[http2]` to maintain persistent socket connections and eliminate per-request handshake overhead.

#### Scenario: HTTP/2 connection pooling
- **WHEN** the decision client initializes in an environment with `typesafe-sdk[http2]` installed
- **THEN** the client SHALL enable HTTP/2 transport multiplexing
- **AND** when `http2=True` and `transport is None`, the client MUST pass the resolved timeout to `httpx2.AsyncClient(http2=True, timeout=timeout)` / `httpx2.Client(http2=True, timeout=timeout)` so `httpx2` does not fall back to its internal 5.0s default timeout
- **AND** the client MUST expose `close()` / `aclose()` methods and implement sync/async context managers (`__enter__`/`__exit__`, `__aenter__`/`__aexit__`) for explicit lifecycle shutdown
- **AND** repeated decision calls SHALL reuse open sockets without renegotiating TLS handshakes
### Requirement: Native Pydantic Response Models

The client SHALL support structured validation using TypeSafe native response models subclassing `SystemOneResponse` (or Pydantic `BaseModel`).

#### Scenario: Strongly typed response parsing
- **WHEN** a caller provides a typed `response_model` class to `system_one`
- **THEN** custom typed response schemas declaring top-level question fields MUST subclass `SystemOneResponse` so that `SystemOneResponse._decode()` lifts `decoded["answers"][field]` onto top-level model attributes and attaches `_request_id` and `raw_http_response` (as a plain `pydantic.BaseModel` passed to `parse_response()` validates un-lifted wire JSON `{"model": ..., "answers": {...}, "usage": ...}` without attribute lifting), or `JevDecisionClient` MUST normalize and lift `answers` when a plain `BaseModel` is supplied
- **AND** the client SHALL return an instance of that model containing validated question answers
- **AND** callers SHALL access answer fields directly as typed attributes without indexing raw dictionaries

### Requirement: Pydantic AI Gateway Compatibility

The configuration and client SHALL support proxying requests through Pydantic AI Gateway or enterprise proxies via `PYDANTIC_AI_GATEWAY_API_KEY` and base URL configuration.

#### Scenario: Gateway proxy routing
- **WHEN** `PYDANTIC_AI_GATEWAY_API_KEY` or custom `TYPESAFE_BASE_URL` is set
- **THEN** because `typesafe_sdk._core.config.resolve_and_validate_api_key()` only checks the explicit `api_key` argument or `os.environ.get("TYPESAFE_API_KEY")`, `JevDecisionClient` MUST explicitly resolve `api_key = api_key or os.environ.get("TYPESAFE_API_KEY") or os.environ.get("PYDANTIC_AI_GATEWAY_API_KEY")` and pass `api_key` and `base_url=settings.jev.base_url or os.environ.get("TYPESAFE_BASE_URL") or None` into `TypeSafeClient` / `AsyncTypeSafeClient`
- **AND** the client SHALL route decision requests through the configured gateway endpoint
- **AND** telemetry headers SHALL be passed transparently for unified fleet governance
### Requirement: Reusable Cross-Ecosystem Decision Contracts

The decision runtime SHALL expose modular interfaces so sister repositories can consume decision primitives without duplicating client or retry logic.

#### Scenario: Downstream banking and planning integration
- **WHEN** downstream packages such as `shb-agent-core` or `shb-agent-harness` import decision abstractions
- **THEN** the runtime SHALL expose reusable question definitions and risk classifiers
- **AND** callers SHALL execute custom domain gates such as transfer triage or stage skipping
