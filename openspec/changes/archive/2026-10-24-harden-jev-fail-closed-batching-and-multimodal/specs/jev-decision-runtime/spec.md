# Spec Delta: jev-decision-runtime

## ADDED Requirements

### Requirement: Fail-Closed Required-Answer and Answer-Type Validation

The System One decision runtime (`shb-core`) and all downstream policy, guardrail, compliance, skill-matching, and citation-verification callers (`shb-agent-core`, `shb-mcp-servers`, `shb-ai-harness-skills`, `shb-ai-review`) SHALL validate that every requested question identifier is present in the response `answers` mapping and matches its expected answer kind (`noul`, `choice`, `score`, or `box`) before evaluating domain policy or returning `PROCEED`.

#### Scenario: Incomplete or wrong-kind response fails closed on guardrail and compliance evaluations
- **WHEN** `JevDecisionClient.evaluate()` or `await JevDecisionClient.a_evaluate()` completes an upstream `system_one` request with `require_all_answers=True` (the default), or when `evaluate_guardrail_policy()`, `await a_evaluate_guardrail_policy()`, `JevToolGuardrail`, `screen_beneficiary`, or `compliance_sanction_screen` evaluates a response whose `answers` mapping is empty, omits any requested question key, or returns a mismatched answer `type`
- **THEN** `JevDecisionClient` MUST raise `TypeSafeError` (and record an `"incomplete_response"` span attribute on `shb.jev.decision`) rather than silently substituting `default=0.0` or `default=1.0` via `noul_prob()`
- **AND** `evaluate_guardrail_policy()` and `await a_evaluate_guardrail_policy()` MUST catch the validation error inside their fail-closed handler and return `GuardrailOutcome.ESCALATE` (with `fail_closed_triggered=True` on `OPERATIONAL`, `FINANCIAL_TRANSFER`, and `COMPLIANCE_CRITICAL` tools, or whenever `fail_closed=True`) instead of computing all-zero risk (`effective_risk=0.0`, `certainty=1.0`) and returning `GuardrailOutcome.PROCEED`
- **AND** when an explicit caller-supplied `probabilities` mapping is passed to `evaluate_guardrail_policy(..., probabilities=...)`, it MUST reject empty mappings (`{}`) or non-finite values out of `[0.0, 1.0]` by failing closed while continuing to support partial non-empty probability dicts supplied by unit tests
- **AND** `JevEvaluationResult` MUST expose strict accessors (`require_noul_prob(key)`, `require_choice(key)`, `require_score(key)`, `require_box(key)`) that raise `TypeSafeError` when the requested key is missing or has a non-matching answer kind

#### Scenario: Incomplete citation or AML screening response fails closed
- **WHEN** `verify_stage_deliverable_evidence()` (`shb-ai-harness-skills`), `HunkGate.filter_findings()` (`shb-ai-review`), `screen_beneficiary()` (`shb-agent-core`), or `compliance_sanction_screen` (`shb-mcp-servers`) receives a partial response missing any required `Noul` answer or encounters a `TypeSafeError`
- **THEN** `screen_beneficiary()` and `compliance_sanction_screen` MUST fail closed to `clearance_status="FLAGGED_FOR_MANUAL_REVIEW"` (with `risk_score >= 75.0` and `"JEV_AML_FAIL_CLOSED"` in `matched_rules`) rather than suppressing the error and returning `"CLEARED"`
- **AND** `verify_stage_deliverable_evidence()` MUST return `is_valid=False` and `jev_passed=False` with a fail-closed error entry when `STAGE_DELIVERABLE_CITATION_CONTRACT.fail_closed` is `True`
- **AND** in `HunkGate.filter_findings()`, if `active_client.evaluate()` returns a response missing any required `MR_FINDING_CITATION_CONTRACT` answer (`grounded_in_diff`, `contains_speculative_language`, `contradicts_diff`), the AI finding MUST be treated as ungrounded (`ungrounded_ai_filtered += 1`) rather than defaulting `grounded_in_diff` to `1.0`, whereas transport timeouts or 5xx exceptions on `active_client.evaluate()` SHALL continue to fail open (`True`) so deterministic hunk checks stand

### Requirement: Batched Multi-Item Review Triage, Single-Pass AML Fan-Out, and Online Output Guardrails

The SHB ecosystem SHALL batch multi-file diff triage and multi-finding citation verification in `shb-ai-review` into parallel state-referenced `system_one` requests, unify pre-flight tool guardrails and semantic AML screening into a single speculative fan-out request across `shb-agent-core` and `shb-mcp-servers`, and provide an online output guardrail battery (`OUTPUT_GUARDRAIL_QUESTIONS`) combining hazard `Noul`s with a harm-severity `Score` rubric.

#### Scenario: Batched pre-flight diff hunk triage and post-generation citation filtering in shb-ai-review
- **WHEN** `AiReviewer.review_diff()` evaluates $N$ non-preserved diff files and `HunkGate.filter_findings()` verifies $M$ in-hunk AI-generated findings (`finding.source.startswith("ai:")`)
- **THEN** `AiReviewer.review_diff()` MUST evaluate all non-preserved diff files in a batched `system_one` request (`state={"hunks": {file_key: {"file_path": ..., "redacted_diff": ...}}}`, `questions={file_key: Noul(...)}`, chunking only if total state exceeds `28,000` tokens) rather than issuing $N$ sequential single-file HTTP requests, strictly requiring exact `file_key` answers for multi-hunk batches (allowing unprefixed `"requires_ai_review"` fallback only when a batch has `len == 1`) so an unprefixed response never skips multiple files in an MR
- **AND** `HunkGate.filter_findings()` MUST evaluate all $M$ in-hunk AI-generated findings in a single batched `system_one` request (`state={"hunks": ..., "findings": {idx_key: ...}}`, `questions={f"{idx_key}.{q_name}": Noul(...)}`) rather than issuing $M$ sequential HTTP requests, while transparently supporting unprefixed keys returned by single-item test mocks and preserving per-finding `MR_FINDING_CITATION_CONTRACT.is_grounded()` filtering (`grounded_in_diff >= 0.70`, `contradicts_diff < 0.50`, `contains_speculative_language < 0.70`)

#### Scenario: Single-pass combined guardrail and AML screening across agent and MCP tools
- **WHEN** `screen_beneficiary` in `shb-agent-core` (`src/shb_agent/tools/compliance.py`, invoked directly or via `ShbAgent`'s `@hooks.on.before_tool_execute`) or `compliance_sanction_screen` in `shb-mcp-servers` (`src/shb_mcp/tools.py`) executes with Jev enabled
- **THEN** `JevToolGuardrail` and `evaluate_guardrail_policy()` / `a_evaluate_guardrail_policy()` MUST evaluate `COMBINED_AML_GUARDRAIL_QUESTIONS` (`GUARDRAIL_QUESTIONS | AML_SCREENING_QUESTIONS`: 6 `Noul` questions in one `system_one` request, attaching `aml_probabilities` on `GuardrailEvaluationResult`) whenever the tool is `screen_beneficiary` or `compliance_sanction_screen`
- **AND** both `screen_beneficiary` and `compliance_sanction_screen` MUST consume the single evaluation result without issuing a second Jev request, rejecting the request (`clearance_status="REJECTED"`, `risk_score=100.0`) when `prompt_injection` triggers `GuardrailOutcome.BLOCK` and escalating to `FLAGGED_FOR_MANUAL_REVIEW` when `max(aml_probabilities.values()) >= AML_ESCALATION_THRESHOLD` (`0.50`)

#### Scenario: Online output guardrail screening and two-stage skill suggestion gating
- **WHEN** `evaluate_output_guardrail()` (`shb_core.decisions` and `JevToolGuardrail.evaluate_output()`) screens an outgoing assistant reply, or `SkillMatcher.match_jev()` / `a_match_jev()` reranks shortlisted skills
- **THEN** `evaluate_output_guardrail()` MUST evaluate `OUTPUT_GUARDRAIL_QUESTIONS` (4 hazard `Noul`s: `broke_policy`, `unmasked_pan_or_secret_leak`, `unauthorized_financial_commitment`, `harmful_or_illegal_assistance`, plus 1 `Score` question `harm_severity` with 4 ordered levels `0..3`) in one `system_one` request and return `GuardrailOutcome.BLOCK` or `GuardrailOutcome.ESCALATE` when any hazard or severity threshold fires
- **AND** `SkillMatcher.match_jev()` and `a_match_jev()` MUST support a companion `"needs_any_skill"` gate `Noul` and `min_probability: float = 0.0` (with `--min-prob` on `shb-skills match`) that filters out candidates below `min_probability` or returns `[]` when `"needs_any_skill"` is below the gate threshold when gating is enabled

### Requirement: Complete Upstream Multimodal Box/Image Headers, Long Context, and TypeSafeProvider Pooling

The foundation client (`shb-core`), banking agent runtime (`shb-agent-core`), and browser CLI (`shb-browser-cli`) SHALL automatically send upstream's `TypeSafe-Danger-Zone-Images` and `TypeSafe-Danger-Zone-Long-Context` headers, preserve `Image` objects in `sanitize_jev_state`, pair `Box` spatial grounding questions with companion presence `Noul`s, share `JevDecisionClient.get_async_sdk_client()` with `TypeSafeProvider`, and expose `DecisionHandOff` SDE cascades.

#### Scenario: Automatic Danger-Zone headers, Image-safe state sanitization, and opt-in 262k Long Context
- **WHEN** `JevDecisionClient.evaluate()` or `await JevDecisionClient.a_evaluate()` is called with `assets`, an `Image` object inside `state` or `questions`, or any `Box` question, or when `long_context=True` (or `settings.jev.long_context=True`) is enabled
- **THEN** `sanitize_jev_state()` MUST preserve `Image` instances untouched (using a lightweight placeholder when estimating JSON character length so binary image payloads are never stringified or truncated) and `JevDecisionClient` MUST automatically merge `"TypeSafe-Danger-Zone-Images": "true"` into `extra_headers`
- **AND** when `long_context=True` is active, `JevDecisionClient` MUST merge `"TypeSafe-Danger-Zone-Long-Context": "true"` into `extra_headers` and raise the state sanitization ceiling from `32,000` tokens to `262,000` tokens

#### Scenario: Multimodal Box spatial grounding paired with companion presence Noul in banking tools and browser CLI
- **WHEN** a caller localizes a visual target (such as a VietQR code via `locate_vietqr_region` in `shb-agent-core` or a document/signature/table region via `DocumentExtractor.locate_visual_region` and `shb-browser-cli locate-region` in `shb-browser-cli`) using `build_box_grounding_questions(target_key, image_ref, description)` and `extract_grounded_box(eval_res, target_key, presence_threshold=0.5, min_confidence=0.6, pad=0.05)`
- **THEN** the request MUST pair `<target_key>` (`Box(instructions=...)`) with a companion `<target_key>_present` (`Noul(instructions=...)`) in the same `system_one` call because `typesafe-sdk>=0.7.5` `BoxAnswer` (`type: "box"`, `box: BoxCoordinates(top, bottom, left, right)`, `confidence: float | None`) always returns four normalized edges without a `present` field
- **AND** `extract_grounded_box()` MUST return `GroundedBoxResult(present=False, box=None, ...)` when `<target_key>_present` probability is `< presence_threshold` (`0.5`), and when present with `confidence < min_confidence` (`0.6`) and `pad > 0.0`, pad `top`, `bottom`, `left`, `right` outward within `[0.0, 1.0]`

#### Scenario: TypeSafeProvider client pool sharing and DecisionHandOff SDE cascade
- **WHEN** `resolve_typesafe_decision_model()` or `create_typesafe_sde_cascade_chain()` in `shb-agent-core` (`src/shb_agent/model.py`) constructs a `TypeSafeModel`
- **THEN** `resolve_typesafe_decision_model()` MUST pass `typesafe_client=active_jev.get_async_sdk_client()` into `TypeSafeProvider(typesafe_client=...)` whenever `active_jev` has a resolved credential or custom transport, so `TypeSafeModel` shares `JevDecisionClient`'s HTTP/2 connection pool, custom mock transports, and `effective_compression` configuration
- **AND** `create_typesafe_sde_cascade_chain()` MUST construct a `FallbackModel(typesafe_model, primary_llm, *fallback_llms, fallback_on=DecisionHandOff)` cascade that escalates uncertain System One decisions (`DecisionHandOff`) to the generative fallback model
