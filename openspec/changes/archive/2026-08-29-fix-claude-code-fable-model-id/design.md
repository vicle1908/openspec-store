## Context

`~/.claude/settings.json` env block currently contains:

- `ANTHROPIC_BASE_URL=https://api.phanmemvip.shop` (Claude Code appends `/v1/messages`)
- `ANTHROPIC_MODEL=fable[1m]` — STALE: direct probe returns 401 invalid model
- `ANTHROPIC_DEFAULT_FABLE_MODEL` / `OPUS` / `SONNET` / `HAIKU` / `CLAUDE_CODE_SUBAGENT_MODEL` = `Claude-Fable[1m]` — all working ids

The 2026-08-29 dialect probes (recorded in the OmniRoute recheck session) proved `Claude-Fable[1m]` serves proper Anthropic Messages SSE on phanmemvip (message_start → thinking content blocks) while `fable[1m]` is gone (401).

## Goals / Non-Goals

**Goals:**

- Make `ANTHROPIC_MODEL` point at the verified model id so every Claude Code resolution path (primary model included, not just tier defaults) hits a working id.
- Preserve every other env value byte-identical.

**Non-Goals:**

- No change to `ANTHROPIC_BASE_URL` (Claude Code stays direct-to-phanmemvip; routing it through OmniRoute is a separate future change that requires registering an anthropic-compatible phanmemvip connection in OmniRoute first).
- No changes to other tools' configs.

## Decisions

1. **Edit the value in place, preserving JSON formatting** — a surgical value swap in the env block; the file is JSON so a JSON-aware edit with value equality assertions is safer than sed.
2. **Verify with a fresh live probe after the edit** — repeat the direct Anthropic-format request with `Claude-Fable[1m]` (expect 200; already proven pre-edit, re-confirmed post-edit for the record) and assert the settings file still parses as JSON with all other keys unchanged (count of env entries before == after).
3. **Backup before mutation** — mode-600 copy of `~/.claude/settings.json` with sha256 recorded, `cmp`-verified restore path, kept outside the git-tracked store (the file may embed other operator values).

## Risks / Trade-offs

- [Claude Code session currently running with old env] → env is read at startup; running sessions keep old behavior until restart. No breakage either way since the tier-default ids already work.
- [Other automation referencing fable[1m]] → grep for `fable[1m]` across workspace configs; only this one occurrence is expected (verified in the session: the DEFAULT_* vars already use the new id).

## Migration Plan

1. Backup `~/.claude/settings.json` (mode 600, sha256).
2. Swap `ANTHROPIC_MODEL` value `fable[1m]` → `Claude-Fable[1m]` via JSON-aware edit.
3. Verify: JSON parses, env entry count unchanged, only the one value differs (redacted diff vs backup), live probe 200 on `Claude-Fable[1m]`.
4. Validate the change strictly and commit the store change.
