## Why

The agent-docs-sync agent works correctly but users can't see what it's doing:

1. **No agent activity logs** — When agent runs, CLI shows only final result
2. **No tool usage visibility** — Can't see which tools the agent calls
3. **No LLM call timing** — Can't see how long LLM calls take
4. **No logging configuration** — agent-docs-sync CLI doesn't use agent-core's logging infrastructure

Users need visibility into agent operations to:
- Debug issues when agent doesn't work as expected
- Understand what the agent is doing
- Monitor performance and costs
- Verify tool usage is correct

## What Changes

- **Integrate agent-core logging infrastructure** — Use `configure_logging()` from `agent_core.foundation`
- **Add `--verbose` flag** to CLI commands for detailed output
- **Standardize logging** — Follow agent-core patterns for consistency
- **Show agent activity**: LLM calls, tool usage, iterations
- **Add progress indicators** during agent execution

## Architecture Decision

```
┌─────────────────────────────────────────────────────────────┐
│  LOGGING ARCHITECTURE                                        │
└─────────────────────────────────────────────────────────────┘

  agent-core (PROVIDES):
  ├─ foundation/logging.py
  │  ├─ configure_logging(level, log_format, agent_id)
  │  ├─ bind_task_context(task_id, agent_id)
  │  └─ clear_task_context()
  │
  └─ Already has --verbose, --quiet, --json flags

  agent-docs-sync (USES):
  ├─ Import configure_logging from agent_core.foundation
  ├─ Add --verbose flag to CLI
  └─ Call configure_logging when verbose enabled

  Do NOT: Modify agent-core
  DO: Use agent-core's existing logging infrastructure
```

## Capabilities

### Modified Capabilities

- `agent-docs-sync`: Integrate agent-core logging infrastructure and add verbose output

## Impact

- **Code changes:** `cli.py`, `agent.py` (minimal)
- **Dependencies:** agent-core (already a dependency)
- **Breaking changes:** None — verbose flag is optional
