# Tasks: hermes-vars-unguarded-calls-fix

## Phase 1: Fix primary vars() bug (conversation_loop.py)
- [ ] Read `~/.hermes/hermes-agent/agent/conversation_loop.py` around line 2631
- [ ] Wrap `vars(response)` in try/except (TypeError, AttributeError)
- [ ] Add fallback: `{"type": type(response).__name__, "repr": repr(response)[:200]}`
- [ ] Verify the fix doesn't break normal response handling

## Phase 2: Fix compression vars() calls
- [ ] Read `~/.hermes/hermes-agent/agent/conversation_compression.py` lines 292-438
- [ ] Wrap all unguarded `vars(compressor)` calls in try/except
- [ ] Add fallback to `str(compressor)` or empty dict
- [ ] Verify compression still works

## Phase 3: Fix Anthropic adapter vars() call
- [ ] Read `~/.hermes/hermes-agent/agent/anthropic_adapter.py` around line 1887
- [ ] Wrap `vars(value)` in try/except
- [ ] Verify Anthropic provider still works

## Phase 4: Fix run_agent.py vars() calls
- [ ] Read `~/.hermes/hermes-agent/run_agent.py` around lines 2740, 3061, 7368, 7373, 7547
- [ ] Assess risk: most are `vars(self)` on AIAgent instances (always have __dict__)
- [ ] Add guards where risk is non-zero
- [ ] Verify agent initialization and compression fence management

## Phase 5: Update delegation skill
- [ ] Update `workspace-knowledge-tools` skill with delegation best practices
- [ ] Add pitfall: "Always pass inline context, never file paths, to delegate_task"
- [ ] Add pitfall: "Pre-collect ALL evidence before spawning reviewers"
- [ ] Verify skill is accessible

## Phase 6: Test delegation
- [ ] Run a simple delegate_task with 3 parallel reviewers
- [ ] Verify all reviewers produce clean summaries (no vars() error)
- [ ] Verify iteration budget is not exhausted
- [ ] Commit all changes
