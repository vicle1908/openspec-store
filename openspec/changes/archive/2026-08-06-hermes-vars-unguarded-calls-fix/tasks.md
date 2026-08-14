# Tasks: hermes-vars-unguarded-calls-fix

## Phase 1: Update delegation skill
- [x] Update openspec-workflow skill with inline context mandate
- [x] Add subagent-serialization-error-fallback.md reference
- [x] Document vars() error root cause and workaround
- [x] Add pitfall: "Do NOT patch framework code"

## Phase 2: Report upstream
- [x] [historical] File issue on hermes-agent GitHub repo with bug locations
- [x] [historical] Include reproduction steps (delegate_task with max_iterations)
- [x] [historical] Suggest fix: try/except (TypeError, AttributeError) guards

## Phase 3: Verify delegation works
- [x] [historical] Run 5-reviewer batch with inline context
- [x] [historical] Confirm ~60% automated success rate
- [x] [historical] Verify manual consolidation works for failures
- [x] [historical] Document actual success rate in review-plan.md

## Done
- [x] Revert all framework patches (turn_finalizer.py, conversation_loop.py, conversation_compression.py)
- [x] Skill updated with proper guidance
- [x] Proposal updated to reflect no-framework-patch approach


---

> **Historical record:** This change was archived with 7 incomplete task(s) (7/14 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
