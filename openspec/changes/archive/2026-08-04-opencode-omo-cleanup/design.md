# Design: opencode-omo-cleanup

## Architecture

### Current State
```
OpenCode CLI v1.18.10
  ├── plugins/
  │   ├── opencode-antigravity-auth@beta
  │   ├── opencode-openai-codex-auth@latest
  │   ├── @tarquinen/opencode-dcp@latest
  │   └── oh-my-opencode@latest  ← REMOVE
  ├── opencode.jsonc (main config)
  ├── oh-my-opencode.json  ← REMOVE
  └── oh-my-opencode.json.bak.*  ← REMOVE
```

### Target State
```
OpenCode CLI v1.18.12
  ├── plugins/
  │   ├── opencode-antigravity-auth@beta
  │   ├── opencode-openai-codex-auth@latest
  │   └── @tarquinen/opencode-dcp@latest
  ├── opencode.jsonc (main config + native agents)
  └── agents/ (optional markdown agent definitions)
```

## Agent Mapping (oh-my-opencode → vanilla)

| omo Agent | omo Model | Vanilla Equivalent |
|---|---|---|
| build (default) | opus-4-5 max | Build primary agent (default) |
| plan | — | Plan primary agent (default) |
| atlas | sonnet-4-5 | General subagent |
| sisyphus | opus-4-5 max | Build primary (with opus-4-5) |
| sisyphus-junior | opus-4-5 thinking | Subagent with thinking budget |
| oracle | fable-5.2 | Custom subagent via config |
| prometheus | opus-4-5 max | Plan primary (with opus-4-5) |
| metis | opus-4-5 max | Subagent via config |
| momus | gpt-5.2 | Subagent via config |
| librarian | fable-5-4.7 | Subagent via config |
| explore | haiku-4-5 | Explore subagent (default, with haiku-4-5) |
| frontend | fable-5-pro | Subagent via config |
| document-writer | fable-5-3-flash | Subagent via config |
| multimodal-looker | gemini-3-flash | Subagent via config |

## Implementation Strategy

1. **Backup** — Copy all config files to `.bak.$(date)` variants
2. **Upgrade OpenCode** — `brew upgrade opencode` or `opencode upgrade`
3. **Clean config** — Remove oh-my-opencode plugin from plugin array, add native agent definitions
4. **Remove omo files** — Delete `oh-my-opencode.json` and backups
5. **Smoke test** — Verify `opencode run` and TUI work correctly
6. **Iterate** — Add/adjust agents based on actual usage patterns

## Risks

| Risk | Mitigation |
|---|---|
| Missing a feature from omo | Backup preserves ability to restore; can re-install plugin |
| Native agents don't support all omo agent features | Accept trade-off; native system is sufficient for our use cases |
| Local proxy behavior differs without omo hooks | omo hooks were not being used for proxy routing |
