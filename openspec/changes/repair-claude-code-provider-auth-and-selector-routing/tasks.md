# Tasks: repair-claude-code-provider-auth-and-selector-routing

## Phase 0: Pre-change Baseline

- [x] 0.1 Capture Claude Code version and confirm auth warning present.
  - Evidence: `claude --version` → 2.1.228; screenshot and local capture confirm `Both ANTHROPIC_AUTH_TOKEN and apiKeyHelper set` warning.
- [x] 0.2 Capture pre-change state of `~/.claude/settings.json`.
  - Evidence: `model: fable[1m]`, `apiKeyHelper` present, no `ANTHROPIC_AUTH_TOKEN` in env block. mode=644.
- [x] 0.3 Capture pre-change state of all three profile JSONs.
  - Evidence: shopapikey (fable[1m], mode=600), giaoduc (Advance[1m], mode=600), cockpit (gpt-5.6-luna [BARE, missing [1m]], mode=600).
- [x] 0.4 Capture pre-change state of `~/.claude/helpers/*.sh`.
  - Evidence: all three scripts present, mode=700, source `~/.hermes/.env`.
- [x] 0.5 Capture pre-change state of `~/.zshrc` launcher block.
  - Evidence: L240-243 contain literal credential exports; L250-257 define `_claude_require_token`; L283-346 define launchers and reset. `ANTHROPIC_AUTH_TOKEN` exported by all three launchers. `CLAUDE_CODE_SUBAGENT_MODEL` not unset by `claude_reset()`.

## Phase 1: OpenSpec Artifacts

- [x] 1.1 Write `proposal.md` with Why, What Changes, Security, Rollback.
- [x] 1.2 Write `design.md` with Problem, Solution Architecture, Auth Mutual Exclusivity Contract, Files Modified, Security, Verification.
- [x] 1.3 Write delta spec for `claude-code-provider-routing` with ADDED requirements for auth mutual exclusivity, helper preflight, credential-free shell config, and reset completeness.
- [x] 1.4 Write delta spec for `claude-code-provider-profile-resolution` with ADDED requirements for launcher auth isolation, helper preflight, credential-free shell config.
- [x] 1.5 Write `tasks.md` and `evidence.md`.
- [x] 1.6 Run focused OpenSpec validation for this change.
  - Evidence: `openspec validate repair-claude-code-provider-auth-and-selector-routing --store openspec-store` → valid.
- [x] 1.7 Run full-store OpenSpec validation.
  - Evidence: final `openspec validate --all --store openspec-store` → 362 passed, 0 failed.
- [x] 1.8 Run `git diff --check` on the store.
  - Evidence: clean.

## Phase 2: Backup

- [x] 2.1 Back up `~/.zshrc` to `~/.zshrc.pre-repair-auth-20260812_113415`.
- [x] 2.2 Back up `~/.claude/profiles/cockpit.json` to `~/.claude/profiles/cockpit.json.pre-repair-20260812_113415`.
- [x] 2.3 Verify backup files exist and have expected content.
  - Evidence: both files exist mode 600; backup contents captured before mutation.

## Phase 3: Remove Plaintext Credentials from ~/.zshrc

- [x] 3.1 Remove credential export block (L240-243: all four `HERMES_CUSTOM_*_API_KEY` assignments).
  - Evidence: post-change grep found zero literal provider credential assignments/values in `~/.zshrc`, `~/.zshenv`, or `~/.zprofile`.
- [x] 3.2 Run `zsh -n ~/.zshrc` to verify syntax.
  - Evidence: PASS.

## Phase 4: Refactor Auth Validation

- [x] 4.1 Replace `_claude_require_token` with `_claude_require_helper` that invokes the helper script with stdout/stderr to /dev/null and produces a generic provider-named error on failure.
  - Evidence: `_claude_require_helper` present; negative preflight returned exit 1, `Error: shopapikey credential unavailable`, stdout empty.
- [x] 4.2 Update all three launcher guard calls to `_claude_require_helper <helper-path> <provider-name>`.
  - Evidence: shim output and structural grep show 3 provider calls plus function definition.

## Phase 5: Remove ANTHROPIC_AUTH_TOKEN from Launchers

- [x] 5.1 Remove `export ANTHROPIC_AUTH_TOKEN="$HERMES_CUSTOM_*_API_KEY"` from all three launcher subshells.
  - Evidence: structural grep found zero exports.
- [x] 5.2 Add defensive `unset ANTHROPIC_AUTH_TOKEN` inside all three launcher subshells.
  - Evidence: shim output showed `ANTHROPIC_AUTH_TOKEN=<absent>` for shopapikey, giaoduc, cockpit.
- [x] 5.3 Run `zsh -n ~/.zshrc` to verify syntax.
  - Evidence: PASS.

## Phase 6: Restore Cockpit [1m] Selector

- [x] 6.1 Update `~/.claude/profiles/cockpit.json` selectors and aliases to `gpt-5.6-luna[1m]`.
  - Evidence: all seven model selector fields verified; JSON mode=600.
- [x] 6.2 Update `~/.zshrc` cockpit launcher fallback to `gpt-5.6-luna[1m]`.
  - Evidence: shim argv contains `--model gpt-5.6-luna[1m]`.
- [x] 6.3 Validate JSON: `python3 -m json.tool ~/.claude/profiles/cockpit.json`.
  - Evidence: PASS.

## Phase 7: Fix claude_reset()

- [x] 7.1 Add `unset CLAUDE_CODE_SUBAGENT_MODEL` to `claude_reset()`.
  - Evidence: source grep and reset shim output.
- [x] 7.2 Run `zsh -n ~/.zshrc` to verify syntax.
  - Evidence: PASS.

## Phase 8: Verification

- [x] 8.1 Fake-claude shim test: all launchers and reset.
  - Evidence: all three passed `--settings`, correct fallback model, `ANTHROPIC_AUTH_TOKEN=<absent>`; reset showed all provider vars absent.
- [x] 8.2 Fresh-shell auth warning check.
  - Evidence: shopapikey, giaoduc, cockpit fresh-shell live runs had `auth_warning=False`.
- [x] 8.3 Cockpit local selector check.
  - Evidence: init model `gpt-5.6-luna[1m]`; profile and shim argv verified.
- [x] 8.4 Cockpit wire model check.
  - Evidence: local capture received bare `gpt-5.6-luna`, effort `max`.
- [x] 8.5 Reset probe.
  - Evidence: all provider variables absent including `CLAUDE_CODE_SUBAGENT_MODEL`.
- [x] 8.6 Security check for shell init files.
  - Evidence: zero literal provider credential matches; profiles 600, helpers 700, `.hermes/.env` 600.
- [x] 8.7 Shopapikey live smoke.
  - Evidence: exit 0, exact `SHOP_AUTH_REPAIR_228`, `is_error=False`, `apiKeySource=apiKeyHelper`, no auth warning.
- [x] 8.8 Giaoduc live smoke.
  - Evidence: exit 0, exact `GIA_AUTH_REPAIR_228`, `is_error=False`, `apiKeySource=apiKeyHelper`, no auth warning.
- [x] 8.9 Cockpit live smoke.
  - Evidence: exit 0, exact `COCKPIT_AUTH_REPAIR_228`, `is_error=False`, `apiKeySource=apiKeyHelper`, no auth warning.
- [x] 8.10 Adapter unit tests.
  - Evidence: `uv run pytest -q` → 55 passed in 0.43s.
- [x] 8.11 Final `zsh -n ~/.zshrc`.
  - Evidence: PASS.

## Phase 9: Documentation and Closure

- [x] 9.1 Update routing skill, provider-profile reference, governance reference, and adapter README.
  - Evidence: stale-reference sweep found and corrected obsolete token-export guidance; archived historical artifacts were not edited.
- [x] 9.2 Update `evidence.md` with all evidence IDs and results.
- [x] 9.3 Run `git diff --check` on the store.
  - Evidence: clean.
- [ ] 9.4 Stage and commit the change directory only.
- [x] 9.5 Run focused and full OpenSpec validation post-implementation.
  - Evidence: focused change valid; full store 362/362 passed.
- [x] 9.6 Reconcile task statuses against evidence.
- [ ] 9.7 Archive the change.

## Open Security Action (outside this change)

- [ ] S.1 Rotate provider credentials that were previously present in plaintext in `~/.zshrc`.
  - The values have been removed from shell configuration, but removal does not revoke them.

## Rollback

- [ ] R.1 Restore `~/.zshrc` from backup (not exercised; backup verified).
- [ ] R.2 Restore `~/.claude/profiles/cockpit.json` from backup (not exercised; backup verified).
- [ ] R.3 Run `zsh -n ~/.zshrc` after rollback (not exercised).
- [ ] R.4 Verify each launcher with `--print` after rollback (not exercised).
