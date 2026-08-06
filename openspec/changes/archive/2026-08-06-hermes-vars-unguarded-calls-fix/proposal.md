# hermes-vars-unguarded-calls-fix

## Why

The `vars()` built-in Python function raises `TypeError: vars() argument must have __dict__ attribute` when called on objects without a `__dict__` attribute during LLM response serialization in hermes-agent.

This error manifests in subagent delegation:
- ~40% of reviewers fail with the error as their final summary
- The error is intermittent — same code path succeeds for some reviewers
- It only appears when the LLM response object lacks `__dict__`

## What Changes

### Do NOT: Patch hermes-agent framework code

The framework gets overwritten on every update. Direct patches are fragile and create maintenance burden. The vars() error is a **framework bug** that should be reported upstream.

### Do: Improve delegation workflow

1. **Always pass inline context** in `delegate_task` context parameter (never file paths)
2. **Accept ~60% automated review rate** — manual consolidation for failures
3. **Report the bug upstream** to hermes-agent maintainers
4. **Use the fallback procedure** when reviewers fail — see `references/subagent-serialization-error-fallback.md`

### Upstream Report

The bug locations are:
- `conversation_loop.py:2631` — unguarded `vars(response)` in error handling
- `turn_finalizer.py:142` — `_handle_max_iterations()` not wrapped in try/except
- `conversation_compression.py:326-327, 442` — unguarded `vars(compressor)`

All need try/except (TypeError, AttributeError) guards with fallback to str() or empty dict.

## Compatibility

- **No framework changes** — delegation pattern improvement only
- **Backward compatible** — existing reviews continue to work
- **60% automated rate** — acceptable for most use cases

## Rollback

No rollback needed — no code changes made.
