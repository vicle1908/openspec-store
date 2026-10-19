# Spec Delta: Jev Decision Runtime

## Purpose
Provides sub-second, deterministic System One decision primitives — Noul yes/no probabilities, Choice routing, and ordinal Score — for the SHB Banking Ecosystem (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`) and Workspace Ecosystem Foundation, powering banking tool guardrails, AML screening triage, LangGraph harness branching, skill catalog reranking, and trace evaluation without generative token latency or output-token cost.

## ADDED Requirements

### Requirement: System One Decision Client

The banking runtime foundation SHALL provide a dedicated System One decision client (`shb_core.jev.JevDecisionClient`) wrapping `typesafe_sdk.TypeSafeClient` and `AsyncTypeSafeClient` (`evaluate` and `a_evaluate`) to evaluate `state` against typed `Noul`, `Choice`, and `Score` questions, reading answers via SDK accessors or `answers` and guarding availability with `JevCircuitBreaker`.

#### Scenario: Successful decision evaluation
- **WHEN** the client evaluates a state against a question map with a configured `TYPESAFE_API_KEY` (or `PYDANTIC_AI_GATEWAY_API_KEY`)
- **THEN** it MUST return typed answers keyed by the question IDs supplied
- **AND** a `Noul` answer MUST expose the yes-probability on a 0-to-1 scale ($p \in [0.0, 1.0]$) and certainty $|2p - 1|$ (where $p \approx 0.5$ represents maximal uncertainty between yes and no, not medium intensity)
- **AND** a `Choice` answer MUST expose the selected value, its distribution concentration `confidence`, and probabilities mapping
- **AND** a `Score` answer MUST evaluate 0-indexed levels ($0 \dots N-1$, `min_length=2`) and return expected value $\sum_{i=0}^{N-1} i \cdot P(i) \in [0.0, N-1]$ alongside `confidence`, `probabilities`, and `legend`
- **AND** no generative text SHALL be returned or parsed

#### Scenario: Multiple atomic questions evaluated in one request
- **WHEN** a caller supplies several independent questions for the same state (such as speculative fan-out or composite scoring)
- **THEN** the client MUST send them in a single `system_one` request so they are evaluated in parallel (~11.5x lower cost, ~9.6x lower latency compared to generative function calling)
- **AND** code SHALL combine the answers using domain weights and thresholds, rather than asking one question per request

#### Scenario: Answer provenance, token attribution, and safe request_id extraction
- **WHEN** the client completes a request
- **THEN** it MUST surface the response's `model` identifier, `request_id`, and normalized `usage` (`JevUsage`)
- **AND** because `typesafe_sdk.Usage` (`typesafe_sdk/_core/response_types.py:59-67` and `typesafe_sdk/_schemas/models.py:130-137`, configured with `ConfigDict(extra="ignore", frozen=True, strict=True)`) defines only `input_tokens: int | None = None` and `output_tokens: int | None = None` (without `question_tokens` or `total_tokens`), `JevDecisionClient` MUST read `input_tokens = response.usage.input_tokens or 0` and `output_tokens = response.usage.output_tokens if response.usage.output_tokens is not None else (getattr(response.usage, "question_tokens", 0) or 0)` and surface normalized `JevUsage(input_tokens=input_tokens, output_tokens=output_tokens, question_tokens=output_tokens, total_tokens=input_tokens + output_tokens)` on the decision result, OTel span (`jev.input_tokens`, `jev.output_tokens`, `jev.total_tokens`), and `TelemetryStore.record_jev_decision` (with mock transport JSON bodies supplying `"usage": {"input_tokens": ..., "output_tokens": ...}`)
- **AND** because `SystemOneResponse.request_id` in `typesafe-sdk` (`typesafe_sdk/_core/schemas/base.py:67-73`) raises `TypeSafeError("The response did not include a request ID.")` when the `x-typesafe-request-id` response header is absent, `JevDecisionClient` MUST safely extract `request_id` (catching `TypeSafeError` or reading `raw_http_response.headers.get("x-typesafe-request-id")` with a `None` or empty string fallback when absent)
- **AND** SHALL NOT assume the answering model version, because an alias such as `jev-latest` moves between releases

#### Scenario: Circuit breaker protects downstream availability
- **WHEN** the client experiences consecutive transport errors or 5xx failures exceeding `circuit_breaker_threshold` (default 3)
- **THEN** `JevCircuitBreaker` MUST transition to open state and fast-fail subsequent evaluation requests during the `circuit_breaker_cooldown_seconds` (default 30.0s) window without making network calls
- **AND** the caller SHALL immediately execute its deterministic fallback or fail-closed path
### Requirement: Configuration Management for Jev System One

The foundation settings module (`shb_core.config`) SHALL expose a typed `JevSettings` model on `ShbSettings.jev` bound to `JEV_` and `SHB_JEV_` environment prefixes and loaded from `~/.shb/.env` and `~/.shb/config.yaml` in strict isolation from `~/.tdt/`. Settings SHALL configure the model identifier, timeout, retries, circuit breaker, and fail-closed policy without storing API credentials.

#### Scenario: Default configuration loading
- **WHEN** the banking runtime initializes without custom environment variables
- **THEN** `JevSettings` SHALL default to `enabled=False`, pinned `model="jev-1.13.0"` (with support for preview `jev-1.14.0`), `timeout_seconds=1.5`, `max_retries=2`, `http2=True`, `base_url=None`, `fail_closed=True`, `circuit_breaker_threshold=3`, `circuit_breaker_cooldown_seconds=30.0`, and `compression=None` (where `compression=False` is enforced when a custom gateway `base_url` or mock `transport` is configured)

#### Scenario: Environment variable override
- **WHEN** `JEV_ENABLED=true` or `SHB_JEV_ENABLED=true` and `JEV_TIMEOUT_SECONDS=1.0` are set in the execution environment
- **THEN** `JevSettings` SHALL reflect the overridden values with precedence over file-based configuration

#### Scenario: Secret isolation and workspace isolation
- **WHEN** configuration is loaded from `~/.shb/config.yaml` containing a top-level or nested `jev` `typesafe_api_key` or `pydantic_ai_gateway_api_key` key
- **THEN** the loader SHALL strip the secret field, emit a `UserWarning`, and require the credential through `TYPESAFE_API_KEY` (or `PYDANTIC_AI_GATEWAY_API_KEY`) or `~/.shb/.env`
- **AND** configuration paths SHALL be strictly isolated to `~/.shb/` without reading `~/.tdt/.env` or `~/.tdt/config.yaml`
- **AND** the SDK's own environment variables (`TYPESAFE_API_KEY`, `TYPESAFE_BASE_URL`, `TYPESAFE_DEFAULT_MODEL`) SHALL remain authoritative for transport concerns

#### Scenario: Model identifier may be pinned
- **WHEN** decision thresholds have been calibrated against a specific release
- **THEN** the configuration SHALL allow pinning versioned model identifiers (`jev-1.13.0` stable or `jev-1.14.0` preview) instead of a moving alias
### Requirement: Credential and transport handling

The client SHALL obtain its credential from `TYPESAFE_API_KEY` or `PYDANTIC_AI_GATEWAY_API_KEY`, SHALL fail fast on an invalid or missing key, and SHALL bound every request with a timeout, circuit breaker, and retry policy that respects rate-limit and service status signalling.

#### Scenario: Missing credential
- **WHEN** no credential is configured and Jev is enabled
- **THEN** the client SHALL report an explicit configuration error rather than attempting a request
- **AND** the caller's fallback path SHALL run without hanging

#### Scenario: Invalid credential fails before any request
- **WHEN** a malformed or empty credential is supplied, or an unauthorized credential is rejected by the service
- **THEN** a malformed or empty key SHALL raise `TypeSafeError` during client construction before any request, and an unauthorized key SHALL raise `TypeSafeAuthenticationError` on the first call without retries
- **AND** the runtime SHALL treat this as an authentication error and trigger the caller's fallback or fail-closed path

#### Scenario: Timeout and rate-limit handling
- **WHEN** a request exceeds its configured timeout (`timeout_seconds=1.5`), or the service returns a rate-limit (429) or overloaded status
- **THEN** the client SHALL abort or back off according to its retry policy (`max_retries=2`)
- **AND** SHALL NOT retry indefinitely within a banking tool authorization or workflow routing path

### Requirement: Pre-Flight Tool Guardrail

The banking agent tool registry (`shb-agent-core`) SHALL provide pre-flight semantic safety guardrails (`shb_agent.tools.guardrails.JevToolGuardrail`) evaluating atomic `Noul` conditions on sanitized payloads, combining probabilities in code using `shb_core.decisions` weights, and applying risk thresholds per `AuthorityClass` without bypassing human or maker-checker approvals.

#### Scenario: Atomic conditions are judged independently across tool registry
- **WHEN** the guardrail evaluates an invocation across all 10 registered tools in `src/shb_agent/tools/__init__.py` mapped to `TOOL_AUTHORITY_MAP`:
  - `READ_ONLY`: `get_account_balance`, `query_transaction_status`, `get_transaction_history`, `query_bill`
  - `OPERATIONAL`: `verify_beneficiary_account`, `generate_vietqr`, `parse_vietqr` (`src/shb_agent/tools/vietqr.py:135`, extracting EMVCo Tag 62 `purpose` content when present for Jev prompt-injection screening while preserving `is_valid_crc: True` for 4-hex-char CRCs such as `...6304ABCD` and exposing `crc_matches_computed: bool`)
  - `FINANCIAL_TRANSFER`: `initiate_fund_transfer` (inviolable `> 50,000,000 VND` maker-checker supervisor token + sub-50M VND structuring escalation) AND `pay_bill` (`src/shb_agent/tools/biller.py`: high-value biller debit & `amount != amount_due` anomaly escalation)
  - `COMPLIANCE_CRITICAL`: `screen_beneficiary` (deterministic `RESTRICTED_KEYWORDS` & `HIGH_RISK_ACCOUNTS` first, then Jev `Noul` for transliterated/diacritic-stripped Vietnamese and English PEP/OFAC/SBV sanction evasion)
- **THEN** it MUST ask one `Noul` per condition using structured `JSONContent` criteria dicts (`definition`, `includes`, `excludes`, `contrast_with`) and backticked JSON state paths (e.g., `` `transaction.narrative` ``, `` `beneficiary.name` ``) because question IDs are not sent to the model
- **AND** it MUST sanitize the payload via `sanitize_jev_state(state, max_tokens=32_000)` by masking primary account numbers (`mask_pan`) and recursively redacting sensitive credential keys (`secret`, `token`, `password`, `key`, `supervisor_approval_token`, excluding `idempotency_key`) before transmitting bounded state (`<32k` tokens)
- **AND** it MUST combine the returned probabilities in code using code-owned weights from `shb_core.decisions`

#### Scenario: Dynamic tool preparation via Speculative Fan-Out
- **WHEN** `ShbAgent` prepares tools for an execution turn via Pydantic AI 2.54.0 `PrepareTools(fn)` capability (`Agent(..., capabilities=[PrepareTools(fn)])`) or `Hooks`
- **AND** tool names are normalized via `tool_name.removeprefix("tool_")` so both `tool_`-prefixed registrations (`tool_get_account_balance`, `tool_query_transaction_status`, `tool_initiate_fund_transfer`) and unprefixed `tool_plain` tools (`initiate_fund_transfer`, `pay_bill`) match against `TOOL_AUTHORITY_MAP` (`{"initiate_fund_transfer", "pay_bill"}`)
- **AND** speculative fan-out (`recommended_tool_family` with `confidence >= 0.85`) classifies the user turn intent as read-only
- **THEN** financial debit tools (`tool_initiate_fund_transfer`, `initiate_fund_transfer`, `pay_bill`) SHALL be dynamically omitted from the active turn toolset so indirect prompt injection (such as malicious VietQR Tag 62 `purpose` payloads) cannot trigger unintended debits
- **AND** when `get_settings().jev.enabled` (`JEV_ENABLED=false`) is false or no Jev credential/mock client is configured, `ShbAgent.run()` simulation and `TestModel` execution (`tests/test_agent.py`) SHALL remain preserved without modification
#### Scenario: Maker-Checker invariant strictly enforced for large transfers
- **WHEN** `initiate_fund_transfer` is called with an amount exceeding `50,000,000 VND` (`MAKER_CHECKER_THRESHOLD_VND`)
- **THEN** the runtime MUST enforce supervisor approval token validation (`ModelRetry` / `PENDING_APPROVAL`) regardless of Jev decision scores
- **AND** Jev SHALL NEVER downgrade or bypass this mandatory maker-checker invariant

#### Scenario: Sub-threshold transfer risk escalation
- **WHEN** `initiate_fund_transfer` is called with an amount at or below `50,000,000 VND` but Jev detects structuring patterns, suspicious narrative indicators, or injection attempts exceeding the escalation threshold
- **THEN** the guardrail SHALL escalate the transfer to `PENDING_APPROVAL` (requiring a valid `supervisor_approval_token`) or `BLOCK` execution before any banking transaction occurs
- **AND** when a valid `supervisor_approval_token` (min 8 chars) is supplied, an `ESCALATE` outcome SHALL be satisfied and complete cleanly with `status="COMPLETED"`
#### Scenario: AML beneficiary screening triage
- **WHEN** `screen_beneficiary` executes compliance screening in `src/shb_agent/tools/compliance.py`
- **THEN** deterministic rules (`RESTRICTED_KEYWORDS` and `HIGH_RISK_ACCOUNTS`) SHALL remain strictly authoritative and execute first
- **AND** when Jev is enabled, semantic `Noul` checks SHALL evaluate transliterated or obfuscated PEP/sanction narratives and flag suspicious matches as `FLAGGED_FOR_MANUAL_REVIEW`
- **AND** on any Jev timeout or failure, screening SHALL fail closed to deterministic rule results

#### Scenario: Genuinely uncertain judgment escalates instead of guessing
- **WHEN** a condition's probability falls within the uncertain band ($p \in [0.4, 0.6]$), or a `Choice`/`Score` answer's `confidence` is below the configured threshold
- **THEN** the guardrail SHALL escalate to human supervisor review (`ESCALATE`) rather than guessing

#### Scenario: Safe command progression to authority checks
- **WHEN** an invocation's combined risk is below its risk-class threshold
- **THEN** the guardrail SHALL return `PROCEED` and pass the invocation to standard authority and approval gating without bypassing mandatory policy checks

#### Scenario: Guardrail timeout or service failure fail-closed
- **WHEN** the guardrail encounters a network error, service timeout, or unavailable credential while evaluating an `OPERATIONAL`, `FINANCIAL_TRANSFER`, or `COMPLIANCE_CRITICAL` invocation
- **THEN** the guardrail SHALL fail closed (`BLOCK` or escalate to mandatory `supervisor_approval_token` validation, where a valid `supervisor_approval_token` of min 8 chars satisfies `ESCALATE` on `initiate_fund_transfer` and returns `status="COMPLETED"`) in accordance with `fail_closed=True`
- **AND** SHALL NOT permit unapproved tool execution
### Requirement: State-Driven Graph Routing

The workflow engine (`shb-agent-harness`, package `shb_harness`) SHALL support confidence-gated graph routing using TypeSafe `Choice` decisions (`_should_skip_api_contract` / `a_should_skip_api_contract`) wired via `builder.add_conditional_edges(StageName.SPEC.value, ...)`, treating `confidence` as a second axis and failing safe to `StageName.API_CONTRACT` while preserving human interrupt gates.

#### Scenario: Confident routing decision bypasses intermediate stage
- **WHEN** `StageName.SPEC` completes and `_should_skip_api_contract` / `a_should_skip_api_contract` evaluates the state (normalizing `state = HarnessState.model_validate(state) if isinstance(state, dict) else state` at entry)
- **THEN** it MUST first execute the deterministic `ClassificationStage` metadata check (`category == "internal_refactor"` or `has_api_impact is False`) so deterministic internal-refactor routing always routes to `StageName.DESIGN.value` (`"design"`)
- **AND** otherwise, if Jev `Choice` (`"design"` vs `"api_contract"`) selects `"design"` with `confidence >= 0.85` (indicating internal changes with no external API contract impact), execution SHALL bypass `StageName.API_CONTRACT` directly to `StageName.DESIGN`

#### Scenario: Low confidence or unrecognized target fails safe to standard stage
- **WHEN** Jev is disabled or unconfigured, or the routing decision returns `confidence < 0.85`, returns an unrecognized target, or returns `"api_contract"` (`StageName.API_CONTRACT.value`)
- **THEN** the routing engine SHALL route execution to `StageName.API_CONTRACT`
- **AND** human interrupt review gates at `StageName.PLAN_REVIEW` SHALL remain strictly preserved

#### Scenario: State routing error handling
- **WHEN** evaluation of state routing fails due to a network error, timeout, or circuit breaker open state
- **THEN** the routing engine SHALL fail safe and route execution to `StageName.API_CONTRACT` (`"api_contract"`)

#### Scenario: Async-safe conditional routing in workflow engine
- **WHEN** the harness executes a workflow graph via synchronous `graph.invoke(...)` (`HarnessRunner.run_all()` with synchronous `SqliteSaver`) or asynchronous `await graph.ainvoke(...)` (with async checkpointer)
- **THEN** `shb_harness/workflow.py` MUST wire `RunnableCallable(_should_skip_api_contract, a_should_skip_api_contract)` into `builder.add_conditional_edges(StageName.SPEC.value, ...)`
- **AND** both functions MUST normalize `dict` or `HarnessState` inputs and evaluate deterministic `classification.metadata` before Jev `Choice` (`"design"` vs `"api_contract"`)
- **AND** synchronous `graph.invoke(...)` SHALL invoke `_should_skip_api_contract` calling `JevDecisionClient.evaluate()` (`TypeSafeClient`) without raising `TypeError('No synchronous function provided to "branch:to:..."')`
- **AND** asynchronous `await graph.ainvoke(...)` SHALL invoke `a_should_skip_api_contract` calling `await JevDecisionClient.a_evaluate()` (`AsyncTypeSafeClient`) without calling `asyncio.run()` or blocking the active asyncio event loop
### Requirement: Two-Stage Skill Candidate Selection

The skill package (`shb-agent-skills`) SHALL create `shb_skills.matcher.SkillMatcher` (re-exported in `shb_skills.__init__`) over `SkillsCatalog` to provide Stage 1 deterministic shortlist retrieval (`match()`) and Stage 2 Jev reranking (`match_jev()` / `a_match_jev()`) using one `Noul` per candidate in a single batched request, enforcing shortlist subset invariance and Stage 1 fallback.

#### Scenario: Independent per-candidate scoring
- **WHEN** `SkillMatcher` (in `src/shb_skills/matcher.py`, initialized over `SkillsCatalog` from `load_skills_registry()`) retrieves a Stage 1 lexical/category shortlist via `match(query, *, category=None, top_k=5)` and reranks candidates via `match_jev()` or `a_match_jev()`
- **THEN** it MUST ask one `Noul` per query-candidate pair, keyed by a code-generated question ID with candidate profile and query formatted in state
- **AND** it MUST order candidates by the returned yes-probability, highest first
- **AND** candidates MUST NOT be forced to compete inside one compound question

#### Scenario: The shortlist bounds what reranking can select
- **WHEN** candidate reranking completes
- **THEN** the matcher SHALL only reorder candidates already present in the retrieved Stage 1 shortlist
- **AND** SHALL NOT introduce a candidate the first-stage retrieval did not return

#### Scenario: Reranking failure preserves baseline order
- **WHEN** candidate reranking encounters a decision timeout, service error, or circuit breaker open state
- **THEN** the skill matcher SHALL fall back immediately to the initial Stage 1 ranking order without throwing an unhandled exception
### Requirement: Non-Generative Evaluation Scorer

The evaluation subsystem (`shb-agent-core`, package `shb_agent.evaluation`) SHALL provide a `JevEvaluator` compatible with `pydantic-evals` that assesses trace outputs by scoring independent rubric dimensions (`Score` and `Noul`) in a single parallel request and combining them in code without generative LLM completion.

#### Scenario: Fast rubric evaluation
- **WHEN** `JevEvaluator` in `src/shb_agent/evaluation/jev_scorer.py` (re-exported in `src/shb_agent/evaluation/__init__.py` alongside built-in `BANKING_EVAL_DATASET` using `pydantic_evals.Dataset` / `Case`) evaluates an agent output or trace against a multi-dimensional rubric (e.g., accuracy, tone, compliance adherence) using `pydantic-evals>=1.70.0`
- **THEN** it SHALL score each rubric dimension independently using a `Score` (normalized as $\text{score}/(N-1)$) or `Noul` question in one request
- **AND** it SHALL return a numeric result composed in code without invoking autoregressive LLM completion
- **AND** the per-dimension answers SHALL remain available so the composition is inspectable
#### Scenario: Evaluator error handling during dataset run
- **WHEN** the evaluation service encounters a network error or timeout during a test case evaluation in a benchmark run
- **THEN** the evaluator SHALL record an `EvaluationReason(value=False, reason=...)` failed assertion with the error details and allow the remainder of the dataset run to complete without aborting
### Requirement: Centralized Question and Threshold Definitions

All TypeSafe questions, criteria, code-owned weights, and confidence thresholds across the SHB ecosystem SHALL be defined in a single reviewable module (`shb_core.decisions`), so reviewers can inspect judgments without editing business logic, and SHALL provide portable foundation contracts (`DecisionContract`, `GuardrailPolicy`, `CitationCheckContract`) reusable across workspace organizations.

#### Scenario: Questions and thresholds are reviewable in one place
- **WHEN** a reviewer inspects the decision configuration in `src/shb_core/decisions.py`
- **THEN** every question, criterion, weight, and threshold across guardrails, triage, routing, and skills SHALL be visible in a single module, using `typesafe_sdk`'s real classes (`typesafe_sdk._core.question_types`, `typesafe_sdk._core.response_types`) when installed and lightweight Pydantic/TypedDict fallback shims (`Noul`, `Choice`, `Score`, `NoulCriteria`, `NoulAnswer`, `ChoiceAnswer`, `ScoreAnswer`, `Usage`, `SystemOneResponse`, `TypeSafeError`, `TypeSafeAuthenticationError`) in `shb_core.jev` and `shb_core.decisions` when `typesafe-sdk` is not installed
- **AND** changing a weight or threshold SHALL NOT require editing the logic that combines the answers
- **AND** `src/**/*.py` (including `src/shb_core/decisions.py` criteria examples and docstrings) MUST NOT contain any `api_key|secret_key|private_key|password|jwt_secret` string literal $\ge 12$ chars (`SEC-001`) or any unmasked 16-digit PAN (`PCI-001`) enforced by `shb-tools` `ComplianceScanner`
#### Scenario: Questions remain atomic
- **WHEN** a judgment depends on several independent factors
- **THEN** each factor SHALL be asked as its own atomic question using backticked JSON state paths (e.g., `` `transaction.narrative` ``, `` `beneficiary.name` ``, `` `ticket.stage_results.spec.summary` ``)
- **AND** criteria MUST use structured `JSONContent` dicts (`definition`, `includes`, `excludes`, `contrast_with`) to define nuanced domain boundaries since question IDs are not sent to the model
- **AND** `Choice` questions MAY provide `None` criteria values for self-explanatory keys or pre-parsed candidate spans
- **AND** `Score` questions MUST define 0-indexed levels ($0 \dots N-1$, `min_length=2`) returning expected value $\sum_{i=0}^{N-1} i \cdot P(i)$
- **AND** the factors SHALL be combined by code rather than by asking one compound question

#### Scenario: Portable foundation contract reusability
- **WHEN** another workspace organization (such as `platform`, `vds`, `ascend`, `ghtk`, or `fpt`) adopts System One decision primitives
- **THEN** `DecisionContract`, `GuardrailPolicy`, and `CitationCheckContract` in `shb_core.decisions` SHALL provide generic parameterization that can be imported without depending on banking-specific schemas
### Requirement: Decision Observability

Jev decisions SHALL be observable through OpenTelemetry spans (`shb.jev.decision`) emitted via `shb_core.telemetry.get_tracer("shb_core.jev")` and recorded in `shb_observability.collector.TelemetryStore` with metrics. The runtime MUST clamp `typesafe_sdk` logging to `>= logging.INFO` and sanitize state projections with `mask_pan` and `sanitize_payload` before evaluation or logging.

#### Scenario: Decision spans and metrics are emitted
- **WHEN** a Jev decision completes in any layer
- **THEN** an OpenTelemetry span named `shb.jev.decision` SHALL be emitted carrying the model identifier that answered, question identifiers, returned probabilities or confidences, outcome, observed latency, and normalized token attribution (`jev.input_tokens`, `jev.output_tokens`, and computed `jev.total_tokens = input_tokens + output_tokens` derived from `typesafe_sdk.Usage` in `typesafe_sdk/_core/response_types.py:59-67`, with `question_tokens` aliased to `output_tokens` on `JevUsage`)
- **AND** a counter metric `shb_jev_decisions_total` SHALL be incremented with tags for outcome and model
- **AND** `TelemetryStore.record_jev_decision(...)` in `shb-observability` (`src/shb_observability/collector.py`) SHALL record decision spans, token usage, and latency metrics alongside `OTelTraceSpan.attributes: dict[str, Any] = Field(default_factory=dict)` while keeping `TelemetryStore.record_span(trace_id, span_id, service, operation, duration)` backward-compatible

#### Scenario: Wire logging clamping and sensitive data sanitization
- **WHEN** decision evaluation executes or debug logging is active
- **THEN** because `typesafe_sdk._core.transport.RequestState._log_wire` logs unredacted `request.content` when the `"typesafe_sdk"` logger is at `DEBUG`, the runtime MUST clamp `logging.getLogger("typesafe_sdk")` to `>= logging.INFO`
- **AND** state projections (<32k tokens) MUST be sanitized via `sanitize_jev_state(state, max_tokens=32_000)` using `shb_core.security.crypto.mask_pan` and recursive secret-key redaction (`secret`, `token`, `password`, `key`, `supervisor_approval_token`, excluding `idempotency_key`) before creating evaluation states or emitting spans
### Requirement: HTTP/2 Transport Multiplexing

The client transport SHALL support HTTP/2 multiplexing via `typesafe-sdk[http2]>=0.7.2` to maintain persistent socket connections and eliminate per-request handshake overhead, passing explicit timeouts to prevent falling back to defaults and providing explicit lifecycle shutdown.

#### Scenario: HTTP/2 connection pooling
- **WHEN** the decision client initializes in an environment with `typesafe-sdk[http2]` installed
- **THEN** the client SHALL enable HTTP/2 transport multiplexing
- **AND** when `http2=True` and `transport is None`, the client MUST pass the resolved timeout to `httpx2.AsyncClient(http2=True, timeout=timeout)` / `httpx2.Client(http2=True, timeout=timeout)` so `httpx2` does not fall back to its internal 5.0s default timeout
- **AND** repeated decision calls SHALL reuse open sockets without renegotiating TLS handshakes

#### Scenario: Request body compression and gateway compatibility
- **WHEN** `JevDecisionClient` initializes `TypeSafeClient` or `AsyncTypeSafeClient`
- **THEN** it MUST resolve `effective_compression = False if (base_url or transport is not None) else settings.jev.compression`, store `effective_compression` on the client wrapper, and pass `compression=effective_compression` to `TypeSafeClient` / `AsyncTypeSafeClient` **only when `"compression" in inspect.signature(TypeSafeClient.__init__).parameters`** so both `typesafe-sdk==0.7.2` (which does not accept `compression=...`) and `typesafe-sdk>=0.7.5` (`compression: Literal["zstd", False] | None = None`) operate without `TypeError`
- **AND** when connecting directly to TypeSafe API over HTTP/2 on `typesafe-sdk>=0.7.5`, request bodies $\ge 1\text{ KiB}$ MAY use `zstd` compression, whereas proxy gateways (`base_url` set) or mock HTTP transports receive `effective_compression=False` to prevent `415 Unsupported Media Type` or `400 Bad Request` transport failures
#### Scenario: Explicit lifecycle management
- **WHEN** the decision client is closed or exits a context
- **THEN** the client MUST expose `close()` and `aclose()` methods and implement sync and async context managers (`__enter__`/`__exit__`, `__aenter__`/`__aexit__`) to cleanly shut down active connection pools and release resources
### Requirement: Native Pydantic Response Models

The client SHALL support structured validation using TypeSafe native response models subclassing `SystemOneResponse` or plain Pydantic `BaseModel` normalized by `JevDecisionClient`.

#### Scenario: Strongly typed response parsing
- **WHEN** a caller provides a typed `response_model` class to `system_one`
- **THEN** custom typed response schemas declaring top-level question fields MUST subclass `SystemOneResponse` so that `SystemOneResponse._decode()` lifts `decoded["answers"][field]` onto top-level model attributes and attaches `_request_id` and `raw_http_response`
- **AND** when a plain `pydantic.BaseModel` is passed as `response_model`, `JevDecisionClient` MUST normalize and lift `answers` onto the model fields rather than validating un-lifted wire JSON (`{"model": ..., "answers": {...}, "usage": ...}`)
- **AND** callers SHALL access answer fields directly as typed attributes without indexing raw dictionaries

### Requirement: Pydantic AI Gateway Compatibility

The configuration and client SHALL support proxying requests through Pydantic AI Gateway or enterprise proxies via `PYDANTIC_AI_GATEWAY_API_KEY` and base URL configuration, resolving credentials explicitly to accommodate SDK resolution behavior.

#### Scenario: Gateway proxy routing
- **WHEN** `PYDANTIC_AI_GATEWAY_API_KEY` or custom `TYPESAFE_BASE_URL` is set
- **THEN** because `typesafe_sdk._core.config.resolve_and_validate_api_key()` only checks the explicit `api_key` argument or `os.environ.get("TYPESAFE_API_KEY")`, `JevDecisionClient` MUST explicitly resolve `api_key = api_key or os.environ.get("TYPESAFE_API_KEY") or os.environ.get("PYDANTIC_AI_GATEWAY_API_KEY")` and pass `api_key` and `base_url=settings.jev.base_url or os.environ.get("TYPESAFE_BASE_URL") or None` into `TypeSafeClient` / `AsyncTypeSafeClient`
- **AND** the client SHALL resolve `effective_compression = False` and pass `compression=effective_compression` when `"compression" in inspect.signature(TypeSafeClient.__init__).parameters` unless the gateway endpoint explicitly supports `Content-Encoding: zstd`
- **AND** the client SHALL route decision requests through the configured gateway endpoint
- **AND** telemetry headers SHALL be passed transparently for unified fleet governance
### Requirement: Reusable Cross-Ecosystem Decision Contracts

The decision runtime in `shb-core` (`shb_core.decisions`) SHALL expose portable decision contracts (`DecisionContract`, `GuardrailPolicy`, `CitationCheckContract`) across all SHB packages and workspace organizations without duplicating client or circuit-breaker logic, while keeping `tdt/agent-core` strictly decoupled and frozen.

#### Scenario: Downstream banking and planning integration
- **WHEN** downstream packages such as `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, or `shb-mcp-servers` import decision abstractions from `shb_core.decisions` and `shb_core.jev`
- **THEN** the runtime SHALL expose reusable question definitions, risk classifiers (including `MCP_TOOL_AUTHORITY_MAP` mapping the 12 MCP tool names such as `banking_transfer_initiate`, `biller_pay`, `vietqr_parse`, and `compliance_sanction_screen` to `AuthorityClass`), and client interfaces
- **AND** in `shb-mcp-servers` (`src/shb_mcp/tools.py:176`), `execute_tool` SHALL apply `mask_pan` / `sanitize_jev_state` to guardrail evaluation state and audit metadata without mutating top-level tool response fields (`account_number`) expected by MCP callers
- **AND** callers SHALL execute custom domain gates such as transfer triage, maker-checker escalation, stage skipping, or skill candidate reranking

#### Scenario: Pre-flight diff triage and post-generation finding citation verification in shb-ai-review
- **WHEN** `shb-ai-review` evaluates merge request diffs via `src/shb_review/ai/reviewer.py` and `src/shb_review/validation/hunk_gate.py`
- **THEN** diffs MUST be sanitized with `redact_outbound_content` (populating `DiffHunkInfo.redacted_diff: str = ""` in `HunkGate.from_diff_entries()`) before Jev pre-flight hunk triage (`MR_DIFF_TRIAGE_CONTRACT`) to classify hunks as substantive vs formatting/trivial, skipping generative LLM invocation on trivial hunks while failing open to `_execute_provider` in `AiReviewer.review_diff()` when Jev is disabled or errors
- **AND** post-generation citation verification via `MR_FINDING_CITATION_CONTRACT` (`Noul` questions: `grounded_in_diff`, `contains_speculative_language`, `contradicts_diff`) MUST execute only on AI-generated findings (`finding.source.startswith("ai:")`) after deterministic line and range checks against `DiffHunkInfo.redacted_diff`
- **AND** AI findings where `grounded_in_diff < 0.70` or `contradicts_diff >= 0.50` or `contains_speculative_language >= 0.70` SHALL be demoted in `HunkGate` to `suppressed_findings` with reason `"jev_citation_ungrounded"`

#### Scenario: Stage deliverable evidence citation verification in shb-ai-harness-skills
- **WHEN** `verify_stage_deliverable_evidence()` in `src/shb_ai_harness/contracts.py` and `src/shb_ai_harness/cli.py:20` read `resources/harness-13/schema.yaml` via `schema.get("artifacts", [])` (replacing `schema.get("stages", {})` which silently returned `{}`)
- **THEN** `verify_stage_deliverable_evidence()` SHALL map 12-stage `StageName` aliases (`implementation_plan -> impl_plan`, `test_plan -> test_cases`, `verification -> verify`) to the 13-stage artifact schema and enforce deterministic artifact ID rules (`REQ`, `AC`, `EVD`, `DES`, `DEC`, `API`, `TASK`, `TC`, `ATP`, `VER`) in code
- **AND** it SHALL evaluate batched `CitationCheckContract` `Noul`s (`observed_claims_grounded_in_evd`, `upstream_requirements_traced`, `planning_only_boundary_preserved`) to verify that claims cite concrete evidence files before stage transitions
#### Scenario: Workspace cross-organization reusability without tdt coupling
- **WHEN** other workspace organizations utilize the decision runtime patterns established in `shb-core`
- **THEN** `DecisionContract`, `GuardrailPolicy`, and `CitationCheckContract` SHALL operate without depending on banking-specific schemas or any `tdt` packages
- **AND** `tdt/agent-core` SHALL remain completely frozen and unmodified as an explicit non-goal
