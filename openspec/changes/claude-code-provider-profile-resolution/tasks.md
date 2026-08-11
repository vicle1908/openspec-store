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
  - Evidence: `system_model: Advance[1m]`, `modelUsage: ['Advance[1m]']`, exit 0, response `GIAODUC_PROFILE_LIVE`.

## Phase 3: Documentation (complete)

- [x] 3.1 Write `proposal.md` with Why, What Changes, Architecture, Security.
- [x] 3.2 Write `design.md` with problem, solution architecture, profile format, wiring, security, rollback.
- [x] 3.3 Write `specs/claude-code-provider-profile-resolution/spec.md` with requirements and scenarios.
- [x] 3.4 Write `tasks.md` with completed checkboxes and evidence.
- [x] 3.5 Write `evidence.md` with structured verification results.
- [x] 3.6 Validate this change: `openspec validate claude-code-provider-profile-resolution --store openspec-store`.
- [x] 3.7 Run `git diff --check`.

## Phase 4: Commit

- [ ] 4.1 Stage only the new change files.
- [ ] 4.2 Commit with scoped message.
- [ ] 4.3 Archive after all gates green (deferred — this change documents a fix, not a new feature).
