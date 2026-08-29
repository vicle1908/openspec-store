# Tasks: fix-claude-code-fable-model-id

Never print credential values from the settings file; probe outputs record status codes and model ids only.

## 1. Preparation

- [x] 1.1 Grep workspace configs for `fable[1m]` occurrences; found exactly two in `~/.claude/settings.json` (`ANTHROPIC_MODEL` env entry and top-level `model`) and none in other tool configs or workspace repos — both fixed by this change
- [x] 1.2 Capture a mode-600 backup of `~/.claude/settings.json` with recorded sha256 and verify byte-identical restore (`cmp`)

## 2. Mutate and verify

- [x] 2.1 Swap `ANTHROPIC_MODEL` from `fable[1m]` to `Claude-Fable[1m]` via JSON-aware edit; verify the file parses, env entry count is unchanged, and a redacted diff against the backup shows exactly one value changed
- [x] 2.2 Live-probe api.phanmemvip.shop `/v1/messages` with `Claude-Fable[1m]` (Anthropic format) and confirm HTTP 200 with `message_start` framing

## 3. Delivery

- [x] 3.1 Run `openspec validate fix-claude-code-fable-model-id --strict --store openspec-store` and confirm it passes
- [x] 3.2 Record sanitized evidence in the change directory and commit the store change
