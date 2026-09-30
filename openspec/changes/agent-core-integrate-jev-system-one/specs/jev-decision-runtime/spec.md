# Spec Delta: Jev Decision Runtime

## Purpose
Provides sub-second, deterministic System One decision primitives (boolean checks, discrete choice routing, ordinal risk scoring, and evaluation metrics) for agent-core tool guardrails, graph branching, skill dispatch, and trace evaluation without generative token latency or output token costs.

## ADDED Requirements

### Requirement: System One Decision Client
The agent runtime SHALL provide a dedicated System One decision evaluation client capable of assessing structured prompts against defined question types (`bool`, `choice`, `score`) with calibrated probabilities.

#### Scenario: Successful decision evaluation
- **WHEN** a client evaluates an input state against a typed question schema using a valid TypeSafe credentials environment
- **THEN** the client SHALL return structured decision values matching the requested output types without streaming free-form text tokens.

#### Scenario: Missing credentials fail-safe fallback
- **WHEN** the System One client is invoked without a configured `TYPESAFE_API_KEY`
- **THEN** the client SHALL raise an explicit configuration error or execute the pre-configured heuristic fallback without hanging.

#### Scenario: Network failure or timeout handling
- **WHEN** a call to the System One decision service exceeds the configured timeout (default 500ms) or encounters a network error
- **THEN** the client SHALL abort the request and trigger the configured fail-safe error or fallback handler.

### Requirement: Configuration Management for Jev System One
The foundation settings module SHALL expose a typed `JevSettings` model bound to the `JEV_` environment variable prefix and `~/.tdt/config.yaml` layered configuration.

#### Scenario: Default configuration loading
- **WHEN** agent runtime initializes without custom environment variables
- **THEN** `JevSettings` SHALL default to `enabled=False`, `model="jev-latest"`, `timeout_seconds=0.5`, and `fail_closed=True`.

#### Scenario: Environment variable override
- **WHEN** `JEV_ENABLED=true` and `JEV_TIMEOUT_SECONDS=1.0` are set in the execution environment
- **THEN** `JevSettings` SHALL reflect the overridden values with precedence over file-based configuration.

#### Scenario: Secret isolation in configuration
- **WHEN** configuration is loaded from `~/.tdt/config.yaml` containing a `typesafe_api_key` key
- **THEN** the loader SHALL strip the secret field, emit a user warning, and require credentials via environment or `.env`.

### Requirement: Pre-Flight Tool Guardrail
The tool registry SHALL support an optional pre-flight semantic safety guardrail that intercepts tool invocations before execution or authority approval to evaluate destructive potential. The guardrail SHALL NOT downgrade or bypass AuthorityClass requirements; for tools with `AuthorityClass.high_authority=True`, a benign evaluation by Jev permits progress to standard authority approval gating but SHALL NEVER bypass human approval requirements.

#### Scenario: High-risk command interception
- **WHEN** an agent issues a tool invocation containing potentially destructive or out-of-scope actions
- **THEN** the guardrail SHALL evaluate the command intent and raise an approval requirement or block execution before subprocess spawning.

#### Scenario: Safe command progression to authority checks
- **WHEN** an agent issues a benign command evaluated as safe by the guardrail
- **THEN** the guardrail SHALL complete evaluation within 250ms and pass the invocation to standard authority and approval gating without bypassing mandatory policy checks.

#### Scenario: Guardrail timeout or service failure fail-closed
- **WHEN** the guardrail encounters a network error, service timeout, or unavailable API key while evaluating a high-authority tool invocation
- **THEN** the guardrail SHALL fail closed by enforcing standard AuthorityClass approval and legacy regex blocklists, and SHALL NOT permit tool execution without review.

### Requirement: State-Driven Graph Routing
The orchestration engine SHALL support decision-based edge routing in workflow graphs using discrete choice evaluations over the active state dictionary.

#### Scenario: Deterministic workflow branching
- **WHEN** a graph execution node reaches a conditional branch governed by a decision router
- **THEN** the router SHALL classify the state dictionary into one of the designated target node IDs and transition execution without invoking a generative LLM node.

#### Scenario: Unrecognized decision target fallback
- **WHEN** a decision router returns a target edge identifier not defined in the configured target route map
- **THEN** the router SHALL transition to the configured default or fallback edge descriptor without raising an unhandled exception.

#### Scenario: State routing error handling
- **WHEN** evaluation of state routing fails due to a network error or timeout
- **THEN** the routing engine SHALL route execution to the error edge descriptor (`EdgeCondition.ON_FAILURE`).

### Requirement: Two-Stage Skill Candidate Selection
The skill matcher SHALL support reranking top-K skill candidates using a choice evaluation against the agent task description.

#### Scenario: Disambiguating overlapping skill candidates
- **WHEN** multiple skill candidates exceed the initial lexical/semantic retrieval threshold with similar relevance scores
- **THEN** the matcher SHALL select the single best skill choice or return the ranked sequence with calibrated confidence metrics.

#### Scenario: Reranking failure preserves baseline order
- **WHEN** candidate reranking encounters a decision timeout or API error
- **THEN** the skill matcher SHALL fall back to the initial blended lexical and semantic ranking order.

### Requirement: Non-Generative Evaluation Scorer
The evaluation and observability subsystem SHALL provide a `JevEvaluator` compatible with `pydantic-evals` dataset evaluation to assess trace outputs against rubrics or ground truth metadata.

#### Scenario: Fast rubric evaluation
- **WHEN** `JevEvaluator` evaluates an agent output against a binary correctness or policy assertion rubric
- **THEN** the evaluator SHALL return a numeric or boolean score with confidence metrics without invoking autoregressive LLM completion.

#### Scenario: Evaluator error handling during dataset run
- **WHEN** the evaluation service encounters a network error or timeout during a test case evaluation
- **THEN** the evaluator SHALL record a failed assertion with an error indicator and allow the remainder of the dataset run to complete.
