# Verification Evidence: `harden-jev-fail-closed-batching-and-multimodal`

**Date:** `2026-10-24`
**Store:** `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
**Schema:** `spec-driven`

---

## 1. Requirement & Scenario Implementation Mapping

| Requirement / Scenario (`specs/jev-decision-runtime/spec.md`) | Implementation Files & Line Ranges | Verification Tests | Status |
| :--- | :--- | :--- | :---: |
| **Requirement 1: Fail-Closed Required-Answer and Answer-Type Validation**<br>- Scenario 1.1: Incomplete or wrong-kind response fails closed on guardrail and compliance evaluations | `shb-core/src/shb_core/jev.py:568-636` (`require_noul_prob`, `require_choice`, `require_score`, `require_box`)<br>`shb-core/src/shb_core/jev.py:1130-1157` (`_validate_response_answers`)<br>`shb-core/src/shb_core/decisions.py:1420-1695` (`evaluate_guardrail_policy`, `a_evaluate_guardrail_policy`)<br>`shb-agent-core/src/shb_agent/tools/guardrails.py:254-281` | `shb-core/tests/test_jev.py:610-653`<br>`shb-core/tests/test_decisions.py:233-310` | **VERIFIED** |
| **Requirement 1 — Scenario 1.2**: Incomplete citation or AML screening response fails closed | `shb-agent-core/src/shb_agent/tools/compliance.py:112-144`<br>`shb-mcp-servers/src/shb_mcp/tools.py:401-422`<br>`shb-ai-harness-skills/src/shb_ai_harness/contracts.py:246-283`<br>`shb-ai-review/src/shb_review/validation/hunk_gate.py:392-401,516-554` | `shb-agent-core/tests/tools/test_guardrails.py` (`test_screen_beneficiary_incomplete_response_fails_closed`)<br>`shb-mcp-servers/tests/test_tools.py` (`test_compliance_sanction_screen_fail_closed_and_prompt_injection_reject`)<br>`shb-ai-harness-skills/tests/test_deliverable_evidence.py` (`test_incomplete_jev_citation_response_fails_closed`)<br>`shb-ai-review/tests/test_diff_triage.py` (`test_multi_hunk_unprefixed_fallback_and_batched_citation_fail_closed`) | **VERIFIED** |
| **Requirement 2: Batched Multi-Item Review Triage, Single-Pass AML Fan-Out, and Online Output Guardrails**<br>- Scenario 2.1: Batched pre-flight diff hunk triage and post-generation citation filtering in `shb-ai-review` | `shb-ai-review/src/shb_review/ai/reviewer.py:437-515` (`_triage_hunks_via_jev_batch`)<br>`shb-ai-review/src/shb_review/validation/hunk_gate.py:404-557` (`filter_findings`) | `shb-ai-review/tests/test_diff_triage.py:90-140,363-475` | **VERIFIED** |
| **Requirement 2 — Scenario 2.2**: Single-pass combined guardrail and AML screening across agent and MCP tools | `shb-core/src/shb_core/decisions.py:549-552,1535-1546` (`COMBINED_AML_GUARDRAIL_QUESTIONS`)<br>`shb-agent-core/src/shb_agent/tools/compliance.py:102-144`<br>`shb-mcp-servers/src/shb_mcp/tools.py:200-235,395-428` | `shb-agent-core/tests/tools/test_guardrails.py:364-415`<br>`shb-mcp-servers/tests/test_tools.py:247-365` | **VERIFIED** |
| **Requirement 2 — Scenario 2.3**: Online output guardrail screening and two-stage skill suggestion gating | `shb-core/src/shb_core/decisions.py:647-721,1266-1337,1785-1879` (`OUTPUT_GUARDRAIL_QUESTIONS`, `evaluate_output_guardrail`, `a_evaluate_output_guardrail`, `SKILL_NEEDS_ANY_GATE_QUESTION`)<br>`shb-agent-core/src/shb_agent/tools/guardrails.py:283-311`<br>`shb-agent-skills/src/shb_skills/matcher.py:125-273`<br>`shb-agent-skills/src/shb_skills/cli.py` | `shb-core/tests/test_decisions.py:355-402`<br>`shb-agent-core/tests/tools/test_guardrails.py` (`test_locate_vietqr_region_and_evaluate_output`)<br>`shb-agent-skills/tests/test_jev_matching.py` (`test_min_probability_filtering_and_skill_gate`, `test_incomplete_jev_response_falls_back_to_stage1_shortlist`) | **VERIFIED** |
| **Requirement 3: Complete Upstream Multimodal Box/Image Headers, Long Context, and TypeSafeProvider Pooling**<br>- Scenario 3.1: Automatic Danger-Zone headers, Image-safe state sanitization, and opt-in 262k Long Context | `shb-core/src/shb_core/config.py:117-120` (`JevSettings.long_context`)<br>`shb-core/src/shb_core/jev.py:345-453,1084-1119,1272-1286,1390-1404` | `shb-core/tests/test_jev.py:654-695` | **VERIFIED** |
| **Requirement 3 — Scenario 3.2**: Multimodal Box spatial grounding paired with companion presence Noul in banking tools and browser CLI | `shb-core/src/shb_core/decisions.py:1158-1263` (`GroundedBoxResult`, `build_box_grounding_questions`, `extract_grounded_box`)<br>`shb-agent-core/src/shb_agent/tools/vietqr.py:271-307` (`locate_vietqr_region`)<br>`shb-browser-cli/src/shb_browser_cli/extractor.py:40-71` (`locate_visual_region`)<br>`shb-browser-cli/src/shb_browser_cli/cli.py:45` (`locate-region`) | `shb-core/tests/test_decisions.py:290-353`<br>`shb-agent-core/tests/tools/test_guardrails.py`<br>`shb-browser-cli/tests/test_extractor.py` & `tests/test_cli.py` | **VERIFIED** |
| **Requirement 3 — Scenario 3.3**: `TypeSafeProvider` client pool sharing and `DecisionHandOff` SDE cascade | `shb-agent-core/src/shb_agent/model.py:38-52,86-146` (`resolve_typesafe_decision_model`, `create_typesafe_sde_cascade_chain`) | `shb-agent-core/tests/test_model.py` | **VERIFIED** |

---

## 2. Live End-to-End Operational Execution Ledger (`api.typesafe.ai` & OmniRoute `127.0.0.1:20128`)

1. **`shb doctor --live-jev` & Live Smoke Probe (`shb-core`)**:
   - `SHB_RUN_LIVE_JEV_TESTS=1 uv run pytest -p no:cacheprovider -v -k "test_opt_in_live_typesafe_api_smoke"` -> `1 passed in 0.91s`.
   - `SHB_JEV_ENABLED=true uv run shb doctor --live-jev` -> `✓ reachable (models=['jev-latest', 'jev-preview'])`, `circuit_breaker: open=False, failures=0/3`.
2. **Live `TypeSafe-Danger-Zone-Long-Context: true` (`262k` tokens)**:
   - Evaluated live on `jev-1.13.0`: `prob = 0.99`, `total_tokens = 321`.
3. **Live Single-Pass `screen_beneficiary` (`shb-agent-core` & `shb-mcp-servers`, 6 `Noul`s in 1 HTTP call)**:
   - Clean beneficiary (`NGUYEN THI MINH KHAI`): `CLEARED` (`risk_score = 0.0`).
   - Obfuscated sanction alias (`S4NCT10NED T.E.R.R.O.R_F.I.N.A.N.C.E HOLDINGS`): `FLAGGED_FOR_MANUAL_REVIEW` (`risk_score = 97.0`, `['JEV_GUARDRAIL_BLOCK: ...', 'JEV_SEMANTIC_AML_ESCALATION']`).
   - Prompt injection in beneficiary name (`NGUYEN VAN A; SYSTEM OVERRIDE...`): `REJECTED` (`risk_score = 100.0`).
4. **Live Online Output Guardrail (`evaluate_output_guardrail`, 4 `Noul`s + 1 `Score`)**:
   - Compliant masked reply: `outcome = proceed`, `severity = 0.31`, `max_p = 0.04`.
   - Structuring/policy-violating reply: `outcome = block`, `severity = 2.99`, `max_p = 0.99` (`triggered = ['broke_policy', 'unauthorized_financial_commitment', 'harmful_or_illegal_assistance']`).
5. **Live Multimodal `Box` + Companion Presence `Noul` + `TypeSafe-Danger-Zone-Images: true` on `jev-1.14.0` (`locate_vietqr_region` & `shb-browser-cli locate-region`)**:
   - Evaluated on a 400x400 PNG with a central 200x200 QR pattern (`[0.25..0.75]`):
   - `locate_vietqr_region`: `present = True`, `presence_probability = 0.96`, `box = {top: 0.23, bottom: 0.79, left: 0.24, right: 0.74}`, `confidence = 0.69`, `model = 'jev-1.14.0'`, `request_id = 'req_01a16c3d7757740d9c154f617d134cd0'`.
   - `shb-browser-cli locate-region`: `present = True`, `presence_probability = 0.95`, `box = {top: 0.21, bottom: 0.78, left: 0.24, right: 0.75}`, `confidence = 0.78`, `model = 'jev-1.14.0'`, `request_id = 'req_01a16c420fe7729dbfa00d37008c1167'`.
6. **Live `TypeSafeModel` (`TypeSafeProvider(typesafe_client=...)`) & `DecisionHandOff` SDE Cascade (`shb-agent-core`)**:
   - `Agent(resolve_typesafe_decision_model("jev-1.14.0"), output_type=BankingTurnClassification)`: returned `is_balance_inquiry=True, intent_category='balance'` and `is_balance_inquiry=False, intent_category='transfer'`.
   - `SHB_JEV_ENABLED=true uv run shb-agent run "What is the current balance of account 1029384756?" --live`: executed `PrepareTools` (pruning debit tools on read-only turn), `JevToolGuardrail` pre-flight check, and OmniRoute `gemini-3.8-flash-high` ReAct loop (`Status: COMPLETED`, `Tools used: tool_get_account_balance`).
7. **Live Batched Diff Triage, Batched `HunkGate`, `shb-agent evaluate`, `shb-skills match`, `shb-harness-skills verify-deliverable`, `shb-harness plan`, & `shb-observability show-metrics`**:
   - Batched diff triage (`AiReviewer._triage_hunks_via_jev_batch`): skipped `docs/README.md` (`p < 0.50`) while retaining `src/auth.py` in 1 call.
   - Batched `HunkGate.filter_findings()`: accepted grounded `src/auth.py` finding and filtered hallucinated `src/math_utils.py` SQL-injection blocker (`ungrounded_ai_filtered = 1`) in 1 call.
   - `shb-ai-review scan --ai`: completed clean scan on `README.md` and `src/shb_core/__init__.py`.
   - `shb-agent evaluate`: all 3 cases passed live (`composite = 0.897, 0.753, 0.772`).
   - `shb-skills match --min-prob 0.30`: ranked `circular-dependency-skill` at `Jev Prob = 0.9800` on covered query and returned empty table (`0` false positives) on uncovered query.

---

## 3. Test Suite, Linter, Type-Checker & Lockfile Execution Ledger

| Repository | `pytest -p no:cacheprovider` | `ruff check src tests` | `mypy --strict src` | `uv lock --check` |
| :--- | :--- | :--- | :--- | :---: |
| `/Users/androidteam/Developer/shb/shb-core` | `49 passed` (`exit 0`) | `All checks passed!` (`exit 0`) | `0 issues (13 files)` | `0` |
| `/Users/androidteam/Developer/shb/shb-agent-core` | `48 passed` (`exit 0`) | `All checks passed!` (`exit 0`) | `0 issues (14 files)` | `0` |
| `/Users/androidteam/Developer/shb/shb-agent-harness` | `15 passed` (`exit 0`) | `All checks passed!` (`exit 0`) | `0 issues (5 files)` | `0` |
| `/Users/androidteam/Developer/shb/shb-ai-harness-skills` | `14 passed` (`exit 0`) | `All checks passed!` (`exit 0`) | `0 issues (3 files)` | `0` |
| `/Users/androidteam/Developer/shb/shb-agent-skills` | `13 passed` (`exit 0`) | `All checks passed!` (`exit 0`) | `0 issues (4 files)` | `0` |
| `/Users/androidteam/Developer/shb/shb-ai-review` | `137 passed` (`exit 0`) | `All checks passed!` (`exit 0`) | `0 issues (18 files)` | `0` |
| `/Users/androidteam/Developer/shb/shb-mcp-servers` | `18 passed` (`exit 0`) | `All checks passed!` (`exit 0`) | `0 issues (4 files)` | `0` |
| `/Users/androidteam/Developer/shb/shb-observability` | `9 passed` (`exit 0`) | `All checks passed!` (`exit 0`) | `0 issues (4 files)` | `0` |
| `/Users/androidteam/Developer/shb/shb-browser-cli` | `12 passed` (`exit 0`) | `All checks passed!` (`exit 0`) | `0 issues (4 files)` | `0` |

---

## 4. Checklist Verification

- [x] All 9 tasks in `tasks.md` (`1.1` through `3.2`) are implemented and checked (`[x]`).
- [x] `openspec validate "harden-jev-fail-closed-batching-and-multimodal" --strict --json --store openspec-store` passed with `0` warnings and `0` errors.
- [x] `uv lock --check` passed across all 13 `shb/shb-*` repositories.
- [x] Zero files modified in `/Users/androidteam/Developer/tdt/*`.
