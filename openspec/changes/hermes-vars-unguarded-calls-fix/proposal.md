# hermes-vars-unguarded-calls-fix

## Why

The `vars()` built-in Python function raises `TypeError: vars() argument must have __dict__ attribute` when called on objects without a `__dict__` attribute (e.g., Pydantic models with `__slots__`, frozen dataclasses, custom provider response types).

This error is causing **all 10 subagent reviewers** (across 2 batches of 5) to fail with serialization errors when producing their final summaries. The error manifests as:

```
summary: vars() argument must have __dict__ attribute
exit_reason: max_iterations (iteration budget exhausted)
```

**Root cause**: `conversation_loop.py:2631` has an unguarded `vars(response)` call in the error handling path for invalid provider responses. When the provider returns a non-standard response object during the max_iterations summary call, the `vars()` call fails, and the error string becomes the agent's final response.

**Impact**: Subagent delegation is effectively broken for any task that hits max_iterations or encounters provider errors. The parent agent receives an error string instead of the subagent's actual analysis.

## What Changes

### Fix unguarded vars() calls

8 locations in the hermes-agent codebase have unguarded `vars()` calls that can fail:

| File | Line | Context | Risk |
|------|------|---------|------|
| `agent/conversation_loop.py` | 2631 | Response attribute logging | **PRIMARY** — triggers the delegation error |
| `agent/conversation_compression.py` | 326-327 | Compressor attribute access | Medium — compression failures |
| `agent/conversation_compression.py` | 404 | Compressor values | Medium — compression failures |
| `agent/conversation_compression.py` | 438 | Compressor values | Medium — compression failures |
| `agent/anthropic_adapter.py` | 1887 | Response attribute iteration | Medium — Anthropic provider errors |
| `run_agent.py` | 2740 | Hook JSONable serialization | Low — caught by try/except |
| `run_agent.py` | 3061 | Compression fence access | Low — self always has __dict__ |
| `run_agent.py` | 7368, 7373, 7547 | Compression fence management | Low — self always has __dict__ |

**Fix pattern**: Wrap each unguarded `vars()` call in `try/except (TypeError, AttributeError)` with a fallback to `str(value)` or empty dict, matching the existing pattern in `relay_tools.py:100`:

```python
# Before (unguarded)
resp_attrs = {k: str(v)[:100] for k, v in vars(response).items()}

# After (guarded)
try:
    resp_attrs = {k: str(v)[:100] for k, v in vars(response).items()}
except (TypeError, AttributeError):
    resp_attrs = {"type": type(response).__name__, "repr": repr(response)[:200]}
```

### Improve delegation context delivery

The five-provider review pattern was passing file PATHS to subagents instead of inline content. This caused reviewers to exhaust their iteration budget reading files instead of producing analysis.

**Fix**: Always pre-collect ALL evidence into the `context` parameter as a string, never as a file path. The orchestration reference already states this:

> "Pre-collect ALL evidence in the orchestrator BEFORE spawning reviewers. Reviewers receive string context only — they cannot write files or run commands reliably within iteration budgets."

## Compatibility

- **Backward compatible**: All fixes are internal error handling improvements
- **No API changes**: Same tool interfaces, same provider contracts
- **No config changes**: No new configuration required

## Rollback

- Revert the git commits to hermes-agent
- Revert the skill updates for delegation pattern
