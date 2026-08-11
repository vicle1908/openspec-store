# Tasks: claude-code-provider-profile-resolution

## Phase 0: Diagnosis (complete)

- [x] 0.1 Diagnose why `~/.zshrc` launcher subshells were not setting the model correctly in new shells.
  - Evidence: `~/.claude/settings.json` had `"model": "Advance[1m]"` hardcoded globally, overriding all launcher env vars and CLI flags.
- [x] 0.2 Verify launcher env vars were not reaching Claude Code's resolution pipeline.
  - Evidence: fake-claude probe confirmed subshell env vars (ANTHROPIC_MODEL, ANTHROPIC_BASE_URL, etc.) were `<unset>` — the old `_claude_model_default` helper only passed `--model` via CLI flag, never exported the required env vars.

## Phase 1: Fix (complete)

- [x] 1.1 Remove global `"model"` override from `~/.claude/settings.json`.
  - Evidence: `json.load(open(settings.json))` shows `model` key absent; backup at `~/.claude/settings.json.pre-provider-profiles-20260811`.
- [x] 1.2 Create `~/.claude/profiles/` directory.
  - Evidence: `ls ~/.claude/profiles/` shows three files.
- [x] 1.3 Create `~/.claude/profiles/shopapikey.json` with model, base URL, aliases, effort, capabilities.
  - Evidence: JSON valid, `model=fable[1m]`, `ANTHROPIC_BASE_URL=https://api.phanmemvip.shop`, no auth tokens, `chmod 600`.
- [x] 1.4 Create `~/.claude/profiles/giaoduc.json` with model, base URL, aliases, effort, capabilities.
  - Evidence: JSON valid, `model=Advance[1m]`, `ANTHROPIC_BASE_URL=https://api.giaoduc.online`, no auth tokens, `chmod 600`.
- [x] 1.5 Create `~/.claude/profiles/cockpit.json` with model, base URL, aliases, effort, capabilities.
  - Evidence: JSON valid, `model=gpt-5.6-luna[1m]`, `ANTHROPIC_BASE_URL=http://localhost:8787`, no auth tokens, `chmod 600`.
- [x] 1.6 Replace `_claude_model_default` helper with `_claude_with_profile` in `~/.zshrc`.
  - Evidence: `grep _claude_with_profile ~/.zshrc` shows helper definition and three call sites; `grep _claude_model_default ~/.zshrc` returns 0 matches.
- [x] 1.7 Update `shopapikey()` launcher to use `_claude_with_profile` with `--settings` flag.
  - Evidence: `grep --settings.*shopapikey ~/.zshrc` shows correct profile path.
- [x] 1.8 Update `giaoduc()` launcher to use `_claude_with_profile` with `--settings` flag.
  - Evidence: `grep --settings.*giaoduc ~/.zshrc` shows correct profile path.
- [x] 1.9 Update `cockpit()` launcher to use `_claude_with_profile` with `--settings` flag.
  - Evidence: `grep --settings.*cockpit ~/.zshrc` shows correct profile path.
- [x] 1.10 Add `_claude_require_token` guard helper.
  - Evidence: function defined, checks `${(P)token_var}` and exits with clear error if unset.
- [x] 1.11 Add `_claude_require_token` guard call to `shopapikey()`.
  - Evidence: `grep _claude_require_token.*SHOPAPIKEY ~/.zshrc` shows guard present.
- [x] 1.12 Add `_claude_require_token` guard call to `giaoduc()`.
  - Evidence: `grep _claude_require_token.*GIAODUC ~/.zshrc` shows guard present.
- [x] 1.13 Add `_claude_require_token` guard call to `cockpit()`.
  - Evidence: `grep _claude_require_token.*COCKPIT ~/.zshrc` shows guard present.

## Phase 2: Verification (complete)

- [x] 2.1 Run `zsh -n ~/.zshrc` to verify syntax.
  - Evidence: exit 0, no errors.
- [x] 2.2 Verify `~/.claude/settings.json` has no global model or base URL.
  - Evidence: `python3 -c "..."` confirmed `model` key absent, `ANTHROPIC_BASE_URL` absent from env.
- [x] 2.3 Verify all three profiles are valid JSON, credential-free, `chmod 600`.
  - Evidence: `python3 -c "..."` confirmed all three pass assertions.
- [x] 2.4 Verify OpenSpec store full validation passes.
  - Evidence: `openspec validate --all --store openspec-store` → 358 passed, 0 failed.
- [x] 2.5 Run local capture test for giaoduc profile.
  - Evidence: captured `model: Advance`, `output_config.effort=xhigh`, auth present, response `GIAODUC_E2E_OK`.
- [x] 2.6 Run local capture test for shopapikey profile.
  - Evidence: captured `model: fable-5`, `output_config.effort=xhigh`, auth present, response `SHOP_E2E_PROFILE`.
- [x] 2.7 Run local capture test for cockpit profile.
  - Evidence: captured `model: gpt-5.6-luna`, `output_config.effort=max`, auth present, response `COCKPIT_E2E_PROFILE`.
- [x] 2.8 Run real `giaoduc --print` through actual launcher function.
  - Evidence: `system_model: Advance[1m]`, `modelUsage: ['Advance[1m]']`, exit 0, exact sentinel `GIAODUC_FRESH_GREEN`.

## Phase 3: Documentation (complete)

- [x] 3.1 Write `proposal.md` with Why, What Changes, Architecture, Security.
- [x] 3.2 Write `design.md` with problem, solution architecture, profile format, wiring, security, rollback.
- [x] 3.3 Write `specs/claude-code-provider-profile-resolution/spec.md` with requirements and scenarios.
- [x] 3.4 Write `tasks.md` with completed checkboxes and evidence.
- [x] 3.5 Write `evidence.md` with structured verification results.
- [x] 3.6 Validate this change: `openspec validate claude-code-provider-profile-resolution --store openspec-store`.
- [x] 3.7 Run `git diff --check`.

## Phase 4: Auth (complete)

- [x] 4.1 Create provider-specific helper scripts under `~/.claude/helpers/`.
  - Evidence: `ls ~/.claude/helpers/` shows `shopapikey-key.sh`, `giaoduc-key.sh`, `cockpit-key.sh`. Each reads `$HERMES_CUSTOM_*_API_KEY` via `set -eu` + named-variable validation. `chmod 700` on all three.
- [x] 4.2 Add `apiKeyHelper` to `~/.claude/settings.json`.
  - Evidence: `d.get('apiKeyHelper')` returns `/Users/androidteam/.claude/helpers/shopapikey-key.sh`.
- [x] 4.3 Add `apiKeyHelper` to all three provider profiles.
  - Evidence: `grep apiKeyHelper ~/.claude/profiles/*.json` shows each profile points to its provider-specific helper.
- [x] 4.4 Run isolated apiKeyHelper capture test.
  - Evidence: `env -i` capture server test proved `apiKeyHelper` supplies auth to Claude: wire model=fable-5, effort=xhigh, authorization present, exact sentinel `HELPER_AUTH_OK`.
- [x] 4.5 Run bare Claude smoke (no launcher, no `--settings`).
  - Evidence: `claude --print --output-format json` used global settings.json defaults: `system_model: fable-5[1m]`, `modelUsage: ['fable-5[1m]']`, exact sentinel `BARE_CLAUDE_WORKS`, exit 0.
- [x] 4.6 Verify profile-over-global precedence.
  - Evidence: Giaoduc profile (port 19999) overrode shopapikey defaults (port 19998). Captured on 19998: 0, captured on 19999: 2, wire model=Advance, effort=xhigh.
- [x] 4.7 Verify no literal credentials in any JSON file.
  - Evidence: regex scan for `sk-`, `pmv_t`, `Bearer ` in `settings.json` and all profile JSONs returned zero matches.

## Phase 5: Documentation (complete)

- [x] 5.1 Write `proposal.md` with Why, What Changes, Architecture, Auth Architecture, Security.
- [x] 5.2 Write `design.md` with problem, solution, profile format, launcher wiring, `apiKeyHelper` authentication, `[1m]` contract, security, rollback.
- [x] 5.3 Write `specs/.../spec.md` with requirements and scenarios including `apiKeyHelper`.
- [x] 5.4 Write `tasks.md` with completed checkboxes and evidence.
- [x] 5.5 Write `evidence.md` with structured verification results.
- [x] 5.6 Validate this change: `openspec validate claude-code-provider-profile-resolution --store openspec-store`.
- [x] 5.7 Run `git diff --check`.

## Phase 6: Archive (complete)

- [x] 6.1 Mark `2.8` complete with giaoduc fresh green evidence.
  - Evidence: `system_model: Advance[1m]`, `modelUsage: ['Advance[1m]']`, exit 0, exact sentinel `GIAODUC_FRESH_GREEN`.
- [x] 6.2 Run `openspec archive` and fix stale checkboxes.
  - Evidence: change archived as `2026-08-11-claude-code-provider-profile-resolution`; spec created under `openspec/specs/claude-code-provider-profile-resolution/`.
- [x] 6.3 Stage archive transition files only.
  - Evidence: staged `openspec/changes/claude-code-provider-profile-resolution/`, `openspec/changes/archive/2026-08-11-claude-code-provider-profile-resolution/`, `openspec/specs/claude-code-provider-profile-resolution/`. Unrelated `CLAUDE.md` and `.claude/scripts/` NOT staged.
- [x] 6.4 Validate: `git diff --cached --check` and `openspec validate --all`.
  - Evidence: `git diff --cached --check` clean; `openspec validate --all` 360/360 passed.
- [x] 6.5 Commit archive transition with scoped message.
  - Evidence: commit exists.
- [ ] R.1 Restore the prior launcher function block from the pre-change backup or remove only the new variables.
- [ ] R.2 Revert the adapter effort mapping while retaining the healthy containerization change.
- [ ] R.3 Verify `claude_reset()` returns to a provider-neutral environment.
