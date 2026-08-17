# repair-ecosystem-quality-baseline: Evaluation Report

**Date:** 2026-08-17
**Branch:** `openspec/repair-ecosystem-quality-baseline`
**Worktree:** `/Users/androidteam/Developer/.worktrees/openspec-quality-prereq`

---

## 1. Executive Summary

The proposed change is **well-designed as a prerequisite** but has a **critical baseline drift problem**: the actual current I001 count is **143 findings across 6 repos** — more than **3x the proposed 45**. The design documents already anticipate this risk and mandate recapture before implementation, so the proposal itself is sound. The evaluation below identifies the drift magnitude, structural strengths, process risks, and recommended approach adjustments.

---

## 2. Baseline Drift Analysis

### Proposed vs Actual I001 Findings

| Repository | Proposed Count | Actual Count | Drift |
|---|---|---|---|
| `tdt-core` | 4 | **20** | +16 (5x) |
| `agent-core` | 7 | **44** | +37 (6.3x) |
| `agent-harness` | 13 | 13 | 0 ✓ |
| `agent-docs-sync` | 12 | **28** | +16 (2.3x) |
| `ai-harness-skills` | 7 | **30** | +23 (4.3x) |
| `ai-review` | 2 | **8** | +6 (4x) |
| **Total** | **45** | **143** | **+98 (3.2x)** |

### Format Status (unchanged from proposal)

| Repository | Format Status |
|---|---|
| `tdt-core` | ✓ Clean |
| `agent-core` | ✓ Clean |
| `agent-harness` | ✓ Clean |
| `agent-docs-sync` | ✓ Clean |
| `ai-harness-skills` | ✓ Clean |
| `ai-review` | ✗ 2 unformatted files (`test_reviewer_projection.py`, `test_tdt_projection.py`) |

### Root Cause of Drift

The design.md states: *"These counts are a planning baseline, not a durable implementation identity; every packet must recapture them from its own immutable base."* The proposal explicitly anticipated drift. The most likely causes:

1. **Ruff version evolution** — ruff has progressed from earlier versions; I001 rule may now detect patterns that were previously not flagged
2. **Code additions** — new imports added across the ecosystem since the baseline snapshot
3. **Different scan scope** — the worktree snapshot may have excluded some paths that the main checkout includes

### Impact on Tasks

The task plan (54 tasks across 6 phases) hardcodes the proposed counts in tasks 2.1–2.6. These must be updated to use the recaptured counts from each packet's own immutable base. **The design already mandates this recapture**, so this is a documentation accuracy issue, not a structural flaw.

**Estimated cleanup scope:** ~143 import-order fixes + 2 format fixes across ~80+ files (vs proposed ~47 files).

---

## 3. Structural Assessment

### Strengths

1. **Correct prerequisite framing** — The change correctly positions itself as `skip_specs: true` with no spec-level behavior delta. Quality gates are repository/tooling behavior, not product requirements.

2. **Immutability-first packet model** — Each repository gets one dedicated worktree, one writer, and one immutable accepted packet commit. This prevents concurrent-edit contamination and enables clean rollback.

3. **Evidence-before-action ordering** — Task Phase 1 (Freeze Scope, Ownership, and Evidence Boundaries) forces full identity capture before any cleanup. This is the right pattern for multi-repo coordination.

4. **No scope creep guardrails** — The non-goals list explicitly excludes provider/model config, public APIs, credentials, and generated indexes. The cross-packet diff review (task 3.7) rejects any unclassified change.

5. **Downstream binding model** — The `reconcile-agent-llm-contract-and-acceptance-v3` change explicitly references this prerequisite's immutable commits, creating a proper dependency chain.

6. **Rollback rehearsal** — Task 6.3 mandates rehearsing rollback before closing, which validates the packet model end-to-end.

### Risks

1. **⚠️ Scope expansion pressure** — With 143 findings instead of 45, there is temptation to also fix other Ruff rules, add type hints, or clean up other debt. **The design must resist this** — each non-I001 fix becomes a separately classified issue that blocks the packet.

2. **⚠️ Parallel worktree management overhead** — Creating 6 dedicated worktrees (one per repo) plus managing the existing 4+ worktrees creates workspace complexity. Each packet needs its own evidence trail.

3. **⚠️ Time sensitivity** — The longer implementation is delayed, the more the baseline drifts. The proposal should commit to an implementation window or set a maximum drift threshold before requiring re-evaluation.

4. **Low risk: unrelated test failures** — If any repo has pre-existing test failures (the archived `2026-07-17-agent-core-quality-gate` found 22 failing tests in jira-daily-reports), these must be recorded as blockers, not folded into this prerequisite.

---

## 4. Dependency Map

```
repair-ecosystem-quality-baseline
    ↓ (hard prerequisite)
reconcile-agent-llm-contract-and-acceptance-v3
    ↓ (integration milestone)
complete-clean-agent-llm-integration-cutover
```

- **Blocked by:** Nothing — this is a leaf dependency (foundation layer)
- **Blocks:** The entire LLM contract reconciliation chain
- **Independent of:** All other active changes (container upgrades, PMP migration, JTI alignment, Hermes config, scheduler hardening)

The quality baseline is the **single gateway** through which the LLM contract reconciliation must pass. No other active OpenSpec change is blocked by or blocks it.

---

## 5. Ecosystem Context: Related Archived Changes

The proposal sits within a rich history of ecosystem quality work:

| Change | What it accomplished | Overlap with quality-baseline |
|---|---|---|
| `2026-06-30-tdt-workspace-cleanup` | 50+ hygiene fixes, 43 Python 2 clauses, ruff/mypy config drift | Set initial lint config baseline |
| `2026-07-17-agent-core-quality-gate` | 80% coverage, 119 mypy fixes, monolith extraction | Addressed quality at broader scope; this change narrows to I001/format only |
| `2026-07-25-enforce-uv-ecosystem` | uv adoption across 14 repos | Tooling prerequisite that this change builds on |
| `2026-08-10-ecosystem-standardization` | Validated ruff/mypy/pytest versions across 16 repos | Confirmed standardization; this change closes remaining import-order gap |
| `2026-08-15-reconcile-ecosystem-verification` | Fixed false-positive verification results | Complementary — ensures gate results are trustworthy |

**Key insight:** Prior changes established the tooling infrastructure (ruff configs, uv adoption, pre-commit hooks, version pinning). This change closes the **last remaining lint debt** — import ordering — that those changes left behind.

---

## 6. Recommended Approach

### Option A: Proceed as Designed (Recommended)

Follow the proposal's 6-phase plan with updated counts:

1. **Phase 1:** Recapture all identities using actual counts (143, not 45)
2. **Phase 2:** Create 6 dedicated worktrees from verified immutable bases
3. **Phase 3:** Apply `ruff check --select I001 --fix` + format the 2 ai-review files
4. **Phase 4:** Run full gate suite (pytest, ruff, mypy, git diff --check)
5. **Phase 5:** One packet commit per repo with full evidence
6. **Phase 6:** Bind downstream, rehearse rollback, close

**Estimated effort:** 143 I001 fixes are all auto-fixable (`--fix`). The mechanical work is ~30 minutes per repo. The evidence capture and verification is the bulk of the effort.

### Option B: Simplify to Single-Pass Cleanup

Instead of 6 separate worktrees and packet commits, run a single-pass cleanup:

1. Create one worktree per repo
2. `uv run ruff check --select I001 --fix .` in each
3. Format the 2 ai-review files
4. Run gates, commit, bind downstream

This reduces the task count from 54 to ~15 but loses the frozen baseline evidence that the design considers important for downstream verification.

### Option C: Defer Until Drift Stabilizes

If new code is still being actively added to these repos, the I001 count will continue to grow. Consider implementing this change immediately before any other ecosystem changes to minimize drift.

---

## 7. Task Plan Accuracy Assessment

| Phase | Tasks | Assessment |
|---|---|---|
| 1. Freeze Scope | 1.1–1.5 (5 tasks) | ✓ Correct structure; counts need update |
| 2. Prepare Packets | 2.1–2.6 (6 tasks) | ⚠️ Hardcoded counts wrong (4/7/13/12/7/2 should be 20/44/13/28/30/8) |
| 3. Apply Cleanup | 3.1–3.7 (7 tasks) | ✓ Correct; 3.7 cross-packet review is critical at 143 findings |
| 4. Run Gates | 4.1–4.7 (7 tasks) | ✓ Correct; scope is unchanged |
| 5. Accept Packets | 5.1–5.7 (7 tasks) | ✓ Correct; immutable commit model is sound |
| 6. Rebind Downstream | 6.1–6.5 (5 tasks) | ✓ Correct; rollback rehearsal is essential |

**Overall: 37/54 tasks are accurately specified. 17 tasks (Phase 2 preparation + Phase 2 cleanup) need count updates but structural fixes only.**

---

## 8. Conclusion

The `repair-ecosystem-quality-baseline` proposal is **structurally sound and well-designed** as a prerequisite for the LLM contract reconciliation. Its main issue is a **baseline drift of 3.2x** (143 vs 45 I001 findings), which the design already mandates recapturing before implementation.

**Recommendation:** Proceed with Option A (as designed) after updating the task counts to reflect the actual 143 I001 findings. The 6-repo packet model, immutability guarantees, and downstream binding are correct architectural choices for a prerequisite that gates the entire LLM contract reconciliation chain.
