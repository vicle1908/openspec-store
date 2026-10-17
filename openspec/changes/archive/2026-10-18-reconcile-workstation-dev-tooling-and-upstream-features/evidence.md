# Verification Evidence: `reconcile-workstation-dev-tooling-and-upstream-features`

Date: `2026-10-18`
Store: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)

---

## 1. Phase 1 — Central OpenSpec Store Manifests, Reporters, Tests & Runbook (`1.1`–`1.5`)

### Task 1.1 & Task 1.5: `config/Brewfile` Full Homebrew Parity Verification
- Added `tap "anomalyco/tap"`, `brew "anomalyco/tap/opencode"`, `brew "block-goose-cli"`, `brew "googleworkspace-cli"`, `brew "newman"`, `brew "ollama"`, `brew "qwen-code"`, `brew "ruff"`, `cask "copilot-cli"`, `cask "droid"`, `cask "grok-build"`, and `cask "muse-code"`.
- Command:
  ```bash
  HOMEBREW_NO_AUTO_UPDATE=1 brew bundle check --file /Users/androidteam/Developer/platform/openspec-store/config/Brewfile --no-upgrade --verbose
  ```
- Result: Exit code `0` (`The Brewfile's dependencies are satisfied.`).

### Task 1.2 & 1.3: Manifests, Registry, Reporters & Unit Tests
- Validated JSON manifests (`config/workstation-toolchain-manifest.json`, `config/npm-global-tools.json`, `config/uv-tools.json`) via `python3 -m json.tool` (exit code `0`).
- Ran version-authority governance tests:
  ```bash
  python3 /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py
  ```
  Result: `Ran 26 tests in 1.533s ... OK` (exit code `0`).
- Ran portable workstation slice tests:
  ```bash
  pytest /Users/androidteam/Developer/platform/openspec-store/tests/test_portable_workstation_slice_*.py
  ```
  Result: `68 passed, 2 skipped in 5.12s` (exit code `0`).
- Ran `inventory-workstation-toolchain.py --json` & `reconcile-agent-cli-coverage.py --json`:
  - `prefix_reconciliation.status`: `"reconciled"`
  - `manifest_reconciliation`: `status: "aligned"`, `declared_tools_count: 35`, `aligned_count: 33`, `drift_count: 0`, `duplicate_count: 0`, `missing_count: 2` (optional uninstalled `rustup`/`cargo`)
  - `reconcile-agent-cli-coverage.py`: `total_installed: 19`, `undeclared_count: 0`, `lacking_update_path: []`

### Task 1.4: Script Provenance & Documentation Parity
- Mirrored `workstation-daily-update.sh`, `docker-service.sh`, `omniroute-watchdog.sh`, and `knowledge-refresh/refresh-knowledge-indexes.sh` to `/Users/androidteam/Developer/platform/openspec-store/scripts/`.
- Verified SHA-256 byte-identity across all 8 rows of `config/script-provenance-manifest.tsv`:
  - `workstation-daily-update.sh`: `c81e9de74d46aa553248c19e8b1d566960b20154e2c00076965130e86d0e19b0` (`match=True`)
  - `workspace-worktree-scan.sh`: `4402ea55ffd0` (`match=True`)
  - `refresh-knowledge-indexes.sh`: `3b72bda695f1731bb5aae232622dcf6a02cbdaf1e5ffc09a112e27d38cd3d7c7` (`match=True`)
  - `knowledge-status.sh`: `2f3cadceaf44` (`match=True`)
  - `sync-notion-knowledge.sh`: `22d72bc17a7a` (`match=True`)
  - `install-hooks.sh`: `1df79eb5e385` (`match=True`)
  - `install-launchagent.sh`: `1644e68b4bd0` (`match=True`)
  - `omniroute-watchdog.sh`: `7b5c8eba74795bef4ad34431f58c7cd409f02be0b795ca8720ca18469882788e` (`match=True`)

---

## 2. Phase 2 — DBOS Daily Maintenance & Snapshot Store Reclamation (`2.1`–`2.3`)

### Task 2.1: `shb/shb-schedule` Workflow & Unit Tests
- Updated `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`STANDARD_PATH`, `GOVERNED_NPM_AGENTS`, `STATIC_AGENT_COMMANDS` with `"codex": ["codex", "update"]`, `"opencode": ["opencode", "upgrade"]`, `"auggie": ["auggie", "update", "--skip-confirmation"]`, `"ntn": ["ntn", "update"]`, and `step_integrity_and_store_validation()` executing `measure-snapshot-growth.py`, `inventory-workstation-toolchain.py --json`, and `reconcile-agent-cli-coverage.py --json`) and `tests/test_workstation_update_workflow.py`.
- Command:
  ```bash
  uv run --directory /Users/androidteam/Developer/shb/shb-schedule pytest tests/test_workstation_update_workflow.py
  ```
- Result: `20 passed in 20.92s` (exit code `0`); full suite `100 passed` (exit code `0`).

### Task 2.2 & Task 2.3: `~/.agentmemory/snapshots` Non-Destructive Repack & Connectivity-Only Check
- **Pre-Repack (`measure-snapshot-growth.py`)**:
  `Status: EXCEEDED (Ceiling: 1G, Total: 11.65 GiB) | Split: Loose=11.63 GiB (1776 objects) vs Packed=17.41 MiB (1227 objects in 1 pack) | History: 1001 commits`
- **Repack & Integrity Verification**:
  - `git -C /Users/androidteam/.agentmemory/snapshots fsck --no-dangling` → exit `0`
  - `git -C /Users/androidteam/.agentmemory/snapshots -c pack.windowMemory=1g -c pack.threads=2 repack -a -d --window=10 --depth=10` → exit `0`
  - `git -C /Users/androidteam/.agentmemory/snapshots prune-packed` → exit `0`
  - `git -C /Users/androidteam/.agentmemory/snapshots fsck --connectivity-only` → exit `0` (`<1s`)
  - `git -C /Users/androidteam/.agentmemory/snapshots rev-parse HEAD` → `f6dec569f03f18f4c22bbd2da7ea847fc5b6f8cd` (exit `0`)
- **Post-Repack (`measure-snapshot-growth.py`)**:
  `Status: WITHIN_BOUNDS (Ceiling: 1G, Total: 125.48 MiB) | Split: Loose=56.82 MiB (21 objects) vs Packed=68.66 MiB (3006 objects in 1 pack) | History: 1009 commits | Routine Integrity Check: git -C ~/.agentmemory/snapshots fsck --connectivity-only` (~11.57 GiB reclaimed).

---

## 3. Phase 3 — Package Ownership Consolidation, CLI Upgrades & Shell/LaunchAgent Hygiene (`3.1`–`3.5`)

### Task 3.1: Relink & Upgrades
- `goose`: Unlinked regular file backed up (`goose.unlinked.bak`) and relinked via `brew unlink block-goose-cli && brew link --overwrite block-goose-cli` → `lrwxr-xr-x /opt/homebrew/bin/goose -> ../Cellar/block-goose-cli/1.55.0/bin/goose` (`1.55.0`, exit `0`).
- `copilot`: `HOMEBREW_NO_AUTO_UPDATE=1 brew upgrade --cask copilot-cli` → `/opt/homebrew/bin/copilot --version` = `GitHub Copilot CLI 1.0.98.` (exit `0`).
- `droid`: `HOMEBREW_NO_AUTO_UPDATE=1 brew upgrade --cask droid` → `/opt/homebrew/bin/droid --version` = `0.244.0` (exit `0`).
- `ntn`: Updated via official installer → `/Users/androidteam/.local/bin/ntn --version` = `ntn 0.23.20` (exit `0`).

### Task 3.2: Duplicate Cleanup & Single-Owner Resolution
- Removed shadowed npm global `@openai/codex` and `opencode-ai`, Homebrew `openspec` (`1.14.2`), duplicate `gitnexus` (`home-toolchain` & `~/.local/lib`), duplicate `newman` (`npm --prefix ~/.local/share/home-toolchain prune --omit=peer`), and backed up/unlinked `~/go/bin/buf` (`29bf4d67109f...`) and `~/.bun/bin/bun` (`28c7dd0a0691...`).
- Verified single-owner resolution and `inventory-workstation-toolchain.py --json` (`status: "aligned"`, `drift_count: 0`, `duplicate_count: 0`):
  - `which -a codex` → `/opt/homebrew/bin/codex` (`0.163.0`)
  - `which -a opencode` → `/opt/homebrew/bin/opencode` (`1.19.3`)
  - `which -a openspec` → `/Users/androidteam/.npm-global/bin/openspec` (`1.14.3`)
  - `which -a bun` → `/opt/homebrew/bin/bun` (`1.4.3`)
  - `which -a buf` → `/opt/homebrew/bin/buf` (`1.74.0`)
  - `which -a gitnexus` → `/Users/androidteam/.npm-global/bin/gitnexus` (`1.6.12`)
  - `which -a newman` → `/opt/homebrew/bin/newman` (`6.2.3`)

### Task 3.3 & Task 3.5: Shell Startup Normalization & Inherited OrbStack Stripping (Value-Blind)
- Backups stored in `/Users/androidteam/.config/agent-llm/backups-20261017/` (mode `0600`):
  - `~/.zshenv`: initial `c22d4efca930...` → Task 3.3 `7c809343d6b5...` → Task 3.5 `7748a6daa72523201c8feffb2bccf9f00d2f7a005196ef280417f041a73d2100` (`0600`)
  - `~/.zprofile`: initial `ecda8d5aee7c...` → Task 3.3 `4d6ecc594a2b...` (`0644`)
  - `~/.zshrc`: initial `1c77171e0d52...` → Task 3.3 `d0227bf4ae14...` → Task 3.5 `1a24d77e466242370ffa021644476b0ea591ba0825b2f7a9af7bd2133a47dc47` (`0600`)
- Verified `zsh -ilc 'which -a codex opencode openspec psql'` resolves `/opt/homebrew/bin/codex`, `/opt/homebrew/bin/opencode`, `/Users/androidteam/.npm-global/bin/openspec`, and `/opt/homebrew/opt/libpq/bin/psql`.
- Verified `PATH="$HOME/.orbstack/bin:$PATH" zsh -ic 'print -l $path' | grep -c orbstack` outputs `0`.
- Verified `zsh -ic 'echo READY' </dev/null` outputs `READY` without iTerm2 OSC 1337 escape prefixes.

### Task 3.4: LaunchAgent Fleet Remediation
- Relocated `ai.hermes.gateway.plist.bak-pre-refresh-20260828-093206` to `/Users/androidteam/.config/agent-llm/backups-20261017/`.
- Fixed `~/Omniroute/scripts/check-upstream.sh:29-30` (`awk '/^Digest:/ && !found {print $2; found=1}' || true`) and `com.omniroute.update-check.plist` (`HOME` + `/opt/homebrew/bin`); kickstarted and verified exit code `0`.
- Updated `com.victory1908.hermes-webui.plist` (`~/Developer/platform/hermes-webui`) and `Antigravity Tools.plist` (`.../MacOS/antigravity-tools`), reloaded both, and re-enabled `com.developer.workstation-daily-update`.

---

## 4. Phase 4 — Coding Agent Configs, Mode `0600` Hardening & OmniRoute Gate 4b (`4.1`–`4.6`)

### Task 4.1 & Task 4.6: Named Mode-Tightening Approvals, Symlink-Following `stat -L` & Byte-Identity Verification
- Operator-approved `0644` $\rightarrow$ `0600` mode tightening applied with `stat -L -f '%04Lp %N'` (`0600`) and pre/post SHA-256 byte-identity verified:
  - `~/.copilot/mcp-config.json`: `71d6b9ccac1b1444f28b3f47d05fcc6f5fb96916a72a497043cc10491985609a` (`0600`)
  - `~/.gemini/config/mcp_config.json`: `c393fd67558ffd0d26bc852db9482e341dc4f56e8eb202e84b85f9bf988d5e06` (`0600`)
  - `~/.gemini/antigravity/mcp_config.json` (`stat -L` resolved target): `c393fd67558ffd0d26bc852db9482e341dc4f56e8eb202e84b85f9bf988d5e06` (`0600`)
  - `~/.kimi/mcp.json`: `c8d5d9d4c63a3eaa43ba8ceb714ebef29fb440dbc1ec4470ec2298169d2fe8e5` (`0600`)
  - `~/.config/goose/custom_providers/custom_omniroute.json.bak-20261015120603`: `badc0e92556f1e7194ea2d202e6fb2f0f131962800f5df13ae1086ceaac1b219` (`0600`)
  - `~/.config/goose/custom_providers/custom_phanmemvip.json.bak-pre-claude-fable.20260825T221454`: `dc2d1566130a12ab1406ee0ba5541bb8feaaaafe222ab5d296c0d9f0f05690e6` (`0600`)
  - `~/.config/goose/custom_providers/custom_shopapikey.json.bak-pre-claude-fable.20260825T221454`: `e6ecb0897582b779e0d3f537f90a760c8cdfc5a9622aced40f01a0719bb05393` (`0600`)

### Tasks 4.2, 4.3, 4.4: Applied Agent Configuration Surface Register (Value-Blind)

| Target File | Mode | Pre-Apply SHA-256 | Post-Apply SHA-256 | Verification |
| :--- | :---: | :--- | :--- | :--- |
| `~/.qwen/settings.json` | `0600` | `cdf3a332eb0efa8fee9b66938119d99fd032b36e6f4bf119b30bb28a23ed9bd1` | `80a0fe5615635dba60dd87a9193664cb1de42c9eedee6951957a2a599036e54d` | `json.loads` valid; `qwen --version` = `0.25.2` |
| `~/.kimi-code/config.toml` | `0600` | `e95b7941d4b95d5f7c5357e70f7ac98e38970de036a29f85bd0df8cd4dc847fe` | `6fd780c38a3475bad65839c2c8920d5922222b852a6ea08916f1c6f424d90261` | `tomllib.loads` valid (`sh/gpt-5.6-sol`) |
| `~/.kimi/config.toml` | `0600` | `a60a307cff6b2499c34529b69d9c896f84a116b97599e45f4b2e6338fe43ae78` | `c1194a6f0b584f8ba8a37b83991928eb8032b8d4b86bbd68d254ad043dffd482` | `tomllib.loads` valid (`dlg/*` retired) |
| `~/.grok/config.toml` | `0600` | `45cdba83a1c8dee67621005eb8f8a456c7a9abfa9aacaa071248ee93be22cfea` | `408052c84e950d60704688612e76d6c85d7f96dc9678aebba48541939b05800f` | `tomllib.loads` valid (`sh/gpt-5.6-sol`) |
| `~/.pi/agent/models.json` | `0600` | `23b23c03a294df586cc1e8f3f851f70453a39e60a1b4905621491cbffd698bb6` | `f7104795640b2c3f9e3f4a40ef0ddb05dee1f1798546e833a31c24db9c940594` | `json.loads` valid (`ollamacloud/*` removed) |
| `~/.pi/agent/settings.json` | `0600` | `e7b565d6c9d05df6b88ad1c4bac29ef038b29760b5f17a382d4f42fc9a2bf1b7` | `3f72d47355c6beae8a4ded3d73368de0e5b57e8a8e0d898f448ca81ce1019b1e` | `json.loads` valid |
| `~/.config/opencode/opencode.json` | `0600` | `46ee2b99182d82c4146d77848f9f95278641404b4662da440982b546a2e95f85` | `4afed5c937ceaa0b44bed10770a0357f5df8c9e1bb0efa1e0c61f0d0913ed0c1` | `json.loads` valid (duplicate `mcp.agentmemory` removed) |
| `~/.hermes/config.yaml` | `0600` | `952aea5c7391b96a8888c51a6eb938d878103c63f1e3e5920b70865c631a9ada` | `9a06d3910d8570be9e8ba8c5d897895cb495383374abebe83215da559a3eb761` | `yaml.safe_load` valid (`loop_caps`, `delegation`, `discover_models: false`, 45 active coding/reasoning models) |
| `~/.config/goose/custom_providers/custom_omniroute.json` | `0600` | `b598a0e0da8f03ddd7a42ad71b2e72535dc270d9c3902faae5a76826a85ac226` | `b0d16a0e042d4e3836eb93ea626acff5caa828f0ff43d15097e106c33cc5cd2e` | `json.loads` valid (`supports_vision: true`) |
| `~/.omp/agent/config.yml` | `0600` | `ee266cb3319c470c9688d191e67b9615447b6e8bff4fe04b7bead72fdf3cbfb2` | `b06240283d2593ab224b1fe8d64b807922b98721033d8414ed77d7b490293a30` | `omp config list --json` exit `0` (`prewalk.auto: suggest`) |
| `~/.omp/agent/models.yml` | `0600` | `98798996502cba3ec18c81c3fe78647b7514eaf54ff5d3d34c1c87fb4f6141a4` | `e29651e50e93a1e5731ad93e0ba9b2d74fd38f323081d6623e07d51e074e707f` | `omp models --json` exit `0` (`contextWindow: 1000000` on `nx/deepseek-v4-pro` & `nx/gemini-4-argon`, `imageCountBudget: 20`) |
| `~/.claude/settings.json` | `0600` | `014fb044e2bfb12b1779b56ca6e9c49a29fff130f84c95250d00111838e112c6` | `c726d5b98376599db4dd300eef409eb9baf1ce30f9ba9555a9124321517a0668` | `claude --version` = `2.1.302` (`minimumVersion`, retry watchdog) |

### Task 4.5: OmniRoute Gate 4b (`ensure-muse-wire-compat.sh`)
- Created `/Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh` (`0755`, SHA-256 `9d263c518664...`) and wired into `update.sh` (`8ee3036266f2...`), `docker-service.sh` (`951517667d75...`), and `omniroute-watchdog.sh` (`7b5c8eba7479...`) with `--profile base`.
- Verification:
  - `/Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh` → `Muse Code wire-compat normalization verified (already_ok)` (exit `0`).
  - `curl -fsS http://127.0.0.1:20128/v1/muse-code/models` → HTTP 200 JSON catalog containing `muse-spark-1.3`.

---

## 5. Phase 5 — MCP Router `0.6.4`, Knowledge Stack, `gws` Auth, Go `1.27.2` & Docker Compose (`5.1`–`5.5`)

### Task 5.1: `platform/mcp-router`, `/Applications/MCP Router.app` & 21-Agent Fleet Verification
- Updated `packageManager` to `"pnpm@12.14.0"` in `platform/mcp-router/package.json:13` and migrated workspace `overrides`, `onlyBuiltDependencies`, `verifyDepsBeforeRun: false`, `nodeLinker: hoisted`, and `shamefullyHoist: true` into `pnpm-workspace.yaml` (commit `7bce8df3f6109247ec03a6a6e6c0794e8c0f1818`).
- Ran `pnpm --dir /Users/androidteam/Developer/platform/mcp-router run typecheck` (`8/8` tasks, exit `0`), `pnpm --dir /Users/androidteam/Developer/platform/mcp-router test` (`71/71` tests, exit `0`), and `pnpm --dir /Users/androidteam/Developer/platform/mcp-router --filter @mcp_router/electron run package` (exit `0`).
- Deployed `app.asar` (`SHA-256: fc77d9082aa288a5df60d9b68ed7a86d88419f5b18411d2183c6a2df455118fd`) to `/Applications/MCP Router.app/Contents/Resources/app.asar` and restarted `/Applications/MCP Router.app` (`PID 78081`); verified `CFBundleShortVersionString = 0.6.4` and listener on `127.0.0.1:3282`.
- Updated `graphify-microservices` `args` in `~/Library/Application Support/MCP Router/mcprouter.db` to `/Users/androidteam/Developer/platform/go-microservices/graphify-out/graph.json`, granted all `14/14` active MCP servers (`170` tools) across all 25 client tokens in `~/Library/Application Support/MCP Router/shared-config.json`, bound `MCPR_TOKEN` in `~/.qwen/settings.json` (`sha10: 4915ce5483`), `~/Library/Application Support/Code/User/mcp.json` (`sha10: e024aabbec`), and `~/.config/goose/config.yaml` (`sha10: 0887290e10`), enforced mode `0600` across all 21 credential-bearing agent MCP config files, and verified `21/21` agent surfaces return HTTP `200` and `170` tools on `POST http://127.0.0.1:3282/mcp` plus live tool executions (`wiki_read`, `resolve_library_id`, `graph_stats`, `list_repos`, `memory_slot_list`).

### Task 5.2: Graphify 5-Platform Skills & Wiki Entities
- Refreshed all 5 platform skill directories (`agents`, `droid`, `kiro`, `copilot`, `codebuddy`) to `0.9.92`.
- Verified `graphify --version 2>&1` outputs `graphify 0.9.92` with zero stderr warnings (exit `0`).
- Updated `wiki/entities/{graphify,agentmemory,notion-cli,docker-workstation}.md` and `wiki/log.md`; verified `uv run --directory /Users/androidteam/Developer/wiki python3 scripts/wiki-lint.py` exits `0` with `0` errors.

### Task 5.3: Google Workspace CLI (`gws`) Keyring Verification
- Verified `/opt/homebrew/bin/gws auth status` in the user session reports `"encryption_valid": true`, `"has_refresh_token": true`, `"token_valid": true` (`keyring_backend: "keyring"`), and documented `gws auth login` recovery in `docs/mac-development-setup.md`.

### Task 5.4: `platform/go-microservices` Go `1.27.2` & `goroutineleakprofile` Retirement
- Updated all 18 tracked `go.mod` files (`verification/go-module-roots.txt`) + CI workflows, `tools.env`, `preflight.go`, `AGENTS.md`, `docs/adr/0005-go-1.26-runtime.md`, and `tools/templates/{Makefile.platform,README.md}` to `go 1.27.2` and removed `GOEXPERIMENT=goroutineleakprofile`.
- Verified `cd /Users/androidteam/Developer/platform/go-microservices/platform && go test ./...` passes (`20 packages ok`, exit `0`).

### Task 5.5: Workspace Docker Compose Standardization
- Updated `tdt/jira-skill/docker-compose.yml` (`jira-skill-data:/app/data` named volume + `127.0.0.1:` port prefix) and prefixed published ports with `127.0.0.1:` across `tdt/bootstrap-nexus`, `tdt/realtime`, `vds/vds-root-assets`, and `ghtk/ghtk-training-cicd`.
- Verified `/Users/androidteam/Developer/scripts/docker-standardize-check.sh --strict` exits `0` (`✅ All stacks passed validation.` — `0 FAIL, 0 WARN`).
