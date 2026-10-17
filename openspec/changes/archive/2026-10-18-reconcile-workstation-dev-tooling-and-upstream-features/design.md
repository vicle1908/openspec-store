# Design

## Context

See `proposal.md` — Why for the problem statement and motivation.

The workstation (`darwin 27.0.0 arm64`) implements four foundational patterns that this change reuses and reconciles:
1. **Central OpenSpec Store & Provenance Mirroring**: Declarative manifests (`config/Brewfile`, `config/workstation-toolchain-manifest.json`, `config/npm-global-tools.json`, `config/uv-tools.json`, `config/script-provenance-manifest.tsv`), setup runbooks (`docs/mac-development-setup.md`), and read-only reconciliation scripts (`scripts/toolchain_updater_registry.py`, `scripts/inventory-workstation-toolchain.py`, `scripts/reconcile-agent-cli-coverage.py`, `scripts/measure-snapshot-growth.py`) live in `/Users/androidteam/Developer/platform/openspec-store` and are byte-mirrored to `/Users/androidteam/Developer/scripts/`.
2. **DBOS Durable Daily Maintenance (`shb-schedule`)**: `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` delegates `apply` mode (`L394–403`) to `shb-schedule` (`src/shb_schedule/workflows/workstation_update.py`), checkpointing `@DBOS.step()` execution in `~/.shb/scheduler.db` and writing mode-`0600` JSON reports to `~/Developer/data/updates/YYYY-MM-DD.json`.
3. **Gateway & MCP Multiplexing**: Coding agents route inference through local **OmniRoute** (`127.0.0.1:20128`), **Cockpit** (`127.0.0.1:51006` / `:20129`), **Phanmemvip/ShopAPIKey**, and **Google Antigravity** using environment-variable or helper indirection, and multiplex MCP servers through **MCP Router** (`127.0.0.1:3282`) over `@mcp_router/cli connect`.
4. **Per-File Mode-`0600` Backup & Rollback Pattern**: User dotfile and CLI config mutations capture pre-apply SHA-256 hashes and mode-`0600` backups outside Git, verify with isolated sentinel or `--version`/config-load probes, and roll back atomically on failure.

## Goals / Non-Goals

**Goals:**
- Enforce a single installation owner and deterministic `PATH` resolution across all 14 coding agent CLIs, 7 MCP/knowledge tools, and core language/container toolchains, with `0` drift/unknown/undeclared findings from `inventory-workstation-toolchain.py --json` and `reconcile-agent-cli-coverage.py --json`.
- Close the execution gap between `workstation_update.py` (DBOS) and `workstation-daily-update.sh` (Bash) by folding Stages 8–10 (`measure-snapshot-growth.py`, `inventory-workstation-toolchain.py --json`, `reconcile-agent-cli-coverage.py --json`) into `step_integrity_and_store_validation()` (preserving the 9-step DBOS workflow contract tested in `test_workstation_update_workflow.py:186`) and adding `ntn update`.
- Reclaim ~11.59 GiB in `~/.agentmemory/snapshots` via non-destructive `git repack -a -d -f` and ~1.21 GiB in duplicate `gitnexus` installations under explicit operator gates.
- Harden all credential-bearing MCP/provider configs to mode `0600`, wire `qwen` (`0.25.2`, `$version: 4` schema) into OmniRoute + `mcp-router`, repackage `MCP Router.app` `0.6.4` (`app.asar`), preserve OmniRoute Gate 4b (`--profile base` + `ensure-muse-wire-compat.sh`) across container recreates, fix all 3 failing LaunchAgents (`com.omniroute.update-check` exit `255`, `com.victory1908.hermes-webui` exit `78`, `Antigravity Tools` exit `78`), and adopt verified upstream CLI/runtime features.

**Non-Goals:**
- Introducing new custom daemon services, wrapper binaries, or non-standard package managers.
- Performing unattended `rm -rf` or `brew bundle cleanup --force` operations.
- Migrating OpenCode from `1.19.3` (1.x) to `2.0.32` (2.x) before third-party plugin compatibility (`oh-my-opencode`) is verified in isolation.

## Decisions

### Decision 1: Single-Owner Resolution for Dual-Installed Binaries & Reporter Alignment
- **Choice**:
  - Retain **Homebrew Cask/Formula** as authoritative for `codex` (`cask "codex"`, `/opt/homebrew/bin/codex`), `opencode` (`anomalyco/tap/opencode`, `/opt/homebrew/bin/opencode`), `bun` (`oven-sh/bun/bun`), `newman` (`brew "newman"`), `ruff` (`brew "ruff"`), `pytest` (`brew "pytest"`), `qwen` (`brew "qwen-code"`), and `buf` (`bufbuild/buf/buf`), removing shadowed `~/.npm-global` copies of `@openai/codex` and `opencode-ai`, standalone `~/.bun/bin/bun`, and stale `~/go/bin/buf` (`1.72.0`).
  - Retain **`~/.npm-global`** as authoritative for `openspec` (`@fission-ai/openspec@1.14.3`, removing the lagging Homebrew `openspec` `1.14.2` formula) and `gitnexus` (`1.6.12`, removing the duplicate copies in `~/.local/share/home-toolchain` and unsanctioned `~/.local/lib/node_modules/gitnexus`).
  - In `toolchain_updater_registry.py`, `inventory-workstation-toolchain.py`, `reconcile-agent-cli-coverage.py`, `workstation-toolchain-manifest.json`, `config/npm-global-tools.json`, `config/uv-tools.json`, and `tests/test_portable_workstation_slice_{a,b,c}.py` + `scripts/test-version-authority-governance.py`:
    - Add `("codex", "brew-cask")` (`delegating` to `brew`, `supported_verb="codex update"`) while retaining `("codex", "npm")` in `SUPPORTED_UPDATER_REGISTRY` for unit test coverage; add `("qwen", "brew-formula")` (`uncovered_declared`, `delegating_to="brew"`).
    - Add `~/.qoder` and `~/.kimi-code` to `sanctioned_roots` (`inventory-workstation-toolchain.py:131-140`) and recognize `.qoder` and `.kimi-code` as `vendor_download` in `derive_install_root_and_source` (`L164-201`) and `classify_source` (`reconcile-agent-cli-coverage.py:83-97`, before the `package.json` parent walk so `~/.hermes/hermes-agent` and `~/.qoder` are not misclassified as `npm`).
    - Add `"opencode-ai"` to `pkg_keys` for `opencode` (`inventory-workstation-toolchain.py:1141-1150`) and align `reconcile_with_manifest()` (`L1271-1335`) for `cce` (`standalone` pinned), `prime-agent` (`local-dev`), and keg-only `psql` (`/opt/homebrew/opt/libpq/bin/psql`).
- **Alternatives Considered**: Keeping `codex` and `opencode` in `~/.npm-global` while removing Homebrew packages. Rejected because `config/Brewfile` and `docs/mac-development-setup.md` standardize on Homebrew Cask/Formula where vendor-supported (`portable-workstation-toolchain` Requirement 1).

### Decision 2: Zsh `PATH` Normalization (`typeset -U path PATH`) and Homebrew-First Precedence
- **Choice**: Declare `typeset -U path PATH` in `~/.zshenv`, keep `/opt/homebrew/bin` and `/opt/homebrew/sbin` ahead of `~/.npm-global/bin` in `~/.zshrc` (`L134-152`, matching `docs/mac-development-setup.md`), append `/opt/homebrew/opt/libpq/bin` so `psql` (`18.6`) is on `PATH`, remove dangling `~/.orbstack/bin`, add `eval "$(omp completions zsh)"`, and wrap `source ~/.iterm2_shell_integration.zsh` (`L159`) in `[[ -t 0 && -t 1 ]]`.
- **Alternatives Considered**: Leaving `_path_prepend "$HOME/.npm-global/bin"` ahead of `/opt/homebrew/bin`. Rejected because it inverts the documented security and ownership boundary.

### Decision 3: Execute Stages 8–10 Health Reporters Inside DBOS `step_integrity_and_store_validation()`
- **Choice**: Extend `step_integrity_and_store_validation()` in `~/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`L530-578`) to execute `measure-snapshot-growth.py`, `inventory-workstation-toolchain.py --json`, and `reconcile-agent-cli-coverage.py --json` alongside `script-provenance-manifest.tsv` and `openspec validate --all --store openspec-store`. Also update `STATIC_AGENT_COMMANDS` and `AGENT_PROBE_BINARIES` (`L60-76`, plus `test_workstation_update_workflow.py:190-222`) to remove unsupported `kilo update` and align `claude`, `codex`, `pi`, `qoder`, `kimi`, `opencode`, `auggie`, and `ntn`.
- **Alternatives Considered**: Adding a 10th top-level `@DBOS.step()` function. Folding Stages 8–10 into `step_integrity_and_store_validation()` preserves the 9-step workflow structure asserted by `test_plain_workstation_update_workflow_aggregates_steps` (`assert len(res["steps"]) == 9`) while guaranteeing snapshot and inventory checks run on every scheduled execution.

### Decision 4: Non-Destructive Snapshot Repack, LaunchAgent Root-Cause Remediation & OmniRoute Gate 4b Hook
- **Choice**:
  - **Snapshot Store**: Reclaim the 11.60 GiB of loose objects in `~/.agentmemory/snapshots` using `git -C ~/.agentmemory/snapshots repack -a -d -f --depth=250 --window=250` followed by `git prune-packed`, preserving all 997 commits intact.
  - **LaunchAgent Fixes**:
    1. `~/Omniroute/scripts/check-upstream.sh:29-30`: Replace `awk '/^Digest:/{print $2; exit}'` (which closes the pipe early and triggers `SIGPIPE` / exit `141` $\rightarrow$ `launchd` `255` under `set -euo pipefail`) with `awk '/^Digest:/ && !found {print $2; found=1}' || true`, and add `HOME=/Users/androidteam` and `/opt/homebrew/bin` to `com.omniroute.update-check.plist`.
    2. `com.victory1908.hermes-webui.plist:10,15`: Update `/Users/androidteam/Developer/hermes-webui` to `/Users/androidteam/Developer/platform/hermes-webui` (resolving `chdir` `ENOENT` / exit `78`).
    3. `Antigravity Tools.plist:7`: Update `/Applications/Antigravity Tools.app/Contents/MacOS/antigravity_tools` to `.../antigravity-tools` (resolving `execve` `ENOENT` / exit `78`).
  - **OmniRoute Gate 4b**: Extract Gate 4b (`muse-wire-compat` SSE keepalive and `/v1/muse-code/models` normalization) into `~/Omniroute/scripts/ensure-muse-wire-compat.sh` (`0755`) and invoke it (with `--profile base` on `docker compose`) from `~/Omniroute/scripts/update.sh`, `~/Developer/scripts/docker-service.sh` (`cmd_drain`/`cmd_up`), and `~/Developer/scripts/omniroute-watchdog.sh`.
- **Alternatives Considered**: Baking a custom local Docker image tag for OmniRoute. Rejected because custom image tags break `check-upstream.sh` remote index digest comparison against `diegosouzapw/omniroute:latest`.

### Decision 5: Verified Agent Config Schemas (`qwen` v4, `claude` 2.1.302, `omp` 18.11.3)
- **Choice**:
  - **Qwen Code (`0.25.2`)**: In `~/.qwen/settings.json` (`$version: 4`, mode `0600`), set `modelProviders.openai` to a bare `ModelConfig[]` array (`[{ "id": "gemini-3.8-flash-high", "name": "Gemini 3.8 Flash High (OmniRoute)", "baseUrl": "http://localhost:20128/v1", "envKey": "OMNIROUTE_API_KEY", "capabilities": { "vision": true }, "generationConfig": { "contextWindowSize": 1000000, "modalities": { "image": true } } }]`), `security.auth.selectedType: "openai"`, `model.name: "gemini-3.8-flash-high"`, and `mcpServers.mcp-router` while preserving all 12 Orca `hooks` keys.
  - **Claude Code (`2.1.302`)**: Set top-level `"minimumVersion": "2.1.302"` and `env.CLAUDE_CODE_RETRY_WATCHDOG_MAX_USAGE_LIMIT_WAIT_MS: "300000"` (digits-only millisecond string validated by `H.int({min:1,digitsOnly:true})`).
  - **OMP (`18.11.3`)**: Set `prewalk: { enabled: false, auto: suggest, autoTarget: "@smol" }` in `~/.omp/agent/config.yml`, and set `imageCountBudget: 20` on multimodal models (`gemini-3.8-flash-high`, `nx/gemini-4-argon`, `gemini-4-argon`) under `providers.omniroute.models[]` in `~/.omp/agent/models.yml`.

## Transaction Boundaries

```text
+--------------------------------------------------------------------------------------------------+
|                             TRANSACTION & ROLLBACK BOUNDARIES                                    |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|  Boundary 1: Central OpenSpec Store (~/Developer/platform/openspec-store)                        |
|  - Atomic Git commit for specs, Brewfile, workstation-toolchain-manifest.json,                   |
|    npm-global-tools.json, uv-tools.json, script-provenance-manifest.tsv,                         |
|    docs/mac-development-setup.md, scripts/*, and tests/*.                                        |
|  - Gate: `openspec validate reconcile-workstation-dev-tooling-and-upstream-features              |
|          --strict --json --store openspec-store` and `pytest` MUST pass.                         |
|                                                                                                  |
|  Boundary 2: Scheduled Updater Pause & Package/Binary Reconciliations (Host)                     |
|  - Pre-gate: `launchctl bootout` / `disable` on `com.developer.workstation-daily-update`.        |
|  - Each package action (`brew link --overwrite block-goose-cli`, `brew upgrade --cask            |
|    copilot-cli droid`, `ntn update`, duplicate uninstalls) is verified independently via         |
|    `which -a <tool>` and `<tool> --version` before proceeding to the next tool.                  |
|                                                                                                  |
|  Boundary 3: Per-File Dotfile & CLI Config Mutations ($HOME)                                     |
|  - Pre-gate: Mode-0600 backup + SHA-256 baseline hash recorded per file.                         |
|  - Atomic temp-file write + `os.rename()` + syntax/parse validation + CLI sentinel check.        |
|  - On failure: Immediate single-file rollback from backup without affecting sibling CLIs.        |
|                                                                                                  |
|  Boundary 4: External Workspace Repositories (`shb-schedule`, `mcp-router`, `go-microservices`,  |
|              `tdt/*`, `vds/*`, `ghtk/*`, `wiki`, `scripts`, `~/Omniroute`)                       |
|  - Isolated per-repository commits and test/build gates (`uv run pytest`, `package:arm64`,       |
|    `go test ./...`, `docker-standardize-check.sh`, `wiki-lint.py`).                              |
+--------------------------------------------------------------------------------------------------+
```

## Risks / Trade-offs

- **[Risk] Removing duplicate npm global packages (`@openai/codex`, `opencode-ai`) while a shell caches old `PATH` lookups** → **Mitigation**: Verify `/opt/homebrew/bin/{codex,opencode}` first (`--version`), uninstall only the `~/.npm-global` duplicate, and run `hash -r` + `which -a` verification.
- **[Risk] Updating `codex`, `ruff`, and `pytest` ownership in `workstation-toolchain-manifest.json` breaks existing unit tests in `tests/test_portable_workstation_slice_{a,b}.py` and `scripts/test-version-authority-governance.py`** → **Mitigation**: Update `config/npm-global-tools.json`, `config/uv-tools.json`, `tests/test_portable_workstation_slice_{a,b}.py`, and `scripts/test-version-authority-governance.py` in lockstep within the same central store commit and run `pytest` + `python3 scripts/test-version-authority-governance.py`.
- **[Risk] Repacking `~/.agentmemory/snapshots` while `com.agentmemory.server` writes a snapshot** → **Mitigation**: `git repack -a -d -f` writes new packfiles atomically before unlinking packed loose objects; verify with `git -C ~/.agentmemory/snapshots fsck --no-dangling` before and after.
- **[Risk] Tightening mode `0644` MCP config files to `0600` without named approval** → **Mitigation**: Record explicit named approvals in the change manifest prior to apply per `omniroute-agent-cli-routing` Requirement "Mode tightenings SHALL be named-approved before apply", preserving SHA-256 byte identity.

## Migration Plan

1. **Phase 1 — Central Store Manifests, Reporters, Tests & Runbook (`platform/openspec-store`)**: Update `config/{Brewfile,workstation-toolchain-manifest.json,npm-global-tools.json,uv-tools.json,script-provenance-manifest.tsv}`, `scripts/{toolchain_updater_registry.py,inventory-workstation-toolchain.py,reconcile-agent-cli-coverage.py,workstation-daily-update.sh}`, `tests/test_portable_workstation_slice_{a,b,c}.py`, `scripts/test-version-authority-governance.py`, and `docs/mac-development-setup.md`.
2. **Phase 2 — Daily Pipeline & Snapshot Reclamation (`shb-schedule`, `~/Developer/scripts/`, `~/.agentmemory/snapshots`)**: Sync `~/Developer/scripts/workstation-daily-update.sh`, update `workstation_update.py` and `test_workstation_update_workflow.py` in `shb/shb-schedule`, and repack `~/.agentmemory/snapshots`.
3. **Phase 3 — Package Ownership, Binary Upgrades & Zsh/LaunchAgent Hygiene**: Pause daily updater via `launchctl`, re-link `goose` (`1.55.0`), upgrade `copilot-cli` (`1.0.98`), `droid` (`0.244.0`), and `ntn` (`0.23.20`), remove verified duplicate binaries, normalize `~/.zshenv`/`~/.zshrc`, and fix LaunchAgents (`com.omniroute.update-check`, `com.victory1908.hermes-webui`, `Antigravity Tools`, `.bak` relocation).
4. **Phase 4 — Agent Harness Configs, Mode `0600` Hardening & OmniRoute Gate 4b**: Configure `~/.qwen/settings.json` (`0600`), harden mode `0644` MCP/backup files to `0600`, reconcile `kimi-code`, `grok`, `pi`, `opencode`, `hermes`, `omp`, and `claude` configs, and wire `--profile base` + `ensure-muse-wire-compat.sh` into `docker-service.sh` and `omniroute-watchdog.sh`.
5. **Phase 5 — MCP Router `0.6.4` Bundle, Knowledge Skills, `gws` Auth & Go/Docker Alignment**: Update `mcp-router/package.json` (`pnpm@12.14.0`), rebuild and deploy `MCP Router.app` `0.6.4` (`app.asar`), refresh all 5 Graphify `0.9.92` platform skills and Wiki entities, re-authenticate `gws auth login`, bump all 18 `platform/go-microservices` `go.mod` files to `go 1.27.2` (removing `GOEXPERIMENT=goroutineleakprofile`), and fix all 5 flagged `docker-compose*.yml` files.
