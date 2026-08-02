## Context

agent-docs-sync has an agent (GenerationAgent) that can make LLM calls, but the CLI commands don't use it. The `generate_updates` function is a placeholder that doesn't call the agent.

## Goals / Non-Goals

**Goals:**
- Integrate agent into `update` command for doc generation
- Integrate agent into `sync` command via `build_sync_pipeline(use_agent=True)`
- Keep `check` and `validate` deterministic (no LLM needed)
- Properly wire agent invocation with tool access

**Non-Goals:**
- Using agent for deterministic operations (git diff, link checking)
- Adding new agent features (existing agent is sufficient)
- Changing agent-core or pydantic-ai

## Decisions

### Decision 1: Hybrid Approach (Agent + Deterministic)

```
┌─────────────────────────────────────────────────────────┐
│  Command        Agent?    Rationale                      │
│  ───────        ──────    ─────────                      │
│  check          NO        Git diff is deterministic      │
│  validate       NO        Link checking is deterministic │
│  update         YES ✓     Doc generation needs LLM       │
│  sync           YES ✓     generate_updates needs LLM     │
└─────────────────────────────────────────────────────────┘
```

### Decision 2: Agent for generate_updates Only

The agent should only be used for the `generate_updates` step, not for:
- `detect_changes` (git diff)
- `analyze_impact` (config lookup)
- `validate` (link checking)
- `report` (formatting)

### Decision 3: Use build_sync_pipeline(use_agent=True)

For the `sync` command, use the existing `build_sync_pipeline(use_agent=True)` which properly wires the agent into the workflow.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  CLI Command Flow                                         │
└─────────────────────────────────────────────────────────┘

  check (no agent)
  ════════════════
  detect_changes → analyze_impact → validate → report
  └─ All deterministic functions

  update (with agent)
  ═════════════════
  detect_changes → analyze_impact → [AGENT] → validate → report
                              generate_updates
                              └─ agent.run(task)

  validate (no agent)
  ═══════════════════
  CheckLinksTool.execute()
  └─ Deterministic link checking

  sync (with agent)
  ══════════════════
  build_sync_pipeline(use_agent=True)
  └─ Uses WorkflowBuilder with agent node
```

## Implementation Pattern

```python
# cli.py - update command with agent

@app.command()
def update(
    repo: str = typer.Option(".", help="Repository root path"),
    base_ref: str = typer.Option("HEAD~1", help="Base ref for git diff"),
    dry_run: bool = typer.Option(False, help="Preview changes without writing"),
) -> None:
    """Update documentation based on code changes."""
    from pathlib import Path
    from .llm.config import load_llm_config
    from .llm.gateway import create_gateway
    from .agents import build_generation_agent
    from .workflows.sync_pipeline import detect_changes, analyze_impact, validate, report

    async def _run() -> dict:
        # Deterministic steps
        ctx = {"repo_root": repo, "base_ref": base_ref}
        ctx = await detect_changes(ctx)
        ctx = await analyze_impact(ctx)

        # Agent step for doc generation
        if ctx.get("affected_docs"):
            app_root = Path(__file__).parent.parent
            config = load_llm_config(app_root)
            gateway = create_gateway(config)
            agent = build_generation_agent(gateway, config)

            # Run agent with doc generation task
            task = f"Generate documentation updates for: {ctx['affected_docs']}"
            result = await agent.run(task)
            ctx["pending_updates"] = result.output

            await gateway.close()
        else:
            ctx["pending_updates"] = []

        # Deterministic steps
        ctx = await validate(ctx)
        ctx = await report(ctx)
        return ctx

    result = asyncio.run(_run())
    # ... output handling
```

## Error Handling

| Error | Handling |
|-------|----------|
| Agent fails | Log error, continue with remaining steps |
| LLM unavailable | Skip generate_updates, report partial results |
| Tool execution fails | Return ToolResult(success=False, error=...) |

## Testing Strategy

| Test Type | Scope |
|-----------|-------|
| Unit | Agent invocation in CLI |
| Integration | Full sync pipeline with agent |
| E2E | CLI commands with real LLM calls |
