# Design: Jev Decision Runtime

## Context

See `proposal.md` — Why.

The design is written against the **current** TypeSafe API, verified during implementation planning:

- Primitives are `Noul` (yes/no probability), `Choice`, and `Score`. There is no boolean primitive; a yes/no judgment is a `Noul`, and a `Noul` answer carries no separate `confidence` field because its single probability $p \in [0.0, 1.0]$ expresses both answer and certainty (normalized certainty is derived as $|2p - 1|$).
- The official SDK is `typesafe-sdk` (0.7.2): `TypeSafeClient` / `AsyncTypeSafeClient` with `client.system_one(state, questions, ...)`. Answers are read through typed accessors (`response.nouls`, `.choices`, `.scores`), the `answers` map, or a `response_model`.
- `Choice` answers carry `probabilities` and a derived `confidence` on a 0-to-1 scale; `Score` answers evaluate state against $N$ ordered levels ($0 \dots N-1$) returning expected values in $[0.0, N-1]$ along with distribution probabilities and confidence. The response also reports the versioned `model` that answered and a `request_id`.
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

The client wraps `typesafe-sdk` instead of posting to `/v1/systemone` directly. The SDK supplies typed questions and answers, retry-with-backoff honouring rate-limit signalling, and error objects carrying status and request id.

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

`JevSettings` configures the model identifier, timeout, retry policy, and fail-closed behavior. The credential comes from `TYPESAFE_API_KEY`, and a key found in the layered YAML is stripped with a warning.

**Alternative considered:** hold the key in `JevSettings`. Rejected — it would put a secret in the application settings surface, contradicting the existing secret-isolation convention.

### D8: Pin the model identifier once thresholds exist

The default is a pinned `jev-1.13.0` rather than `jev-latest`, because the response's `model` field is the only way to attribute a decision to a version and a moving alias would silently change calibrated behavior.

**Alternative considered:** follow `jev-latest` for automatic improvements. Rejected for the guardrail, where an unreviewed behavior change is unacceptable; acceptable for exploratory, non-gating uses.

### D9: Fail closed for security, fall back for the rest

When the credential is absent or the service is unreachable, a high-authority tool invocation falls through to the existing authority checks and blocklists and does not execute unreviewed. Skill reranking and evaluation fall back to their previous ordering and scoring, because a wrong skill ranking is recoverable and a wrongly executed command is not.

**Alternative considered:** fail closed everywhere. Rejected — it would make the evaluator and matcher brittle for no safety gain.

## Risks / Trade-offs

- **[No credential, so the live path is unverified]** → The mock and fail-closed paths are unit-tested now; the live path is verified when the operator supplies a key, and this is recorded as an open item rather than assumed working.
- **[Thresholds are uncalibrated]** → Thresholds live in one module, are disabled by default, and the guardrail escalates in the uncertain band instead of acting.
- **[An unavailable service degrades tool security]** → Mitigation: fail-closed behavior keeps the existing authority checks authoritative.
- **[Alias drift changes decisions silently]** → Mitigation: pin the model identifier, and record the answering model from each response.
- **[Request budget exceeded by a large state]** → Mitigation: the guardrail sends a bounded projection of the invocation, not the whole conversation; state plus the longest question must fit the 32k budget.
- **[Debug logging emits state bodies]** → The SDK redacts secret headers but not bodies. Mitigation: never place credentials in `state`, and keep the SDK logger below debug in normal operation.
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
