# jev-decision-runtime Specification

## Purpose
Provides sub-second, deterministic System One decision primitives — Noul yes/no probabilities, Choice routing, and ordinal Score — for the SHB Banking Ecosystem (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`) and Workspace Ecosystem Foundation, powering banking tool guardrails, AML screening triage, LangGraph harness branching, skill catalog reranking, and trace evaluation without generative token latency or output-token cost.

## Requirements

### Requirement: System One Decision Client

The banking runtime foundation SHALL provide a System One decision client (`shb_core.jev.JevDecisionClient`) with process-wide `get_jev_client()` / `reset_jev_client()` singleton helpers wrapping `TypeSafeClient` and `AsyncTypeSafeClient` (`evaluate` and `a_evaluate`) to evaluate `state` against typed `Noul`, `Choice`, and `Score` questions, guarded by a thread-safe `JevCircuitBreaker`.

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
- **AND** because `typesafe_sdk.Usage` (`typesafe_sdk/_core/response_types.py:59-67` and `typesafe_sdk/_schemas/models.py:130-137`, configured with `ConfigDict(extra="ignore", frozen=True, strict=True)`) defines only `input_tokens: int | None = None` and `output_tokens: int | None = None` (without `question_tokens` or `total_tokens`), `JevDecisionClient` MUST read `input_tokens = response.usage.input_tokens or 0` and `output_tokens = response.usage.output_tokens or 0` and surface normalized `JevUsage(input_tokens=input_tokens, output_tokens=output_tokens)` (defining `input_tokens: int = 0`, `output_tokens: int = 0`, and `@property def total_tokens(self) -> int: return self.input_tokens + self.output_tokens` without a duplicate `question_tokens` field) on the decision result, OTel span (`jev.input_tokens`, `jev.output_tokens`, `jev.total_tokens`), and `TelemetryStore.record_jev_decision` (with mock transport JSON bodies supplying `"usage": {"input_tokens": ..., "output_tokens": ...}`)
- **AND** because `SystemOneResponse.request_id` in `typesafe-sdk` (`typesafe_sdk/_core/schemas/base.py:67-73`) raises `TypeSafeError("The response did not include a request ID.")` when the `x-typesafe-request-id` response header is absent, `JevDecisionClient` MUST safely extract `request_id` (catching `TypeSafeError` or reading `raw_http_response.headers.get("x-typesafe-request-id")` with a `None` or empty string fallback when absent)
- **AND** SHALL NOT assume the answering model version, because an alias such as `jev-latest` moves between releases

#### Scenario: Circuit breaker protects downstream availability
- **WHEN** the client experiences consecutive transport errors or 5xx failures exceeding `circuit_breaker_threshold` (default 3) across repeated calls via the process-wide `get_jev_client() -> JevDecisionClient` singleton (cleared via `reset_jev_client()`, which is invoked automatically by `shb_core.config.reset_settings()` via a lazy import `from shb_core.jev import reset_jev_client`)
- **THEN** the thread-safe `JevCircuitBreaker` (protected by `threading.Lock` and `time.monotonic()`) MUST persist consecutive failure counts across tool calls (`initiate_fund_transfer`, `screen_beneficiary`) and LangGraph stage transitions (`_should_skip_api_contract`), transition to open state, and fast-fail subsequent evaluation requests during the `circuit_breaker_cooldown_seconds` (default 30.0s) window without making network calls
- **AND** the caller SHALL immediately execute its deterministic fallback or fail-closed path
### Requirement: Configuration Management for Jev System One

The foundation settings module (`shb_core.config`) SHALL expose `JevSettings` on `ShbSettings.jev` (`JEV_` and `SHB_JEV_` `AliasChoices`) loaded from `~/.shb/.env` and environment variables in isolation from `~/.tdt/`, strip API keys via `@model_validator(mode="before")`, lazily invoke `reset_jev_client()` in `reset_settings()`, and surface non-sensitive Jev diagnostics in `shb_core.cli`.

#### Scenario: Default configuration loading
- **WHEN** the banking runtime initializes without custom environment variables
- **THEN** `JevSettings` SHALL default to `enabled=False`, pinned `model="jev-1.13.0"` (with support for preview `jev-1.14.0`), `timeout_seconds=1.5`, `max_retries=2`, `http2=True`, `base_url=None`, `fail_closed=True`, `circuit_breaker_threshold=3`, `circuit_breaker_cooldown_seconds=30.0`, and `compression=None` (where `compression=False` is enforced when a custom gateway `base_url` or mock `transport` is configured)
- **AND** `shb_core.config.reset_settings()` (`src/shb_core/config.py:82`) SHALL invoke `reset_jev_client()` via a lazy import (`from shb_core.jev import reset_jev_client`) to avoid circular imports between `shb_core.config` and `shb_core.jev`
- **AND** `src/shb_core/cli.py` (`shb config-show` and `shb doctor`) SHALL report non-sensitive `SHB_JEV_ENABLED={settings.jev.enabled}` and `SHB_JEV_MODEL={settings.jev.model}` settings in `config_show()` and value-blind Jev readiness diagnostics (`settings.jev.enabled`, `settings.jev.model`, `settings.jev.http2`, `resolved_base_url`, credential provisioned boolean + length + 8-char SHA-256 prefix + `~/.zshenv` `0600` mode check via `_resolve_endpoint_and_api_key()`, `get_jev_client().circuit_breaker` state, and opt-in live ping when `SHB_RUN_LIVE_JEV_TESTS=1` or `--live-jev` is passed) in `doctor()` without ever printing raw secret values

#### Scenario: Environment variable override
- **WHEN** `JEV_ENABLED=true` or `SHB_JEV_ENABLED=true` and `JEV_TIMEOUT_SECONDS=1.0` are set in the execution environment
- **THEN** `JevSettings` SHALL reflect the overridden values with precedence over file-based configuration

#### Scenario: Secret isolation and workspace isolation
- **WHEN** `JevSettings` or `ShbSettings` is initialized with an input or config dictionary containing a top-level or nested `jev` `typesafe_api_key` or `pydantic_ai_gateway_api_key` key
- **THEN** a `@model_validator(mode="before")` (`_strip_jev_secrets`) on `JevSettings` and `ShbSettings` SHALL strip the secret field, emit a `UserWarning`, and require the credential through `TYPESAFE_API_KEY` (or `PYDANTIC_AI_GATEWAY_API_KEY`) or `~/.shb/.env` (without adding an unused `~/.shb/config.yaml` file loader to `shb_core/config.py`)
- **AND** configuration paths SHALL be strictly isolated to `~/.shb/.env` and process environment variables without reading `~/.tdt/.env` or `~/.tdt/config.yaml`
- **AND** the SDK's own environment variables (`TYPESAFE_API_KEY`, `TYPESAFE_BASE_URL`, `TYPESAFE_DEFAULT_MODEL`) SHALL remain authoritative for transport concerns

#### Scenario: Model identifier may be pinned
- **WHEN** decision thresholds have been calibrated against a specific release
- **THEN** the configuration SHALL allow pinning versioned model identifiers (`jev-1.13.0` stable or `jev-1.14.0` preview) instead of a moving alias
### Requirement: Credential and transport handling

The client SHALL resolve its endpoint (`resolved_base_url`) first via `_resolve_endpoint_and_api_key()`, select the matching credential (`TYPESAFE_API_KEY` in Direct Mode vs `PYDANTIC_AI_GATEWAY_API_KEY` before `TYPESAFE_API_KEY` in Gateway Mode), fail fast on an invalid or missing key, and bound every request with a timeout, circuit breaker, and retry policy.

#### Scenario: Missing credential
- **WHEN** no matching credential is resolved by `JevDecisionClient._resolve_endpoint_and_api_key()` after resolving `resolved_base_url = base_url or settings.jev.base_url or os.environ.get("TYPESAFE_BASE_URL") or "https://api.typesafe.ai"` first (normalizing trailing `"/"` and optional trailing `"/v1"` on `https://api.typesafe.ai` to `"https://api.typesafe.ai"`) — checking `api_key` arg -> `os.environ.get("TYPESAFE_API_KEY")` -> `~/.shb/.env` `TYPESAFE_API_KEY` -> `~/.zshenv` `TYPESAFE_API_KEY` in Direct Mode (`resolved_base_url == "https://api.typesafe.ai"`, never sending `PYDANTIC_AI_GATEWAY_API_KEY` to `https://api.typesafe.ai`), or `api_key` arg -> `os.environ.get("PYDANTIC_AI_GATEWAY_API_KEY")` -> `~/.shb/.env` `PYDANTIC_AI_GATEWAY_API_KEY` -> `~/.zshenv` `PYDANTIC_AI_GATEWAY_API_KEY` -> `TYPESAFE_API_KEY` fallback in Custom Proxy / Gateway Mode (`resolved_base_url != "https://api.typesafe.ai"`) — and Jev is enabled
- **THEN** the client SHALL report an explicit `TypeSafeError` configuration error rather than attempting a network request, and the caller's fallback path SHALL run without hanging
- **AND** when reading `~/.zshenv` (only when `allow_env_file_fallback=True` and `JEV_DISABLE_ENV_FILE_FALLBACK` is unset, while strictly refusing to read `~/.tdt/.env`), `_resolve_endpoint_and_api_key()` MUST verify `(zshenv_path.stat().st_mode & 0o022) == 0` (emitting a `UserWarning` and skipping `~/.zshenv` if group- or world-writable) and parse matching `export TYPESAFE_API_KEY=...` / `export PYDANTIC_AI_GATEWAY_API_KEY=...` lines via `shlex.split(line, comments=True)` (ignoring values containing unexpanded `$` shell expressions) so inline `# comments` or quotes never corrupt the parsed key
- **AND** hermetic unit tests testing missing-credential fail-closed paths SHALL pass `allow_env_file_fallback=False` (or set `JEV_DISABLE_ENV_FILE_FALLBACK=1` via `monkeypatch`) so they deterministically verify `TypeSafeError` even when `~/.zshenv` (mode `0600`) contains a live `TYPESAFE_API_KEY`, while `src/shb_core/cli.py` (`shb doctor` and `shb config-show`) reports non-sensitive `SHB_JEV_ENABLED` / `SHB_JEV_MODEL` settings and value-blind credential/circuit-breaker readiness (`_resolve_endpoint_and_api_key()`, `get_jev_client().circuit_breaker`, and opt-in live `https://api.typesafe.ai` verification under `SHB_RUN_LIVE_JEV_TESTS=1` or `--live-jev`) without ever printing or logging raw secret values

#### Scenario: Invalid credential fails before any request
- **WHEN** a malformed or empty credential is supplied, or an unauthorized credential is rejected by the service
- **THEN** a malformed or empty key SHALL raise `TypeSafeError` during client construction before any request, and an unauthorized key SHALL raise `TypeSafeAuthenticationError` on the first call without retries
- **AND** the runtime SHALL treat this as an authentication error and trigger the caller's fallback or fail-closed path

#### Scenario: Timeout and rate-limit handling
- **WHEN** a request exceeds its configured timeout (`timeout_seconds=1.5`), or the service returns a rate-limit (429) or overloaded status
- **THEN** the client SHALL abort or back off according to its retry policy (`max_retries=2`)
- **AND** SHALL NOT retry indefinitely within a banking tool authorization or workflow routing path

### Requirement: Pre-Flight Tool Guardrail

The banking agent tool registry (`shb-agent-core`) SHALL provide pre-flight semantic safety guardrails (`shb_agent.tools.guardrails.JevToolGuardrail`) evaluating atomic `Noul` conditions once per tool invocation on sanitized payloads, combining probabilities via `shb_core.decisions` weights, and applying `AuthorityClass` thresholds without bypassing human or maker-checker approvals.

#### Scenario: Atomic conditions are judged independently across tool registry
- **WHEN** the guardrail evaluates an invocation across all 10 registered tools in `src/shb_agent/tools/__init__.py` mapped to `TOOL_AUTHORITY_MAP`:
  - `READ_ONLY`: `get_account_balance`, `query_transaction_status`, `get_transaction_history`, `query_bill`
  - `OPERATIONAL`: `verify_beneficiary_account`, `generate_vietqr`, `parse_vietqr` (`src/shb_agent/tools/vietqr.py:135`, extracting EMVCo Tag 62 `purpose` content using exact 2-digit TLV length slicing with `rfind("6304")` fallback for Jev prompt-injection screening while preserving `is_valid_crc: True` for 4-hex-char CRCs such as `...6304ABCD` and exposing `crc_matches_computed: bool`)
  - `FINANCIAL_TRANSFER`: `initiate_fund_transfer` (inviolable `> 50,000,000 VND` maker-checker supervisor token + sub-50M VND structuring escalation) AND `pay_bill` (`src/shb_agent/tools/biller.py`: high-value biller debit & `amount != amount_due` anomaly escalation)
  - `COMPLIANCE_CRITICAL`: `screen_beneficiary` (deterministic `RESTRICTED_KEYWORDS` & `HIGH_RISK_ACCOUNTS` first, then Jev `Noul` for transliterated/diacritic-stripped Vietnamese and English PEP/OFAC/SBV sanction evasion)
- **THEN** it MUST ask one `Noul` per condition using structured `JSONContent` criteria dicts (`definition`, `includes`, `excludes`, `contrast_with`) and backticked JSON state paths (e.g., `` `transaction.narrative` ``, `` `beneficiary.name` ``) because question IDs are not sent to the model
- **AND** it MUST sanitize the payload via `sanitize_jev_state(state, max_tokens=32_000)` by masking primary account numbers (`mask_pan`) and recursively redacting sensitive credential keys (`secret`, `token`, `password`, `key`, `supervisor_approval_token`, excluding `_NON_SECRET_STRUCTURAL_KEYS` such as `idempotency_key` and `has_supervisor_token`) before transmitting bounded state (`<32k` tokens)
- **AND** it MUST combine the returned probabilities in code using `any_flag` (`max(p_k)`) and weighted composite scores from `shb_core.decisions` against empirically calibrated `AuthorityClass` (`escalate_threshold` / `block_threshold`) gates measured live on `jev-1.13.0` over HTTP/2 (`READ_ONLY`: `0.55` / `0.85`, `OPERATIONAL`: `0.45` / `0.75`, `FINANCIAL_TRANSFER`: `0.35` / `0.70`, `COMPLIANCE_CRITICAL`: `0.30` / `0.65`)
- **AND** `JevToolGuardrail` MUST execute **once** per tool invocation, strictly deduplicating via an exact `(clean_tool_name, canonical_args)` guard in `_make_dedup_key` (computing and preserving `has_supervisor_token = is_valid_supervisor_token(token)` in `sanitize_invocation_state` and `_make_dedup_key` before stripping `supervisor_approval_token`, and never falling back to tool-name-only matching across different arguments) so `@hooks.on.before_tool_execute` and direct tool functions (`initiate_fund_transfer`, `pay_bill`, `parse_vietqr`, `screen_beneficiary`) never invoke TypeSafe twice for identical calls while never conflating unapproved vs supervisor-approved retries

#### Scenario: Dynamic tool preparation via Speculative Fan-Out
- **WHEN** `ShbAgent` prepares tools for an execution turn via Pydantic AI 2.54.0 `PrepareTools(fn)` capability (`Agent(..., capabilities=[PrepareTools(fn)])`) for turn-level tool-schema filtering while `JevToolGuardrail` executes once per tool invocation (deduplicated across `@hooks.on.before_tool_execute` and `initiate_fund_transfer` / `pay_bill` / `parse_vietqr` / `screen_beneficiary` via a strict exact-key `(clean_tool_name, canonical_args)` guard)
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
- **AND** when `JevToolGuardrail` returns `GuardrailOutcome.BLOCK`, `initiate_fund_transfer` (`src/shb_agent/tools/banking.py:144`) MUST return `FundTransferInitiationResponse(status="REJECTED", requires_maker_checker=False, ...)` (and `pay_bill` MUST return `PayBillResponse(status="REJECTED", ...)`), and `AuditLoggingMiddleware.log_execution` (`src/shb_agent/tools/audit.py:84`) MUST map `result.get("status") in {"REJECTED", "FAILED", "BLOCKED"}` to `AuditEvent(status="FAILED")` (in addition to `PENDING_APPROVAL`) so a transfer or bill payment blocked by Jev is never logged as `status="SUCCESS"` in the PCI-DSS / SBV audit trail
- **AND** when a valid `supervisor_approval_token` (min 8 chars) is supplied, an `ESCALATE` outcome SHALL be satisfied and complete cleanly with `status="COMPLETED"`
#### Scenario: AML beneficiary screening triage
- **WHEN** `screen_beneficiary` executes compliance screening in `src/shb_agent/tools/compliance.py`
- **THEN** deterministic rules (`RESTRICTED_KEYWORDS` and `HIGH_RISK_ACCOUNTS`) SHALL remain strictly authoritative and execute first
- **AND** when Jev is enabled, semantic `Noul` checks SHALL evaluate transliterated, obfuscated, or leet-speak PEP/sanction narratives (calibrated live on `jev-1.13.0`: clean name `p = 0.040` vs obfuscated sanction aliases `p = 0.900–0.910`) and flag matches where `p >= 0.50` as `FLAGGED_FOR_MANUAL_REVIEW`
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
- **THEN** it MUST place shortlisted candidate metadata into `state={"query": query, "candidates": {slug: {"name": ..., "category": ..., "description": ..., "keywords": ...}}}` and ask one `Noul` per candidate whose `instructions` reference both backticked paths (`Does candidate skill \`candidates.<slug>\` directly solve the user task in \`query\`?`, empirically calibrated on `jev-1.13.0` at `p = 0.980` vs `0.020`, `49x` separation)
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
- **THEN** every question, criterion, weight, and threshold across guardrails, triage, routing, and skills SHALL be visible in a single module, using `typesafe_sdk`'s real classes (`typesafe_sdk._core.question_types`, `typesafe_sdk._core.response_types`) when installed and defining only the minimal optional-dependency fallback shims (`Noul`, `Choice`, `Score`, `NoulCriteria`, `SystemOneResponse`, `TypeSafeError`, `TypeSafeAuthenticationError`) once in `src/shb_core/jev.py` (imported by `src/shb_core/decisions.py`) when `typesafe-sdk` is not installed
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
- **THEN** an OpenTelemetry span named `shb.jev.decision` SHALL be emitted carrying the model identifier that answered, question identifiers, returned probabilities or confidences, outcome, observed latency, and normalized token attribution (`jev.input_tokens`, `jev.output_tokens`, and computed `@property total_tokens = input_tokens + output_tokens` on `JevUsage` derived from `typesafe_sdk.Usage` in `typesafe_sdk/_core/response_types.py:59-67`, without a duplicate `question_tokens` field)
- **AND** a counter metric `shb_jev_decisions_total` SHALL be incremented with tags for outcome and model
- **AND** `TelemetryStore.record_jev_decision(...)` in `shb-observability` (`src/shb_observability/collector.py`) SHALL record decision spans, token usage, and latency metrics alongside `OTelTraceSpan.attributes: dict[str, Any] = Field(default_factory=dict)` while keeping `TelemetryStore.record_span(trace_id, span_id, service, operation, duration)` backward-compatible

#### Scenario: Wire logging clamping and sensitive data sanitization
- **WHEN** decision evaluation executes or debug logging is active
- **THEN** because `typesafe_sdk._core.transport.RequestState._log_wire` logs unredacted `request.content` when the `"typesafe_sdk"` logger is at `DEBUG`, the runtime MUST clamp `logging.getLogger("typesafe_sdk")` to `>= logging.INFO`
- **AND** state projections (<32k tokens) MUST be sanitized via `sanitize_jev_state(state, max_tokens=32_000)` using `shb_core.security.crypto.mask_pan` and recursive secret-key redaction (`secret`, `token`, `password`, `key`, `supervisor_approval_token`, excluding `_NON_SECRET_STRUCTURAL_KEYS` such as `idempotency_key` and `has_supervisor_token`) before creating evaluation states or emitting spans
### Requirement: HTTP/2 Transport Multiplexing

The client transport SHALL support HTTP/2 multiplexing via `typesafe-sdk[http2]>=0.7.2` to maintain persistent socket connections and eliminate per-request handshake overhead, lazily creating sync and event-loop-aware async clients, passing explicit timeouts, and providing explicit lifecycle shutdown.

#### Scenario: HTTP/2 connection pooling
- **WHEN** the decision client initializes with `settings.jev.http2` enabled
- **THEN** when `transport is None`, the client MUST compute `use_http2 = bool(settings.jev.http2 and importlib.util.find_spec("h2") is not None)` before constructing `httpx2.Client(http2=use_http2, timeout=timeout)` / `httpx2.AsyncClient(http2=use_http2, timeout=timeout)` so environments with `h2` installed multiplex over HTTP/2 (`213ms–298ms` measured live on `jev-1.13.0`/`jev-1.14.0`) with the explicit timeout, while environments without `h2` fall back cleanly to HTTP/1.1 with `timeout=timeout` instead of raising `ImportError`
- **AND** repeated decision calls over HTTP/2 through the process-wide `get_jev_client()` singleton SHALL lazily create `TypeSafeClient` (`evaluate`) and `AsyncTypeSafeClient` (`a_evaluate`) to reuse open `httpx2.Client` / `httpx2.AsyncClient` socket pools without renegotiating TLS handshakes on each tool call or LangGraph stage transition, while recording `_async_loop_id = id(asyncio.get_running_loop())` and automatically recreating `AsyncTypeSafeClient` (`httpx2.AsyncClient`) whenever `id(asyncio.get_running_loop()) != self._async_loop_id` (preserving the shared `JevCircuitBreaker` state) so multiple `pytest` async test loops or repeated `asyncio.run()` calls never raise `RuntimeError: Event loop is closed`

#### Scenario: Request body compression and gateway compatibility
- **WHEN** `JevDecisionClient` initializes `TypeSafeClient` or `AsyncTypeSafeClient`
- **THEN** it MUST resolve `effective_compression = False if (base_url or transport is not None) else settings.jev.compression`, store `effective_compression` on the client wrapper, and pass `compression=effective_compression` to `TypeSafeClient` / `AsyncTypeSafeClient` **only when `"compression" in inspect.signature(TypeSafeClient.__init__).parameters`** so both `typesafe-sdk==0.7.2` (which does not accept `compression=...`) and `typesafe-sdk>=0.7.5` (`compression: Literal["zstd", False] | None = None`) operate without `TypeError`
- **AND** when connecting directly to TypeSafe API over HTTP/2 on `typesafe-sdk>=0.7.5`, request bodies $\ge 1\text{ KiB}$ MAY use `zstd` compression, whereas proxy gateways (`base_url` set) or mock HTTP transports receive `effective_compression=False` to prevent `415 Unsupported Media Type` or `400 Bad Request` transport failures
#### Scenario: Explicit lifecycle management
- **WHEN** the decision client is closed, exits a context, or switches asyncio event loops
- **THEN** the client MUST expose `close()` and `aclose()` methods and implement sync and async context managers (`__enter__`/`__exit__`, `__aenter__`/`__aexit__`) to cleanly shut down active `TypeSafeClient` / `AsyncTypeSafeClient` connection pools and release resources, while lazily recreating `AsyncTypeSafeClient` on event-loop changes (`id(asyncio.get_running_loop()) != self._async_loop_id`) without resetting `JevCircuitBreaker`
### Requirement: Native Pydantic Response Models

The client SHALL support structured validation using TypeSafe native response models subclassing `SystemOneResponse` or plain Pydantic `BaseModel` normalized by `JevDecisionClient`.

#### Scenario: Strongly typed response parsing
- **WHEN** a caller provides a typed `response_model` class to `system_one`
- **THEN** custom typed response schemas declaring top-level question fields MUST subclass `SystemOneResponse` so that `SystemOneResponse._decode()` lifts `decoded["answers"][field]` onto top-level model attributes and attaches `_request_id` and `raw_http_response`
- **AND** when a plain `pydantic.BaseModel` is passed as `response_model`, `JevDecisionClient` MUST normalize and lift `answers` onto the model fields rather than validating un-lifted wire JSON (`{"model": ..., "answers": {...}, "usage": ...}`)
- **AND** callers SHALL access answer fields directly as typed attributes without indexing raw dictionaries

### Requirement: Pydantic AI Gateway Compatibility

The configuration and client SHALL support proxying requests through custom enterprise proxies or gateways via explicit `base_url` (`settings.jev.base_url` or `TYPESAFE_BASE_URL`) and `PYDANTIC_AI_GATEWAY_API_KEY`, using `_resolve_endpoint_and_api_key()` to resolve the endpoint first so `TYPESAFE_API_KEY` in `~/.zshenv` never overrides a gateway key.

#### Scenario: Gateway proxy routing
- **WHEN** `PYDANTIC_AI_GATEWAY_API_KEY`, `TYPESAFE_API_KEY`, or custom `base_url` (`settings.jev.base_url` or `TYPESAFE_BASE_URL`) is configured (noting that `pydantic_ai/providers/gateway.py:105-112` only supports `openai`, `groq`, `anthropic`, `bedrock`, and `google`/`google-cloud` rather than a built-in `gateway/typesafe` route)
- **THEN** because `typesafe_sdk._core.config.resolve_and_validate_api_key()` only checks the explicit `api_key` argument or `os.environ.get("TYPESAFE_API_KEY")`, `JevDecisionClient._resolve_endpoint_and_api_key()` MUST resolve `resolved_base_url = base_url or settings.jev.base_url or os.environ.get("TYPESAFE_BASE_URL") or "https://api.typesafe.ai"` **first**, and then resolve only the matching credential: in Direct Mode (`resolved_base_url == "https://api.typesafe.ai"`), resolve `api_key` arg -> `os.environ.get("TYPESAFE_API_KEY")` -> `~/.shb/.env` `TYPESAFE_API_KEY` -> `~/.zshenv` `TYPESAFE_API_KEY` (never sending `PYDANTIC_AI_GATEWAY_API_KEY` to `https://api.typesafe.ai`); in Custom Proxy / Gateway Mode (`resolved_base_url != "https://api.typesafe.ai"`), resolve `api_key` arg -> `os.environ.get("PYDANTIC_AI_GATEWAY_API_KEY")` -> `~/.shb/.env` `PYDANTIC_AI_GATEWAY_API_KEY` -> `~/.zshenv` `PYDANTIC_AI_GATEWAY_API_KEY` -> `TYPESAFE_API_KEY` fallback (for self-hosted TypeSafe proxies), so that when both `~/.zshenv` `TYPESAFE_API_KEY` and `PYDANTIC_AI_GATEWAY_API_KEY` + custom gateway `base_url` are set, the gateway key is sent to the gateway rather than overridden by `TYPESAFE_API_KEY`, passing the resolved `api_key` and `base_url` into `TypeSafeClient` / `AsyncTypeSafeClient`
- **AND** when reading `~/.zshenv` (when `allow_env_file_fallback=True` and `JEV_DISABLE_ENV_FILE_FALLBACK` is unset, strictly refusing to read `~/.tdt/.env`), `_resolve_endpoint_and_api_key()` MUST verify `(zshenv_path.stat().st_mode & 0o022) == 0` (skipping `~/.zshenv` with a `UserWarning` if group- or world-writable) and parse `export` lines via `shlex.split(line, comments=True)` (ignoring values containing unexpanded `$` shell expressions)
- **AND** the client SHALL resolve `effective_compression = False` and pass `compression=effective_compression` when `"compression" in inspect.signature(TypeSafeClient.__init__).parameters` unless the gateway endpoint explicitly supports `Content-Encoding: zstd`
- **AND** the client SHALL route decision requests through the configured gateway endpoint
- **AND** telemetry headers SHALL be passed transparently for unified fleet governance
### Requirement: Reusable Cross-Ecosystem Decision Contracts

The decision runtime in `shb-core` (`shb_core.decisions`) SHALL expose portable decision contracts (`DecisionContract`, `GuardrailPolicy`, `CitationCheckContract`, `AuthorityClass`, `GuardrailOutcome`, `TOOL_AUTHORITY_MAP`, `MCP_TOOL_AUTHORITY_MAP`, `evaluate_guardrail_policy`) across all SHB packages without duplicating client logic, while keeping `tdt/agent-core` strictly decoupled and frozen.

#### Scenario: Downstream banking and planning integration
- **WHEN** downstream packages such as `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, or `shb-mcp-servers` import decision abstractions from `shb_core.decisions` and `shb_core.jev`
- **THEN** because `shb-mcp-servers/pyproject.toml` depends only on `shb-core` and `shb-jira-tools` (not `shb-agent-core`), `shb_core.decisions` SHALL define `AuthorityClass`, `GuardrailOutcome`, `GuardrailPolicy`, `TOOL_AUTHORITY_MAP`, `MCP_TOOL_AUTHORITY_MAP` (mapping the 12 MCP tool names such as `banking_transfer_initiate`, `biller_pay`, `vietqr_parse`, and `compliance_sanction_screen` to `AuthorityClass`), `is_valid_supervisor_token`, and the reusable `evaluate_guardrail_policy()` helper (re-exported by `shb_agent.tools.guardrails`) so both `shb-agent-core` (`JevToolGuardrail`) and `shb-mcp-servers` (`src/shb_mcp/tools.py:173` `execute_tool`) evaluate pre-flight guardrails without `shb-mcp-servers` importing `shb_agent`
- **AND** in `shb-mcp-servers` (`src/shb_mcp/tools.py:173-228`), `execute_tool` SHALL block non-transfer MCP tools with `{"status": "REJECTED", ...}` when `evaluate_guardrail_policy()` returns `GuardrailOutcome.BLOCK`, apply `mask_pan` / `sanitize_jev_state` to guardrail evaluation state and audit metadata without mutating top-level tool response fields (`account_number`) expected by MCP callers, and enforce `is_valid_supervisor_token(token)` (`not (token and len(str(token).strip()) >= 8)`) on `supervisor_approval_token` in `banking_transfer_initiate` (`src/shb_mcp/tools.py:213-214`, matching `shb-agent-core/src/shb_agent/tools/banking.py:307-309`) so 1-character or whitespace tokens cannot bypass the `50,000,000 VND` maker-checker gate over MCP
- **AND** callers SHALL execute custom domain gates such as transfer triage, maker-checker escalation, stage skipping, or skill candidate reranking

#### Scenario: Pre-flight diff triage and post-generation finding citation verification in shb-ai-review
- **WHEN** `shb-ai-review` evaluates merge request diffs via `src/shb_review/ai/reviewer.py` and `src/shb_review/validation/hunk_gate.py`
- **THEN** diffs MUST be sanitized with `redact_outbound_content` (populating `DiffHunkInfo.redacted_diff: str = ""` in `HunkGate.from_diff_entries()`) before Jev pre-flight hunk triage (`MR_DIFF_TRIAGE_CONTRACT`) in `AiReviewer.review_diff()` (`src/shb_review/ai/reviewer.py:389`), which MUST preserve its 2-tuple `(list[ReviewFinding], str)` return signature across all callsites (`cli.py:92`, `orchestrator.py:342,357,505`, `test_ai_reviewer.py`), reset and record skipped file paths in `self.last_skipped_files: set[str] = set()`, accept optional `preserve_files: set[str] | None = None` so files with active unresolved bot discussions in `existing_discussions` are never skipped, short-circuit returning `([], ...)` before `_execute_provider` when all diff entries are skipped, and fail open to `_execute_provider` when Jev is disabled or errors
- **AND** whenever `MR_DIFF_TRIAGE_CONTRACT` in `AiReviewer.review_diff()` skips a trivial/formatting-only diff entry, `AiReviewer.review_diff()` and `ReviewerOrchestrator` (`src/shb_review/orchestrator.py:342,357,505,524-525` and `src/shb_review/cli.py:203-205, 242-244`) MUST keep `is_partial=False` (unless a diff is genuinely binary, truncated, or overflowed) and pass `ai_skipped_files=ai_rev.last_skipped_files` to `ReviewDeduplicator.plan_review(..., ai_skipped_files: set[str] | None = None)` (`src/shb_review/validation/deduplicator.py:130, 180`) so open AI-authored threads (including `SHB-AI-*` and `AI-*` rule IDs) on `ai_skipped_files` are strictly distinguished from static compliance rules via `is_static_compliance_rule(rule_id)` and never auto-resolved, while fixed static compliance threads on those files still resolve normally and clean formatting/docs MRs still receive `ReviewVerdict.APPROVED` (`exit 0`)
- **AND** post-generation citation verification via `MR_FINDING_CITATION_CONTRACT` (`Noul` questions: `grounded_in_diff`, `contains_speculative_language`, `contradicts_diff`) MUST execute in `HunkGate.filter_findings()` (`src/shb_review/validation/hunk_gate.py:348`) only on AI-generated findings (`finding.source.startswith("ai:")`) after deterministic line and range checks against `DiffHunkInfo.redacted_diff`
- **AND** AI findings where `grounded_in_diff < 0.70` or `contradicts_diff >= 0.50` or `contains_speculative_language >= 0.70` MUST be dropped from both `accepted_findings` and `suppressed_findings` (incrementing `ungrounded_ai_filtered: int = 0` on `HunkGateResult` with `result.reasons[idx] = "jev_citation_ungrounded"`), and both `ReviewerOrchestrator.run_review()` (`src/shb_review/orchestrator.py:385`) and `ReviewerOrchestrator.review_gitlab_mr()` (`src/shb_review/orchestrator.py:522`) MUST check `FindingSeverity.BLOCKER` only across static findings plus `accepted_findings` so ungrounded AI findings never reject the MR or appear in `gitlab/posting.py:136` under `### Advisory Findings (Outside Modified Hunks)` while static integrity/compliance blockers outside hunks still reject the MR

#### Scenario: Stage deliverable evidence citation verification in shb-ai-harness-skills
- **WHEN** `verify_stage_deliverable_evidence()` in `src/shb_ai_harness/contracts.py` and `src/shb_ai_harness/cli.py:20` read `resources/harness-13/schema.yaml` via `schema.get("artifacts", [])` (replacing `schema.get("stages", {})` which silently returned `{}`)
- **THEN** `verify_stage_deliverable_evidence()` SHALL map 12-stage `StageName` aliases (`implementation_plan -> impl_plan`, `test_plan -> test_cases`, `verification -> verify`) to the 13-stage artifact schema and enforce deterministic artifact ID rules (`REQ`, `AC`, `EVD`, `DES`, `DEC`, `API`, `TASK`, `TC`, `ATP`, `VER`) in code
- **AND** it SHALL evaluate batched `CitationCheckContract` `Noul`s (`observed_claims_grounded_in_evd`, `upstream_requirements_traced`, `planning_only_boundary_preserved`) framed around consistency (`without contradicting them or inventing non-existent modules`, calibrated live on `jev-1.13.0` at `0.910–0.960` valid vs `0.020` invalid with threshold `p >= 0.70`) to verify that claims cite concrete evidence files before stage transitions
#### Scenario: Workspace cross-organization reusability without tdt coupling
- **WHEN** other workspace organizations utilize the decision runtime patterns established in `shb-core`
- **THEN** `DecisionContract`, `GuardrailPolicy`, and `CitationCheckContract` SHALL operate without depending on banking-specific schemas or any `tdt` packages
- **AND** `tdt/agent-core` SHALL remain completely frozen and unmodified as an explicit non-goal
