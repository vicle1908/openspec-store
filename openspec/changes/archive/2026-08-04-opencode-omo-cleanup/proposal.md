# Proposal: Remove oh-my-openagent and Configure Vanilla OpenCode

## Why

The oh-my-openagent (oh-my-opencode) plugin is installed as a layer on top of OpenCode CLI, adding 12 custom agents, category routing, background concurrency limits, and lifecycle hooks. After analysis:

1. **Redundant model routing** — All 12 agents route through a local proxy (127.0.0.1:8045) that already handles provider selection. The plugin's agent-to-model mapping adds no value over vanilla OpenCode agents.
2. **v4.19.4 is the last plugin release** — oh-my-openagent is transitioning to a native CLI. Continuing to invest in plugin config means a double migration later.
3. **Overhead and fragility** — The plugin adds package dependencies, its own config file, and lifecycle hooks that can break across OpenCode upgrades.
4. **OpenCode's native agent system is mature** — Build, Plan, General, Explore, Scout + custom agents via markdown files cover all current use cases.
5. **Token efficiency** — The current setup defaults to Opus 4.5 "max" for the Sisyphus orchestrator, meaning every message hits the most expensive model even for trivial tasks.

## What

### Remove
- `oh-my-opencode@latest` plugin from `opencode.jsonc` plugin array
- `oh-my-opencode.json` config file
- Associated backup files (`.bak.*`)

### Upgrade
- OpenCode CLI from v1.18.10 → v1.18.12 (via Homebrew)

### Add (vanilla agents in opencode.jsonc)
- Recreate essential agent mappings using OpenCode's native `agent` config
- Map explore, oracle, librarian, and frontend agents to appropriate models via subagent definitions
- Keep the local proxy provider setup unchanged

### Keep
- `opencode-antigravity-auth@beta` plugin (Antigravity proxy auth)
- `opencode-openai-codex-auth@latest` plugin (Codex auth)
- `@tarquinen/opencode-dcp@latest` plugin (DCP)
- All MCP servers (mcp-router, agentmemory)
- All provider configurations (Anthropic, Google, Z.ai via local proxy)
- Permission and tool settings

## Compatibility

- **Backward compatible**: No breaking changes to existing workflows
- **Forward compatible**: Vanilla config is aligned with OpenCode's native system, avoiding future plugin→native migration pain
- **Rollback**: Backup all config files before changes; restore from backup if issues arise

## Skip Specs

This is a config/tooling change only — no spec delta required.
