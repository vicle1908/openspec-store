## Why

The agent-docs-sync agent exists but is not integrated into CLI commands. Currently:

1. **Agent created but never called** — `build_generation_agent()` exists but CLI commands don't use it
2. **generate_updates is a placeholder** — Has comment "would call LLM" but doesn't
3. **CLI commands use workflow functions directly** — Bypass the agent entirely

This means no actual LLM calls are made during doc sync operations, defeating the purpose of having an agent.

## What Changes

- **Integrate agent into `update` command** — Use agent for doc generation
- **Integrate agent into `sync` command** — Use `build_sync_pipeline(use_agent=True)`
- **Keep `check` and `validate` deterministic** — No LLM needed for git diff or link checking
- **Add proper agent invocation** — Call `agent.run()` with doc generation tasks

## Capabilities

### Modified Capabilities

- `agent-docs-sync`: Integrate LLM agent into CLI commands where needed

## Impact

- **Code changes:** `cli.py`, `workflows/sync_pipeline.py`
- **No new dependencies** — Agent and gateway already implemented
- **Breaking changes:** None — agent integration is additive
