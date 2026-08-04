# Plan Review: 5provider-review-gates

**Reviewed:** 2026-08-04T06:05:00+07:00
**Providers:** Hermes, Claude Code, Codex, Antigravity, fable-5
**Verdict:** REQUEST CHANGES (5/5 providers)

## Alignment Summary

| Edge | Status | Issues |
|---|---|---|
| Spec ↔ Code | ⚠️ Drifting | 2 critical, 3 warnings |
| Code ↔ Docs | ⚠️ Drifting | 1 critical, 2 warnings |
| Docs ↔ Skills | ⚠️ Drifting | 1 critical, 1 warning |
| Skills ↔ Specs | ⚠️ Drifting | 2 critical, 2 warnings |
| Spec ↔ Docs | ✅ Aligned | 0 critical, 1 suggestion |
| Code ↔ Skills | ⚠️ Drifting | 1 critical, 2 warnings |

## Consensus Issues (flagged by 3+ providers)

### 1. Proposal format doesn't match OpenSpec expectations
**Flagged by:** Hermes, Codex, Antigravity
- Proposal uses "## Intent", "## Problem", "## Scope" but OpenSpec expects "## Why" and "## What Changes"
- The change validates but has warnings about missing required sections

### 2. "Product alignment" lens is not operationally defined
**Flagged by:** fable-5, Hermes, Antigravity
- The fable-5 lens says "Do product specs match UX implementation?" but doesn't define what "product alignment" means in practice
- No clear criteria for what constitutes a product alignment failure

### 3. Test alignment is prompt-level only, not evidence-backed
**Flagged by:** Codex, Hermes, Claude Code
- The quality lens mentions "test coverage" but doesn't define how to measure it
- No integration with `uv run pytest` or `make check-coverage`

## Provider-Specific Findings

### Hermes (Spec ↔ Code Alignment)

**CRITICAL:**
1. `openspec show --json` is not a complete artifact reader — JSON output may not include all artifact content
2. The six-edge contract is not implemented consistently — plan review checks 6 edges but code review only checks 4

**WARNINGS:**
1. No status semantics for alignment edges — what does "drifting" vs "broken" mean?
2. No traceability from alignment findings back to specific requirements
3. Provider review prompts are templated but not validated against actual artifact shapes

**SUGGESTIONS:**
1. Add a "status semantics" section defining exact criteria for each alignment state
2. Validate that `openspec show --json` returns all needed content before implementing

### Claude Code (Security Alignment)

**CRITICAL:**
1. No trust boundary defined — inputs from code, docs, skills could contain prompt injection
2. No least-privilege execution model — reviewers have access to everything

**WARNINGS:**
1. Credential exposure risk if review output includes sensitive data
2. No isolation between provider reviews — one compromised review could influence others

**SUGGESTIONS:**
1. Define trust boundaries for each input source
2. Add credential redaction to review output
3. Isolate provider reviews to prevent cross-contamination

### Codex (Quality Alignment)

**CRITICAL:**
1. Tests are absent from the formal alignment model — no "test ↔ spec" edge defined
2. No integration with actual test runners (pytest, make check-coverage)

**WARNINGS:**
1. Quality alignment is defined as "Do test specs match test coverage?" but no mechanism to measure coverage
2. No evidence collection — reviews are opinion-based, not data-driven

**SUGGESTIONS:**
1. Add a "test ↔ spec" alignment edge to the matrix
2. Integrate with `uv run pytest --cov` for evidence-based quality review
3. Collect coverage data as part of the review process

### Antigravity (Architecture Alignment)

**CRITICAL:**
1. Architecture lens changes between plan review and code review — not consistent
2. No definition of what "architecture alignment" means in practice

**WARNINGS:**
1. No reference architecture defined — how do you know if code follows patterns?
2. Skills integration not validated — will new skills work with existing Hermes skills?

**SUGGESTIONS:**
1. Define a consistent architecture lens for both review gates
2. Create a reference architecture document for the workspace
3. Test skill integration before implementing

### fable-5 (Product Alignment)

**CRITICAL:**
1. "Product alignment" is not operationally defined
2. No success criteria — how do you know if the change succeeded?

**WARNINGS:**
1. No user adoption model — will anyone actually use these skills?
2. No measurement of alignment drift reduction

**SUGGESTIONS:**
1. Define "product alignment" with specific, measurable criteria
2. Add success metrics: "alignment drift reduced by X%"
3. Create a pilot plan to test adoption before full implementation

## Recommended Actions

### Must Fix Before Implementation

1. **Fix proposal format** — Use OpenSpec's expected sections ("## Why", "## What Changes")
2. **Define alignment edge semantics** — What exactly constitutes "aligned", "drifting", "broken"?
3. **Add test alignment edge** — Expand from 6 to 7 edges: spec↔code, code↔docs, docs↔skills, skills↔specs, spec↔docs, code↔skills, **test↔spec**
4. **Define trust boundaries** — What inputs are trusted vs untrusted?
5. **Define success criteria** — How will you measure if this change succeeded?

### Should Address

6. **Validate `openspec show --json` output** — Ensure it returns all needed content
7. **Integrate with test runners** — Add `uv run pytest` and `make check-coverage` evidence
8. **Define architecture reference** — What patterns should code follow?
9. **Add credential redaction** — Prevent sensitive data in review output
10. **Create pilot plan** — Test with one change before full rollout

### Nice to Have

11. **Add adoption metrics** — Track skill usage over time
12. **Create alignment drift dashboard** — Visualize alignment status
13. **Automate alignment checks** — Run on PR creation

## Verdict

**All 5 providers recommend REQUEST CHANGES.** The alignment-drift problem is real and important, but the proposal needs:

1. **Better definition** — What exactly are we measuring?
2. **Evidence-based review** — Not just opinions, but data
3. **Trust boundaries** — Security review found critical gaps
4. **Success criteria** — How do we know it worked?

The two-gate concept and six-edge alignment model are sound foundations. With the above fixes, this can become a valuable addition to the OpenSpec workflow.
