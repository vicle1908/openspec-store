# Reconciliation: establish-agent-observability-contract

**Date:** 2026-08-20
**Change:** establish-agent-observability-contract
**openspec-store HEAD:** `5a3eb4ced4b6bfdea090f63f4a90e45c9a365e32` (main, clean)
**agent-core HEAD:** `82abe02a74b644705437645c0e81eb5a9a8142fb` (main, dirty: graphify-out only)
**agent-docs-sync HEAD:** `5ca0e478768e56d1228a1fc2c4e46d498563be0f` (main, dirty: uncommitted observability changes)

**Superseding closure evidence:** This report is a historical pre-closure reconciliation. The current integrated revisions are agent-core `1c8cf12548f891b92c7428c03b95276fbbf75bd0`, agent-docs-sync `c6c5b1f45ff018fbe42c76e050e82be195c226e5`, and tdt-scheduler `4a73580`. Re-check current source and exact SHAs before using older gap statements below.

---

## P0 — Missing Test Artifact (evidence nonexistent at specified SHA)

### Task 2.5 — `test_command_identity.py` does not exist

**Claimed:** "Evidence: `tests/foundation/test_command_identity.py` passed with root-only attribute and stable `service.name`"

**Reality:** `git ls-tree -r --name-only 82abe02 -- tests/foundation/test_command_identity.py` returns empty. The file does not exist in the commit tree. No test file in the repository validates `set_command_name()` / `reset_command_name()` / `COMMAND_NAME_ATTR` from `src/agent_core/foundation/tracing.py:42-54`. The CLI callback (`cli/app.py:56-57`) does call `set_command_name`, but no test asserts that the root span carries `agent_core.command.name` or that `service.name` remains stable.

**Impact:** The `agent_core.command.name` attribute behavior is implemented (tracing.py:42-62, cli/app.py:56-57) but has zero test coverage. This is a claimed test that simply does not exist.

**Required action:** Create `tests/foundation/test_command_identity.py` asserting: (a) `set_command_name` sets the ContextVar, (b) root span carries `agent_core.command.name`, (c) `service.name` resource is unchanged by command identity.

---

## P0 — Uncommitted Working-Tree Changes (evidence claimed but not committed)

### Task 2.6 — agent-docs-sync has 2 uncommitted changes + 1 untracked file

**Claimed:** "Evidence: `tests/test_observability_import.py` passed."

**Reality (working tree diff):**

| File | Status | Content |
| ------ | -------- | --------- |
| `src/agent_docs_sync/observability/__init__.py` | **M (uncommitted)** | Removes `init_observability()` call; now side-effect free |
| `tests/test_observability_import.py` | **?? (untracked)** | Tests import boundary |
| `tests/test_write_containment.py` | **M (uncommitted)** | Unrelated change: signature update for `create_doc_guardrails` |

The `__init__.py` change (removing import-time init) and its corresponding test (`test_observability_import.py`) exist in the working tree but are **not committed**. The task evidence "tests/test_observability_import.py passed" refers to an untracked file — the test cannot be reliably reproduced from the committed state. The `test_write_containment.py` modification is also uncommitted and unrelated to observability.

**Impact:** The import-time side-effect removal (the key deliverable of task 2.6) is uncommitted. Archiving this change with the current agent-core SHA would leave agent-docs-sync in a state inconsistent with the task's acceptance criteria.

**Required action:** Commit the `__init__.py` and `test_observability_import.py` changes in agent-docs-sync. Determine whether `test_write_containment.py` change belongs in this change or a separate commit.

---

## P1 — Evidence Weaker Than Required

### Task 7.1 — Runtime validation claim is circular

**Claimed:** "Validate a short-lived agent-core CLI trace reaches the selected backend. Evidence: code review + test coverage."

**Reality:** The only test (`tests/cli/test_cli_tracing_init.py:test_cli_callback_calls_init_observability`) mocks `init_observability` and asserts the mock was called with the correct args. This validates that the CLI wires `init_observability` — it does **not** validate that a trace reaches the Langfuse/MLflow backend. There is no test that: (a) starts a real OTel collector, (b) runs a CLI command, (c) asserts a span appears in the collector or backend. The claim "CLI composition root wired" is true; the claim "trace reaches the selected backend" is unverified.

**Impact:** Runtime validation is a hard requirement for deployment-readiness claims (see design.md D13). The absence of backend-validated evidence means this task's acceptance criteria are not met.

**Required action:** Either (a) add a test that exports a real span to a local collector endpoint and asserts receipt, or (b) reclassify the evidence level as "integration-tested" (not "runtime-validated") and add a follow-up task.

### Task 7.2 — Span hierarchy claim is not validated by source inspection

**Claimed:** "Validate expected agent/model/tool span hierarchy. Evidence: pydantic-ai Instrumentation capability produces correct hierarchy — documented in agent.py."

**Reality:** `tests/foundation/test_tracing_extended.py:test_instrumentation_capability_documented` calls `inspect.getsource(AgentRuntime.__init__)` and asserts `"Instrumentation()" in source`. This confirms the capability is passed to pydantic-ai — it does **not** validate the span tree structure (root → model → tool). There is no test that captures exported spans and asserts parent-child relationships. The claim is that pydantic-ai *produces* the hierarchy, but this is asserted by code inspection, not by observed behavior.

**Impact:** The spec requires "each span SHALL contain root invoke_agent span with one child execute_tool span" (observability-tests delta spec). This is unverified.

**Required action:** Add a test using `InMemorySpanExporter` that: (a) runs a simple agent with one tool call, (b) exports spans, (c) asserts the tree structure.

### Task 7.3 — Flush-before-exit claim has no direct test

**Claimed:** "Validate spans flush before CLI exit. Evidence: atexit flush handler registered for Langfuse."

**Reality:** `src/agent_core/foundation/tracing.py:327-341` registers an atexit handler that calls `langfuse_client.flush()`. The code exists but there is no test that: (a) triggers CLI exit, (b) asserts `flush()` was called. The claim relies on code inspection, not behavioral validation.

**Impact:** Low — the code is straightforward and atexit registration is a standard pattern. However, the task's own delta spec requires a "Short-lived process flush test."

**Required action:** Add a test that asserts `atexit.register` was called with the expected flush function.

### Task 1.5 — Focused test suite evidence scope mismatch

**Claimed:** "`uv run pytest tests/observability/ tests/cli/ tests/foundation/test_tracing*.py -v`. Evidence: 3 failed (pass-rate), 2 passed (exception propagation + CLI no-init)."

**Reality:** The scope includes 17 test files across 5 directories. The cited evidence of "3 failed, 2 passed" accounts for only 5 test classes — a subset of the full suite. The actual test count at SHA `82abe02` likely includes many more tests (idempotency, metrics, logging, redaction, backend isolation, etc.). The evidence is a partial snapshot, not a complete run output.

**Impact:** Low — the defects and confirmations cited are accurate for the subset shown. However, the full suite output is not preserved, making it impossible to confirm zero regressions across the full scope.

**Required action:** Re-run the full focused suite and preserve complete output as evidence.

### Task 8.2 — detect_changes() was skipped entirely

**Claimed:** "Run GitNexus `detect_changes()` before commits. Evidence: GitNexus MCP unavailable; Ruff + pytest validation confirms no regressions."

**Reality:** `detect_changes()` was never run. The evidence explicitly states "GitNexus MCP unavailable." The substitute validation (Ruff + pytest) covers different ground — static analysis and test results do not map to execution flow impact the way `detect_changes()` does.

**Impact:** Medium — the task has a specific GitNexus requirement. If GitNexus was genuinely unavailable, the evidence should state that clearly and the task should be marked as having incomplete evidence, not that it was completed.

**Required action:** Re-run `detect_changes()` now that GitNexus is available, or document the unavailability with a timestamp.

---

## P2 — Evidence Mismatch (contradiction or misattribution)

### Task 1.3 — Test description contradicts task description

**Task description says:** "Add a failing test proving agent-core CLI does not currently initialize tracing."

**Actual test at SHA 82abe02 says:** `test_cli_callback_calls_init_observability` — which asserts the callback **does** call `init_observability`. The test was written for the pre-fix state but was committed with the post-fix code. The test name and docstring ("Task 1.3: Prove agent-core CLI does NOT currently initialize tracing") contradict the assertion (`mock_init.assert_called_once_with`).

**Impact:** Low — the test is valid for the fixed state. The task description is stale (describes the pre-fix intent, not the post-fix artifact). But it creates confusion about what the evidence actually proves.

**Required action:** Update the test docstring to reflect current state.

### Task 0.8 — Disposition evidence does not support the claim

**Claimed:** "Both have CLI entry points (`cli.py` with `main()`) and depend on `agent-core`. Neither currently imports observability."

**Reality (working tree, not committed):** `agent-harness` has zero observability imports (confirmed). `code-daily-scan` also has zero observability imports (confirmed). However, the evidence "Neither currently imports observability" is factually correct for the committed state — but the disposition "Both need `init_observability()`" is based on code inspection, not on a verified test or runtime observation. The claim that they "depend on agent-core" is true (both have `agent-core` in their dependencies), but the leap from "depend on agent-core" to "need init_observability()" is not evidence-backed.

**Impact:** Low — the disposition is reasonable but the evidence does not directly prove the need. The acceptance criteria for task 0.8 are "inspect entry points, determine whether each requires composition-root initialization" — which was done via code inspection.

**Required action:** No change needed; document that the disposition is based on code inspection, not runtime verification.

---

## P3 — Minor / Cosmetic Issues

### Task 4.6 — Test count attribution overlaps with task 4.5

**Task 4.5 claims:** "9 tests pass."
**Task 4.6 claims:** "9 tests pass."

Both tasks cite the same test count from `tests/evaluation/test_store.py` (9 tests across `TestEvalRecord` and `TestEvalMetrics`). This is not an error — both tasks correctly identify the same test file — but the duplication makes it unclear which task's evidence is primary.

**Impact:** Negligible.

---

## Summary Checklist (Prioritized)

| Priority | Task | Issue | Action Required |
| ---------- | ------ | ------- | ----------------- |
| **P0** | 2.5 | `test_command_identity.py` does not exist at SHA 82abe02 | Create and commit the missing test file |
| **P0** | 2.6 | agent-docs-sync has uncommitted `__init__.py` and untracked `test_observability_import.py` | Commit the observability changes in agent-docs-sync |
| **P1** | 7.1 | Runtime validation claim is circular (mock-based, not backend-validated) | Add backend-reaching test or reclassify evidence level |
| **P1** | 7.2 | Span hierarchy claim validated by source inspection, not observed behavior | Add `InMemorySpanExporter`-based hierarchy assertion test |
| **P1** | 7.3 | Flush-before-exit validated by code inspection only | Add atexit registration assertion test |
| **P1** | 1.5 | Full focused suite output not preserved (partial snapshot only) | Re-run and preserve complete suite output |
| **P1** | 8.2 | `detect_changes()` was skipped (GitNexus unavailable) | Re-run `detect_changes()` or document unavailability |
| **P2** | 1.3 | Test docstring contradicts post-fix assertion state | Update test docstring to reflect current state |
| **P2** | 0.8 | Disposition evidence is code inspection, not runtime verification | Document evidence basis explicitly |
| **P3** | 4.6 | Test count attribution overlaps with task 4.5 | No action needed |

---

## Verified Tasks (no evidence gaps)

The following tasks have evidence that matches or exceeds their stated acceptance criteria at SHA `82abe02`:

- **0.1** — Errata section in baseline report ✓
- **0.2** — Config files read and documented in design.md ✓
- **0.3** — Langfuse unreachable, collector deferred ✓
- **0.4** — MLflow unreachable, collector deferred ✓
- **0.5** — autolog() compatible with pydantic-ai v2 ✓
- **0.6** — Route decisions in design.md ✓
- **0.7** — Delta specs use direct/autolog defaults ✓
- **1.1** — Exception propagation test passes ✓
- **1.2** — Pass-rate defect tests pass ✓
- **1.4** — Idempotency tests pass (2/2) ✓
- **2.1** — GitNexus impact report captured ✓
- **2.2** — `init_observability()` process-idempotent ✓
- **2.3** — `configure_metrics()` implemented ✓
- **2.4** — CLI callback calls `init_observability()` ✓
- **2.7** — Composition root addendum in design.md ✓
- **3.1–3.4** — Instrumentation ownership model documented ✓
- **3.5** — Duplicate span test passes (limited scope) ✓
- **4.1** — `_Suppress.__exit__` returns `True` ✓
- **4.2** — `_log_to_mlflow` semantics correct ✓
- **4.3** — `EvalRecord.trace_id` / `span_id` fields present ✓
- **4.4** — SQL migration additive and nullable ✓
- **4.5** — `store.py` populates trace_id/span_id ✓
- **5.1** — structlog processor injects trace_id/span_id ✓
- **5.2** — 2 correlation tests pass ✓
- **5.3** — Content-off defaults verified ✓
- **5.4** — `_SecretRedactionProcessor` implemented ✓
- **5.5** — 3 privacy tests pass ✓
- **6.1–6.4** — Route mode settings and deferred behavior ✓
- **6.5** — 5 backend isolation tests pass ✓
- **7.4** — 2 correlation tests pass ✓
- **7.5** — 9 evaluation tests pass ✓
- **7.6** — NoOpTracerProvider confirmed ✓
- **7.7** — Evidence levels in design.md ✓
- **8.1** — Ruff + pytest clean ✓
- **8.3** — openspec validate exit 0 ✓
- **8.4** — 39 deltas verified ✓
- **8.5** — Errata section added ✓
- **8.6** — Non-goals listed ✓
