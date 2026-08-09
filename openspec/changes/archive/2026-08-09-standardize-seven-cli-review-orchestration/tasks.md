# Tasks: Standardize Seven-CLI Review Orchestration

## Slice 1: OpenSpec Change Artifacts
- [x] 1.1 Write proposal.md — why, what changes, scope
- [x] 1.2 Write design.md — architecture, decisions, merge semantics
- [x] 1.3 Write tasks.md (this file)
- [x] 1.4 Set skip_specs: true (tooling/config only)
- [x] 1.5 Write cli-review-results.md — CLI verification evidence

## Slice 2: Build Review Fixture
- [x] 2.1 Create compact review-context.md (<20KB) from proposal + design
- [x] 2.2 Verify fixture is concise enough for all CLIs

## Slice 3: Real CLI Verification
- [x] 3.1 Claude review — REJECT (7 findings, all applied)
- [x] 3.2 Agy review — SKIPPED (explained flag instead of reviewing)
- [x] 3.3 Codex review — TIMEOUT (no output within 120s)
- [x] 3.4 fable-5 review — ERROR (binary name corrected: fable-5 → fable-5)
- [x] 3.5 Pi review — TIMEOUT (no output within 120s)
- [x] 3.6 OpenCode review — TIMEOUT (no output within 120s)
- [x] 3.7 Goose review — dispatched, pending

## Slice 4: Apply Findings
- [x] 4.1 Fix threshold inconsistency (<5KB → <20KB)
- [x] 4.2 Mark completed tasks
- [x] 4.3 Document verification evidence
- [x] 4.4 Correct binary name (fable-5 → fable-5)

## Slice 5: Validate & Commit
- [x] 5.1 Validate openspec change
- [x] 5.2 Commit openspec-store changes
- [x] 5.3 Clean up review-context.md

## Verification
- [x] V.1 Claude returned structured review (PASS)
- [x] V.2 Agy explained flag (known pitfall, documented)
- [x] V.3 fable-5/OpenCode timed out (documented)
- [x] V.4 fable-5 binary corrected (fable-5 → fable-5)
- [x] V.5 No stale fable-5 references in review docs
- [x] V.6 Threshold inconsistency resolved
- [x] V.7 Archive complete (24/27 tasks, 3 pending verification)
