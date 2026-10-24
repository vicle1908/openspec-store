# Design: Harden Jev System One Fail-Closed Answer Validation, Speculative Batching, Multimodal Grounding, and Full Feature Adoption

## Context

See `proposal.md` for motivation and root-cause analysis. Our senior-level review (`ponytail-review`) of the initial plan against all 8 SHB Jev repositories and their 259 existing unit tests surfaced 6 concrete design refinements that must be baked into the implementation:

1. **Distinguish Live Client Responses (`probabilities is None`) from Synthetic Partial Test Dicts (`probabilities={...}`)**:
   - In `shb_core/tests/test_decisions.py:119-139`, `test_risk_scaled_gating_across_all_authority_classes()` calls `evaluate_guardrail_policy("test_tool", authority_class=auth_cls, probabilities={"prompt_injection": proceed_p, "structuring_risk": 0.01})` with only 2 of the 4 keys.
   - Therefore, when `probabilities is None` (live/mocked `JevDecisionClient` evaluation), `_validate_response_answers()` and `require_noul_prob()` MUST require every requested question key in `questions` (`GUARDRAIL_QUESTIONS`). When `probabilities` is explicitly passed as a Python mapping, `evaluate_guardrail_policy()` MUST require `len(probabilities) >= 1` and validate that every provided value is a finite `float` in `[0.0, 1.0]` (failing closed on `{}` or `NaN`/out-of-range values while preserving 2-key unit-test fixtures).
2. **Eliminate Sync/Async Guardrail Duplication (`a_evaluate_guardrail_policy`) & Shared `<field>_untrusted_text` Sanitization**:
   - `JevToolGuardrail.a_evaluate_invocation()` (`shb_agent/tools/guardrails.py:263-330`) currently duplicates 55 lines of `evaluate_guardrail_policy()` and passes `probabilities=probs` into `evaluate_guardrail_policy()`, bypassing `evaluate_guardrail_policy()`'s `try/except` block. Adding `a_evaluate_guardrail_policy()` in `shb_core/decisions.py` (sharing `_compose_guardrail_result_from_eval()` with `evaluate_guardrail_policy()`) lets `JevToolGuardrail.a_evaluate_invocation()` delegate directly to `await a_evaluate_guardrail_policy(...)` in ~15 lines.
   - Similarly, moving the `<field>_untrusted_text` PAN-masked injection preservation loop into `sanitize_jev_state()` in `shb_core/jev.py` eliminates duplicate loops in `shb_agent/tools/guardrails.py:104-111` and `shb_mcp/tools.py:214-224`.
3. **Hook + Tool Body Single-Call Parity for `screen_beneficiary` (`COMBINED_AML_GUARDRAIL_QUESTIONS`)**:
   - In `shb_agent/agent.py:196-208`, `@hooks.on.before_tool_execute` runs `await active_guardrail.a_evaluate_invocation("screen_beneficiary", args, _record_for_tool_body=True)` before `screen_beneficiary()` runs. If `a_evaluate_invocation` only asks `GUARDRAIL_QUESTIONS` (4 questions), `screen_beneficiary()` would still have to make a second Jev call for `AML_SCREENING_QUESTIONS` (2 questions).
   - Solution: Whenever `clean_tool in {"screen_beneficiary", "compliance_sanction_screen"}` (or `include_aml=True`), `evaluate_guardrail_policy()` and `a_evaluate_guardrail_policy()` automatically ask `COMBINED_AML_GUARDRAIL_QUESTIONS` (`GUARDRAIL_QUESTIONS | AML_SCREENING_QUESTIONS`, 6 `Noul`s) in a single `system_one` call and populate `aml_probabilities: dict[str, float]` on `GuardrailEvaluationResult`. When `screen_beneficiary()` consumes the cached `GuardrailEvaluationResult`, it already has both the 4 guardrail answers and the 2 AML answers from that 1 call. Any partial response (including an AML-only response missing the 4 guardrail hazards) fails closed to `FLAGGED_FOR_MANUAL_REVIEW` / `ESCALATE`.
4. **Separate Transport Error Fail-Open from Incomplete-Answer Fail-Closed in `HunkGate.filter_findings()`**:
   - In `shb-ai-review`, if Jev times out (`ReadTimeout`), `HunkGate.filter_findings()` fails open (`True`) so deterministic hunk checks still accept valid findings. However, if `active_client.evaluate()` succeeds (`HTTP 200`) with an incomplete `answers` map missing `grounded_in_diff`, `HunkGate` MUST treat the AI finding as **ungrounded** (`False`, incrementing `ungrounded_ai_filtered`), never defaulting `grounded_in_diff` to `1.0`.
5. **Preserve `typesafe_sdk.Image` Objects Inside `sanitize_jev_state()`**:
   - In `typesafe-sdk==0.7.5`, callers can embed `Image(...)` directly in `state={"door": Image(Path("door.jpg"))}`. `sanitize_jev_state()` (`shb_core/jev.py:346-401`) must detect `Image` instances (`_is_image_asset(node)`), return them untouched in `_sanitize_node()`, and serialize them as `"<ImageAsset>"` when measuring `len(serialized)` against `max_chars` so `Image` objects are never converted to strings or truncated.

## Goals / Non-Goals

**Goals:**
- Guarantee fail-closed behavior whenever a `system_one` response omits required question keys or returns mismatched answer kinds across `shb-core`, `shb-agent-core`, `shb-mcp-servers`, `shb-ai-harness-skills`, and `shb-ai-review`.
- Batch multi-file diff triage and multi-finding citation verification in `shb-ai-review`, and unify guardrail + AML screening into 1 request across `shb-agent-core` and `shb-mcp-servers`.
- Adopt all upstream `jev-1.14.0` and `typesafe-sdk==0.7.5` features (`TypeSafe-Danger-Zone-Images`, `TypeSafe-Danger-Zone-Long-Context`, `Box` + presence `Noul` grounding in `shb-agent-core` and `shb-browser-cli`, `TypeSafeProvider(typesafe_client=...)`, `DecisionHandOff` SDE cascade, `SkillMatcher` relevance gating, and online `OUTPUT_GUARDRAIL_QUESTIONS`) while deleting ~45 lines of duplicated sync/async guardrail and PAN-sanitization code.

**Non-Goals:**
- Any modification to `tdt/*` (`tdt/agent-core`, `tdt-core`, `~/.tdt/`).
- Changing existing deterministic compliance rules (`RESTRICTED_KEYWORDS`, `HIGH_RISK_ACCOUNTS`, `MAKER_CHECKER_THRESHOLD_VND = 50_000_000`).

## Decisions

### 1. Required-Answer & Answer-Type Validation at `JevDecisionClient` + Strict Accessors (`shb-core`)

```
+-----------------------------------------------------------------------------------+
|                HARDENED FAIL-CLOSED VALIDATION PIPELINE                           |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  questions = {"prompt_injection": Noul(...), ...}                                 |
|         |                                                                         |
|         v                                                                         |
|  JevDecisionClient.evaluate(..., require_all_answers=True)                        |
|         |                                                                         |
|         v                                                                         |
|  _validate_response_answers(questions, raw_resp)                                  |
|    - Every q_id in questions MUST exist in raw_resp.answers                       |
|    - Answer type ("noul"|"choice"|"score"|"box") MUST match requested question    |
|    - Missing / mismatched -> raise TypeSafeError("Incomplete Jev response...")    |
|         |                                                                         |
|         +---> On TypeSafeError in evaluate_guardrail_policy /                     |
|               a_evaluate_guardrail_policy:                                        |
|                 fail_closed_triggered = True                                      |
|                 outcome = GuardrailOutcome.ESCALATE (or BLOCK)                    |
+-----------------------------------------------------------------------------------+
```

- **`JevDecisionClient._validate_response_answers(questions, raw_response)` (`shb-core/src/shb_core/jev.py`)**:
  - Controlled by `require_all_answers: bool = True` on `evaluate()` and `a_evaluate()`.
  - Inspects each `(q_id, q_spec)` in the caller's `questions` mapping (strictly `q_id in questions`, never hardcoded contract keys, so single-question calls like `ShbAgent._prepare_banking_tools` asking only `{"recommended_tool_family": TOOL_INTENT_CHOICE}` validate only `"recommended_tool_family"`): determines expected type (`getattr(q_spec, "type", None)` or `q_spec.get("type")` if `Mapping`).
  - Verifies `q_id in answers_dict` and that the returned answer's `type` matches the expected question type.
  - If any key is missing or has the wrong kind, records `outcome="incomplete_response"` on the active `shb.jev.decision` OTel span and raises `TypeSafeError(f"Incomplete or mismatched Jev response for questions: {missing_or_invalid}")` (without tripping the transport `JevCircuitBreaker`).
- **Strict Accessors on `JevEvaluationResult` (`shb-core/src/shb_core/jev.py`)**:
  - Add `require_noul_prob(key: str) -> float`, `require_choice(key: str) -> Any`, `require_score(key: str) -> Any`, and `require_box(key: str) -> Any`.
  - `require_noul_prob(key)` raises `TypeSafeError` if `key` is absent or lacks a finite `0.0 <= noul <= 1.0` float.
- **Shared Sync & Async Guardrail Policy (`evaluate_guardrail_policy` & `a_evaluate_guardrail_policy` in `shb_core/decisions.py`)**:
  - Both functions share `_resolve_guardrail_config()` and `_compose_guardrail_result()`, and `JevToolGuardrail.a_evaluate_invocation()` delegates directly to `await a_evaluate_guardrail_policy(...)`.
  - When `probabilities is None`, extract `extracted_probs = {q_key: eval_res.require_noul_prob(q_key) for q_key in GUARDRAIL_QUESTIONS}` inside the `try:` block so any missing or wrong-kind answer enters the `except Exception as exc:` fail-closed branch (`fail_closed_triggered=True`, `GuardrailOutcome.ESCALATE`).
  - When `probabilities` is passed explicitly (`probabilities is not None`), reject empty dicts (`not probabilities`) or non-finite values outside `[0.0, 1.0]` by returning the fail-closed `GuardrailEvaluationResult`.

### 2. Batched Diff Triage & Finding Citation Verification (`shb-ai-review`) and Single-Pass AML + Guardrail Fan-Out (`shb-agent-core`, `shb-mcp-servers`)

- **Batched Pre-Flight Diff Triage (`AiReviewer._triage_hunks_via_jev_batch`)**:
  - Pack non-preserved diff files into batches bounded by `max_batch_chars = 90_000`:
    - `state = {"hunks": {f"hunk_{i}": {"file_path": path, "redacted_diff": redacted_diff} for i, ...}}`
    - `questions = {f"hunk_{i}": Noul(instructions=..., criteria=MR_DIFF_TRIAGE_QUESTIONS["requires_ai_review"].criteria)}`
  - Call `active_client.evaluate(state, questions, sanitize=False, require_all_answers=False)` once per batch. For each `i`, read `eval_res.require_noul_prob(f"hunk_{i}")`. An unprefixed fallback to `eval_res.require_noul_prob("requires_ai_review")` is strictly restricted to single-item batches (`len(batch) == 1`) where `"requires_ai_review" in eval_res.nouls`. For multi-hunk batches (`len(batch) > 1`), exact `f"hunk_{i}"` keys are strictly required; if any hunk key is missing or an exception occurs, fail open to `False` (do not skip review for that file), preventing a flat response from skipping multiple files across an MR. Test mock fixtures in `test_diff_triage.py` are migrated to return exact `hunk_i` keys, and a regression test asserts that a 2-hunk batch receiving an unprefixed response skips neither file.
- **Batched Post-Generation Finding Citation Verification (`HunkGate.filter_findings`)**:
  - Collect all in-hunk AI findings (`finding.source.startswith("ai:")`). Build `state = {"hunks": {norm_path: {"file_path": norm_path, "redacted_diff": info.redacted_diff} for norm_path, info in matched_hunks.items()}, "findings": {f"f_{idx}": {"file_path": norm_path, "line": finding.line_number, "severity": str(finding.severity), "rule_id": finding.rule_id, "message": finding.message} for idx, (finding, norm_path) in ai_items}}` and `questions = {f"f_{idx}.{q_name}": Noul(instructions=..., criteria=...) for idx, (finding, norm_path) in ai_items for q_name in MR_FINDING_CITATION_QUESTIONS}` where each question explicitly references both `` `findings.f_{idx}` `` and `` `hunks.<norm_path>.redacted_diff` `` so findings across multiple files each judge against their own file's diff hunk.
  - Call `active_client.evaluate(state, batched_questions, sanitize=False, require_all_answers=False)` in 1 batched request:
    - If `active_client.evaluate()` raises a transport exception (e.g. `ReadTimeout`), catch it and fail open (`True`) so deterministic hunk checks stand.
    - Once `eval_res` is returned, extract each finding's 3 probabilities using `require_noul_prob(f"f_{idx}.{q_name}")` (or unprefixed `require_noul_prob(q_name)` if `len(ai_items) == 1` and unprefixed keys are in `eval_res.nouls`). If any of the 3 answers is missing (`TypeSafeError`) or `not MR_FINDING_CITATION_CONTRACT.is_grounded(probs)`, drop the finding (`result.ungrounded_ai_filtered += 1`, `result.reasons[idx] = "jev_citation_ungrounded"`).
- **Single-Pass `COMBINED_AML_GUARDRAIL_QUESTIONS` (`shb-core`, `shb-agent-core`, `shb-mcp-servers`)**:
  - `GuardrailEvaluationResult` gains `aml_probabilities: dict[str, float] = Field(default_factory=dict)`.
  - When `clean_tool in {"screen_beneficiary", "compliance_sanction_screen"}` (or `include_aml=True`), `evaluate_guardrail_policy()` / `a_evaluate_guardrail_policy()` asks `COMBINED_AML_GUARDRAIL_QUESTIONS` (`GUARDRAIL_QUESTIONS | AML_SCREENING_QUESTIONS`: 6 `Noul`s) in 1 request and populates `aml_probabilities`. All 6 answers are strictly required via `require_noul_prob()`: an AML-only response missing the 4 guardrail hazards fails closed (`fail_closed_triggered=True`, `clearance_status="FLAGGED_FOR_MANUAL_REVIEW"`, `risk_score=max(risk_score, 80.0)`, `"JEV_AML_FAIL_CLOSED"`). Test mock fixtures in `test_mcp.py` and `test_guardrails.py` are migrated to supply all 6 answers, with a regression test ensuring partial AML-only responses escalate.

### 3. Multimodal `Box` + Companion Presence `Noul`, Danger-Zone Headers, Long Context, `TypeSafeProvider` Pooling, and Output Guardrails

- **Automatic Danger-Zone Headers, `Image`-Safe `sanitize_jev_state`, & Opt-In Long Context (`shb_core/jev.py` & `shb_core/config.py`)**:
  - Add `long_context: bool = False` to `JevSettings` (`JEV_LONG_CONTEXT` / `SHB_JEV_LONG_CONTEXT`) and `JevDecisionClient.evaluate(..., long_context: bool | None = None)` / `a_evaluate(...)`.
  - In `sanitize_jev_state()`, preserve `Image` instances untouched (`_is_image_asset(node)`) and preserve `<field>_untrusted_text` on PAN fields containing non-digit text.
  - In `JevDecisionClient.evaluate()` / `a_evaluate()`, auto-inject `"TypeSafe-Danger-Zone-Images": "true"` when `_detect_contains_image_or_box(sanitized_state, questions, assets)` is `True`, and `"TypeSafe-Danger-Zone-Long-Context": "true"` (with `max_tokens=262_000`) when `long_context` is `True`.
- **Multimodal `Box` + Companion Presence `Noul` Contract (`shb_core/decisions.py`, `shb-agent-core`, `shb-browser-cli`)**:
  - Add `GroundedBoxResult`, `build_box_grounding_questions()`, and `extract_grounded_box()` in `shb_core.decisions`.
  - Add `locate_vietqr_region` in `shb-agent-core/src/shb_agent/tools/vietqr.py` and `DocumentExtractor.locate_visual_region` + `shb-browser-cli locate-region` in `shb-browser-cli`.
- **`TypeSafeProvider(typesafe_client=...)` & `DecisionHandOff` SDE Cascade (`shb-agent-core/src/shb_agent/model.py`)**:
  - Pass `typesafe_client=active_jev.get_async_sdk_client()` to `TypeSafeProvider` in `resolve_typesafe_decision_model()` when `active_jev` has a resolved credential or custom transport, and add `create_typesafe_sde_cascade_chain()` wrapping `FallbackModel(ts_model, primary, fallback, fallback_on=DecisionHandOff)`.
- **Two-Stage Skill Suggestion Gate & Online Output Guardrails (`shb-agent-skills`, `shb-core`, `shb-agent-core`)**:
  - Add `SKILL_NEEDS_ANY_GATE_QUESTION` (`Noul`), `min_probability: float = 0.0`, and `require_skill_gate: bool = False` in `SkillMatcher.match_jev()` / `a_match_jev()` (plus `--min-prob` on `shb-skills match`), and add `OUTPUT_GUARDRAIL_QUESTIONS` + `evaluate_output_guardrail()` / `a_evaluate_output_guardrail()` in `shb_core.decisions` and `JevToolGuardrail.evaluate_output()`.

## Transaction Boundaries & Risks / Trade-offs

- **Backwards Compatibility Across All 259 Existing Tests**:
  - Supporting both batched keys (`hunk_0`, `f_0.grounded_in_diff`) and single-item unprefixed fallback keys (`requires_ai_review`, `grounded_in_diff` restricted strictly to `len == 1` batches) when `require_all_answers=False` in `shb-ai-review`, plus supporting 2-key explicit `probabilities={...}` dicts in `evaluate_guardrail_policy` and migrating `_FakeMcpJevClient` to return all 6 `COMBINED_AML_GUARDRAIL_QUESTIONS` answers, ensures 100% of unit tests pass with strict fail-closed enforcement on partial network responses.
