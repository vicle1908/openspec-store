# Evidence: repair-claude-code-provider-auth-and-selector-routing

## Pre-change State (Baseline)

### Runtime

- Claude Code: 2.1.228
- Settings: `model: fable[1m]`, `apiKeyHelper` present, no `ANTHROPIC_AUTH_TOKEN` in JSON env
- Profiles: shopapikey (fable[1m]), giaoduc (Advance[1m]), cockpit (gpt-5.6-luna — BARE, missing [1m])
- All helpers: mode 700, source `~/.hermes/.env`
- `.zshrc` launcher block: contains literal credential exports, `ANTHROPIC_AUTH_TOKEN` exported by all launchers, `claude_reset()` missing `unset CLAUDE_CODE_SUBAGENT_MODEL`

### Auth Warning

Observed in Claude Code 2.1.228 startup banner: `Both ANTHROPIC_AUTH_TOKEN and apiKeyHelper set`

## Evidence Log

### AUTH-228-01: Warning reproduced on 2.1.228
- Gate: Pre-change observation
- Result: PASS
- Evidence: Screenshot and local capture both show the warning

### AUTH-228-02: Profile path reports apiKeyHelper as auth source
- Gate: Post-implementation verification
- Result: PASS
- Evidence: fresh-shell live runs for all three launchers reported `apiKeySource=apiKeyHelper` in Claude init output.

### AUTH-228-03: No ANTHROPIC_AUTH_TOKEN in child environment
- Gate: Post-implementation shim verification
- Result: PASS
- Evidence: all three launchers showed `ANTHROPIC_AUTH_TOKEN=<absent>` in shim output. `claude_reset` also showed `<absent>`. Shims ran via `env -u ANTHROPIC_AUTH_TOKEN zsh -dfc 'source ~/.zshrc; export PATH=/tmp/claude-shim:$PATH; rehash; ...'`.

### AUTH-228-04: No auth warning on fresh shell
- Gate: Post-implementation verification
- Result: PASS
- Evidence: shopapikey, giaoduc, cockpit live runs on Claude Code 2.1.228 each had `auth_warning=False`; stderr contained only the SessionEnd hook cancellation line, not the auth warning. Bare default `env -i` smoke also had `auth_warning=False`.

### MODEL-228-01: Cockpit local selector is gpt-5.6-luna[1m]
- Gate: Post-implementation shim verification
- Result: PASS
- Evidence: Shim output: `ARGS: <--settings> </Users/androidteam/.claude/profiles/cockpit.json> <--model> <gpt-5.6-luna[1m]>`. Profile JSON verified: model, ANTHROPIC_MODEL, ANTHROPIC_CUSTOM_MODEL_OPTION all set to `gpt-5.6-luna[1m]`.

### MODEL-228-02: Cockpit wire model is bare gpt-5.6-luna
- Gate: Post-implementation local capture
- Result: PASS
- Evidence: post-change local capture on 2026-08-12 with the repaired cockpit profile; exit 0, `path=/v1/messages?beta=true`, `model=gpt-5.6-luna`, `output_config.effort=max`, `has_authorization=true`, `has_x_api_key=true`, and zero auth-warning matches. Claude Code strips `[1m]` before transmission.

### RESET-228-01: Reset child has no provider variables
- Gate: Post-implementation shim verification
- Result: PASS
- Evidence: `claude_reset --print RESET_SHIM_TEST` shim output: all provider variables `<absent>` including `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `CLAUDE_CODE_SUBAGENT_MODEL`, `CLAUDE_CODE_EFFORT_LEVEL`.

### SEC-228-01: No literal provider keys in shell init files
- Gate: Post-implementation grep verification
- Result: PASS
- Evidence: `grep -E 'pmv_[A-Za-z0-9_-]+|agt_[A-Za-z0-9_-]{10,}' ~/.zshrc ~/.zshenv ~/.zprofile` → zero matches.

### SEC-228-02: Credential files have correct permissions
- Gate: Post-implementation stat verification
- Result: PASS
- Evidence: `~/.hermes/.env` mode=600, all three profile JSONs mode=600, all three helper scripts mode=700.

### SEC-228-03: Exposed credential warning
- Gate: Security finding
- Result: REQUIRES ACTION
- Evidence: Provider API keys (`HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_GIAODUC_API_KEY`, `HERMES_CUSTOM_COCKPIT_API_KEY`, `HERMES_CUSTOM_LOCALHOST_51006_API_KEY`) were previously present in `~/.zshrc` as plaintext exports (lines 240-243). Removal from `.zshrc` does not revoke them. **Recommendation: rotate all four keys** as a precaution. Rotation is outside this change's scope.

### LIVE-SHOP-01: Shopapikey live smoke
- Gate: Live provider acceptance
- Result: PASS
- Evidence: Claude Code 2.1.228 fresh-shell run; exit 0, `is_error=False`, exact sentinel `SHOP_AUTH_REPAIR_228`, `apiKeySource=apiKeyHelper`, init/model usage `fable-5[1m]`, no auth warning.

### LIVE-GIA-01: Giaoduc live smoke
- Gate: Live provider acceptance
- Result: PASS
- Evidence: Claude Code 2.1.228 fresh-shell run; exit 0, `is_error=False`, exact sentinel `GIA_AUTH_REPAIR_228`, `apiKeySource=apiKeyHelper`, init/model usage `Advance[1m]`, no auth warning.

### LIVE-COCKPIT-01: Cockpit live smoke through adapter
- Gate: Live provider acceptance
- Result: PASS
- Evidence: Claude Code 2.1.228 fresh-shell run; exit 0, `is_error=False`, exact sentinel `COCKPIT_AUTH_REPAIR_228`, `apiKeySource=apiKeyHelper`, init/model usage `gpt-5.6-luna[1m]`, no auth warning.

### ADAPTER-01: Adapter unit tests pass
- Gate: Code verification
- Result: PASS
- Evidence: `cd ~/Developer/claude-code-provider-adapter && uv run pytest -q` → `55 passed in 0.43s`.

### PREFLIGHT-228-01: Missing helper credential fails closed
- Gate: Negative verification
- Result: PASS
- Evidence: `HERMES_HOME=/tmp/empty-hermes _claude_require_helper ... shopapikey` → exit 1, stderr `Error: shopapikey credential unavailable`, stdout empty.

### BARE-228-01: Bare default remains operational
- Gate: Regression verification
- Result: PASS
- Evidence: clean `env -i` Claude 2.1.228 smoke; exit 0, exact sentinel `BARE_DEFAULT_REPAIR_228`, `apiKeySource=apiKeyHelper`, model `fable-5[1m]`, no auth warning.

### STATIC-228-01: Static checks
- Gate: Syntax/structure
- Result: PASS
- Evidence: `zsh -n ~/.zshrc`, `python3 -m json.tool ~/.claude/profiles/cockpit.json`, permissions (profiles 600, helpers 700, `.hermes/.env` 600), and stale live-config grep all passed.

### VALIDATE-228-01: OpenSpec validation
- Gate: Structural validation
- Result: PASS
- Evidence: focused `openspec validate repair-claude-code-provider-auth-and-selector-routing` passed; final full store `openspec validate --all --store openspec-store` → 362 passed, 0 failed.

### DOC-228-01: Documentation reconciliation
- Gate: Stale-reference sweep
- Result: PASS
- Evidence: updated `multi-provider-cli-routing` auth mode wording, provider-profile-resolution launcher/auth guidance, and adapter README. Archived historical artifacts were not edited.

### NOTE: Inherited token from Hermes gateway
- The Hermes gateway process exports `ANTHROPIC_AUTH_TOKEN` (from the gateway's own configuration). This is inherited by terminal sessions launched from within the gateway.
- **This is NOT a defect in this change** — it is a separate concern about the gateway environment.
- Profile-based launchers correctly unset `ANTHROPIC_AUTH_TOKEN` in their subshells, so the warning is suppressed for launcher invocations.
- Bare `claude` invocations from within the gateway environment may still trigger the warning if the gateway is restarted without clearing the inherited token.
- A separate follow-up change may address gateway-level environment cleanup, but that is outside the scope of this three-provider repair.
