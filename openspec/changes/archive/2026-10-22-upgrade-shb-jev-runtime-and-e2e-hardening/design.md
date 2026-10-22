# Design: SHB Jev Decision Runtime Upgrades, Live E2E Hardening, and 13-Repo Ecosystem Alignment

## Context

See `proposal.md` — Why.

This design extends the 4-layer System One decision architecture established in `2026-10-21-agent-core-integrate-jev-system-one` across all 13 repositories in the SHB Banking Ecosystem (`~/Developer/shb/*`). While `tdt/agent-core` and `~/.tdt/` remain strictly frozen and `2026-10-21-agent-core-integrate-jev-system-one` remains immutable in `openspec/changes/archive/`, live end-to-end execution across the SHB + OmniRoute (`v3.8.52`, `gemini-3.8-flash-high`) + TypeSafe API (`https://api.typesafe.ai/v1/systemone`, `jev-1.13.0` and `jev-1.14.0` over HTTP/2) stack surfaced 10 operational integration refinements and 5 CLI subcommand requirements, alongside the opportunity to upgrade all 13 SHB repositories to `typesafe-sdk[http2]>=0.7.5` (`httpx2>=2.16.0`) and `pydantic-ai>=2.59.0` (`pydantic-evals>=2.59.0`).

### Existing SHB Ecosystem Patterns Referenced

Before introducing new capabilities, this design grounds directly in existing SHB patterns:
1. **Isolated Foundation Settings & Value-Blind `.zshenv` Resolution (`shb_core.config.ShbSettings`, `shb_core.jev.JevDecisionClient._resolve_endpoint_and_api_key`)**:
   Reuses the existing `~/.shb/.env` configuration loader and value-blind `~/.zshenv` (`0600` mode check + `shlex.split(line, comments=True)`) credential parser to resolve `OMNIROUTE_API_KEY` when `SHB_MODEL_GATEWAY_KEY` is empty in `~/.shb/.env` and `model_gateway_url` targets local loopback (`127.0.0.1` / `localhost`).
2. **Single-Source Optional-Dependency Fallback Shims (`shb_core.jev` -> `shb_core.decisions`)**:
   Extends the existing pattern in `src/shb_core/jev.py` — where `Noul`, `Choice`, `Score`, `NoulCriteria`, `SystemOneResponse`, `TypeSafeError`, and `TypeSafeAuthenticationError` have single-source optional-dependency fallback shims — to also export `Box`, `BoxCoordinates`, `BoxAnswer`, `Image`, and `Asset` from `typesafe-sdk>=0.7.5`.
3. **Exact-Key Single-Evaluation Guardrail Deduplication (`shb_agent.tools.guardrails.JevToolGuardrail`)**:
   Preserves `_make_dedup_key` (`(clean_tool_name, canonical_args)` with `has_supervisor_token = is_valid_supervisor_token(token)`) and shares a single `JevToolGuardrail` instance between `@hooks.on.before_tool_execute` and `@agent.tool_plain` functions bound via `ShbAgent._bind_deps_to_tool_func()`.
4. **Dual Sync/Async LangGraph Conditional Routing (`shb_harness.workflow.RunnableCallable`)**:
   Complements `RunnableCallable(_should_skip_api_contract, a_should_skip_api_contract)` with `DualSqliteSaver(SqliteSaver)` so both synchronous `graph.invoke()` (`HarnessRunner.run_all()`) and asynchronous `await graph.ainvoke()` (`HarnessRunner.a_run_all()`) persist checkpoints to `~/.shb/harness.db`.
5. **Pre-Flight Hunk Triage & Post-Generation Citation Filtering (`shb_review.validation.hunk_gate.HunkGate`, `shb_review.ai.reviewer.AiReviewer`)**:
   Extends `HunkGate.filter_findings()` (`MR_FINDING_CITATION_CONTRACT`) from `review-mr` to `ReviewerOrchestrator.run_review(files=..., use_ai=True)` and `shb-ai-review scan --ai` over un-truncated file diffs.

### Transaction, Idempotency, Maker-Checker, and Checkpoint Boundaries

- **Transaction Boundary**: Jev System One evaluations (`evaluate` / `a_evaluate`, including `Box` spatial grounding and `TypeSafeModel` decision calls) remain strictly read-only, non-transactional computations executing outside database transaction locks.
- **Idempotency Boundary (`IdempotencyManager`)**: Banking tool idempotency keys (`idempotency_key` in `_NON_SECRET_STRUCTURAL_KEYS`) and `_pending_evaluations` deduplication caches remain unaffected by `<field>_untrusted_text` preservation or `Caching(retention=True, messages=True)`.
- **Maker-Checker Boundary (`MAKER_CHECKER_THRESHOLD_VND`)**: Transfers `> 50,000,000 VND` unconditionally enforce `is_valid_supervisor_token(token)` (`len >= 8` stripped) before any unconsumed Jev call; sub-50M VND structuring escalates to `PENDING_APPROVAL` or completes with a valid supervisor token, while prompt/SQL injections (`is_prompt_injection`) are unconditionally blocked (`status="REJECTED"`, `AuditEvent(status="FAILED")`).
- **Checkpoint Boundary (`DualSqliteSaver` at `~/.shb/harness.db`)**: Both synchronous (`SqliteSaver`) and asynchronous (`AsyncSqliteSaver` / `asyncio.to_thread` delegation in `DualSqliteSaver`) LangGraph executions commit stage checkpoints atomically per stage transition while preserving the human `interrupt()` gate at `StageName.PLAN_REVIEW`.

## Goals / Non-Goals

**Goals:**
- Resolve all 10 live E2E operational gaps and expose 5 CLI subcommands (`shb-agent evaluate`, `shb-harness plan -d`, `shb-harness-skills verify-deliverable`, `shb-skills match`, `shb-observability show-metrics` live Jev spans) across the 8 Jev-integrated SHB repositories.
- Upgrade `typesafe-sdk[http2]>=0.7.5` (`httpx2>=2.16.0`) and `pydantic-ai>=2.59.0` (`pydantic-evals>=2.59.0`) and synchronize `pyproject.toml` and `uv.lock` across all 13 SHB repositories with `13/13` `mypy --strict` coverage.
- Integrate `typesafe-sdk 0.7.5` `Box`/`BoxCoordinates`/`BoxAnswer`/`Image`/`Asset` spatial grounding in `shb-core` and `pydantic-ai 2.59.0` `resolve_typesafe_decision_model()` + `Caching(retention=True, messages=True)` in `shb-agent-core`.

**Non-Goals:**
- Modifying `openspec/changes/archive/2026-10-21-agent-core-integrate-jev-system-one` (archived changes are immutable).
- Modifying or importing `tdt/agent-core`, `tdt-core`, or `~/.tdt/`.
- Introducing any JavaScript/TypeScript `package.json` manifests in `shb/*`.

## Decisions

### D1: Live E2E Operational Refinements & Tool Dependency Binding (`shb-core`, `shb-agent-core`, `shb-ai-review`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`)
- **Decision**:
  1. In `shb_core/config.py`, add `@field_validator("model_gateway_key", mode="after")` on `ShbSettings` to normalize empty strings (`SHB_MODEL_GATEWAY_KEY=` in `~/.shb/.env`) and fall back to `OMNIROUTE_API_KEY` when `model_gateway_url` targets `127.0.0.1` / `localhost`.
  2. In `shb_agent/agent.py`, initialize `self.deps.guardrail = JevToolGuardrail(client=jev_client)` in `ShbAgent.__init__` and wrap `@agent.tool_plain` tools (`pay_bill`, `parse_vietqr`, `screen_beneficiary`) with `ShbAgent._bind_deps_to_tool_func(func, self.deps)`, which injects `deps.guardrail` and `deps.jev_client` and strips `VAR_KEYWORD` (`**_kwargs`) from `wrapper.__signature__` so Pydantic AI tool schema introspection remains clean. Add `ShbAgent.run_async()`, `_format_live_result()` (`ToolCallPart` vs `ToolReturnPart` separation), and `shb-agent evaluate`.
  3. In `shb_review/ai/reviewer.py` and `shb_review/cli.py`, update `AiReviewConfig.load_configured_providers()` to use `settings.default_model` (`gemini-3.8-flash-high`) as primary and only attach a secondary provider when `SHB_REVIEW_AI_SECONDARY_MODEL` is explicitly set (preventing `SHB_FALLBACK_MODEL=Advance` from failing closed with HTTP 400 on OmniRoute), remove the 50-line truncation in `shb-ai-review scan --ai`, and route `scan --ai` findings through `HunkGate.filter_findings()` (`MR_FINDING_CITATION_CONTRACT`).
  4. In `shb_ai_harness/contracts.py`, map `"classification" -> "clarify"` in `resolve_canonical_stage_name()`, project full 12-stage context (including `api_contract` `not_applicable` handling), and expose `shb-harness-skills verify-deliverable`. Expose `shb-skills match` in `shb-agent-skills` and live `shb.jev.decision` span tables in `shb-observability show-metrics`.
- **Rationale**: Ensures every CLI entrypoint and live agent workflow operates end-to-end against OmniRoute `v3.8.52` and TypeSafe API without duplicate Jev evaluations or schema leakage.

### D2: `DualSqliteSaver` Async Checkpointer Delegation in `shb-agent-harness`
- **Decision**: Implement `DualSqliteSaver(SqliteSaver)` in `src/shb_harness/workflow.py` delegating asynchronous checkpointer methods (`aget_tuple`, `alist`, `aput`, `aput_writes`, `adelete_thread`) via `asyncio.to_thread` (alongside `AsyncSqliteSaver` support), and expose `HarnessRunner.a_run_all()` and `HarnessRunner.a_resume()` plus `shb-harness plan --description/-d` and structured stage governance IDs (`REQ-001` through `VER-001`).
- **Rationale**: Standard `langgraph.checkpoint.sqlite.SqliteSaver` raises `NotImplementedError` when `await compiled.ainvoke(...)` calls `aget_tuple`. Delegating async methods via `asyncio.to_thread` on `DualSqliteSaver` allows both synchronous (`run_all`) and asynchronous (`a_run_all`) execution against `~/.shb/harness.db` without blocking the event loop.

### D3: PAN-Masked `<field>_untrusted_text` Injection Preservation (`shb-agent-core` & `shb-mcp-servers`)
- **Decision**: In `shb_agent/tools/guardrails.py` (`sanitize_invocation_state`) and `shb_mcp/tools.py` (`execute_tool`), whenever an account/PAN field (`account_number`, `source_account`, `destination_account`, `beneficiary_account`) contains non-PAN characters (such as SQL/command/prompt injection strings like `"1029384756; DROP TABLE accounts; -- IGNORE ALL RULES"`), mask the top-level field with `mask_pan()` AND preserve `f"{key}_untrusted_text"` with digit runs masked via `_DIGIT_RUN_RE.sub(lambda m: mask_pan(m.group(0)), raw_val)`. Update `GUARDRAIL_QUESTIONS["prompt_injection"]` in `shb_core/decisions.py` to inspect `<field>_untrusted_text`.
- **Rationale**: Pure `mask_pan("1029384756; DROP TABLE...")` collapses the string to `"1029****ULES"`, hiding the injection payload from Jev. Preserving `account_number_untrusted_text` with all digit runs masked via `mask_pan()` guarantees zero raw PAN leakage (`PCI-001`) while enabling Jev to block account-field injections (`effective_risk=0.980 -> GuardrailOutcome.BLOCK`).

### D4: `typesafe-sdk 0.7.5` Multimodal `Box`/`Image`/`Asset` Integration in `shb-core`
- **Decision**: Upgrade to `typesafe-sdk[http2]>=0.7.5` (`httpx2>=2.16.0`), export `Box`, `BoxCoordinates`, `BoxAnswer`, `Image`, and `Asset` from `shb_core.jev` (with single-source optional-dependency fallback shims), add `boxes: dict[str, BoxAnswer] = Field(default_factory=dict)` to `JevEvaluationResult`, accept `assets: Sequence[Image | Asset] | None = None` on `evaluate()` / `a_evaluate()`, lift `BoxAnswer.box` (`BoxCoordinates | None`) onto plain Pydantic `BaseModel` `response_model` fields, and expose `get_sync_sdk_client()` / `get_async_sdk_client()`.
- **Rationale**: Adopts the full `typesafe-sdk 0.7.5` primitive surface (`Noul`, `Choice`, `Score`, `Box`) for banking document/VietQR spatial grounding while maintaining 100% optional-dependency safety.

### D5: `pydantic-ai 2.59.0` `resolve_typesafe_decision_model()` and `Caching` in `shb-agent-core`
- **Decision**: Upgrade to `pydantic-ai>=2.59.0` (`pydantic-evals>=2.59.0`), implement `resolve_typesafe_decision_model()` in `src/shb_agent/model.py` constructing `TypeSafeModel` with `TypeSafeModelSettings` (`decision_boolean_threshold`, `decision_route_threshold`, and `max_retries -> TypeSafeRetryPolicy`) and `TypeSafeProvider(typesafe_client=client.get_async_sdk_client())`, and enable `Caching(retention=True, messages=True)` on `ShbAgent`.
- **Rationale**: Connects `JevDecisionClient`'s HTTP/2-pooled `AsyncTypeSafeClient` and endpoint-first credential resolution directly into Pydantic AI 2.59.0's native `TypeSafeModel` / `DecisionHandOff` cascade architecture and prompt caching layer.

### D6: 13-Repository Dependency Synchronization & `13/13` `mypy --strict` Coverage
- **Decision**: Upgrade dependency lower bounds and lockfiles (`uv.lock`) across all 13 SHB repositories (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`, `shb-tools`, `shb-schedule`, `shb-webhook-receiver`, `shb-browser-cli`, `shb-jira-tools`) and enable `[tool.mypy] strict = true` in `shb-jira-tools` and `shb-webhook-receiver`.
- **Rationale**: Eliminates version skew across editable `[tool.uv.sources]` dependencies on `shb-core` and enforces uniform `ruff 0.17.1` + `mypy --strict 2.4.0` + `uv lock --check` hygiene across all `13/13` repositories.

## Risks / Trade-offs

- **Risk**: `TypeSafeProvider` requires an initialized `AsyncTypeSafeClient` when constructing `TypeSafeModel`.
  - **Mitigation**: `JevDecisionClient.get_async_sdk_client()` lazily initializes and returns the event-loop-aware `AsyncTypeSafeClient` using `_resolve_endpoint_and_api_key()`, failing closed with `TypeSafeError` if credentials are unconfigured.
- **Risk**: Preserving untrusted text from account fields could accidentally include embedded card or account digits.
  - **Mitigation**: `_DIGIT_RUN_RE = re.compile(r"\d{6,}")` masks every digit sequence of length $\ge 6$ via `mask_pan()` before storing `<field>_untrusted_text`, verified by `test_jev_guardrail_blocks_prompt_injection_in_account_number` and `shb-compliance-scan` (`PCI-001`).
