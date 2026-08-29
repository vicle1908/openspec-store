## Why

`~/.claude/settings.json` sets `ANTHROPIC_MODEL=fable[1m]`, but live probing shows `fable[1m]` returns HTTP 401 (invalid model) from api.phanmemvip.shop — the id no longer exists there. The working id, verified by direct Anthropic-format request and in active use by the `ANTHROPIC_DEFAULT_*_MODEL` variables, is `Claude-Fable[1m]`. The stale variable risks Claude Code resolving a 401 model in any code path that prefers `ANTHROPIC_MODEL`.

## What Changes

- Update `ANTHROPIC_MODEL` in `~/.claude/settings.json` from `fable[1m]` to `Claude-Fable[1m]`, aligning it with the already-working `ANTHROPIC_DEFAULT_FABLE_MODEL` / `ANTHROPIC_DEFAULT_OPUS_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL` / `ANTHROPIC_DEFAULT_HAIKU_MODEL` values and `CLAUDE_CODE_SUBAGENT_MODEL`.
- No other settings change; no provider, base URL, or capability variables touched.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None.

Config-value fix only — `skip_specs: true`.

## Impact

- `~/.claude/settings.json` — the single `ANTHROPIC_MODEL` env value; nothing else in the file, no other repo, no runtime service.
- Claude Code sessions launched after the edit resolve the verified model id.
- Evidence base: 2026-08-29 direct probes — `fable[1m]` → 401; `Claude-Fable[1m]` → 200 textbook Anthropic SSE.
