# Tasks

## 1. Backup and baseline

- [x] 1.1 Back up `~/.claude/settings.json`, `~/.claude/profiles/shopapikey.json`, `~/.claude/profiles/omniroute-pm.json`, and `~/.zshrc` to timestamped copies preserving mode bits, and verify each copy parses or sources as its original type
- [x] 1.2 Record the pre-change model value for every slot in those files and verify the captured count matches the number of slots the change intends to update

## 2. Global settings (surface yielded to `add-phanmemvip-codex-x-provider`)

- [x] 2.1 Set the top-level `model` key and the model aliases in `~/.claude/settings.json` to `Claude-Fable`, and verify the file parses with no suffixed model value and no credential in its `env` block
- [x] 2.2 Verify `ANTHROPIC_DEFAULT_OPUS_MODEL` resolves to `opus`, distinct from the fable alias
- [x] 2.3 Verify the global-settings requirement is absent from this change's delta, so `add-phanmemvip-codex-x-provider` owns that surface without a collision, and confirm both changes validate strictly with the other's delta applied

## 3. Provider profiles

- [x] 3.1 Set the top-level `model` and every model alias in `~/.claude/profiles/shopapikey.json` to `Claude-Fable` except `ANTHROPIC_DEFAULT_OPUS_MODEL`, which is set to `opus`
- [x] 3.2 Verify `~/.claude/profiles/shopapikey.json` parses, retains mode 600, keeps `ANTHROPIC_BASE_URL=https://api.phanmemvip.shop` and `CLAUDE_CODE_EFFORT_LEVEL=xhigh`, and no longer contains `fable[1m]`
- [x] 3.3 Replace `pm/Claude-Fable[1m]` with `pm/Claude-Fable` in `~/.claude/profiles/omniroute-pm.json`, covering the top-level model and every alias, and verify the file parses, retains mode 600, keeps its `apiKeyHelper` path and `modelOverrides` entry, and preserves the `pm/` prefix

## 4. Launcher arguments

- [x] 4.1 Change the `shopapikey()` model argument in `~/.zshrc` from `fable[1m]` to `Claude-Fable` and verify the function still passes `--settings` with the shopapikey profile
- [x] 4.2 Change the `omniroute()` model argument in `~/.zshrc` from `pm/Claude-Fable[1m]` to `pm/Claude-Fable` and verify the function still passes `--settings` with the omniroute profile
- [x] 4.3 Verify `cockpit()` is unchanged, that `~/.zshrc` parses in a fresh shell, and that all three launcher functions are defined

## 5. Provider acceptance verification

- [x] 5.1 Verify the live messages endpoint accepts `Claude-Fable` with HTTP 200 and a non-empty completion
- [x] 5.2 Verify the live messages endpoint accepts `opus` with HTTP 200 and a non-empty completion
- [x] 5.3 Verify the endpoint does not require the `[1m]` suffix by confirming the unsuffixed identifiers are accepted, and record the served model name for each

## 6. Client verification

- [x] 6.1 Verify a non-interactive Claude Code invocation under the shopapikey profile exits zero, and record whether the client emits an unrecognized-model warning so the difference between a warning and a failure is captured as evidence
- [x] 6.2 Verify no local file owned by this change still contains `Claude-Fable[1m]` or `fable[1m]`

## 7. Specification sync

- [x] 7.1 Verify the three capability deltas validate strictly and that each modified requirement block preserves every scenario the main spec currently has
- [x] 7.2 Sync the deltas into `claude-code-provider-profile-resolution`, `claude-code-provider-routing`, and `claude-code-omniroute-pm-routing`, and verify each main spec now names the unsuffixed identifiers and the full launcher and profile sets
- [x] 7.3 Verify no main spec still asserts a launcher or profile set that excludes `omniroute`, and that `openspec validate --all --strict` reports no new failures

## 8. Integration verification

- [x] 8.1 Verify the cockpit provider is untouched: `cockpit.json` still pins `gpt-5.6-luna[1m]` with `effort,max_effort` and `CLAUDE_CODE_EFFORT_LEVEL=max`
- [x] 8.2 Verify every `apiKeyHelper` path and profile permission is unchanged from the pre-change baseline
- [x] 8.3 Record the operational items this change does not address — the Codex provider account's stale upstream OAuth token and the OmniRoute gateway's missing provider credential — as separate issues in the change notes
