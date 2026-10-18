# Design: Jev Decision Runtime

## Context

See `proposal.md` — Why.

The design is written against the **current** TypeSafe API, verified during implementation planning:

- Primitives are `Noul` (yes/no probability), `Choice`, and `Score`. There is no boolean primitive; a yes/no judgment is a `Noul`, and a `Noul` answer carries no separate `confidence` field because its single probability $p \in [0.0, 1.0]$ expresses both answer and certainty (normalized certainty is derived as $|2p - 1|$).
- The official SDK is `typesafe-sdk` (0.7.2): `TypeSafeClient` / `AsyncTypeSafeClient` with `client.system_one(state, questions, ...)`. Answers are read through typed accessors (`response.nouls`, `.choices`, `.scores`), the `answers` map, or a `response_model`.
- `Choice` answers carry `probabilities` and a derived `confidence` on a 0-to-1 scale; `Score` answers evaluate state against $N$ ordered levels ($0 \dots N-1$) returning expected values in $[0.0, N-1]$ along with distribution probabilities and confidence. The response also reports the versioned `model` that answered and a `request_id`. Note that in `typesafe-sdk` 0.7.2 (`typesafe_sdk/_core/schemas/base.py:67-73`), `SystemOneResponse.request_id` raises `TypeSafeError("The response did not include a request ID.")` when the `x-typesafe-request-id` HTTP response header is absent. `JevDecisionClient` MUST safely extract `request_id` (catching `TypeSafeError` or reading `raw_http_response.headers.get("x-typesafe-request-id")` with a `None`/`""` fallback when absent).
- Every question in a request sees the same `state` and is evaluated in parallel and in isolation. Asking several questions in one request barely changes latency — the documented fan-out benchmark is 13 batched questions at roughly 11.5x lower cost and 9.6x lower latency than 13 separate calls.
- Request budget is 64k tokens (state plus all questions), or 32k for state plus the longest question. Text only; English is the strongest language.
- Model `jev-1.13.0` is current, behind the aliases `jev-latest` and `jev-preview`. An alias moves between releases, so the response's versioned `model` field must be recorded.
- The credential is `TYPESAFE_API_KEY`. A missing key raises `TypeSafeError` during client construction; an invalid, revoked, or unauthorized key raises `TypeSafeAuthenticationError` on the first API call.
- An official agent skill ships current guidance (`typesafe-ai/skills`); it has been installed into the workspace so this design can be checked against live docs rather than recalled.

**Constraint:** no `TYPESAFE_API_KEY` exists on this machine yet. The full decision path is therefore designed and unit-tested against a mock transport, and the live path is explicitly deferred.

## Goals / Non-Goals

### Goals

- Give `agent-core` a sub-second, typed decision layer that returns values code can branch on, with no generated text and no output-token cost.
- Make every security-relevant decision fail closed and escalate rather than guess.
- Keep every question, weight, and threshold in one reviewable place.

### Non-Goals

- Calibrating thresholds against real traffic. This design fixes the mechanism and the place thresholds live; picking their values requires data.
- Streaming, free-form generation, or explainability prose.
- Any change to generative provider routing.

## Decisions

### D1: Use the official SDK rather than direct HTTP

The client wraps `typesafe-sdk` instead of posting to `/v1/systemone` directly. The SDK supplies typed questions and answers, retry-with-backoff honouring rate-limit signalling, and error objects carrying status and request id. The client wrapper encapsulates safe `request_id` extraction, catching `TypeSafeError("The response did not include a request ID.")` or safely probing `raw_http_response.headers.get("x-typesafe-request-id")` with a `None`/`""` fallback when headers are stripped by intermediaries or omitted by mock transports.

**Alternative considered:** direct HTTP. Rejected — it would reimplement retry, error mapping, and typing, and would drift from the published contract.

### D2: Model a yes/no judgment as a `Noul`, never a boolean

There is no boolean primitive. A `Noul` returns a probability, which means the caller receives answer and certainty together and can choose its own threshold. A boolean-shaped wrapper around a `Noul` would discard exactly the information the guardrail needs.

**Alternative considered:** coerce `Noul` to `bool` at the client boundary. Rejected — it forces a threshold inside the client, hiding a policy decision that belongs to the caller.

### D3: One atomic question per condition; combine in code

Each destructive condition is its own `Noul`, and the code combines probabilities with weights the code owns. Compound questions degrade on this class of model, and separate questions keep each judgment independently reviewable and independently tunable.

**Alternative considered:** a single question such as "is this destructive?" Rejected — it collapses conditions that carry different risk, and a single probability cannot express which condition fired.

### D4: Risk-scaled confidence thresholds, with escalation between the extremes

The guardrail uses three outcomes rather than two: act when the combined risk is clearly below the threshold for the invocation's risk class, block or require approval when clearly above, and escalate to human review in between. `confidence` is the second axis — the answer says *what*, the confidence says *whether to act*.

**Alternative considered:** a single global threshold. Rejected — the consequences of a wrong call differ sharply between a read-only and a destructive invocation.

**Alternative considered:** treat any nonzero risk as blocking. Rejected — it would make the guardrail unusable and push callers to disable it.

### D5: Reranking scores each candidate independently

The matcher asks one `Noul` per query-candidate pair and orders by the returned probability. Independent pair scoring is what makes scores comparable; a single choice across candidates makes them compete inside one question and loses the ordering signal.

**Alternative considered:** one `Choice` over the candidate list. Rejected — it yields a winner but not a calibrated ordering, and the shortlist is deliberately larger than the number of candidates worth choosing between.

### D6: Centralize questions, criteria, weights, and thresholds

Every judgment definition lives in one module. Official guidance is explicit that questions and thresholds are the reviewable artifact, and that they benefit from collaborative editing rather than being buried in consuming logic.

**Alternative considered:** define questions next to each consumer. Rejected — it scatters the policy surface a reviewer must inspect.

### D7: The credential is transport config, not application settings

`JevSettings` configures the model identifier, timeout, retry policy, base URL, and fail-closed behavior. The credential comes from `TYPESAFE_API_KEY` (or explicit `PYDANTIC_AI_GATEWAY_API_KEY` fallback), and a key found in the layered YAML is stripped with a warning. Because `typesafe_sdk._core.config.resolve_and_validate_api_key()` only inspects the explicit `api_key` argument or `os.environ.get("TYPESAFE_API_KEY")`, `JevDecisionClient` MUST explicitly resolve `api_key = api_key or os.environ.get("TYPESAFE_API_KEY") or os.environ.get("PYDANTIC_AI_GATEWAY_API_KEY")` and pass `api_key` and `base_url=settings.jev.base_url or os.environ.get("TYPESAFE_BASE_URL") or None` into `TypeSafeClient` / `AsyncTypeSafeClient`.

**Alternative considered:** hold the key in `JevSettings`. Rejected — it would put a secret in the application settings surface, contradicting the existing secret-isolation convention.

### D8: Pin the model identifier once thresholds exist

The default is a pinned `jev-1.13.0` rather than `jev-latest`, because the response's `model` field is the only way to attribute a decision to a version and a moving alias would silently change calibrated behavior.

**Alternative considered:** follow `jev-latest` for automatic improvements. Rejected for the guardrail, where an unreviewed behavior change is unacceptable; acceptable for exploratory, non-gating uses.

### D9: Fail closed for security, fall back for the rest

When the credential is absent or the service is unreachable, a high-authority tool invocation falls through to the existing authority checks and blocklists and does not execute unreviewed. Skill reranking and evaluation fall back to their previous ordering and scoring, because a wrong skill ranking is recoverable and a wrongly executed command is not.

**Alternative considered:** fail closed everywhere. Rejected — it would make the evaluator and matcher brittle for no safety gain.

### D10: Support HTTP/2 transport multiplexing via `typesafe-sdk[http2]`

The integration specifies `typesafe-sdk[http2]` to leverage persistent HTTP/2 connection multiplexing in `AsyncTypeSafeClient` and `TypeSafeClient` via `httpx2.AsyncClient(http2=True, timeout=timeout)` / `httpx2.Client(http2=True, timeout=timeout)` when no custom `transport` override is supplied (as `transport` and `http_client` are mutually exclusive in `typesafe_sdk`). Multiplexing removes per-request TCP/TLS handshake round trips and avoids socket churn under rapid tool or graph evaluations, keeping decision round-trips strictly within the sub-200ms envelope. Crucially, when `http2=True` and `transport is None`, `JevDecisionClient` must pass the resolved timeout to `httpx2.AsyncClient` / `httpx2.Client` as well as the SDK client so `httpx2` does not fall back to its internal 5.0s default timeout. In addition, `JevDecisionClient` MUST expose `close()` / `aclose()` methods and implement sync/async context managers (`__enter__`/`__exit__`, `__aenter__`/`__aexit__`) delegating to the underlying SDK client lifecycle.

**Alternative considered:** default HTTP/1.1 keep-alive only. Rejected — HTTP/2 provides superior multiplexing and lower latency when multiple tool calls or graph evaluations occur in quick succession behind local or network proxies.

### D11: Native Pydantic response models for typed decision validation

The client leverages TypeSafe's native `response_model` parameter accepting subclasses of `SystemOneResponse` (or Pydantic `BaseModel`). In `typesafe-sdk` 0.7.2 (`typesafe_sdk/_core/schemas/base.py:84-99`, `response_types.py:72-123`), `SystemOneResponse._decode()` lifts `decoded["answers"][field]` onto top-level model attributes and attaches `_request_id` and `raw_http_response`, whereas a plain `pydantic.BaseModel` passed to `parse_response()` validates raw wire JSON (`{"model": ..., "answers": {...}, "usage": ...}`) without lifting answer fields. Therefore, custom typed response schemas declaring top-level question fields MUST subclass `SystemOneResponse` (or `JevDecisionClient` must normalize/lift `answers` when a plain `BaseModel` is supplied). Callers can declare strongly typed schemas for their expected question sets (e.g. `ToolGuardResponse`, `GraphRoutingResponse`) and receive structured, validated objects rather than indexing raw dictionaries.

**Alternative considered:** unvalidated dictionary access only (`result.nouls[...]`). Rejected — while low-level access remains supported, typed Pydantic models eliminate key typo bugs and align directly with `agent-core`'s Pydantic AI foundation.

### D12: Support Pydantic AI Gateway and enterprise proxy endpoints

In addition to direct TypeSafe endpoints via `TYPESAFE_API_KEY`, the client configuration supports Pydantic AI Gateway proxies via `PYDANTIC_AI_GATEWAY_API_KEY` and `TYPESAFE_BASE_URL` (`https://gateway-us.pydantic.dev/proxy/typesafe` or local gateway). Because `typesafe_sdk._core.config.resolve_and_validate_api_key()` does not automatically recognize `PYDANTIC_AI_GATEWAY_API_KEY`, `JevDecisionClient` explicitly resolves the key and configures `base_url` on client instantiation, enabling centralized enterprise governance, rate-limiting, and cost tracking across agent fleets.

**Alternative considered:** hardcoded TypeSafe cloud URL. Rejected — prevents using local enterprise AI gateways or Pydantic AI Gateway proxies.

### D13: Establish cross-ecosystem consumer contracts for downstream reuse

Design the decision client and guardrail primitives as cleanly decoupled components so that sister repositories — specifically `shb-agent-core` (banking maker-checker gates, AML sanction screening pre-flight), `shb-agent-harness` (12-stage LangGraph conditional skip routing), and `ai-review` (fast diff classification) — can import or mirror the exact decision contracts without rewriting transport or retry logic.

**Alternative considered:** ad-hoc implementations in each repository. Rejected — duplicates question definitions, retry logic, and fallback behaviors across repositories.
### D14: Async-safe LangGraph conditional routing

In `agent_core.orchestration.graph` (`src/agent_core/orchestration/graph.py:312-405`), `WorkflowEngine.run()` and `resume()` invoke `await compiled.ainvoke(...)` inside an active asyncio event loop. The conditional router wired via `graph.add_conditional_edges` in `WorkflowEngine._wire_edges` MUST be an `async def` routing function invoking `AsyncTypeSafeClient` / `JevDecisionClient.a_evaluate` directly, never calling `asyncio.run()` or blocking synchronous operations inside an active event loop.


## Risks / Trade-offs

- **[No credential, so the live path is unverified]** → The mock and fail-closed paths are unit-tested now; the live path is verified when the operator supplies a key, and this is recorded as an open item rather than assumed working.
- **[Thresholds are uncalibrated]** → Thresholds live in one module, are disabled by default, and the guardrail escalates in the uncertain band instead of acting.
- **[An unavailable service degrades tool security]** → Mitigation: fail-closed behavior keeps the existing authority checks authoritative.
- **[Alias drift changes decisions silently]** → Mitigation: pin the model identifier, and record the answering model from each response.
- **[Request budget exceeded by a large state]** → Mitigation: the guardrail sends a bounded projection of the invocation (<32k tokens), not the whole conversation; state plus the longest question must fit the 32k budget. Invocation states are sanitized using `_redact_secret_value` from `agent_core.foundation.tracing`.
- **[Debug logging emits unredacted wire content]** → In `typesafe_sdk._core.transport.RequestState._log_wire`, `request.content` is logged unredacted when `logging.getLogger("typesafe_sdk")` is at `DEBUG`. Mitigation: the runtime MUST clamp `logging.getLogger("typesafe_sdk")` to `>= logging.INFO` (or attach a body-redacting logging Filter), never place credentials in `state`, and apply `_redact_secret_value` from `agent_core.foundation.tracing` when projecting bounded tool invocation state (<32k tokens).
- **[Strict typing & Ruff TC001/TC002 compliance]** → `src/agent_core/**` enforces Ruff `TC001`/`TC002` and `mypy --strict`. Mitigation: type-only imports placed under `if TYPE_CHECKING:`, optional `typesafe_sdk` imports safely guarded against runtime absence, and Pydantic `SystemOneResponse` runtime field annotations tagged with `# noqa: TC001, TC002`.
- **[Guardrail latency on the critical path]** → A network round trip adds latency to every guarded invocation. Mitigation: a bounded timeout with fail-closed behavior, one batched request rather than several, and a circuit breaker that stops calling a failing service.

## Migration Plan

1. Add the optional dependency and confirm resolution.
2. Implement settings and the decision client with a mock transport, and unit-test the success, timeout, missing-credential, and invalid-credential paths.
3. Implement the centralized question and threshold module.
4. Implement the guardrail and wire it into tool execution, disabled by default.
5. Implement routing, reranking, and the evaluator.
6. Add tracing attributes and confirm no state body is logged.
7. Run the full suite and compare against the recorded 916-test baseline; any new failure is a regression to fix, not to accept.

**Rollback:** the feature is disabled by default and additive; disabling the setting restores the prior behavior with no code change. The dependency can be dropped without touching existing paths.

## Open Questions

- What confidence thresholds should the guardrail use per `AuthorityClass`? Deferrable: the mechanism is fixed and the values are deliberately left to calibration against real traffic, which does not change the specs, approach, or task breakdown.
