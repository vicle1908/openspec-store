# Implementation & Verification Evidence: `agent-core-integrate-jev-system-one`

## 1. Pytest Verification Across All 9 SHB Repositories

All 8 modified SHB repositories (plus `shb-tools`) pass their full test suites with **0 failures** and **+57 new hermetic unit tests** (+58 including the opt-in live TypeSafe API smoke test in `shb-core`):

| Repository | Baseline Passed | Current Passed (Hermetic) | Delta | CLI Entrypoint(s) |
| :--- | :---: | :---: | :---: | :--- |
| `shb-core` | 23 | **44** (+1 opt-in live = **45**) | +21 (+22 live) | `shb` |
| `shb-agent-core` | 27 | **39** | +12 | `shb-agent` |
| `shb-agent-harness` | 9 | **14** | +5 | `shb-harness` |
| `shb-ai-harness-skills` | 7 | **11** | +4 | `shb-harness-skills` |
| `shb-agent-skills` | 7 | **10** | +3 | `shb-skills` |
| `shb-observability` | 5 | **8** | +3 | `shb-observability` |
| `shb-ai-review` | 129 | **133** | +4 | `shb-ai-review`, `mr-coverage` |
| `shb-mcp-servers` | 12 | **17** | +5 | `shb-mcp` |
| **Subtotal (8 Modified Repos)** | **219** | **276** (**277** with live) | **+57** (**+58** live) | |
| `shb-tools` | 9 | **9** | 0 | `shb-tools`, `shb-compliance-scan`, `shb-docs-sync`, `shb-recon` |
| **Total (All 9 SHB Repos)** | **228** | **285** (**286** with live) | **+57** (**+58** live) | |

## 2. Static Analysis, Type Checking & Lockfile Integrity (`ruff`, `mypy --strict`, `uv lock --check`)

| Repository | `uv run ruff check src tests` | `uv run mypy --strict --ignore-missing-imports src` | `uv lock --check` |
| :--- | :--- | :--- | :--- |
| `shb-core` | `All checks passed!` (exit 0) | `Success: no issues found in 13 source files` (exit 0) | `Resolved 49 packages` (exit 0) |
| `shb-agent-core` | `All checks passed!` (exit 0) | `Success: no issues found in 14 source files` (exit 0) | `Resolved 123 packages` (exit 0) |
| `shb-agent-harness` | `All checks passed!` (exit 0) | `Success: no issues found in 5 source files` (exit 0) | `Resolved 62 packages` (exit 0) |
| `shb-ai-harness-skills` | `All checks passed!` (exit 0) | `Success: no issues found in 3 source files` (exit 0) | `Resolved 50 packages` (exit 0) |
| `shb-agent-skills` | `All checks passed!` (exit 0) | `Success: no issues found in 4 source files` (exit 0) | `Resolved 50 packages` (exit 0) |
| `shb-observability` | `All checks passed!` (exit 0) | `Success: no issues found in 4 source files` (exit 0) | `Resolved 51 packages` (exit 0) |
| `shb-ai-review` | `All checks passed!` (exit 0) | `Success: no issues found in 18 source files` (exit 0) | `Resolved 126 packages` (exit 0) |
| `shb-mcp-servers` | `All checks passed!` (exit 0) | `Success: no issues found in 4 source files` (exit 0) | `Resolved 66 packages` (exit 0) |

## 3. Compliance Scanner (`SEC-001`, `PCI-001`, `SYN-001`) & Documentation Sync (`shb-tools`)

Executed from `/Users/androidteam/Developer/shb/shb-tools`:

- `uv run shb-compliance-scan --target-dir /Users/androidteam/Developer/shb/shb-core`: `PASS: Compliance Scan: PASSED | Scanned: 13 files | Violations: 0 (Critical: 0, High: 0)`
- `uv run shb-compliance-scan --target-dir /Users/androidteam/Developer/shb/shb-agent-core`: `PASS: Compliance Scan: PASSED | Scanned: 14 files | Violations: 0 (Critical: 0, High: 0)`
- `uv run shb-compliance-scan --target-dir /Users/androidteam/Developer/shb/shb-agent-harness`: `PASS: Compliance Scan: PASSED | Scanned: 5 files | Violations: 0 (Critical: 0, High: 0)`
- `uv run shb-compliance-scan --target-dir /Users/androidteam/Developer/shb/shb-ai-harness-skills`: `PASS: Compliance Scan: PASSED | Scanned: 4 files | Violations: 0 (Critical: 0, High: 0)`
- `uv run shb-compliance-scan --target-dir /Users/androidteam/Developer/shb/shb-agent-skills`: `PASS: Compliance Scan: PASSED | Scanned: 53 files | Violations: 0 (Critical: 0, High: 0)`
- `uv run shb-compliance-scan --target-dir /Users/androidteam/Developer/shb/shb-observability`: `PASS: Compliance Scan: PASSED | Scanned: 4 files | Violations: 0 (Critical: 0, High: 0)`
- `uv run shb-compliance-scan --target-dir /Users/androidteam/Developer/shb/shb-ai-review`: `PASS: Compliance Scan: PASSED | Scanned: 18 files | Violations: 0 (Critical: 0, High: 0)`
- `uv run shb-compliance-scan --target-dir /Users/androidteam/Developer/shb/shb-mcp-servers`: `PASS: Compliance Scan: PASSED | Scanned: 4 files | Violations: 0 (Critical: 0, High: 0)`
- `uv run shb-docs-sync --root /Users/androidteam/Developer/shb`: `Status: IN_SYNC | Checked: 12 repos`

## 4. Value-Blind Live TypeSafe API Smoke & Empirical Calibration Verification

Executed in `/Users/androidteam/Developer/shb/shb-core`:

- **`uv run shb config-show`**:
  - `SHB_JEV_ENABLED=False`
  - `SHB_JEV_MODEL=jev-1.13.0`
- **`uv run shb doctor --live-jev`** (value-blind, zero secret leakage):
  - `Jev Runtime: enabled=False, model=jev-1.13.0, http2=True, base_url=https://api.typesafe.ai`
  - `Jev Credential: provisioned=True (len=107, sha256_prefix=7c434594, zshenv_mode=0600)`
  - `Jev Circuit Breaker: open=False, failures=0/3`
  - `Jev Live Probe: ✓ reachable (models=['jev-latest', 'jev-preview'])`
- **`SHB_RUN_LIVE_JEV_TESTS=1 GRAPHIFY_SKIP_HOOK=1 uv run pytest -q`**:
  - `45 passed in 2.05s`
- **Live Empirical Calibration Summary (`jev-1.13.0` & `jev-1.14.0` over HTTP/2, `213ms–298ms`)**:
  - **Banking Tool Guardrails & Structuring Supervisor Override (`banking.py`, `shb_mcp/tools.py`)**:
    - **Finding 1 Fixed & Verified (Global Tool Block Enforcement in MCP)**: In `shb-mcp-servers` (`src/shb_mcp/tools.py:execute_tool`), when `evaluate_guardrail_policy(...)` returns `GuardrailOutcome.BLOCK` (e.g. prompt injection), the rejection is enforced globally across all 12 MCP tools (`banking_account_summary`, `vietqr_parse`, `jira_issue_lookup`, etc.), preventing prompt injection payloads from bypassing guardrails via read-only tools. Verified by `test_jev_guardrail_blocks_non_transfer_tools_on_prompt_injection`.
    - **Finding 2 Fixed & Verified (Deduplication Cache Key Distinction)**: In `shb-agent-core` (`src/shb_agent/tools/guardrails.py:JevToolGuardrail.sanitize_invocation_state` and `_make_dedup_key`), deduplication explicitly computes and preserves `has_supervisor_token: bool` in canonical state before stripping `supervisor_approval_token` (with `"has_supervisor_token"` allowlisted in `_NON_SECRET_STRUCTURAL_KEYS` in `shb_core/jev.py`), ensuring retried transfers with supervisor approval tokens do not collide with earlier unapproved attempts. Verified by `test_dedup_cache_distinguishes_presence_of_supervisor_token`.
    - **Finding 3 Fixed & Verified (Centralized Supervisor Token Validation)**: Centralized `is_valid_supervisor_token` helper in `shb_core.decisions` (`len >= 8` stripped check) imported and reused across `shb_agent.tools.guardrails`, `shb_agent.tools.banking`, and `shb_mcp.tools` to maintain single-source-of-truth maker-checker validation contracts across agent and MCP runtimes.
    - **Finding 4 Fixed & Verified (Direct Mode `/v1` URL Normalization & Clean Async Loop Reset)**: In `shb_core/jev.py:JevDecisionClient._resolve_endpoint_and_api_key`, trailing `"/"` and optional trailing `"/v1"` on `https://api.typesafe.ai` normalize to `DEFAULT_BASE_URL` (`https://api.typesafe.ai`) so `TYPESAFE_BASE_URL="https://api.typesafe.ai/v1/"` remains in Direct Mode without doubling `/v1/v1/systemone` (verified by `test_direct_mode_normalizes_trailing_v1_on_default_base_url`), and `_get_async_client()` clears stale `_async_client` and `_async_http_client` references when switching event loops. In `shb-agent-harness` (`src/shb_harness/workflow.py`), `RunnableCallable` falls back to `langchain_core.runnables.RunnableLambda(func=sync_fn, afunc=async_fn)` and a pure-Python `.invoke`/`.ainvoke` wrapper.
    - Strict exact-key `(clean_tool_name, canonical_args)` deduplication (never falling back to loose tool-name matching across different arguments) preventing double-billing or false-cache reuse across tool executions.
    - Sub-50M VND structuring split-transfer escalation: when a transfer $\le 50,000,000	ext{ VND}$ (e.g. `49,500,000 VND`) triggers `structuring_risk` (`struct=0.980`, effective risk `0.70`, `GuardrailOutcome.BLOCK`), pure structuring without prompt injection or sanction evasion is overridden by a valid `supervisor_approval_token` (`len >= 8`), returning `status="COMPLETED"`. Transfers without a token return `status="PENDING_APPROVAL"`. In contrast, transfers with prompt injection (`is_prompt_injection`) or direct sanction hits are unconditionally rejected (`status="REJECTED"`), recording `AuditEvent(status="FAILED")` in `AuditLoggingMiddleware`.
    - MCP Tool Parity: `shb-mcp-servers` (`src/shb_mcp/tools.py`) strictly enforces `is_valid_supervisor_token(token)` on `banking_transfer_initiate`, matching `shb-agent-core` so 1-character or whitespace tokens cannot bypass maker-checker controls.
  - **AML Beneficiary Screening Triage (`compliance.py`)**:
    - Pre-flight tool guardrails in `screen_beneficiary` only block prompt injection attempts, allowing suspicious or obfuscated entity names to proceed to the dedicated `AML_SCREENING_QUESTIONS` to evaluate exact risk probabilities and attach `JEV_SEMANTIC_AML_ESCALATION` with `FLAGGED_FOR_MANUAL_REVIEW` (clean `'NGUYEN THI MINH KHAI'` `p=0.040` vs obfuscated `'T.E.R.R.O.R_F.I.N.A.N.C.E TRADING CO'` `p=0.910` and `'S4NCT10NED ILL1C1T HOLDINGS'` `p=0.900` at threshold `p >= 0.50`).
  - 12-stage LangGraph harness routing (`_should_skip_api_contract`): internal refactor (`choice='design', confidence=1.000`) vs public API change (`choice='api_contract', confidence=1.000`) at threshold `confidence >= 0.85`.
  - State-referenced skill reranking (`SkillMatcher.match_jev`): target candidate in `state["candidates"]` (`p=0.980`) vs non-matching candidates (`p=0.020`, `49x` separation).
  - Stage deliverable citation check (`STAGE_DELIVERABLE_CITATION_CONTRACT`): valid deliverable (`p=0.910–0.960`) vs ungrounded deliverable (`p=0.020`) at threshold `p >= 0.70`.
  - MR diff triage and citation check (`MR_DIFF_TRIAGE_CONTRACT` & `MR_FINDING_CITATION_CONTRACT`): grounded finding (`grounded_in_diff=0.970, contradicts_diff=0.040`) vs hallucinated finding (`grounded_in_diff=0.010, contradicts_diff=0.950`); two-tier thread resolution strictly distinguishes static compliance rules (`is_static_compliance_rule`) from open AI discussions (including `SHB-AI-*` and `AI-*` rule IDs) so open AI findings are preserved on Jev-skipped files while fixed static findings resolve cleanly.

## 5. Modified & Created Files Across All 8 SHB Repositories

- **`shb-core`**:
  - `pyproject.toml`, `uv.lock`, `SPEC_INDEX.md`, `README.md`
  - `src/shb_core/__init__.py`, `src/shb_core/config.py`, `src/shb_core/jev.py`, `src/shb_core/decisions.py`, `src/shb_core/cli.py`
  - `tests/test_config.py`, `tests/test_cli.py`, `tests/test_jev.py`, `tests/test_decisions.py`
- **`shb-agent-core`**:
  - `pyproject.toml`, `uv.lock`, `SPEC_INDEX.md`, `README.md`
  - `src/shb_agent/agent.py`, `src/shb_agent/tools/__init__.py`, `src/shb_agent/tools/guardrails.py`, `src/shb_agent/tools/banking.py`, `src/shb_agent/tools/biller.py`, `src/shb_agent/tools/vietqr.py`, `src/shb_agent/tools/compliance.py`, `src/shb_agent/tools/audit.py`
  - `src/shb_agent/evaluation/__init__.py`, `src/shb_agent/evaluation/jev_scorer.py`
  - `tests/tools/test_guardrails.py`, `tests/evaluation/test_jev_scorer.py`
- **`shb-agent-harness`**:
  - `pyproject.toml`, `uv.lock`, `SPEC_INDEX.md`, `README.md`
  - `src/shb_harness/workflow.py`, `src/shb_harness/cli.py`
  - `tests/test_jev_routing.py`
- **`shb-ai-harness-skills`**:
  - `pyproject.toml`, `uv.lock`, `SPEC_INDEX.md`, `README.md`
  - `src/shb_ai_harness/contracts.py`, `src/shb_ai_harness/cli.py`
  - `tests/test_deliverable_evidence.py`
- **`shb-agent-skills`**:
  - `pyproject.toml`, `uv.lock`, `SPEC_INDEX.md`, `README.md`
  - `src/shb_skills/__init__.py`, `src/shb_skills/registry.py`, `src/shb_skills/matcher.py`
  - `tests/test_jev_matching.py`
- **`shb-observability`**:
  - `pyproject.toml`, `uv.lock`, `SPEC_INDEX.md`, `README.md`
  - `src/shb_observability/collector.py`, `src/shb_observability/cli.py`
  - `tests/test_jev_telemetry.py`
- **`shb-ai-review`**:
  - `pyproject.toml`, `uv.lock`, `SPEC_INDEX.md`, `README.md`
  - `src/shb_review/validation/hunk_gate.py`, `src/shb_review/validation/deduplicator.py`, `src/shb_review/ai/reviewer.py`, `src/shb_review/gitlab/posting.py`, `src/shb_review/orchestrator.py`, `src/shb_review/coverage/cli.py`
  - `tests/test_diff_triage.py`
- **`shb-mcp-servers`**:
  - `pyproject.toml`, `uv.lock`, `SPEC_INDEX.md`, `README.md`
  - `src/shb_mcp/tools.py`, `src/shb_mcp/server.py`, `src/shb_mcp/cli.py`
  - `tests/test_tools.py`
