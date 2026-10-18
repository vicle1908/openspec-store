# Proposal

## Why

Discrete decision-making in multi-agent workflows currently incurs excessive latency and cost by forcing full autoregressive LLM generations, or relies on brittle regex patterns for split-second choices. In `agent-core`, tool authorization guards, LangGraph conditional branching, skill dispatch, and evaluation scoring repeatedly either pay seconds of token generation overhead or fall back to rigid pattern matching that misses obfuscated commands.

TypeSafe's Jev is a System One model: it evaluates typed questions against a state and returns typed values and calibrated probabilities that code can branch on directly — no text generation, no parsing, no output-token cost. Adopting it equips `agent-core` with fast semantic pre-flight guardrails, deterministic graph routing, candidate skill reranking, and fast evaluation judges, while staying fully decoupled from streaming chat protocols.

## What Changes

- **Add a System One decision client to `agent-core`** using the official `typesafe-sdk` (`TypeSafeClient` / `AsyncTypeSafeClient` and its `system_one` method), with a typed `JevSettings` (`JEV_` prefix) in `agent_core.foundation.settings`, safe `request_id` extraction (handling absent `x-typesafe-request-id` response headers), and credential resolution supporting `TYPESAFE_API_KEY` and explicit `PYDANTIC_AI_GATEWAY_API_KEY` fallbacks.
- **Support HTTP/2 transport multiplexing (`typesafe-sdk[http2]`)** with explicit timeout propagation (`httpx2.AsyncClient(http2=True, timeout=timeout)` / `httpx2.Client(http2=True, timeout=timeout)`) to avoid default 5.0s client fallbacks, and expose client lifecycle (`close()` / `aclose()` and context managers) for sub-200ms decision paths.
- **Model the three real primitives.** TypeSafe exposes `Noul` (yes/no probability), `Choice`, and `Score`. There is no boolean primitive; a yes/no judgment is a `Noul`, whose single probability carries both answer and certainty.
- **Support typed Pydantic response models** via the SDK's native `response_model` parameter subclassing `SystemOneResponse` (whose `_decode()` lifts `answers[field]` onto model attributes, unlike plain `BaseModel` which validates un-lifted wire JSON), ensuring end-to-end schema validation aligned with `agent-core`'s Pydantic AI foundation.
- **Support Pydantic AI Gateway proxying** (`PYDANTIC_AI_GATEWAY_API_KEY` / `TYPESAFE_BASE_URL`) alongside direct TypeSafe endpoints with explicit gateway key fallback resolution in `JevDecisionClient`, enabling unified gateway governance across `agent-core` and sister ecosystems.
- **Semantic pre-flight tool guardrail** in `agent_core.tool_registry.guardrails`: one atomic `Noul` per destructive condition, combined by code with code-controlled weights, gated by a confidence threshold scaled to the invocation's risk class. It catches obfuscated commands that bypass regex, without generation latency, and never bypasses human approval.
- **Confidence-gated graph routing** in `agent_core.orchestration.graph`: an async-safe `Choice`-based conditional router (`async def`) directly awaiting `AsyncTypeSafeClient` / `a_evaluate` within LangGraph's event loop, treating confidence as a second decision axis so low-confidence answers escalate rather than silently selecting the highest-probability branch.
- **Per-candidate skill reranking** in `agent_core.skill_system.matcher`: one `Noul` per query-candidate pair, ordered by the returned probability, replacing the design's single-choice comparison across candidates.
- **Non-generative evaluation scorers**: `JevEvaluator` scoring independent rubric dimensions and composing them in code, compatible with `agent_core.observability.scorers.runner`.
- **Ecosystem capability contracts**: Clean abstractions that allow downstream consumers (such as `shb-agent-core` and `shb-agent-harness` for banking guardrails, AML screening, and LangGraph 12-stage conditional skip routing) to consume System One decisions without duplicating transport logic.
- **One reviewable decision module** holding every question, criterion, weight, and threshold, so judgments can be reviewed and retuned without editing the logic that consumes them.
- **Fail-closed degradation**: when the credential is absent or the service is unreachable, security-critical checks fail closed to the existing authority checks and blocklists, while skills and evaluations fall back to lexical/vector logic.
- **BREAKING**: none. Jev is additive and optional; every existing generative path is preserved.

### Non-Goals

- Modifying `tdt-core.provider_model_profile.ProviderProtocol`, which remains dedicated to streaming generative backends. Jev emits no tokens.
- Replacing human-in-the-loop approval (`ApprovalMode.AUTHENTICATED_SUBJECT`). Jev is an early risk classifier, never an approval bypass.
- Generating free-form text or explainability prose.
- Validating live decision quality. This change delivers the integration and its fail-closed behavior; thresholds require calibration against real traffic, which is explicitly deferred.

## Capabilities

### New Capabilities

- `jev-decision-runtime`: Owns the System One decision client, its settings and credential handling, the pre-flight tool guardrail, confidence-gated graph routing, per-candidate skill reranking, the non-generative evaluation scorer, the centralized question/threshold definitions, and decision observability.

### Modified Capabilities

None. The affected `agent-core` subsystems gain an optional decision path behind a disabled-by-default setting; no existing requirement's behavior changes for callers that do not enable it.

## Impact

- **Target repository**: `~/Developer/tdt/agent-core` (`agent_core` package). Source tree is clean; the only working-tree changes are generated `graphify-out/*` artifacts.
- **New dependency**: `typesafe-sdk` (0.7.2, verified resolvable via `uv`). Optional; the runtime must operate with the package absent or the feature disabled.
- **Files**: `agent_core/foundation/jev.py` and settings additions; `agent_core/tool_registry/guardrails.py`; `agent_core/orchestration/graph.py`; `agent_core/skill_system/matcher.py`; `agent_core/observability/scorers/jev_scorer.py`; a centralized decision-questions module; tracing additions; tests.
- **Credentials**: requires `TYPESAFE_API_KEY` (or `PYDANTIC_AI_GATEWAY_API_KEY`). **Not present on this machine**, so live-path verification is deferred to the operator. Mock and fail-closed paths are fully verifiable now.
- **Regression & Typing risk**: measured against the existing suite — 916 tests, 0 failures, 0 errors, 11 skipped (recorded baseline) — plus Ruff `TC001`/`TC002` and `mypy --strict` compliance across `src/agent_core/**` with `TYPE_CHECKING` guards and `# noqa: TC001, TC002` on runtime Pydantic response models.
- **Operational**: TypeSafe enforces a 64k-token request budget, a 32k budget for state plus the longest question, and rate limits that the SDK retries with backoff. Debug-level SDK wire logging emits raw request bodies, so `typesafe_sdk` logging MUST be clamped to `>= logging.INFO` (or filtered) and state projections sanitized with `_redact_secret_value` (<32k tokens).
