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
- **WHEN** configuration is loaded from `~/.tdt/config.yaml` containing a `typesafe_api_key` key
- **THEN** the loader SHALL strip the secret field, emit a user warning, and require the credential through `TYPESAFE_API_KEY` or an `.env` file
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
- **WHEN** an invalid credential is supplied
- **THEN** the SDK SHALL raise during client construction, before any request or retry
- **AND** the runtime SHALL treat this as a configuration error, not a per-call failure

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
