## 1. Add FTS repair fallback to refresh script

- [x] 1.1 In `gitnexus_refresh()`, after the first `gitnexus analyze --index-only` fails (exit != 0 and exit != 124), add a fallback block: run `gitnexus analyze --repair-fts` inside the same subshell pattern (cd to root, same env vars, own `run_with_timeout` call piped through `redact`)
- [x] 1.2 Log the repair attempt: on success log `repair_attempted` with `note`, on failure log `repair_failed` with `warn`, capturing exit code
- [x] 1.3 If repair-fts succeeds (exit 0), treat as success and jump to the verification section (indexed_rev check)
- [x] 1.4 If repair-fts times out (exit 124), log `timeout_repair` and return 1 — do NOT proceed to force stage

## 2. Add force re-index fallback to refresh script

- [x] 2.1 When repair-fts fails with non-zero exit (not timeout), attempt `gitnexus analyze --force --index-only --default-branch "$branch" --name "$name"` with its own subshell (cd to root, same env vars) and `run_with_timeout` call. This is the primary fix for the `incrementalInProgress` flag (12 of 13 failing repos).
- [x] 2.2 Log the force attempt: on success log `force_attempted` with `note`, on failure log `force_failed` with `warn`
- [x] 2.3 If force succeeds (exit 0), treat as success and continue to verification section
- [x] 2.4 Only log `failed` and return 1 if all three stages (normal, repair, force) have failed
- [x] 2.5 On timeout (exit 124) in force stage, log `timeout_force` and return 1

## 3. Fix knowledge-status.sh version detection

- [x] 3.1 In `tool_version()`, change `"$tool" --version 2>&1 | head -1` to `"$tool" --version 2>/dev/null | head -1` so stderr warnings don't corrupt the version string

## 4. Update graphify skills across all platforms

- [x] 4.1 Run `graphify install --platform codex` to update `~/.codex/skills/graphify/`
- [x] 4.2 Run `graphify install --platform hermes` to update `~/.hermes/skills/graphify/`
- [x] 4.3 Run `graphify install --platform pi` to update `~/.pi/agent/skills/graphify/`
- [x] 4.4 Run `graphify install --platform copilot` to update `~/.copilot/skills/graphify/`
- [x] 4.5 Run `graphify install --platform opencode` to update `~/.config/opencode/skills/graphify/`
- [x] 4.6 Run `graphify install --platform gemini` to update `~/.gemini/skills/graphify/`
- [x] 4.7 Run `graphify install --platform agents` to update `~/Developer/.agents/skills/graphify/`
- [x] 4.8 Verify all platform `.graphify_version` files show `0.9.46`

## 5. Verify and test

- [x] 5.1 Run `bash refresh-knowledge-indexes.sh --repo /Users/androidteam/Developer/agent-docs-sync` to verify force fallback works on an `incrementalInProgress` repo
- [x] 5.2 Run `bash refresh-knowledge-indexes.sh --repo /Users/androidteam/Developer/tdt-core` to verify repair-fts fallback works on FTS-corrupted repo
- [x] 5.3 Run `bash knowledge-status.sh` and verify graphify version shows `0.9.46` (not warning text)
- [x] 5.4 Verify `gitnexus list` shows all repos with fresh index dates
