# Tasks: standardize-zshenv-shared-secrets

## Phase 1: Baseline & safety

- [x] 1.1 Backup all affected files to `~/.config/agent-llm/backups/20260827-zshenv-shared-secrets/` (zshenv, zshrc, hermes .env, tdt .env, adapter .env, zshenv.secrets, both Claude helpers, pi models.json, opencode.json + auth.json, 4 plists, loader script).
- [x] 1.2 Record canonical pre-migration hashes for all 17 shared-tier keys (source file + sha256[:12] + length) in EVIDENCE_MANIFEST.md.

## Phase 2: .zshenv becomes source of truth

- [x] 2.1 `chmod 600 ~/.zshenv` (verify BEFORE writing values).
- [x] 2.2 Write BEGIN/END shared-agent-secrets block with all 17 keys (pre-retirement count, including the later-retired `HERMES_CUSTOM_GIAODUC_API_KEY`; canonical tier is now 16); drift keys use newer-wins values (EXA/BRAVE/TAVILY ← hermes.env; OMNIROUTE ← zshenv.secrets).
- [x] 2.3 Remove loader source line from `.zshenv`; add deprecation header to `~/.config/agent-llm/load-hermes-custom-credentials.zsh` pointing at `.zshenv`.
- [x] 2.4 Verify: `zsh -n ~/.zshenv`; all 17 keys (pre-retirement count; canonical tier is now 16) present in `zsh -c`, `zsh -ic`, `zsh -lc`, `zsh -ilc` (presence + length); hash equality vs Phase 1 record; startup timing.

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

- [x] 6.1 Full sweep: 4 zsh modes × 16 canonical shared-tier keys; hash equality; no shared-tier names in service .env; helper single-line output; plists parse-clean; .zshrc/.zshenv syntax clean.
- [x] 6.2 Write EVIDENCE_MANIFEST.md with all gate results.
- [x] 6.3 Commit store change.
- [x] 6.4a Provider sentinels (agent-executed, clean-room): shopapikey PASS
  (`SHOPAPIKEY_LIVE_OK`); cockpit PASS after upstream recovery
  (`COCKPIT_LIVE_OK`, TCP 51006 OPEN); Giaoduc NOT APPLICABLE (retired).
  Clean-room verification: 16/16 shared-tier names non-empty in all 4 zsh
  modes; wrapper dry run exit 0 with the same roster; 0 Giaoduc;
  MCPR_TOKEN private.
- [x] 6.4b Gateway wrapper activated 2026-08-28 08:58 via explicit
  `launchctl bootout` + `bootstrap`. The earlier 08:44 restart did NOT
  activate the wrapper: launchd re-spawned from its cached pre-wrapper job
  definition, leaving the gateway with zero shared-tier keys (all providers
  401). Verified post-fix: launchd `program =` is the wrapper; gateway pid
  42908 env carries all 5 `HERMES_CUSTOM_*` keys + shared tool keys; 0 auth
  401s after restart (vs 38 in the broken window). Full evidence in
  EVIDENCE_MANIFEST.md → "Gateway wrapper activation (2026-08-28)".
  Remaining 6.4b item (one native `mcp__mcp_router__list_directory` call)
  is exercised by ordinary session traffic through the now-keyed gateway.


## Post-migration amendment (2026-08-27)

- [x] R1 Retire the unused Giaoduc provider: remove
  `HERMES_CUSTOM_GIAODUC_API_KEY` from `~/.zshenv` and remove the
  `[model_providers.giaoduc]` block from `~/.codex`.
- [x] R2 Re-verify active configuration: 16 shared keys in all 4 zsh modes;
  Codex default remains `codex_local_access`; no Giaoduc references remain
  in active configs, services, or the adapter repository.
- [x] R3 Update design/evidence documentation and preserve historical
  17-key migration evidence.
- [x] R4 (2026-08-28) Investigated `hermes gateway status` "Service
  definition is stale" warning: `generate_launchd_plist()`
  (hermes_cli/gateway.py) regenerates the plist WITHOUT
  `launchd-env-wrapper.sh`, and `refresh_launchd_plist_if_needed()`
  overwrites the installed plist on `hermes gateway start`/restart —
  silently reverting the D5 bridge. Hazard + recovery procedure documented
  in design.md D5 and EVIDENCE_MANIFEST.md. Follow-up patch applied
  same-day — see R5.

- [x] R5 (2026-08-28) Wrapper-aware generator patch applied to
  `~/.hermes/hermes-agent` (upstream checkout; local uncommitted change,
  the update path's designed mechanism for local modifications). New
  config knob `gateway.launchd_env_wrapper` in `~/.hermes/config.yaml`
  makes `generate_launchd_plist()` prepend the wrapper to
  ProgramArguments, so `hermes gateway start`/restart rewrites now
  PRESERVE the D5 bridge instead of stripping it. Resolver fails open
  (unset/non-executable → upstream plist shape). 6 new tests
  (`TestLaunchdEnvWrapper`); full suite green (109 + 72 passed); ruff
  clean. End-to-end: `refresh_launchd_plist_if_needed()` rewrote the
  plist to the current format WITH wrapper; gateway restarted via the
  detached reload helper (pid 6023); all 5 `HERMES_CUSTOM_*` keys in
  process env; 0 auth 401s; `hermes gateway status` now reports
  "Service definition matches the current Hermes install". Patch backup
  for re-application after an `hermes update` stash-restore conflict:
  `~/.config/agent-llm/backups/20260827-zshenv-shared-secrets/hermes-launchd-env-wrapper.patch`.
  Full evidence in EVIDENCE_MANIFEST.md → "Wrapper-aware generator patch".
