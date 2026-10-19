# Design: Jev Decision Runtime (SHB Banking Ecosystem & Workspace Foundation)

## Context

See `proposal.md` — Why.

The design establishes a high-performance, non-generative System One decision runtime centered in the **SHB Banking Ecosystem (`~/Developer/shb/*`)**, establishing a shared Foundation Hub in `shb-core` (`shb_core`) and serving all 7 consumer packages (`shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`), while serving as a portable architectural blueprint across other workspace organizations (`platform`, `vds`, `ascend`, `ghtk`, `fpt`). **`tdt/agent-core`, `tdt-core`, and `~/.tdt/` are explicitly frozen, out of scope, and untouched.**

The design is written against the **current** TypeSafe API, verified during implementation planning against `typesafe-sdk>=0.7.2` (including latest PyPI release `0.7.5` released Oct 14, 2026):

- **Primitive Semantics & Confidence Math (`docs.typesafe.ai/confidence.md`)**:
  - `Noul`: There is no boolean primitive; a yes/no judgment is a `Noul` returning a probability $p \in [0.0, 1.0]$. A `Noul` answer carries no separate confidence field because $p$ expresses both direction and certainty: normalized certainty is derived as $|2p - 1|$. A probability near $0.5$ signifies model uncertainty between yes and no, NOT a medium intensity.
  - `Choice`: `Choice(criteria=Mapping[str, JSONContent | None])` supports categorical selection over distinct options. The SDK permits `None` as a criterion value for self-explanatory keys or pre-parsed candidate spans (`typesafe_sdk/_core/question_types.py`). `ChoiceAnswer.confidence` measures categorical probability distribution concentration.
  - `Score`: `Score(criteria=Sequence[JSONContent])` evaluates state against $N$ ordered levels ($0 \dots N-1$, `min_length=2`), returning expected value $\sum_{i=0}^{N-1} i \cdot P(i) \in [0.0, N-1]$ (`ScoreAnswer.score`, `confidence`, `probabilities`, `legend`).
- **Rich `JSONContent` Criteria & Backticked JSON State Paths**:
  Question IDs are strictly local identifiers for caller code and are never sent over the wire to the model (`docs.typesafe.ai/primitives.md`). Questions in `shb_core/decisions.py` MUST carry complete semantic meaning in `instructions` and `criteria`, using structured `JSONContent` dictionaries (`{"definition": ..., "includes": [...], "excludes": [...], "contrast_with": ...}`) for nuanced domain boundaries. Criteria reference nested fields in `state` via backticked JSON paths (e.g., `` `transaction.narrative` ``, `` `beneficiary.name` ``, `` `ticket.stage_results.spec.summary` ``) per TypeSafe state binding rules (`docs.typesafe.ai/concepts/state.md`).
- **The Official SDK (`typesafe-sdk>=0.7.2`, `0.7.5`) & Optional-Dependency Fallback Shims**:
  `TypeSafeClient` / `AsyncTypeSafeClient` exposes `client.system_one(state, questions, ...)`. Answers are accessed via typed accessors (`response.nouls`, `.choices`, `.scores`), the `answers` dictionary, or a typed `response_model`. Because each SHB repository maintains an isolated `.venv` and must also operate cleanly when `typesafe-sdk` is not installed, `shb_core/jev.py` and `shb_core/decisions.py` define lightweight Pydantic/TypedDict fallback shims (`Noul`, `Choice`, `Score`, `NoulCriteria`, `NoulAnswer`, `ChoiceAnswer`, `ScoreAnswer`, `Usage`, `SystemOneResponse`, `TypeSafeError`, `TypeSafeAuthenticationError`) when `typesafe_sdk` is absent, while importing and using `typesafe_sdk`'s real classes when installed.
- **Usage Token Attribution (`response.usage` -> `JevUsage`)**:
  In both `typesafe-sdk==0.7.2` and `0.7.5` (`typesafe_sdk/_core/response_types.py:59-67` and `typesafe_sdk/_schemas/models.py:130-137`, re-exported as `typesafe_sdk.Usage`), `Usage` defines **only** `input_tokens: int | None = None` and `output_tokens: int | None = None` with `ConfigDict(extra="ignore", frozen=True, strict=True)` (it does not define `question_tokens` or `total_tokens` attributes, and `typesafe_sdk/response_types.py` does not exist). State `input_tokens` are billed once per batched request and `output_tokens` represent the billed question tokens summed across questions. `JevDecisionClient` reads `input_tokens = response.usage.input_tokens or 0` and `output_tokens = response.usage.output_tokens if response.usage.output_tokens is not None else (getattr(response.usage, "question_tokens", 0) or 0)` from `typesafe_sdk.Usage`, and surfaces normalized `JevUsage(input_tokens=input_tokens, output_tokens=output_tokens, question_tokens=output_tokens, total_tokens=input_tokens + output_tokens)` on the client's evaluation result, OTel spans (`shb.jev.decision` with `jev.input_tokens`, `jev.output_tokens`, `jev.total_tokens`), and `TelemetryStore`. Mock transport JSON bodies MUST include `"usage": {"input_tokens": ..., "output_tokens": ...}`.
- **Request Body Compression & Version-Aware Inspection Guard (`0.7.2` vs `0.7.5`)**:
  In `typesafe-sdk>=0.7.5`, request body compression using `zstd` is enabled by default for request bodies $\ge 1\text{ KiB}$ (`compression: Literal["zstd", False] | None = None`), whereas cached `typesafe-sdk==0.7.2` (`typesafe_sdk/_core/client/sync/client.py:21-33`) does not accept a `compression` keyword argument (`TypeError` if passed unconditionally). Furthermore, non-official proxy gateways (such as Pydantic AI Gateway proxies via `PYDANTIC_AI_GATEWAY_API_KEY` / custom `base_url`) and mock `httpx2` transports may not support or decompress `Content-Encoding: zstd`. Therefore, `JevSettings` exposes `compression: Literal["zstd", False] | None = None`, and `JevDecisionClient` resolves `effective_compression = False if (base_url or transport is not None) else settings.jev.compression`, stores it on the wrapper (`self.compression = effective_compression`), and passes `compression=effective_compression` to `TypeSafeClient` / `AsyncTypeSafeClient` **only when `"compression" in inspect.signature(TypeSafeClient.__init__).parameters`**.
- **Safe `request_id` Extraction**:
  In `typesafe-sdk` 0.7.2 (`typesafe_sdk/_core/schemas/base.py:67-73`), `SystemOneResponse.request_id` raises `TypeSafeError("The response did not include a request ID.")` when the `x-typesafe-request-id` HTTP response header is absent. `JevDecisionClient` MUST safely extract `request_id` (catching `TypeSafeError` or reading `raw_http_response.headers.get("x-typesafe-request-id")` with a `None`/`""` fallback when absent).
- **Native Pydantic `response_model` Decoding**:
  `SystemOneResponse._decode()` lifts `decoded["answers"][field]` onto top-level model attributes, whereas a plain `pydantic.BaseModel` validates raw wire JSON (`{"model": ..., "answers": {...}, "usage": ...}`) without lifting answer fields. Custom typed schemas declaring top-level question fields MUST subclass `SystemOneResponse`, or `JevDecisionClient` normalizes/lifts `answers` when a plain `BaseModel` is supplied.
- **Parallel Question Fan-Out**:
  Every question in a request sees the same `state` and is evaluated in parallel and in isolation. Asking several questions in one request barely changes latency — the documented fan-out benchmark is 13 batched questions at roughly 11.5x lower cost and 9.6x lower latency than 13 separate calls (`patterns/fan-out.md`).
- **Request Budget**:
  64k tokens (state plus all questions), or 32k for state plus the longest question. Text only; English is the primary language, with evaluated support for transliterated and accented Vietnamese banking narratives.
- **Model Versioning**:
  Model `jev-1.13.0` is the default pinned version, with evaluated forward compatibility for `jev-1.14.0` (preview in `typesafe-sdk>=0.7.5`).
- **Wire Logging Security**:
  In `typesafe_sdk._core.transport.RequestState._log_wire`, `request.content` is logged unredacted when `logging.getLogger("typesafe_sdk")` is at `DEBUG`. The runtime MUST clamp `logging.getLogger("typesafe_sdk")` to `>= logging.INFO` and sanitize state projections before dispatch.
- **Pydantic AI & Pydantic Evals Framework Integration (`pydantic-ai==2.54.0`, `pydantic-evals==2.54.0`)**:
  `pydantic-ai==2.54.0` and `pydantic-evals==2.54.0` are installed in the SHB virtual environments (`shb-agent-core/.venv`, `shb-agent-harness/.venv`). `pydantic-ai 2.54.0` natively provides `TypeSafeModel` / `SystemOneModel` (`pydantic_ai.models.typesafe`, `pydantic_ai.models.decision.DecisionModel`, `DecisionHandOff` for `FallbackModel(TypeSafeModel(...), primary_llm, fallback_on=DecisionHandOff)` SDE cascades) and middleware capabilities (`Hooks` with `@hooks.on.before_tool_execute` / `after_tool_validate`, `PrepareTools(prepare_func)`, `ApprovalRequiredToolset`, `OnlineEvaluation`). Agent-wide tool filtering is wired via `Agent(..., capabilities=[PrepareTools(fn)])` or per-tool `@agent.tool(prepare=fn, args_validator=...)`.

### Existing SHB Ecosystem Patterns Referenced

The design directly grounds in and extends established patterns from the SHB banking codebase:

1. **Configuration & Secret Isolation (`shb_core.config.ShbSettings`)**:
   `JevSettings(BaseSettings)` is attached as `jev: JevSettings` on `ShbSettings` (`get_settings().jev`). It loads environment variables exclusively from `~/.shb/.env` and process environment with `JEV_` and `SHB_JEV_` aliases, and optional `~/.shb/config.yaml`. Any raw API keys placed in YAML configuration are stripped with a `UserWarning`. It remains strictly isolated from other organizations (e.g., `~/.tdt/`).
2. **Data Masking & PCI-DSS Compliance (`shb_core.security.crypto.mask_pan`)**:
   Account numbers and Primary Account Numbers (PANs) are masked per PCI-DSS and State Bank of Vietnam (SBV) regulations (preserving first 4 and last 2 characters).
3. **Payload Sanitization & Bounded State Projection (`shb_core.jev.sanitize_jev_state`, `shb_agent.tools.audit.sanitize_payload`, `AuditLoggingMiddleware`)**:
   `shb_core.jev` provides `sanitize_jev_state(state: Any, *, max_tokens: int = 32_000) -> Any` combining `shb_core.security.crypto.mask_pan` and recursive secret-key redaction (`secret`, `token`, `password`, `key`, `supervisor_approval_token`, excluding `idempotency_key`) to ensure all outbound state projections sent to external models are redacted and bounded (<32k tokens).
4. **Banking Tool Catalog, Name Prefix Normalization & Authority Classes (`shb_agent.tools`, 10 registered tools)**:
   All 10 tools registered in `src/shb_agent/tools/__init__.py` map to distinct `AuthorityClass` tiers in `shb_core.decisions.TOOL_AUTHORITY_MAP` (with `PrepareTools` and `Hooks` normalizing the 3 `tool_`-prefixed registrations in `src/shb_agent/agent.py:86-152` via `tool_name.removeprefix("tool_")`):
   - `READ_ONLY`: `get_account_balance`, `query_transaction_status`, `get_transaction_history`, `query_bill`
   - `OPERATIONAL`: `verify_beneficiary_account`, `generate_vietqr`, `parse_vietqr` (`src/shb_agent/tools/vietqr.py:135`: extracts EMVCo Tag 62 `purpose` content when present for indirect prompt-injection screening while preserving `is_valid_crc: True` for 4-hex-char CRCs and exposing `crc_matches_computed: bool`)
   - `FINANCIAL_TRANSFER`: `initiate_fund_transfer` (inviolable `> 50,000,000 VND` maker-checker supervisor token + sub-50M structuring escalation; a valid `supervisor_approval_token` with `len >= 8` satisfies an `ESCALATE` outcome and returns `status="COMPLETED"`) AND `pay_bill` (`src/shb_agent/tools/biller.py`: high-value biller debit & `amount != amount_due` anomaly escalation)
   - `COMPLIANCE_CRITICAL`: `screen_beneficiary` (deterministic `RESTRICTED_KEYWORDS` & `HIGH_RISK_ACCOUNTS` first, then Jev `Noul` for transliterated/diacritic-stripped Vietnamese & English PEP/OFAC/SBV sanction evasion)
5. **Deterministic AML Screening Baseline (`shb_agent.tools.compliance.screen_beneficiary`)**:
   Deterministic regex and watchlist rules (`RESTRICTED_KEYWORDS`, `HIGH_RISK_ACCOUNTS`) remain authoritative for SBV, OFAC, and PEP registries before semantic escalation.
6. **LangGraph StateGraph, Checkpointing & Dual Sync/Async Routing (`shb_harness.workflow.build_harness_graph`, `SqliteSaver`, `RunnableCallable`)**:
   12-stage planning DAG using `HarnessState`. Runtime invariant: `langgraph/_internal/_runnable.py:424-436` requires wrapping sync `_should_skip_api_contract` and async `a_should_skip_api_contract` in LangGraph's `RunnableCallable(_should_skip_api_contract, a_should_skip_api_contract)` to support both synchronous `graph.invoke()` (`HarnessRunner.run_all()`) and `await graph.ainvoke()` without raising `TypeError`. Persistent checkpointing uses `SqliteSaver` at `~/.shb/harness.db`.
7. **Stage Deliverable Evidence & Citation Verification (`shb_ai_harness.contracts.verify_stage_deliverable_evidence`)**:
   In `shb-ai-harness-skills` (`src/shb_ai_harness/contracts.py`, `resources/harness-13/schema.yaml`), deterministic ID prefix checks (`REQ`, `AC`, `EVD`, `DES`, `DEC`, `API`, `TASK`, `TC`, `ATP`, `VER`) combined with Jev `citation_check` `Noul`s (`observed_claims_grounded_in_evd`, `upstream_requirements_traced`, `planning_only_boundary_preserved`) and a 12-to-13 stage alias map (`implementation_plan -> impl_plan`, `test_plan -> test_cases`, `verification -> verify`) verify stage deliverable artifacts (`schema.get("artifacts", [])`, fixing `src/shb_ai_harness/cli.py:20` where `schema.get("stages", {})` silently returned `{}`).
8. **Skills Catalog & Two-Stage SkillMatcher (`shb_skills.registry.SkillsCatalog`, `shb_skills.matcher.SkillMatcher`)**:
   Loads 38+ engineering skills from `registry.yaml` and creates `src/shb_skills/matcher.py` (`SkillMatcher`, re-exported in `src/shb_skills/__init__.py`) for Stage 1 deterministic lexical/category shortlist retrieval (`match()`) + Stage 2 batched `Noul` reranking (`match_jev()` / `a_match_jev()`).
9. **Telemetry & Metrics Store (`shb_observability.collector.TelemetryStore`)**:
   Extends `OTelTraceSpan` with backward-compatible `attributes: dict[str, Any] = Field(default_factory=dict)` and adds `TelemetryStore.record_jev_decision(...)` to record execution metrics (`shb_agent_tool_calls_total`, `shb_jev_decisions_total`) and distributed trace spans (`shb.jev.decision`) with normalized `JevUsage` token attribution (`jev.input_tokens`, `jev.output_tokens`, `jev.total_tokens`).
10. **Outbound Content Redaction, Diff Triage & Finding Citation (`shb_review.validation.hunk_gate.HunkGate`, `shb_review.ai.reviewer.redact_outbound_content`)**:
    Adds `redacted_diff: str = ""` to `DiffHunkInfo` (populated via `redact_outbound_content` in `HunkGate.from_diff_entries()`) to run Pre-Flight Diff Hunk Triage (`MR_DIFF_TRIAGE_CONTRACT`) and Post-Generation Finding Citation Verification (`MR_FINDING_CITATION_CONTRACT` with atomic `Noul`s `grounded_in_diff`, `contains_speculative_language`, `contradicts_diff`, demoting ungrounded AI review findings where `finding.source.startswith("ai:")` to `suppressed_findings` with reason `"jev_citation_ungrounded"`).
11. **MCP Tool Execution Guardrails & Masking (`shb_mcp.tools.execute_tool`)**:
    In `shb-mcp-servers` (`src/shb_mcp/tools.py:176`), `MCP_TOOL_AUTHORITY_MAP` maps all 12 MCP tools to `AuthorityClass` tiers, and `execute_tool` applies `mask_pan` / `sanitize_jev_state` to guardrail state and audit metadata while preserving top-level return payload fields (`account_number`).
### Boundaries: Transaction, Idempotency, Maker-Checker, Checkpoints & Citations

- **Transaction Boundary**: The Jev runtime is purely computational and advisory. It operates strictly outside database transaction locks and never commits or aborts database transactions. Database transactions for banking operations are managed within individual tool handlers.
- **Idempotency Boundary (`IdempotencyManager`)**: Banking mutations and tool calls maintain idempotency through `IdempotencyManager` (`shb_core.idempotency`) using `idempotency_key`. Jev evaluations do not alter idempotency records; cached evaluations reuse the invocation state.
- **Maker-Checker Boundary**: Transfers `> 50,000,000 VND` (`MAKER_CHECKER_THRESHOLD_VND`) unconditionally require supervisor approval token verification. Jev CANNOT approve or bypass this gate. Sub-threshold transfers (`<= 50,000,000 VND`) evaluated by Jev for suspicious patterns (structuring, split-transfers, evasive narratives) escalate to require supervisor approval (`ModelRetry` / `PENDING_APPROVAL`) or block execution.
- **Checkpoint Boundary (`SqliteSaver`)**: LangGraph workflow executions in `shb-agent-harness` persist checkpoints to `~/.shb/harness.db`. Jev routing decisions are evaluated at stage transitions and persisted within `HarnessState.stage_results`. Human approval gates (`interrupt()` at `StageName.PLAN_REVIEW`) remain inviolable.
- **Deliverable Citation Boundary (`verify_stage_deliverable_evidence`)**: In `shb-ai-harness-skills` and `shb-ai-review`, Jev citation checks verify that generated conclusions, findings, or planning artifacts are grounded in provided evidence (`EVD`, diff hunks). Jev cannot fabricate citations; lack of verifiable evidence results in ungrounded flags or demotion.

### Architecture Diagram

```
+===================================================================================================================+
|                                            WORKSPACE ECOSYSTEM BLUEPRINT                                          |
|      (Portable Foundation Contracts: DecisionContract, GuardrailPolicy, CitationCheckContract, JevDecisionClient) |
|      Available to: platform/ | vds/ | ascend/ | ghtk/ | fpt/ | wiki/ | (tdt/ explicitly frozen & untouched)        |
+===================================================================================================================+
                                                           |
                                                           v
+===================================================================================================================+
| LAYER 1: SHARED ECOSYSTEM FOUNDATION HUB (shb/shb-core -> package shb_core)                                       |
|                                                                                                                   |
|   +---------------------------------------+       +-----------------------------------------------------------+   |
|   | JevSettings (shb_core.config)         |       | JevDecisionClient (shb_core.jev)                          |   |
|   | - JEV_ / SHB_JEV_ env aliases         |       | - TypeSafeClient / AsyncTypeSafeClient (>=0.7.2 / 0.7.5)  |   |
|   | - Loaded from ~/.shb/.env             | ----> | - Safe request_id extraction (header fallback probe)      |   |
|   | - Secret-stripping with warning       |       | - typesafe-sdk[http2] multiplexing (httpx2)               |   |
|   | - fail_closed=True, timeout=1.5s      |       | - Request compression toggle: zstd (default False proxy)  |   |
|   | - Pinned models: jev-1.13.0 / 1.14.0  |       | - Usage token attribution (input_tokens billed once)      |   |
|   | - Circuit breaker: 3 err / 30s cool   |       | - Clamp typesafe_sdk log >= INFO                          |   |
|   +---------------------------------------+       +-----------------------------------------------------------+   |
|                                                           |                                                       |
|                                                           v                                                       |
|   +-----------------------------------------------------------------------------------------------------------+   |
|   | Centralized Policy & Decisions (shb_core.decisions)                                                       |   |
|   | - Rich JSONContent Criteria (definition, includes, excludes, contrast_with) & Backticked JSON State Paths |   |
|   | - Code-owned Weights, 0-indexed Score Math, & Risk-scaled Confidence Thresholds                           |   |
|   | - Portable Contracts: DecisionContract, GuardrailPolicy, CitationCheckContract, AuthorityClass            |   |
|   | - 6 Cookbook Patterns: Fan-Out, Composite Scoring, Citation Check, SDE Cascade, Pre-Parsed Extraction,   |   |
|   |   and Two-Stage Reranking                                                                                 |   |
|   +-----------------------------------------------------------------------------------------------------------+   |
+===================================================================================================================+
          |                                         |                                         |
          v                                         v                                         v
+===================================+ +===================================+ +=======================================+
| LAYER 2: BANKING AGENT            | | LAYER 3: 12-STAGE HARNESS         | | LAYER 4: SKILLS, OBS, REVIEW & MCP   |
| (shb/shb-agent-core)              | | (shb-agent-harness & skills)      | | (shb-skills, obs, review, mcp)      |
|                                   | |                                   | |                                       |
| - 10 Tools across 4 AuthorityTiers| | - WorkflowEngine:                 | | - SkillMatcher (shb_skills):          |
|   READ_ONLY (4), OPERATIONAL (3), | |   Dual Sync/Async conditional     | |   Stage 1: Lexical shortlist (top-K)  |
|   TRANSFER (2), COMPLIANCE (1)    | |   routing using LangGraph         | |   Stage 2: Batched Noul rerank        |
| - JevToolGuardrail:               | |   RunnableCallable wrapper        | |                                       |
|   Atomic Noul checks              | | - _should_skip_api_contract &     | | - TelemetryStore (shb_observability): |
|   sanitize_payload + mask_pan     | |   a_should_skip_api_contract      | |   shb.jev.decision OTel spans         |
| - Pydantic AI 2.54.0 Integration: | |   SPEC -> DESIGN skip evaluation  | |   Usage token attribution metrics     |
|   PrepareTools dynamic filtering  | | - verify_stage_deliverable_       | |                                       |
|   (omits debit tools on read-only)| |   evidence (shb-ai-harness-skills)| | - HunkGate (shb-ai-review):           |
|   TypeSafeModel / DecisionHandOff | |   Validates EVD/REQ/AC citations  | |   MR_DIFF_TRIAGE_CONTRACT (pre-flight)|
| - Banking Invariants:             | | - Preserves interrupt() gate      | |   MR_FINDING_CITATION_CONTRACT (post) |
|   >50M VND Maker-Checker NEVER    | | - Checkpoint:                     | |                                       |
|   bypassed + structuring triage   | |   SqliteSaver at                  | | - shb_mcp.tools (shb-mcp-servers):    |
| - AML screen_beneficiary (PEP/SBV)| |   ~/.shb/harness.db               | |   Execution guardrail & mask_pan      |
| - JevEvaluator: pydantic-evals    | |                                   | |                                       |
+===================================+ +===================================+ +=======================================+
```

## Goals / Non-Goals

### Goals

- Deliver a centralized, high-performance, typed System One decision runtime in `shb-core` (`shb_core.jev`, `shb_core.decisions`, `shb_core.config.JevSettings`) with zero output-token cost, single-state token billing, and sub-200ms latency.
- Equip `shb-agent-core` with semantic pre-flight guardrails for all 10 banking tools across 4 authority tiers, dynamic tool preparation omitting debit tools on read-only turns, AML screening triage, and evaluation scoring while strictly preserving banking maker-checker enforcement.
- Enable confidence-gated conditional edge routing in `shb-agent-harness` across 12 LangGraph stages for both sync (`run_all` via `graph.invoke`) and async (`await graph.ainvoke`) execution via LangGraph's `RunnableCallable`.
- Create `SkillMatcher` in `shb-agent-skills` (`src/shb_skills/matcher.py`, re-exported in `src/shb_skills/__init__.py`) using two-stage lexical shortlist + batched Jev `Noul` reranking over 38+ engineering skills.
- Deliver automated deliverable evidence and citation verification in `shb-ai-harness-skills` across 13 stages and diff triage & finding citation verification in `shb-ai-review`.
- Capture decision spans and metrics with normalized `JevUsage` token attribution (`input_tokens`, `output_tokens`, `question_tokens`, `total_tokens`) in `shb-observability` via OpenTelemetry (`OTelTraceSpan.attributes` and `TelemetryStore.record_jev_decision`).
- Provide a clean, portable foundation contract blueprint in `shb_core.decisions` (`DecisionContract`, `GuardrailPolicy`, `CitationCheckContract`) for sister workspace organizations (`platform`, `vds`, `ascend`, `ghtk`, `fpt`, `wiki`).

### Non-Goals

- **`tdt/agent-core` is explicitly frozen and out of scope**: NO changes to `~/Developer/tdt/agent-core`, `tdt-core`, or `~/.tdt/`.
- Bypassing banking maker-checker approvals: Jev NEVER bypasses `MAKER_CHECKER_THRESHOLD_VND` (> 50,000,000 VND) or supervisor token verification.
- Calibrating real-world confidence thresholds against production traffic (thresholds and weights are centralized in code; baseline defaults are conservative and disabled by default).
- Free-form text generation, chat streaming, or explainability prose (System One is non-generative).
- Direct database transactions inside Jev runtime (transactionality and idempotency remain strictly within `IdempotencyManager` and banking service boundaries).

## Decisions

### D1: Use the official SDK rather than direct HTTP

The client wraps `typesafe-sdk` in `shb_core.jev.JevDecisionClient` (`evaluate` and `a_evaluate`) instead of posting to `/v1/systemone` directly. The SDK supplies typed questions and answers, retry-with-backoff honouring rate-limit signalling, and error objects carrying status and request id. The client wrapper encapsulates safe `request_id` extraction, catching `TypeSafeError("The response did not include a request ID.")` or safely probing `raw_http_response.headers.get("x-typesafe-request-id")` with a `None`/`""` fallback when headers are stripped by intermediaries or omitted by mock transports.

**Alternative considered:** direct HTTP. Rejected — it would reimplement retry, error mapping, and typing, and would drift from the published contract.

### D2: Model a yes/no judgment as a `Noul`, never a boolean

There is no boolean primitive in Jev. A `Noul` returns a probability $p \in [0.0, 1.0]$, which means the caller receives answer and certainty together ($|2p - 1|$) and can choose its own threshold. A boolean-shaped wrapper around a `Noul` would discard exactly the information the banking guardrail needs.

**Alternative considered:** coerce `Noul` to `bool` at the client boundary. Rejected — it forces a threshold inside the client, hiding a policy decision that belongs to the caller.

### D3: One atomic question per condition; combine in code using structured `JSONContent` criteria and Composite Scoring

In `shb_agent.tools.guardrails`, each destructive or suspicious condition is its own atomic `Noul` (`is_destructive_operation`, `exceeds_local_scope`, `is_unauthorized_beneficiary`, `matches_structuring_pattern`), and the code combines probabilities with weights defined in `shb_core.decisions`.

Crucially, questions use structured `JSONContent` criteria dictionaries (`{"definition": ..., "includes": [...], "excludes": [...], "contrast_with": ...}`) and backticked JSON state paths (e.g., `` `transaction.narrative` ``) per official primitives guidance (`docs.typesafe.ai/primitives.md`, `docs.typesafe.ai/concepts/state.md`). Question IDs are caller-only and never sent over the wire, so instructions and criteria must be fully self-contained.

Following the official **Composite Scoring pattern (`patterns/composite-scoring.md`)**, the runtime evaluates independent `Score` (normalized as $\text{score}/(N-1)$) and hard-veto `Noul` dimensions in a single batched request and combines them in Python. This cleanly decouples judgment extraction from business weighting and allows tuning thresholds and weights without re-running inference or re-evaluating tokens.

**Alternative considered:** one composite question ("Is this action safe to execute?"). Rejected — composite questions produce uncalibrated probabilities, obscure individual risk factors, and cannot be mapped to granular security policies.
### D4: Guardrail outcomes are risk-scaled and escalate before blocking

Outcomes are `PROCEED`, `ESCALATE`, and `BLOCK`. An operation is escalated to human supervisor review (`ModelRetry` / `PENDING_APPROVAL`) if any condition falls into the uncertain band, and blocked only when risk is clear. The threshold depends on the tool's `AuthorityClass` (`READ_ONLY`, `OPERATIONAL`, `FINANCIAL_TRANSFER`, `COMPLIANCE_CRITICAL`). Financial and compliance tools have the narrowest proceed bands.

**Alternative considered:** treat any nonzero risk as blocking. Rejected — it would make the banking guardrail unusable and push operators to disable it.

### D5: Reranking scores each candidate independently

We create `src/shb_skills/matcher.py` defining `SkillMatcher` over `SkillsCatalog` (populated from `load_skills_registry()`, and re-exported in `src/shb_skills/__init__.py`). Stage 1 (`match(query, *, category=None, top_k=5)`) performs deterministic lexical/category shortlist retrieval to select candidate skills. Stage 2 (`match_jev` / `a_match_jev`) asks one `Noul` per query-candidate pair in one batched request and orders by returned probability. Independent pair scoring ensures scores are comparable across queries; a single choice across candidates makes them compete inside one question and loses ordering signal.

**Alternative considered:** one `Choice` over the candidate list. Rejected — it yields a single winner but not a calibrated ordering, and the shortlist is deliberately larger than the number of candidates worth choosing between.

### D6: Centralize questions, criteria, weights, and thresholds in `shb_core.decisions`

Every judgment definition lives in `shb_core.decisions`. Official guidance is explicit that questions, criteria, and thresholds are the primary reviewable policy artifact, and that they benefit from collaborative editing rather than being scattered across consuming packages.

`shb_core.decisions` formalizes the six official TypeSafe cookbook patterns across the ecosystem:
1. **Speculative Fan-Out (`patterns/fan-out.md`) & Single-Pass Function Calling (`cookbooks/function_calling.md`)**: Batch intent/tool-family routing (`Choice`), per-tool safety `Noul`s, and domain risk `Noul`s in one parallel `system_one` request (`~11.5x` lower cost, `~9.6x` lower latency than serial calls).
2. **Composite Scoring (`patterns/composite-scoring.md`)**: Evaluate independent `Score` (normalized as $\text{score}/(N-1)$) and hard-veto `Noul` dimensions in one request and combine in Python so weights and thresholds can be retuned without re-running inference.
3. **Citation & Groundedness Verification (`cookbooks/citation_check.md`)**: Atomic `Noul`s (`grounded_in_evidence`, `supports_claim`, `contains_speculative_language`, `contradicts_claim`) powering both `shb-ai-review` finding citation checks against redacted diff hunks and `shb-ai-harness-skills` stage deliverable evidence verification.
4. **SDE Cascade / Escalation (`cookbooks/sde_cascade.md` & `pydantic_ai.models.decision.DecisionHandOff`)**: Fast System One pass handles clear cases in `~70-200ms` and escalates uncertain ($|2p - 1| < \text{threshold}$) or low-confidence cases to generative models (`gemini-3.8-flash-high` / `Advance` or `pydantic_ai.models.decision.DecisionHandOff`) or supervisor review.
5. **Pre-Parsed Candidate Value Selection (`cookbooks/pre_parsed_value_extraction_cookbook.md`)**: Extract candidate spans (account numbers, amounts, biller codes) in Python code first and pass them to `Choice(criteria={..., "none": None})` with `None` criteria so the model selects only from verified source spans and never hallucinates banking parameters.
6. **Two-Stage Reranking (`cookbooks/rerank_typesafe.md`) & Hierarchical Classification (`cookbooks/hierarchical_classification.md`)**: Stage 1 lexical shortlist + Stage 2 batched per-candidate `Noul` reranking (`SkillMatcher`).

**Alternative considered:** define questions next to each consumer. Rejected — it scatters the banking security policy surface across multiple repositories.
### D7: The credential is transport config, not application settings

`JevSettings` (`src/shb_core/config.py`) configures the model identifier, timeout, retry policy, base URL, compression, and fail-closed behavior, loaded from `~/.shb/.env` and `~/.shb/config.yaml` (isolated from `~/.tdt/`). The credential comes from `TYPESAFE_API_KEY` (or explicit `PYDANTIC_AI_GATEWAY_API_KEY` fallback), and a key found in layered YAML is stripped with a `UserWarning`. Because `typesafe_sdk._core.config.resolve_and_validate_api_key()` only inspects explicit `api_key` or `os.environ.get("TYPESAFE_API_KEY")`, `JevDecisionClient` MUST explicitly resolve:
```python
api_key = api_key or os.environ.get("TYPESAFE_API_KEY") or os.environ.get("PYDANTIC_AI_GATEWAY_API_KEY")
base_url = settings.jev.base_url or os.environ.get("TYPESAFE_BASE_URL") or None
```
and pass `api_key` and `base_url` into `TypeSafeClient` / `AsyncTypeSafeClient`.

Furthermore, in `typesafe-sdk>=0.7.5`, request body compression using `zstd` is enabled by default for request bodies $\ge 1\text{ KiB}$ (`compression: Literal["zstd", False] | None = None`), whereas cached `typesafe-sdk==0.7.2` (`typesafe_sdk/_core/client/sync/client.py:21-33`) does not accept a `compression` keyword argument (`TypeError: unexpected keyword argument 'compression'`). Because non-official proxy gateways (such as Pydantic AI Gateway proxies or mock `httpx2` transports) may not support or decompress `Content-Encoding: zstd`, `JevSettings` exposes `compression: Literal["zstd", False] | None = None`, and `JevDecisionClient` resolves `effective_compression = False if (base_url or transport is not None) else settings.jev.compression`, stores it on the wrapper (`self.compression = effective_compression`), and passes `compression=effective_compression` to `TypeSafeClient` / `AsyncTypeSafeClient` **only when `"compression" in inspect.signature(TypeSafeClient.__init__).parameters`**.

**Alternative considered:** hold the key in `JevSettings`. Rejected — it would put a secret in the application settings surface, contradicting the existing secret-isolation convention.
### D8: Pin the model identifier once thresholds exist

The default is a pinned `jev-1.13.0` rather than `jev-latest`, because the response's `model` field is the only way to attribute a decision to a version and a moving alias would silently change calibrated behavior across banking tools. Evaluated support for `jev-1.14.0` (preview introduced in `typesafe-sdk>=0.7.5`) is provided via configuration toggle.

**Alternative considered:** follow `jev-latest` for automatic improvements. Rejected for banking guardrails, where unreviewed behavior drift is unacceptable.
### D9: Fail closed for security, fall back for the rest

When the credential is absent or the service is unreachable, financial transfers, compliance checks, and high-authority tool invocations fail closed (block or escalate to supervisor approval). Skill reranking and evaluation scoring fall back to their previous ordering and scoring, because a suboptimal skill ranking is recoverable and an unauthorized financial execution is not.

**Alternative considered:** fail closed everywhere. Rejected — it would make the evaluator and skill matcher brittle for no security gain.

### D10: Support HTTP/2 transport multiplexing via `typesafe-sdk[http2]` and Usage token attribution

The integration specifies `typesafe-sdk[http2]` to leverage persistent HTTP/2 connection multiplexing in `AsyncTypeSafeClient` and `TypeSafeClient` via `httpx2.AsyncClient(http2=True, timeout=timeout)` / `httpx2.Client(http2=True, timeout=timeout)` when no custom `transport` override is supplied (as `transport` and `http_client` are mutually exclusive in `typesafe_sdk`). Multiplexing removes per-request TCP/TLS handshake round trips and avoids socket churn under rapid tool or graph evaluations, keeping decision round-trips strictly within the sub-200ms envelope. Crucially, when `http2=True` and `transport is None`, `JevDecisionClient` must pass the resolved `timeout` to both `httpx2` and the client constructor so `httpx2` does not fall back to its 5.0s default, and forwards `compression=effective_compression` only when `"compression" in inspect.signature(TypeSafeClient.__init__).parameters`. Lifecycle methods `close()`, `aclose()`, and context managers are exposed.

Furthermore, because `typesafe_sdk.Usage` (`typesafe_sdk/_core/response_types.py:59-67` and `_schemas/models.py:130-137`) defines only `input_tokens: int | None = None` and `output_tokens: int | None = None` (`ConfigDict(extra="ignore", frozen=True, strict=True)`), `JevDecisionClient` reads `input_tokens = response.usage.input_tokens or 0` and `output_tokens = response.usage.output_tokens if response.usage.output_tokens is not None else (getattr(response.usage, "question_tokens", 0) or 0)`, where state `input_tokens` are billed once per batch, and surfaces normalized `JevUsage(input_tokens=input_tokens, output_tokens=output_tokens, question_tokens=output_tokens, total_tokens=input_tokens + output_tokens)` on the client evaluation result, OpenTelemetry spans (`shb.jev.decision` with `jev.input_tokens`, `jev.output_tokens`, `jev.total_tokens`), and `TelemetryStore.record_jev_decision`, ensuring full token accounting.
**Alternative considered:** standard HTTP/1.1 without connection multiplexing. Rejected — adds 50-100ms TLS renegotiation overhead per decision, violating the sub-200ms banking SLA.
### D11: Safe `request_id` extraction and native Pydantic `response_model` decoding

In `typesafe_sdk` 0.7.2 (`_core/schemas/base.py:67-73`), accessing `SystemOneResponse.request_id` raises `TypeSafeError("The response did not include a request ID.")` when `x-typesafe-request-id` is absent. `JevDecisionClient` wraps this accessor to return `None` or empty string safely. Furthermore, `SystemOneResponse._decode()` lifts decoded answer fields onto top-level model attributes, whereas passing a plain `pydantic.BaseModel` validates raw wire JSON without lifting answer fields. Custom typed response schemas declaring top-level question fields MUST subclass `SystemOneResponse`. `JevDecisionClient` also normalizes and lifts `answers` when a plain `BaseModel` is supplied.

**Alternative considered:** allow unhandled `TypeSafeError`. Rejected — crashes mock-transport tests and proxies that omit proprietary headers.

### D12: Support Pydantic AI Gateway proxies alongside direct TypeSafe endpoints

In addition to direct TypeSafe endpoints via `TYPESAFE_API_KEY`, the client configuration supports Pydantic AI Gateway proxies via `PYDANTIC_AI_GATEWAY_API_KEY` and `TYPESAFE_BASE_URL` (`https://gateway-us.pydantic.dev/proxy/typesafe` or local gateway). Because `typesafe_sdk._core.config.resolve_and_validate_api_key()` does not automatically recognize `PYDANTIC_AI_GATEWAY_API_KEY`, `JevDecisionClient` explicitly resolves the key and configures `base_url` on client instantiation, enabling centralized enterprise governance, rate-limiting, and cost tracking across agent fleets.

**Alternative considered:** hardcoded TypeSafe cloud URL. Rejected — prevents using local enterprise AI gateways or Pydantic AI Gateway proxies.

### D13: `shb-core` Foundation Hub & Workspace Ecosystem Blueprint

`shb-core` serves as the centralized foundation hub for all `shb-*` repositories (`shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`) via uv path dependencies (`[tool.uv.sources]`).

`shb_core.decisions` formalizes three portable foundation contracts:
1. `DecisionContract`: Base schema for domain decisions, state schemas, question batches, and threshold policies.
2. `GuardrailPolicy`: Authority class mapping, risk weighting, and outcome escalation rules (`PROCEED`, `ESCALATE`, `BLOCK`).
3. `CitationCheckContract`: Grounding and citation verification primitives (`grounded_in_evidence`, `supports_claim`, `contains_speculative_language`, `contradicts_claim`) following `cookbooks/citation_check.md`.

These foundation contracts and the runtime wrapper in `shb_core.jev` (`JevDecisionClient`) serve as a portable architectural blueprint that other workspace organizations (`platform`, `vds`, `ascend`, `ghtk`, `fpt`, `wiki`) can mirror or adopt without coupling to or modifying `~/.tdt/`.

**Alternative considered:** duplicate Jev client implementation in each SHB repository. Rejected — causes configuration drift, duplicate HTTP/2 connections, and uncoordinated policy definitions.

### D14: Sync + Async LangGraph Conditional Routing in `shb-agent-harness` via `RunnableCallable`

In `shb_harness.workflow.build_harness_graph`, routing after `StageName.SPEC` uses `Choice` with criteria keys `"design"` (`StageName.DESIGN.value`) and `"api_contract"` (`StageName.API_CONTRACT.value`) to evaluate whether `StageName.API_CONTRACT` can be skipped directly to `StageName.DESIGN`. The workflow supports both synchronous execution (`HarnessRunner.run_all` via `graph.invoke`) and asynchronous execution (`await graph.ainvoke`).

**LangGraph Runtime Invariant (`langgraph/_internal/_runnable.py:424-436`)**: Passing a bare `async def` function to `builder.add_conditional_edges` causes synchronous `graph.invoke(...)` (used by `HarnessRunner.run_all()`) to raise `TypeError('No synchronous function provided to "branch:to:..."')`, while `SqliteSaver` raises `NotImplementedError` under `ainvoke()` (which requires `AsyncSqliteSaver` or `MemorySaver`).

Therefore, `shb_harness/workflow.py` MUST wrap synchronous `_should_skip_api_contract` and asynchronous `a_should_skip_api_contract` in LangGraph's `RunnableCallable(_should_skip_api_contract, a_should_skip_api_contract)`. Both functions:
1. Normalize dict state inputs at entry via `state = HarnessState.model_validate(state) if isinstance(state, dict) else state`.
2. Execute the deterministic `classification.metadata` check (`category == "internal_refactor"` or `has_api_impact is False` -> return `StageName.DESIGN.value`) **FIRST** before Jev so existing deterministic routing (`tests/test_harness.py:47` `test_harness_conditional_routing_skip_api_contract`) always passes regardless of `JEV_ENABLED`.
3. When deterministic metadata does not already skip and `get_settings().jev.enabled` is `True`, invoke `JevDecisionClient.evaluate()` (in `_should_skip_api_contract`) or `await JevDecisionClient.a_evaluate()` (in `a_should_skip_api_contract`) using `HARNESS_SKIP_API_CONTRACT_DECISION` (`Choice` keys `"design"` vs `"api_contract"`). High confidence (`>= 0.85` for `"design"`) routes to `StageName.DESIGN.value`; disabled Jev, missing credentials, low confidence (`< 0.85`), `"api_contract"` selection, unrecognized targets, or transport errors fail safe to `StageName.API_CONTRACT.value`. Human review checkpoints (`interrupt()` at `StageName.PLAN_REVIEW`) and `SqliteSaver` checkpoints (`~/.shb/harness.db`) are strictly preserved.
**Alternative considered:** calling `asyncio.run()` in conditional edges. Rejected — raises `RuntimeError: This event loop is already running` inside async graph execution.

### D15: Banking Maker-Checker, Tool Authority Mapping & Dynamic Tool Preparation in `shb_agent`

Banking operations in `shb-agent-core` and `shb-mcp-servers` enforce strict human-in-the-loop security boundaries:
1. **Tool Authority Mapping (`TOOL_AUTHORITY_MAP`) & Prefix Normalization**: All 10 tools registered in `src/shb_agent/tools/__init__.py` are mapped to distinct `AuthorityClass` tiers in `shb_core.decisions`. Because `src/shb_agent/agent.py:86-152` registers 3 tools with a `tool_` prefix (`tool_get_account_balance`, `tool_query_transaction_status`, `tool_initiate_fund_transfer`) and 7 tools without `tool_` via `tool_plain`, `PrepareTools` and `Hooks` normalize tool names via `tool_name.removeprefix("tool_")` (`td.name.removeprefix("tool_")`) when matching against `TOOL_AUTHORITY_MAP`:
   - `READ_ONLY`: `get_account_balance`, `query_transaction_status`, `get_transaction_history`, `query_bill`
   - `OPERATIONAL`: `verify_beneficiary_account`, `generate_vietqr`, `parse_vietqr` (`src/shb_agent/tools/vietqr.py:135`: extracts EMVCo Tag 62 `purpose` content when present for Jev prompt-injection screening while preserving `is_valid_crc: True` for 4-hex-char CRCs as tested by `test_parse_vietqr` and exposing `crc_matches_computed: bool`)
   - `FINANCIAL_TRANSFER`: `initiate_fund_transfer` (inviolable `> 50,000,000 VND` maker-checker supervisor token + sub-50M structuring escalation) AND `pay_bill` (`src/shb_agent/tools/biller.py`: high-value biller debit & `amount != amount_due` anomaly escalation)
   - `COMPLIANCE_CRITICAL`: `screen_beneficiary` (deterministic `RESTRICTED_KEYWORDS` & `HIGH_RISK_ACCOUNTS` first, then Jev `Noul` for transliterated/diacritic-stripped Vietnamese & English PEP/OFAC/SBV sanction evasion)
2. **Maker-Checker Invariant**: Transfers `> 50,000,000 VND` (`MAKER_CHECKER_THRESHOLD_VND`) unconditionally enforce supervisor approval token validation (`ModelRetry` / `PENDING_APPROVAL`). Jev CANNOT approve or bypass this gate under any condition.
3. **Sub-Threshold Structuring Triage & Supervisor Token Satisfaction**: Sub-threshold transfers (`<= 50,000,000 VND`) are evaluated by `JevToolGuardrail` for structuring, split-transfers, or evasive narratives. If `JevToolGuardrail` returns `BLOCK`, execution is rejected (`TransferResponse(status="FAILED_COMPLIANCE", ...)`). If `JevToolGuardrail` returns `ESCALATE` (including fail-closed escalation when Jev credentials are missing), an absent/short `supervisor_approval_token` raises `ModelRetry` / returns `PENDING_APPROVAL`, whereas a valid `supervisor_approval_token` (`len >= 8`) satisfies the `ESCALATE` gate and completes the transfer (`status="COMPLETED"`).
4. **Dynamic Tool Preparation (`PrepareTools`) & `ShbAgent.run()` Dual-Path Preservation**: In `pydantic-ai==2.54.0`, agent-wide `PrepareTools` (`Agent(..., capabilities=[PrepareTools(filter_banking_tools)])`) dynamically filters active tools based on the turn's classified intent. When speculative fan-out classifies a turn as read-only with high confidence (`>= 0.85`), financial transfer tools (`td.name.removeprefix("tool_") in {"initiate_fund_transfer", "pay_bill"}`) are dynamically omitted from the LLM tool schema, eliminating the attack surface for indirect prompt injection. `ShbAgent.run()` preserves its deterministic simulation path and `TestModel` compatibility (`tests/test_agent.py`) when `JEV_ENABLED=false` or when no Jev credential/mock client is configured.
5. **SDE Cascade & Native Decision Hand-Off**: `pydantic-ai 2.54.0` native `TypeSafeModel` (`pydantic_ai.models.typesafe`) and `DecisionHandOff` provide native fallback cascades (`FallbackModel(TypeSafeModel(...), primary_llm, fallback_on=DecisionHandOff)`) when fast decision confidence falls below the escalation threshold, alongside `src/shb_agent/evaluation/__init__.py` and `src/shb_agent/evaluation/jev_scorer.py` (`JevEvaluator` and built-in `BANKING_EVAL_DATASET`).
6. **AML Screening Pre-Flight**: In `screen_beneficiary`, deterministic `RESTRICTED_KEYWORDS` and `HIGH_RISK_ACCOUNTS` rules remain authoritative. Jev `Noul` checks add semantic detection for transliterated or obfuscated PEP/sanctioned names; on detection, the beneficiary is marked `FLAGGED_FOR_MANUAL_REVIEW`. On Jev error, the check fails closed to deterministic rules.
7. **State Sanitization & MCP Tool Authority Alignment (`shb-mcp-servers`)**: Account numbers and PANs are masked with `shb_core.security.crypto.mask_pan` and sanitized with `shb_core.jev.sanitize_jev_state` / `shb_agent.tools.audit.sanitize_payload` before constructing bounded state projections (<32k tokens) for Jev. In `src/shb_mcp/tools.py:176`, `MCP_TOOL_AUTHORITY_MAP` in `shb_core.decisions` maps the 12 MCP tool names (`banking_transfer_initiate`, `biller_pay`, `vietqr_parse`, `compliance_sanction_screen`, etc.) to `AuthorityClass` tiers, and `execute_tool` applies `mask_pan` / `sanitize_jev_state` to guardrail state and audit metadata without mutating top-level response fields (`account_number`) asserted by `tests/test_server.py:42` and `tests/test_tools.py:47`.
**Alternative considered:** allow Jev to auto-approve transfers when confidence is high. Rejected — violates SBV banking compliance and internal maker-checker policy.

### D16: Citation & Groundedness Verification (`citation_check` Pattern) for `shb-ai-review` and `shb-ai-harness-skills`

Following the official TypeSafe citation check cookbook (`cookbooks/citation_check.md`), the ecosystem implements dual-stage evidence verification in code review and harness planning:
1. **Pre-Flight Diff Hunk Triage (`MR_DIFF_TRIAGE_CONTRACT`) & `DiffHunkInfo.redacted_diff`**:
   In `shb-ai-review` (`src/shb_review/validation/hunk_gate.py` and `src/shb_review/ai/reviewer.py`), `DiffHunkInfo` is extended with `redacted_diff: str = ""` (populated via `redact_outbound_content` in `HunkGate.from_diff_entries()`). Before invoking generative model review (`OpenAIChatModel`), `HunkGate` runs a fast System One `Noul` check (`requires_ai_review`) on `redacted_diff` using structured criteria to triage whether the diff contains substantive logic changes versus trivial formatting, whitespace, imports, or boilerplate comments. If Jev is disabled or raises an error, `AiReviewer.review_diff()` fails open to `_execute_provider` so existing `test_ai_reviewer.py` and `test_hunk_gate.py` suites pass 100%.
2. **Post-Generation Finding Citation Verification (`MR_FINDING_CITATION_CONTRACT`)**:
   When generative review findings (`finding.source.startswith("ai:")`) pass deterministic line/range checks in `HunkGate.validate_findings()`, `HunkGate` validates each AI finding's reported code location and citation against the hunk's `redacted_diff` using the 3 standardized atomic `Noul`s in `MR_FINDING_CITATION_CONTRACT`: `grounded_in_diff`, `contains_speculative_language`, and `contradicts_diff`. An AI finding is demoted to `suppressed_findings` with reason `"jev_citation_ungrounded"` when `grounded_in_diff < 0.70` (which covers both low groundedness $p \le 0.30$ and the uncertain band $0.30 < p < 0.70$ where $|2p - 1| < 0.40$, leaving no gap) or `contradicts_diff >= 0.50` or `contains_speculative_language >= 0.70`.
3. **Stage Deliverable Evidence Verification (`verify_stage_deliverable_evidence`) & 12-to-13 Stage Alias Map**:
   In `shb-ai-harness-skills` (`src/shb_ai_harness/contracts.py` and `resources/harness-13/schema.yaml`), deliverable verification maps 12-stage `StageName` aliases to `harness-13` stage IDs (`implementation_plan -> impl_plan`, `test_plan -> test_cases`, `verification -> verify`) and combines deterministic ID regex checks (`REQ`, `AC`, `EVD`, `DES`, `DEC`, `API`, `TASK`, `TC`, `ATP`, `VER`) with Jev `citation_check` `Noul`s (`observed_claims_grounded_in_evd`, `upstream_requirements_traced`, `planning_only_boundary_preserved`). `src/shb_ai_harness/cli.py:20` (`stages = schema.get("stages", {})`, which silently returned `{}` and printed `Total stages defined: 0`) is fixed to `stages = schema.get("artifacts", [])` (`13` artifacts). Deliverables that assert unverified claims or violate planning boundaries are flagged for revision prior to transition.
**Alternative considered:** rely solely on generative LLM self-reflection for citation checks. Rejected — generative self-reflection suffers from self-reinforcing hallucinations and adds 3-5s of latency per review finding.

## Risks / Trade-offs

- **[No credential, so the live path is unverified]** → The mock and fail-closed paths are unit-tested; the live path is activated when the operator supplies `TYPESAFE_API_KEY` or `PYDANTIC_AI_GATEWAY_API_KEY`.
- **[Thresholds are uncalibrated]** → Thresholds live in `shb_core.decisions`, are disabled by default (`enabled=False`), and guardrails escalate in the uncertain band rather than guessing.
- **[An unavailable service degrades banking operations]** → A circuit breaker (`JevCircuitBreaker`) in `shb_core.jev` trips after 3 consecutive transport/5xx failures for a 30.0s cooldown. Fail-closed behavior ensures high-authority operations require human approval rather than executing unguarded.
- **[Alias drift changes decisions silently]** → Mitigation: pin `jev-1.13.0` by default, and record the answering model from each response in telemetry.
- **[Request budget exceeded by large banking payloads]** → The guardrail sends a bounded projection of the invocation (<32k tokens), not full conversation history. State is sanitized using `mask_pan` and `sanitize_payload`.
- **[Zstd request body compression proxy & version incompatibility]** → In `typesafe-sdk>=0.7.5`, request compression is enabled by default for bodies $\ge 1\text{ KiB}$, whereas cached `typesafe-sdk==0.7.2` does not have a `compression` parameter in `TypeSafeClient.__init__`. Mitigation: `JevSettings` exposes `compression: Literal["zstd", False] | None = None`, and `JevDecisionClient` computes `effective_compression = False if (base_url or transport is not None) else settings.jev.compression` and passes `compression=effective_compression` only when `"compression" in inspect.signature(TypeSafeClient.__init__).parameters`.
- **[LangGraph dual sync/async conditional routing]** → Passing a bare `async def` raises `TypeError` under synchronous `graph.invoke()`. Mitigation: `RunnableCallable(_should_skip_api_contract, a_should_skip_api_contract)` wraps both sync and async functions, normalizes dict state via `HarnessState.model_validate(state)`, and evaluates deterministic `classification.metadata` before Jev.
- **[Prompt injection via indirect tool inputs]** → QR payloads or biller text could attempt prompt injection. Mitigation: `parse_vietqr` screens Tag 62 `purpose` while preserving 4-hex-char CRC compatibility (`is_valid_crc: True`) and `crc_matches_computed: bool`; `PrepareTools` normalizes `td.name.removeprefix("tool_")` and dynamically omits debit tools on read-only turns.
- **[Debug logging emits unredacted wire content]** → In `typesafe_sdk._core.transport.RequestState._log_wire`, `request.content` is logged unredacted when `logging.getLogger("typesafe_sdk")` is at `DEBUG`. Mitigation: the runtime MUST clamp `logging.getLogger("typesafe_sdk")` to `>= logging.INFO`, never place secrets in `state`, and sanitize state projections via `sanitize_jev_state`.
- **[ComplianceScanner (`SEC-001` / `PCI-001` / `SYN-001`) Source Scanning Guardrail]** → `shb-tools` `ComplianceScanner` scans all non-comment lines in `src/**/*.py`. Therefore, `src/**/*.py` (including `src/shb_core/decisions.py` criteria examples and docstrings) MUST NOT contain any `api_key|secret_key|private_key|password|jwt_secret` string literal $\ge 12$ chars (`SEC-001`) or any unmasked 16-digit PAN (`PCI-001`), and must maintain clean syntax (`SYN-001`).
- **[Strict typing & Ruff TC001/TC002 compliance]** → `src/shb_*/**` enforces Ruff `line-length = 100`, `TC001`/`TC002`, `UP006`/`UP007`/`UP035`/`B904`, and `uv run mypy --strict --ignore-missing-imports src`. Type-only imports are placed under `if TYPE_CHECKING:`, and Pydantic models are cleanly annotated.
- **[Guardrail latency on the critical path]** → Network round trips add latency. Mitigations: HTTP/2 multiplexing, bounded timeout (1.5s), one batched request per evaluation, and circuit breakers.

## Migration Plan

1. **Phase 1: Foundation Layer (`shb-core`) & Dependency Groups**:
   - Add `"typesafe-sdk[http2]>=0.7.2"` to `[project.optional-dependencies].jev` and `[dependency-groups].dev` in `shb-core/pyproject.toml` and `shb-agent-core/pyproject.toml` (plus `"pydantic-evals>=1.70.0"` in `shb-agent-core/pyproject.toml`), and add `"typesafe-sdk[http2]>=0.7.2"` to `[dependency-groups].dev` in `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, and `shb-mcp-servers`.
   - Implement `JevSettings` in `src/shb_core/config.py` attached to `ShbSettings.jev` with `compression` toggle.
   - Implement `JevDecisionClient`, `JevCircuitBreaker`, `JevUsage`, `sanitize_jev_state`, and optional-dependency fallback shims in `src/shb_core/jev.py` with normalized `JevUsage` token attribution (`input_tokens`, `output_tokens`, `question_tokens=output_tokens`, `total_tokens=input_tokens + output_tokens`), `"compression" in inspect.signature(...)` guard, and safe `request_id` extraction.
   - Implement `shb_core.decisions` with optional-dependency fallback shims, centralized criteria (free of `SEC-001` $\ge 12$-char secret literals and `PCI-001` 16-digit PANs), weights, thresholds, `TOOL_AUTHORITY_MAP`, `MCP_TOOL_AUTHORITY_MAP`, six cookbook patterns, and portable contracts (`DecisionContract`, `GuardrailPolicy`, `CitationCheckContract`).
   - Unit-test success, timeout, missing-credential, invalid-header, compression, fallback-shim, and circuit-breaker paths against mock transports (`"usage": {"input_tokens": ..., "output_tokens": ...}`).
2. **Phase 2: Banking Agent Guardrails, Dynamic Tool Filtering & AML (`shb-agent-core`)**:
   - Implement `JevToolGuardrail` in `src/shb_agent/tools/guardrails.py` with `AuthorityClass` scaling, `tool_name.removeprefix("tool_")` normalization, and state sanitization across all 10 tools.
   - Wire `PrepareTools` dynamic tool filtering omitting debit tools (`initiate_fund_transfer`, `pay_bill`) on read-only turns while preserving `ShbAgent.run()` simulation and `TestModel` paths.
   - Wire pre-flight checks into `initiate_fund_transfer` (preserving `MAKER_CHECKER_THRESHOLD_VND` and satisfying `ESCALATE` when a valid `supervisor_approval_token` is supplied), `pay_bill`, `parse_vietqr` (Tag 62 `purpose` screening while preserving `is_valid_crc: True` for 4-hex-char CRCs and `crc_matches_computed: bool`), and `screen_beneficiary`.
   - Create `src/shb_agent/evaluation/__init__.py` and `src/shb_agent/evaluation/jev_scorer.py` (`JevEvaluator` and `BANKING_EVAL_DATASET`) compatible with `pydantic-evals==2.54.0`.
3. **Phase 3: 12-Stage LangGraph Routing & Deliverable Verification (`shb-agent-harness`, `shb-ai-harness-skills`)**:
   - Implement sync `_should_skip_api_contract` and async `a_should_skip_api_contract` wrapped in `RunnableCallable` in `src/shb_harness/workflow.py` with `HarnessState.model_validate(state)` normalization, deterministic `classification.metadata` precedence before Jev, and `Choice` keys `"design"` vs `"api_contract"`.
   - Implement `verify_stage_deliverable_evidence()` in `shb-ai-harness-skills` (`src/shb_ai_harness/contracts.py`) with 12-to-13 stage alias mapping (`implementation_plan -> impl_plan`, `test_plan -> test_cases`, `verification -> verify`) and fix `src/shb_ai_harness/cli.py:20` (`schema.get("artifacts", [])`).
   - Verify graph compile with `SqliteSaver` checkpoints and `interrupt()` human reviews.
4. **Phase 4: Two-Stage Skill Reranking (`shb-agent-skills`)**:
   - Create `src/shb_skills/matcher.py` implementing `SkillMatcher` (`match`, `match_jev`, and `a_match_jev`) over `SkillsCatalog` and re-export `SkillMatcher` in `src/shb_skills/__init__.py`.
5. **Phase 5: Observability, Review & MCP Integration (`shb-observability`, `shb-ai-review`, `shb-mcp-servers`)**:
   - Add backward-compatible `attributes: dict[str, Any] = Field(default_factory=dict)` to `OTelTraceSpan` and `record_jev_decision(...)` to `TelemetryStore` in `src/shb_observability/collector.py`, recording `shb.jev.decision` spans with normalized `JevUsage` attributes (`jev.input_tokens`, `jev.output_tokens`, `jev.total_tokens`) and `shb_jev_decisions_total` metrics.
   - Add `redacted_diff: str = ""` to `DiffHunkInfo` and implement diff triage (`MR_DIFF_TRIAGE_CONTRACT`) and post-generation AI finding citation check (`MR_FINDING_CITATION_CONTRACT` with `grounded_in_diff < 0.70`, `contradicts_diff >= 0.50`, `contains_speculative_language >= 0.70`) in `shb-ai-review` (`src/shb_review/validation/hunk_gate.py` and `src/shb_review/ai/reviewer.py`).
   - Align `shb-mcp-servers` (`src/shb_mcp/tools.py:176`) execution guardrails using `MCP_TOOL_AUTHORITY_MAP` and `mask_pan` / `sanitize_jev_state` without mutating top-level return payload fields (`account_number`).
6. **Phase 6: Full Suite Verification & Compliance Scan**:
   - Run full pytest test suite across all 8 modified SHB repos (plus `shb-tools`), verifying zero regressions against the recorded **219-test baseline across the 8 modified repos** (**228 total** including `shb-tools`):
     - `shb-core`: 23
     - `shb-agent-core`: 27
     - `shb-agent-harness`: 9
     - `shb-ai-harness-skills`: 7
     - `shb-agent-skills`: 7
     - `shb-observability`: 5
     - `shb-ai-review`: 129
     - `shb-mcp-servers`: 12
     - **Total across 8 modified repos: 219 passed** (plus `shb-tools`: 9 = **228 passed** across all 9 verified SHB repos)
   - Execute `ComplianceScanner` (`SEC-001`, `PCI-001`, `SYN-001`), `uv run ruff check src tests`, and `uv run mypy --strict --ignore-missing-imports src` (including fallback-shim verification when `typesafe-sdk` is uninstalled).
**Rollback:** The feature is disabled by default (`enabled=False`). Disabling the setting (`SHB_JEV_ENABLED=false` or `JEV_ENABLED=false`) completely restores previous deterministic behaviors with no code changes.

## Open Questions

- What fine-grained confidence thresholds should `shb-agent-core` use for each `AuthorityClass` in production? Deferrable: the mechanism and code-owned weights are fixed in `shb_core.decisions`, and the runtime escalates in the uncertain band to human supervisor approval rather than taking automated risks.
