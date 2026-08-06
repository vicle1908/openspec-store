# Tasks: hermes-vars-unguarded-calls-fix

## Phase 1: Update delegation skill
- [x] Update openspec-workflow skill with inline context mandate
- [x] Add subagent-serialization-error-fallback.md reference
- [x] Document vars() error root cause and workaround
- [x] Add pitfall: "Do NOT patch framework code"

## Phase 2: Report upstream
- [ ] File issue on hermes-agent GitHub repo with bug locations
- [ ] Include reproduction steps (delegate_task with max_iterations)
- [ ] Suggest fix: try/except (TypeError, AttributeError) guards

## Phase 3: Verify delegation works
- [ ] Run 5-reviewer batch with inline context
- [ ] Confirm ~60% automated success rate
- [ ] Verify manual consolidation works for failures
- [ ] Document actual success rate in review-plan.md

## Done
- [x] Revert all framework patches (turn_finalizer.py, conversation_loop.py, conversation_compression.py)
- [x] Skill updated with proper guidance
- [x] Proposal updated to reflect no-framework-patch approach
