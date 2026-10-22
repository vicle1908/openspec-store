# Proposal: Upgrade SHB Jev Decision Runtime, Live E2E Operational Hardening, and 13-Repo Dependency Modernization

## Why

Post-archive live end-to-end (E2E) operational verification across the 13 SHB repositories exposed 10 runtime and CLI integration gaps alongside outdated SDK lower bounds (`typesafe-sdk>=0.7.2`, `pydantic-ai>=2.54.0`) that prevented adopting `typesafe-sdk>=0.7.5` (`Box`/`Image`/`Asset` spatial grounding and SDK client accessors) and `pydantic-ai>=2.59.0` (`TypeSafeModel`/`TypeSafeProvider` resolution and `Caching` capability).

Following the initial archive of `2026-10-21-agent-core-integrate-jev-system-one` (which remains strictly immutable per OpenSpec governance), live end-to-end testing against OmniRoute (`v3.8.52`, `gemini-3.8-flash-high`) and TypeSafe API (`https://api.typesafe.ai/v1/systemone`, `jev-1.13.0` and `jev-1.14.0` over HTTP/2) identified concrete runtime edge cases in tool dependency binding (`@agent.tool_plain`), account-field prompt/SQL injection sanitization (`<field>_untrusted_text`), async LangGraph SQLite checkpointing (`DualSqliteSaver`), stage governance IDs, AI code review secondary model isolation and `scan --ai` citation filtering, and missing CLI subcommands across 5 packages. Simultaneously, upgrading the 13 SHB repositories to the latest ecosystem releases unlocks native `typesafe-sdk 0.7.5` multimodal spatial grounding (`Box`, `BoxCoordinates`, `BoxAnswer`, `Image`, `Asset`) and `pydantic-ai 2.59.0` native `TypeSafeModel` / `TypeSafeModelSettings` / `TypeSafeProvider` decision model resolution and prompt `Caching(retention=True, messages=True)`.

### Non-Goals

- **Never Modifying Archived Changes**: The archived change directory `openspec/changes/archive/2026-10-21-agent-core-integrate-jev-system-one` is strictly immutable and untouched; all post-archive operational fixes, CLI subcommands, and SDK upgrades are governed by this follow-up change.
- **Freezing `tdt/agent-core` and `tdt-core`**: The entire `~/Developer/tdt/agent-core` codebase, `tdt-core`, and `~/.tdt/` configuration directory remain strictly out of scope and frozen. Zero `shb/*` modules import `tdt` or read `~/.tdt/`.
- **No JavaScript/TypeScript `package.json` Manifests in `shb/*`**: All 13 repositories under `~/Developer/shb/*` are pure Python (`>=3.14`, `uv`-managed) packages (`0` `package.json` files exist across `shb/*`); no Node.js or frontend toolchains are introduced.
- **Never Bypassing Maker-Checker or Human Review Gates**: Transfers exceeding `50,000,000 VND` (`MAKER_CHECKER_THRESHOLD_VND`) unconditionally require supervisor approval token validation, and the 12-stage LangGraph harness `interrupt()` gate at `StageName.PLAN_REVIEW` remains inviolable.

### Affected Ownership Boundaries

This change spans all 13 SHB repositories (`~/Developer/shb/*`), the centralized OpenSpec store (`~/Developer/platform/openspec-store`), and the workspace knowledge base (`~/Developer/wiki`):
1. **`shb-core` (`ff05007`)**: Owns `ShbSettings.model_gateway_key` empty-string normalization and `OMNIROUTE_API_KEY` loopback fallback, `STAGE_DELIVERABLE_CITATION_QUESTIONS` refinement, `typesafe-sdk[http2]>=0.7.5` (`httpx2>=2.16.0`) upgrade, `Box` / `BoxCoordinates` / `BoxAnswer` / `Image` / `Asset` exports and fallback shims, `JevEvaluationResult.boxes`, `assets=...` attachment on `evaluate()` / `a_evaluate()`, and `get_sync_sdk_client()` / `get_async_sdk_client()` accessors.
2. **`shb-agent-core` (`120ae6c`)**: Owns `ShbAgent._bind_deps_to_tool_func()` (`deps.guardrail` and `deps.jev_client` binding into `@agent.tool_plain` tools with `**_kwargs` stripped from `__signature__`), `ShbAgent.run_async()`, `_format_live_result()` (`ToolCallPart` vs `ToolReturnPart` separation), `<field>_untrusted_text` PAN-masked injection preservation in `sanitize_invocation_state()`, `shb-agent evaluate` CLI subcommand, `resolve_typesafe_decision_model()` (`TypeSafeModel`, `TypeSafeModelSettings`, `TypeSafeProvider` on `pydantic-ai>=2.59.0`), and `Caching(retention=True, messages=True)`.
3. **`shb-agent-harness` (`2ea6e7f`)**: Owns `DualSqliteSaver(SqliteSaver)` (`asyncio.to_thread` async delegation for `aget_tuple`, `alist`, `aput`, `aput_writes`, `adelete_thread` alongside `AsyncSqliteSaver`), `HarnessRunner.a_run_all()` / `a_resume()`, `shb-harness plan --description/-d`, and structured stage governance IDs (`REQ-001`, `EVD-001`, `AC-001`, `DES-001`, `API-001`, `TASK-001`, `TC-001`, `VER-001`) on `langgraph>=1.2.16` and `langgraph-checkpoint-sqlite>=3.1.2`.
4. **`shb-ai-harness-skills` (`9feafff`)**: Owns `"classification" -> "clarify"` canonical stage mapping in `resolve_canonical_stage_name()`, `verify_stage_deliverable_evidence()` state projection across all 12 harness stages (including `api_contract` `not_applicable`), and `shb-harness-skills verify-deliverable` CLI subcommand.
5. **`shb-agent-skills` (`1c05758`)**: Owns `shb-skills match <query> [--top-k] [--category] [--no-jev]` CLI subcommand invoking two-stage `SkillMatcher().match_jev()`.
6. **`shb-observability` (`c51c58b`)**: Owns live Jev span rendering (`shb.jev.decision` table alongside `shb_jev_decisions_total`, `shb_jev_latency_ms`, and `shb_jev_total_tokens`) in `shb-observability show-metrics` and `doctor` on `opentelemetry-api/sdk>=1.45.1`.
7. **`shb-ai-review` (`d3310ec`)**: Owns `AiReviewConfig.load_configured_providers()` primary model selection (`settings.default_model` = `gemini-3.8-flash-high`) with opt-in `SHB_REVIEW_AI_SECONDARY_MODEL` isolation (preventing `SHB_FALLBACK_MODEL=Advance` HTTP 400 failures on OmniRoute), un-truncated file diff construction in `shb-ai-review scan --ai`, and `HunkGate.filter_findings()` + `MR_FINDING_CITATION_CONTRACT` enforcement across both `review-mr` and `scan --ai`.
8. **`shb-mcp-servers` (`395180c`)**: Owns PAN-masked `<field>_untrusted_text` preservation on account fields (`account_number`, `source_account`, `destination_account`, `beneficiary_account`) in `src/shb_mcp/tools.py:execute_tool` so prompt/SQL injections embedded in account numbers are blocked by Jev without leaking raw PAN digits.
9. **`shb-tools` (`4d20169`), `shb-schedule` (`649aa38`), `shb-webhook-receiver` (`5461ead`), `shb-browser-cli` (`3f618bd`), `shb-jira-tools` (`b0aebdc`)**: Own synchronized dependency lower bounds (`dbos>=3.3.0`, `fastapi>=0.159.1`, `python-gitlab>=8.6.0`, `pydantic>=2.14.1`, `ruff>=0.17.1`, etc.), `uv.lock` alignment with `shb-core[jev]`, and `[tool.mypy] strict = true` enforcement across all `13/13` SHB repositories.
10. **`platform/openspec-store` & `wiki`**: Own canonical specification `openspec/specs/jev-decision-runtime/spec.md`, archived change governance, and ecosystem knowledge documentation (`entities/shb.md`, `log.md`).

## What Changes

### 1. Live E2E Operational Fixes & CLI Subcommands Across 8 Jev-Integrated Repositories
- **`shb-core`**:
  - Adds `@field_validator("model_gateway_key", mode="after")` on `ShbSettings` (`src/shb_core/config.py`) to normalize empty `.env` strings (`SHB_MODEL_GATEWAY_KEY=`) and automatically fall back to `OMNIROUTE_API_KEY` from process environment or `~/.zshenv` (`0600` mode check) when `model_gateway_url` targets local loopback (`127.0.0.1` / `localhost`, unless `SHB_DISABLE_ENV_FILE_FALLBACK` is set).
  - Refines `STAGE_DELIVERABLE_CITATION_QUESTIONS` and `prompt_injection` criteria in `src/shb_core/decisions.py` to handle downstream planning stages and `api_contract` (`not_applicable`) deliverables and detect SQL/command/prompt injections embedded inside `<field>_untrusted_text`.
- **`shb-agent-core`**:
  - Adds `ShbAgent._bind_deps_to_tool_func(func, self.deps)` (`src/shb_agent/agent.py`) to bind active `deps.guardrail` and `deps.jev_client` into `@agent.tool_plain` functions (`pay_bill`, `parse_vietqr`, `screen_beneficiary`) while stripping `**_kwargs` from `wrapper.__signature__` so Pydantic AI tool schema generation never exposes internal dependency parameters.
  - Initializes `self.deps.guardrail = JevToolGuardrail(client=jev_client)` in `ShbAgent.__init__` so `@hooks.on.before_tool_execute` and direct tool bodies share a single `_pending_evaluations` deduplication cache.
  - Adds `ShbAgent.run_async()` and `_format_live_result()` (`ToolCallPart` vs `ToolReturnPart` separation) for async agent execution and clean CLI output formatting.
  - Updates `JevToolGuardrail.sanitize_invocation_state()` (`src/shb_agent/tools/guardrails.py`) to preserve `f"{key}_untrusted_text"` with digit runs masked via `mask_pan()` whenever an account/PAN field (`account_number`, `source_account`, `destination_account`, `beneficiary_account`) contains non-PAN injection text.
  - Adds `shb-agent evaluate <prompt> --output <output> [--expected <expected>] [--no-live]` CLI subcommand (`src/shb_agent/cli.py`).
- **`shb-agent-harness`**:
  - Implements `DualSqliteSaver(SqliteSaver)` (`src/shb_harness/workflow.py`) delegating `aget_tuple`, `alist`, `aput`, `aput_writes`, and `adelete_thread` via `asyncio.to_thread` (alongside `AsyncSqliteSaver` support) so both synchronous `HarnessRunner.run_all()` / `resume()` and asynchronous `await HarnessRunner.a_run_all()` / `a_resume()` work with `~/.shb/harness.db`.
  - Adds `--description` / `-d` to `shb-harness plan` (`src/shb_harness/cli.py`) and emits structured stage governance IDs (`REQ-001`, `EVD-001`, `AC-001`, `DES-001`, `API-001`, `TASK-001`, `TC-001`, `VER-001`) across the 12 stages.
- **`shb-ai-harness-skills`**:
  - Maps `"classification" -> "clarify"` in `resolve_canonical_stage_name()` (`src/shb_ai_harness/contracts.py`), updates `verify_stage_deliverable_evidence()` state projection across all 12 harness stages, and adds `shb-harness-skills verify-deliverable <stage> --summary ... [--artifact-id ...] [--evidence-id ...] [--no-jev]` (`src/shb_ai_harness/cli.py`).
- **`shb-agent-skills`**:
  - Adds `shb-skills match <query> [--top-k] [--category] [--no-jev]` CLI subcommand (`src/shb_skills/cli.py`) invoking two-stage `SkillMatcher().match_jev()`.
- **`shb-observability`**:
  - Updates `shb-observability show-metrics` and `doctor` (`src/shb_observability/cli.py`) to execute a live Jev probe when `JEV_ENABLED=true` and render recorded `shb.jev.decision` spans (`jev.model`, `jev.outcome`, `jev.total_tokens`) alongside `shb_jev_decisions_total`.
- **`shb-ai-review`**:
  - Updates `AiReviewConfig` and `load_configured_providers()` (`src/shb_review/ai/reviewer.py`) to use `settings.default_model` (`gemini-3.8-flash-high`) as primary (falling back to `get_settings().model_gateway_key.get_secret_value()`) and only add a secondary provider when `SHB_REVIEW_AI_SECONDARY_MODEL` is explicitly set (`secondary_model: str | None = None`), preventing `SHB_FALLBACK_MODEL=Advance` from failing closed with HTTP 400 on OmniRoute.
  - Removes the 50-line file truncation in `shb-ai-review scan --ai` (`src/shb_review/cli.py`) and gates both `scan --ai` and `ReviewerOrchestrator.run_review(files=..., use_ai=True)` through `HunkGate.filter_findings()` + `MR_FINDING_CITATION_CONTRACT`.
- **`shb-mcp-servers`**:
  - Updates `execute_tool` (`src/shb_mcp/tools.py:173-245`) to preserve `f"{arg_key}_untrusted_text"` with digit runs masked via `mask_pan()` whenever an account field (`account_number`, `source_account`, `destination_account`, `beneficiary_account`) contains non-PAN injection text, blocking prompt/SQL injections embedded in account numbers (`effective_risk=0.980 -> BLOCK`) without leaking raw PAN digits or mutating top-level response fields.

### 2. Dependency Modernization & `13/13` Strict Typing Across All 13 SHB Repositories
- Upgrades `pyproject.toml` lower bounds and synchronizes `uv.lock` (`uv lock --check` `13/13` pass, `0` `package.json` files in `shb/*`) across all 13 SHB repositories:
  - `typesafe-sdk[http2]>=0.7.5` (`0.7.5`), `httpx2>=2.16.0` (`httpcore2==2.16.0`)
  - `pydantic-ai>=2.59.0`, `pydantic-evals>=2.59.0` (`pydantic-graph==2.59.0`)
  - `pydantic>=2.14.1` (`pydantic-core==2.50.1`), `pydantic-settings[yaml]>=2.16.1`
  - `langgraph>=1.2.16`, `langgraph-checkpoint-sqlite>=3.1.2` (`langgraph-checkpoint==4.3.0`)
  - `opentelemetry-api>=1.45.1`, `opentelemetry-sdk>=1.45.1`
  - `python-gitlab>=8.6.0`, `dbos>=3.3.0`, `fastapi>=0.159.1`, `typer>=0.27.3`
  - `ruff>=0.17.1`, `pytest-mock>=3.17.0`, `pytest-asyncio>=1.4.0`
- Enables `[tool.mypy] strict = true` in `shb-jira-tools` and `shb-webhook-receiver` with full return-type annotations so all `13/13` SHB repositories pass `uv run mypy --strict --ignore-missing-imports src` (`0` issues).

### 3. Adoption of `typesafe-sdk 0.7.5` Spatial Grounding (`Box`/`Image`/`Asset`) and `pydantic-ai 2.59.0` Decision Model & Caching
- **`shb-core` (`src/shb_core/jev.py`, `src/shb_core/decisions.py`, `src/shb_core/__init__.py`)**:
  - Exports `Asset`, `Box`, `BoxAnswer`, `BoxCoordinates`, and `Image` from `typesafe-sdk 0.7.5` alongside single-source optional-dependency fallback shims when `typesafe-sdk` is absent.
  - Extends `JevEvaluationResult` with `boxes: dict[str, BoxAnswer] = Field(default_factory=dict)` and updates `evaluate()` / `a_evaluate()` to accept optional `assets: Sequence[Image | Asset] | None = None` (`attach_assets`), extracting `response.boxes` and lifting `BoxAnswer.box` (`BoxCoordinates | None`) onto plain Pydantic `BaseModel` `response_model` attributes.
  - Exposes public `get_sync_sdk_client()` and `get_async_sdk_client()` accessors on `JevDecisionClient`.
- **`shb-agent-core` (`src/shb_agent/model.py`, `src/shb_agent/agent.py`, `src/shb_agent/__init__.py`)**:
  - Implements `resolve_typesafe_decision_model()` integrating `pydantic_ai.models.typesafe.TypeSafeModel`, `TypeSafeModelSettings` (`decision_boolean_threshold`, `decision_route_threshold`, and `max_retries -> TypeSafeRetryPolicy` forwarding in `pydantic-ai>=2.59.0`), and `pydantic_ai.providers.typesafe.TypeSafeProvider` backed by `JevDecisionClient.get_async_sdk_client()`.
  - Enables `pydantic_ai.capabilities.Caching(retention=True, messages=True)` alongside `PrepareTools` on `ShbAgent`.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `jev-decision-runtime`: Updates existing requirements (`System One Decision Client`, `Configuration Management for Jev System One`, `Pre-Flight Tool Guardrail`, `State-Driven Graph Routing`, `Two-Stage Skill Candidate Selection`, `Non-Generative Evaluation Scorer`, `Centralized Question and Threshold Definitions`, `Decision Observability`, `HTTP/2 Transport Multiplexing`, `Pydantic AI Gateway Compatibility`, `Reusable Cross-Ecosystem Decision Contracts`) to incorporate the 10 live E2E operational fixes, 5 CLI subcommands, and `typesafe-sdk>=0.7.5` / `pydantic-ai>=2.59.0` lower bounds, and adds `Spatial Grounding Box Primitives and Pydantic AI Decision Model Integration`.

## Impact

- **Target Repositories (All 13 SHB Repositories)**:
  - `shb-core` (`ff05007`), `shb-agent-core` (`120ae6c`), `shb-agent-harness` (`2ea6e7f`), `shb-ai-harness-skills` (`9feafff`), `shb-agent-skills` (`1c05758`), `shb-observability` (`c51c58b`), `shb-ai-review` (`d3310ec`), `shb-mcp-servers` (`395180c`), `shb-tools` (`4d20169`), `shb-schedule` (`649aa38`), `shb-webhook-receiver` (`5461ead`), `shb-browser-cli` (`3f618bd`), `shb-jira-tools` (`b0aebdc`).
- **Verification Baseline**:
  - `443` passing tests across all 13 SHB repositories (`292` across the 8 Jev-integrated repos including opt-in live `test_live_typesafe_api_smoke` + `151` across the remaining 5 SHB repos), `13/13` `ruff check` pass, `13/13` `mypy --strict` pass, `13/13` `uv lock --check` pass, `0` compliance violations (`shb-compliance-scan`), and `IN_SYNC` documentation index (`shb-docs-sync`).
