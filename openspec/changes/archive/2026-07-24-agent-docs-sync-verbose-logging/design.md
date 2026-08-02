## Context

agent-docs-sync agent works correctly but CLI doesn't show agent activity. The CLI doesn't use agent-core's existing logging infrastructure.

## Goals / Non-Goals

**Goals:**
- Integrate agent-core's `configure_logging()` infrastructure
- Add `--verbose` flag to CLI commands
- Show agent activity: LLM calls, tool usage, iterations
- Standardize logging patterns across TDT ecosystem

**Non-Goals:**
- Modifying agent-core (it already provides logging infrastructure)
- Adding Postgres audit logging (separate concern)
- Real-time streaming (batch is sufficient)

## Decisions

### Decision 1: Use agent-core Logging Infrastructure

```python
# agent-docs-sync/cli.py — Import from agent-core
from agent_core.foundation import configure_logging

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    quiet: bool = typer.Option(False, "--quiet", "-q"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """agent-docs-sync CLI."""
    level = "DEBUG" if verbose else "WARNING" if quiet else "INFO"
    fmt = "json" if json_output else "console"
    configure_logging(level=level, log_format=fmt)
```

### Decision 2: Agent Activity Logging

```python
# agent-docs-sync/agent.py — Use bind_task_context
from agent_core.foundation import bind_task_context, clear_task_context

async def run_agent_with_logging(agent, task):
    run_id = str(uuid.uuid4())
    bind_task_context(task_id=run_id, agent_id=agent.name)
    
    try:
        result = await agent.run(task)
        return result
    finally:
        clear_task_context()
```

### Decision 3: Progress Indicators

```
┌─────────────────────────────────────────────────────────┐
│  docs-sync update --verbose                              │
└─────────────────────────────────────────────────────────┘

  [INFO] Detecting changes...
  [INFO] Found 2 source files changed
  [INFO] Analyzing impact...
  [INFO] Found 3 docs affected
  [INFO] Calling agent for doc generation...
  [DEBUG] Agent run_id: abc123
  [DEBUG] Using model: cx/claude-opus-4.8-4.8-4.8.5
  [DEBUG] Tool called: read_doc (docs/api.md)
  [INFO] Agent completed in 2.3s
  [INFO] Updated 3 files
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Logging Integration                                         │
└─────────────────────────────────────────────────────────────┘

  agent-core.foundation.logging
         │
         ▼
  configure_logging(level, log_format)
         │
         ▼
  structlog configured
         │
         ▼
  Agent logs events
         │
         ├─ agent_run_complete
         ├─ tool_registered
         └─ skill_shadowed
         │
         ▼
  CLI displays logs (when --verbose)
```

## Implementation Pattern

```python
# cli.py - Use agent-core's logging

from agent_core.foundation import configure_logging

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed agent activity"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """agent-docs-sync CLI."""
    level = "DEBUG" if verbose else "WARNING" if quiet else "INFO"
    fmt = "json" if json_output else "console"
    configure_logging(level=level, log_format=fmt)
```

## Testing Strategy

| Test Type | Scope |
|-----------|-------|
| Unit | Logging configuration, verbose flag |
| Integration | CLI with verbose output |
| E2E | Agent activity visibility |
