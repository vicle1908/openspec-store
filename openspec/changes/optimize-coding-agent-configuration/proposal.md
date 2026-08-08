## Why

All 6 coding agents (Claude Code, agy, OpenCode, Pi, Codex, fable-5) are functional but running with conservative defaults that limit agentic potential:
- Claude Code: 68 redundant permission rules, bounded timeouts
- OpenCode: missing `external_directory` for cross-repo work
- Pi: 77 direct MCP tools causing timeouts
- Codex: `approval_policy` not set in config (requires per-invocation flag)
- fable-5: `plan_mode=false`, conservative context reserves

Goal: Maximize each agent's autonomous capability — full permissions, generous budgets, no approval prompts, all features enabled.

## What Changes

- Claude Code: clean permissions, unlimited timeouts, remove disabled-hooks list
- agy: no changes (already maximum)
- OpenCode: add `external_directory`, `doom_loop`, full `*` permission
- Pi: increase compaction reserves
- Codex: set `approval_policy=never` in config
- fable-5: enable `plan_mode`, reduce retry attempts, increase context reserves

## Impact

- Agent behavior: all agents become fully autonomous
- No production impact: config changes only
