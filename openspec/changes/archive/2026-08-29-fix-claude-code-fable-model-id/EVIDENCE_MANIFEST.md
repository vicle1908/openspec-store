# Evidence Manifest: fix-claude-code-fable-model-id

Date: 2026-08-29 · Applied and verified in one session. Sanitized — no credential values retained.

## 1. Preparation

- Grep across `~/.claude/settings.json`, `~/.claude/settings.local.json`, `~/.codex/config.toml`, `~/.grok/config.toml`, `~/.omp/agent/config.yml`, `~/.omp/agent/models.yml`, and workspace repos: `fable[1m]` appears in exactly TWO places, both in `~/.claude/settings.json` — line 11 (`"ANTHROPIC_MODEL": "fable[1m]"`) and line 82 (top-level `"model": "fable[1m]"`). No other config or repo references the stale id.
- Backup: `~/.claude/settings.json.bak-fix-claude-code-fable-model-id.20260829T170503` — mode 600, sha256 `4a470743b364201bffa1fc8d8703a737572919784e6a7b5ccb74641b500c33a3`, `cmp` byte-identical at capture time. Pre-edit env entry count: 15.

## 2. Mutation and verification

- Both stale values replaced with the verified id `Claude-Fable[1m]` via string-exact JSON-aware edit (pre/post assertions in the edit script):
  - `ANTHROPIC_MODEL`: `fable[1m]` → `Claude-Fable[1m]` (x1)
  - top-level `model`: `fable[1m]` → `Claude-Fable[1m]` (x1)
- Post-edit file parses as JSON; env entry count unchanged (15); `ANTHROPIC_DEFAULT_FABLE_MODEL` and neighbors byte-identical
- Redacted diff vs backup: exactly two value lines differ (lines 11 and 82); nothing else changed
- Live probe (post-edit): `POST https://api.phanmemvip.shop/v1/messages` with model `Claude-Fable[1m]`, Anthropic format → HTTP 200, `message_start` framing confirmed
- Contrasting evidence (from the 2026-08-29 dialect recheck): `fable[1m]` → HTTP 401 invalid model on the same endpoint; `Claude-Fable[1m]` is served as model `Claude-Fable` with the 1M-context selector

## 3. Notes

- Env values are read at Claude Code startup: running sessions keep the old resolution until restarted; new sessions pick up `Claude-Fable[1m]` immediately. No breakage in either window — the tier-default variables (`ANTHROPIC_DEFAULT_FABLE/OPUS/SONNET/HAIKU_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL`) already pointed at the working id.
- Rollback: restore the backup byte-identically (mode 600 lineage outside the git-tracked store).

## 4. Delivery

- Strict OpenSpec validation passed (skip_specs config fix)
- Committed to the store; see git log for the exact commit
