# Verification Evidence: `optimize-omp-v18-12-runtime-and-typesafe-judge`

## 1. Baseline Backups, Isolated-Profile Staging (`omp-v18-12-opt`), and Pre-Mutation Smoke Gates

### Task 1.1: Baseline Backups & Legacy Clutter Archival
- Created `/Users/androidteam/.omp/agent/backups-archive/` (`mode 0700`) and `/Users/androidteam/.omp/agent/backups-archive/baseline-20261020/` (`mode 0700`).
- Moved all `16` legacy `.bak*`, `*.pre-*`, and `backups-*` items from `~/.omp/agent/` into `~/.omp/agent/backups-archive/` while preserving active `/Users/androidteam/.omp/agent/config.yml.lock`.
- Captured WAL-checkpointed baseline backups (`mode 0600`):
  - `config.yml`: `mode=0600`, `size=3399`, `md5=c65effbdc9475752b948e22b16ee21de`, `sha256=d887ff4f5de3f588c4bc4bdc94361d4f25bbcaa7eea434d261056e2af6408b7b`
  - `models.yml`: `mode=0600`, `size=8978`, `md5=9122435b92ee4d64ca75fa36f777aea9`, `sha256=2dd10d1fe5bfbdd8f6578cee5133ead526536643179196d69268147ebe86e933`
  - `.env`: `mode=0600` (live pre-change `0644`), `size=672`, `md5=bb8c3841c93a2941747f51260a14935e`, `sha256=03e937de533d9a6dad067a393f058cbdeed54b4b835705843ce16d8ec67908e4`
  - `.zshenv`: `mode=0600`, `size=2975`, `md5=499d850f2b47b149927aa5d733561b9f`, `sha256=1472dbed8a8f18ff436a0573c334adfab8ff834371b307ce9bbe4105cca51dc5`
  - `agent.db` (via `sqlite3 "file:$HOME/.omp/agent/agent.db?mode=ro" ".backup '<dest>'"`): `mode=0600`, `size=6410240`, `md5=d0dcaaaca1b9ef6bd7803a732a85d78d`, `sha256=14393d17e462e6edc8dc37c11e22c94aa66cc9e3731cc1f3a47f03642bb6c661`

### Task 1.2: Staged `.env` and `agent.db` in Isolated Profile `omp-v18-12-opt`
- Seeded `/Users/androidteam/.omp/profiles/omp-v18-12-opt/agent/agent.db` (`mode 0600`) and `models.db` (`mode 0600`) via `sqlite3 ".backup"`.
- Value-blind populated `/Users/androidteam/.omp/profiles/omp-v18-12-opt/agent/.env` (`mode 0600`, `size=567`, `sha256_8=77b89334`) with all 5 active keys (`TYPESAFE_API_KEY` `len=107`, `OMNIROUTE_API_KEY` `len=35`, `HERMES_CUSTOM_COCKPIT_API_KEY` `len=42`, `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` `len=36`, `HERMES_CUSTOM_PHANMEMVIP_API_KEY` `len=36`) and zero retired empty keys.
- Executed `PRAGMA busy_timeout=5000; BEGIN IMMEDIATE;` transaction on staged `agent.db` deleting `openrouter` and `typesafe` rows from `auth_credential_blocks` and `auth_credentials` and inserting `('typesafe', 'api_key', json_object('key', ?, 'source', 'login'), NULL, NULL)`:
  ```text
  $ sqlite3 "file:$HOME/.omp/profiles/omp-v18-12-opt/agent/agent.db?mode=ro" "SELECT provider, credential_type, json_extract(data,'$.source'), length(json_extract(data,'$.key')) FROM auth_credentials WHERE provider IN ('typesafe','openrouter');"
  typesafe|api_key|login|107
  ```

### Task 1.3: Staged `models.yml` and `config.yml` in Isolated Profile `omp-v18-12-opt`
- Staged `/Users/androidteam/.omp/profiles/omp-v18-12-opt/agent/models.yml` (`mode 0600`, `size=7417`, `sha256_8=8f846203`): pruned all 14 `sh/*` entries from `providers.omniroute.models` (leaving 11 active models), removed `omniroute-chat`, set `contextWindow: 128000` on `nx/deepseek-v4.1-flash` and `contextWindow: 200000` on `omniroute-anthropic` (`pm/Claude-*`), and added `reasoning: true`, `thinking` (`efforts: [low, medium, high, xhigh]`, `defaultLevel: high`), `supportsTools: true`, and `imageCountBudget: 20` on all 5 `providers.cockpit.models` entries.
- Staged `/Users/androidteam/.omp/profiles/omp-v18-12-opt/agent/config.yml` (`mode 0600`, `size=3400`, `sha256_8=9294c9df`): added `modelRoles.judge: typesafe/jev-1.14.0`, `retry.fallbackChains.judge: [typesafe/jev-latest, typesafe/jev-preview]`, `retry.fallbackChains['cockpit/*']: [google-antigravity/gemini-4-argon:high, omniroute/gemini-3.8-flash-high, google-antigravity/gemini-3.8-flash:high]`, `retry.fallbackChains['google-antigravity/*']: [omniroute/gemini-3.8-flash-high, google-antigravity/gemini-3.8-flash:high]`, `disabledProviders: [openrouter, lm-studio, llama.cpp, vscode]`, `isolation.backend: apfs`, `externalThinking: false`, `providers.tinyModelDevice: mlx`, `tui.renderMermaid: true`, and removed legacy keys `memories`, `renderMermaid`, `calc`, and `bashInterceptor.redirects`.

### Task 1.4: Isolated-Profile Smoke Gates (`zsh -lic` and `zsh -fc`)
- Verified live `~/.omp/agent/{config.yml,models.yml,.env}` hashes were untouched before smoke execution.
- `omp --profile omp-v18-12-opt models --kind judge --json` in both `zsh -lic` and `env -u TYPESAFE_API_KEY -u OMNIROUTE_API_KEY -u HERMES_CUSTOM_COCKPIT_API_KEY -u HERMES_CUSTOM_SHOPAPIKEY_API_KEY -u HERMES_CUSTOM_PHANMEMVIP_API_KEY zsh -fc` returned `['typesafe/jev-1.14.0', 'typesafe/jev-latest', 'typesafe/jev-preview']` (`exit 0`).
- Uncached `omp --profile omp-v18-12-opt find "workstation toolchain manifest" /Users/androidteam/Developer/platform/openspec-store/config --json -q`:
  - `OMP_JUDGMENT_CACHE_DB=/tmp/omp-judge-lic.db zsh -lic`: `exit 0`, `coverage="complete"`, `stats.requests=4`, `stats.failed=0`, `stats.apiMs=1140.60`.
  - `env -u ... OMP_JUDGMENT_CACHE_DB=/tmp/omp-judge-fc.db zsh -fc`: `exit 0`, `coverage="complete"`, `stats.requests=3`, `stats.failed=0`, `stats.apiMs=792.31`.
- Default chat + post-turn `advisor: cockpit/gpt-6.1-sol:xhigh` smoke probes (`omp --profile omp-v18-12-opt --mode json --no-session -p "reply only: pong"`) in both `zsh -lic` and `zsh -fc`: `exit 0`, `provider=google-antigravity`, `model=gemini-4-argon`, `text='pong'`, `fallbacks=0`.

---

## 2. Atomic Live Rollout (`~/.omp/agent/`, `~/.zshenv`, and `.claude/CLAUDE.md`)

### Task 2.1: Atomic Live Config/Credential Promotion & Staging Cleanup
- Atomically replaced live `~/.omp/agent/.env`, `~/.omp/agent/models.yml`, and `~/.omp/agent/config.yml` (`mode 0600`), preserving `~/.omp/agent/config.yml.lock`.
- Executed the `BEGIN IMMEDIATE` `auth_credential_blocks` and `auth_credentials` transaction on live `~/.omp/agent/agent.db`, commented out `export OPENROUTER_API_KEY=...` on line 26 of `~/.zshenv` (`mode 0600`), and removed `~/.omp/profiles/omp-v18-12-opt` and `/tmp/omp-judge-*`:
  ```text
  $ stat -L -f '%04Lp' ~/.omp/agent/.env ~/.omp/agent/models.yml ~/.omp/agent/config.yml ~/.zshenv
  0600
  0600
  0600
  0600
  $ sqlite3 "file:$HOME/.omp/agent/agent.db?mode=ro" "SELECT provider, credential_type, json_extract(data,'$.source'), length(json_extract(data,'$.key')) FROM auth_credentials WHERE provider IN ('typesafe','openrouter');"
  typesafe|api_key|login|107
  ```

### Task 2.2: `.claude/CLAUDE.md` `@../AGENTS.md` Fix, Duplicate `herdr` Skill Removal & Live Smoke Verification
- Updated `/Users/androidteam/Developer/.claude/CLAUDE.md:L153` from `@AGENTS.md` to `@../AGENTS.md` and unlinked `/Users/androidteam/.omp/agent/skills/herdr`.
- Verified live `omp` from `/Users/androidteam/Developer` in both `zsh -lic` (`stats.requests=4, stats.failed=0, apiMs=1081.08`) and `env -u ... zsh -fc` (`stats.requests=3, stats.failed=0, apiMs=812.31`), plus `omp --mode json --no-session -p "reply only: pong"` (`exit 0`, `0` `@-import: file not found` warnings in `omp.2026-10-20.67286.log` and `omp.2026-10-20.68229.log`).

---

## 3. Declarative Workstation Toolchain Registration & Shadow-Path Hardening for `omp`

### Task 3.1: `workstation-toolchain-manifest.json`, `Brewfile`, and `docs/mac-development-setup.md`
- Registered `"omp"` in `profiles.ai-agents` and `tools.omp` in `/Users/androidteam/Developer/platform/openspec-store/config/workstation-toolchain-manifest.json`, added `tap "can1357/tap"` + `brew "can1357/tap/omp"` to `config/Brewfile`, and added **Oh My Pi (OMP)** to `docs/mac-development-setup.md`.
- Verification (`exit 0`):
  ```text
  $ jq -e '.tools.omp.authoritative_owner == "brew-formula" and .tools.omp.release_channel == "stable" and .tools.omp.dispatch_classification == "none" and (.profiles["ai-agents"] | index("omp") != null)' config/workstation-toolchain-manifest.json
  true
  ```

### Task 3.2: Updater Registry, Inventory, Agent CLI Coverage, Daily Update Mirror Parity & Unit Tests
- Registered `("omp", "brew-formula")` in `scripts/toolchain_updater_registry.py`, updated `scripts/inventory-workstation-toolchain.py` and `scripts/reconcile-agent-cli-coverage.py`, synchronized `AGENT_CLI_KNOWN_UNCOVERED` across `scripts/workstation-daily-update.sh` and `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` (`sha256: 356f131ccd237222fe2c97ae2c42da4c8b861e9289ca0da6679e642b6d48160c`), and added unit tests in `scripts/test-version-authority-governance.py` and `tests/test_portable_workstation_slice_a.py`.
- Verification (`exit 0`):
  - `python3 scripts/test-version-authority-governance.py`: `Ran 35 tests in 6.135s — OK`
  - `python3 -m unittest tests/test_portable_workstation_slice_a.py tests/test_portable_workstation_slice_b.py tests/test_portable_workstation_slice_c.py`: `Ran 70 tests in 7.441s — OK (skipped=2)`
  - `python3 scripts/inventory-workstation-toolchain.py --json | jq -e '(.manifest_reconciliation.items.aligned | any(.name == "omp" and .state == "aligned")) and (.authority_reconciliation.items | any(.name == "omp" and .authority == "brew-formula" and .drift_status == "clean"))'` $\to$ `true`
  - `python3 scripts/reconcile-agent-cli-coverage.py --json | jq -e '.undeclared_count == 0'` $\to$ `true`
