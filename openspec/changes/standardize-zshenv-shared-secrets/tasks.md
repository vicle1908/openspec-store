# Tasks: standardize-zshenv-shared-secrets

## Phase 1: Baseline & safety

- [x] 1.1 Backup all affected files to `~/.config/agent-llm/backups/20260827-zshenv-shared-secrets/` (zshenv, zshrc, hermes .env, tdt .env, adapter .env, zshenv.secrets, both Claude helpers, pi models.json, opencode.json + auth.json, 4 plists, loader script).
- [x] 1.2 Record canonical pre-migration hashes for all 17 shared-tier keys (source file + sha256[:12] + length) in EVIDENCE_MANIFEST.md.

## Phase 2: .zshenv becomes source of truth

- [x] 2.1 `chmod 600 ~/.zshenv` (verify BEFORE writing values).
- [x] 2.2 Write BEGIN/END shared-agent-secrets block with all 17 keys; drift keys use newer-wins values (EXA/BRAVE/TAVILY ← hermes.env; OMNIROUTE ← zshenv.secrets).
- [x] 2.3 Remove loader source line from `.zshenv`; add deprecation header to `~/.config/agent-llm/load-hermes-custom-credentials.zsh` pointing at `.zshenv`.
- [x] 2.4 Verify: `zsh -n ~/.zshenv`; all 17 keys present in `zsh -c`, `zsh -ic`, `zsh -lc`, `zsh -ilc` (presence + length); hash equality vs Phase 1 record; startup timing.

## Phase 3: Consumer rewiring

- [x] 3.1 Rewrite `~/.claude/helpers/shopapikey-key.sh` + `cockpit-key.sh`: env-first, restricted single-key parse fallback, no `set -a`. Verify each prints exactly 1 line.
- [x] 3.2 Fix `~/.pi/agent/models.json` cockpit `apiKey` (URL → `${HERMES_CUSTOM_COCKPIT_API_KEY}` env template, verified through Pi resolver).
- [x] 3.3 OpenCode: migrate shopapikey + cockpit from auth.json literals to `{env:...}` in opencode.json; verify provider resolution.
- [x] 3.4 `.zshrc`: remove zshenv.secrets source block (lines 54–64) + stale cline_* launchers; `zsh -n` clean; launchers still defined.
- [x] 3.5 Delete `~/.zshenv.secrets` (after hash-verified migration of its 7 keys).

## Phase 4: launchd bridge

- [x] 4.1 Edit `com.tdt.ai-review.plist` + `com.tdt.webhook-receiver.plist`: zsh wrapper ProgramArguments; plist parse validation; reload; health-check both services.
- [x] 4.2 Edit `com.workspace.claude-code-provider-adapter.plist`: zsh wrapper; update docker-compose to environment passthrough; drain + delete adapter `.env`; restart adapter.
- [x] 4.3 Edit `ai.hermes.gateway.plist`: zsh wrapper; plist parse validation; DO NOT restart (user-deferred).

## Phase 5: Drain duplicates

- [x] 5.1 Remove shared-tier keys present in `~/.hermes/.env` (keep service-private tier intact). Verify no shared-tier names remain; `MCPR_TOKEN` remains private.
- [x] 5.2 Remove `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` + drifted tool keys from `~/.tdt/.env`. Verify service config keys untouched.
- [x] 5.3 Verify TDT services still healthy (they now inherit shared tier via zsh wrapper).

## Phase 6: Final verification & evidence

- [x] 6.1 Full sweep: 4 zsh modes × 17 keys; hash equality; no shared-tier names in service .env; helper single-line output; plists parse-clean; .zshrc/.zshenv syntax clean.
- [x] 6.2 Write EVIDENCE_MANIFEST.md with all gate results.
- [ ] 6.3 Commit store change.
- [ ] 6.4 User action (documented, not agent-executed): restart Hermes gateway to activate plist wrapper; run one live sentinel per provider.
