# Proposal

## Why

A comprehensive workstation audit across AI coding agent harnesses, the OmniRoute gateway, MCP/knowledge tooling, core language runtimes, and daily maintenance automation revealed runtime-versus-specification drift, split package ownership, unexecuted daily health audits (masking an 11.62 GiB snapshot loose-object breach), unhardened MCP token files, stale desktop/CLI builds, and untapped upstream capabilities across newly released tool versions. Reconciling our declarative manifests, specifications, configurations, and maintenance workflows now restores single-owner determinism, closes security and operational gaps, and adopts high-leverage upstream features across the developer ecosystem.

## What Changes

- **Workstation Package Ownership, Shell `PATH` & Daily Maintenance Parity (`portable-workstation-toolchain`, `workstation-toolchain-inventory`, `agent-cli-inventory-coverage`, `snapshot-store-growth-bounds`)**:
  - Reconcile `config/Brewfile`, `config/workstation-toolchain-manifest.json`, `config/npm-global-tools.json`, `config/uv-tools.json`, and `scripts/toolchain_updater_registry.py` so every tool has a single authoritative owner: add `cask "muse-code"`, `brew "googleworkspace-cli"`, and `brew "ollama"` to `config/Brewfile`; align `codex` (`brew-cask`), `opencode` (`brew-formula` `anomalyco/tap/opencode`), `openspec` (`npm-global` `@fission-ai/openspec`), `newman` (`brew-formula`), `hermes` (`standalone` git checkout at `~/.hermes/hermes-agent`), `qwen` (`brew-formula` `qwen-code`), `ruff` and `pytest` (`brew-formula`), `prime-agent` (`local-dev`), `cce` (`standalone` pinned), and `qoder`/`qodercli` (`vendor_download` with `~/.qoder/entry` and `~/.kimi-code/bin` in `sanctioned_roots` and `STANDARD_PATH`).
  - Resolve duplicate and broken binary installations via operator-authorized steps: re-link `/opt/homebrew/bin/goose` (`1.54.0` unlinked regular file blocking Cellar `1.55.0`), upgrade `copilot-cli` (`1.0.95` -> `1.0.98`), `droid` (`0.238.0`/`0.242.0` -> `0.244.0`), and `ntn` (`0.23.17` -> `0.23.20`), and clean up duplicate shadowed binaries (`codex`, `opencode`, `openspec`, `bun`, `newman`, `~/go/bin/buf`, and ~1.21 GiB of duplicate `gitnexus` trees in `~/.local/share/home-toolchain` and `~/.local/lib/node_modules`).
  - Normalize Zsh initialization (`~/.zshenv`, `~/.zprofile`, `~/.zshrc`) with `typeset -U path PATH`, align `PATH` ordering so `/opt/homebrew/bin` precedes `~/.npm-global/bin`, expose `/opt/homebrew/opt/libpq/bin` (`psql 18.6`), remove dangling `~/.orbstack/bin`, add `eval "$(omp completions zsh)"`, and guard `~/.iterm2_shell_integration.zsh` with `[[ -t 0 && -t 1 ]]`.
  - Unify `shb-schedule` (`workstation_update.py`) and `workstation-daily-update.sh` so Stages 8–10 (`measure-snapshot-growth.py`, `inventory-workstation-toolchain.py`, `reconcile-agent-cli-coverage.py`) execute inside `step_integrity_and_store_validation()` on every scheduled `apply` run, align the covered agent CLI roster (removing unsupported `kilo update` from DBOS and aligning `kimi`, `opencode`, `auggie`, `ntn`, and `qwen`), and reclaim ~11.59 GiB in `~/.agentmemory/snapshots` via non-destructive `git repack -a -d -f --depth=250 --window=250`.
  - Remediate LaunchAgent fleet hygiene: relocate `ai.hermes.gateway.plist.bak-*` out of `~/Library/LaunchAgents/`, register `omniroute-watchdog.sh` in `config/script-provenance-manifest.tsv`, fix `com.omniroute.update-check` (`exit 255` caused by `awk ... exit` `SIGPIPE` under `set -euo pipefail` in `~/Omniroute/scripts/check-upstream.sh:29-30` and missing `HOME` in plist `EnvironmentVariables`), fix `com.victory1908.hermes-webui.plist` (`exit 78` caused by stale `~/Developer/hermes-webui` path vs `~/Developer/platform/hermes-webui`), and fix `Antigravity Tools.plist` (`exit 78` caused by `antigravity_tools` underscore vs `antigravity-tools` hyphen in `Contents/MacOS/`).

- **AI Coding Agent Harnesses, OmniRoute Gateway & Upstream Feature Adoption (`omniroute-agent-cli-routing`, `omp-provider-routing`, `claude-code-provider-routing`, `hermes-runtime-efficiency`)**:
  - Configure Qwen Code (`~/.qwen/settings.json`, `$version: 4`, mode `0600`) with `modelProviders.openai` array (`gemini-3.8-flash-high` via `http://localhost:20128/v1`, `envKey: "OMNIROUTE_API_KEY"`), `security.auth.selectedType: "openai"`, `model.name: "gemini-3.8-flash-high"`, and `mcpServers.mcp-router` while preserving all 12 Orca lifecycle hook arrays.
  - Harden mode `0644` credential-bearing MCP/provider files (`~/.copilot/mcp-config.json`, `~/.gemini/config/mcp_config.json`, `~/.gemini/antigravity/mcp_config.json`, `~/.kimi/mcp.json`, and `~/.config/goose/custom_providers/*.bak*`) to mode `0600`, and remove duplicate `mcp.agentmemory` from `~/.config/opencode/opencode.json`.
  - Reconcile model selector drift in `~/.kimi-code/config.toml` (`[models.or-gpt-5-6-sol]` -> `sh/gpt-5.6-sol`), `~/.grok/config.toml` (`[model.omniroute-sol]` -> `sh/gpt-5.6-sol`), `~/.pi/agent/models.json` (retire `ollamacloud/*`), and `~/.hermes/config.yaml` (restore `tool_loop_guardrails.loop_caps`, bounded `delegation.*`, and prune `aihorde/*` catalog bloat).
  - Reconcile `omp-provider-routing` and `claude-code-provider-routing` specs with live configurations (`google-antigravity/gemini-4-argon` default/smol roles, hyphenated `nx/gemini-4-argon`, `cockpit.json` on `:20129`, `omniroute-pm.json` on `gemini-3.8-flash-high`).
  - Ensure `docker-service.sh` and `omniroute-watchdog.sh` pass `--profile base` for `~/Omniroute` and invoke `~/Omniroute/scripts/ensure-muse-wire-compat.sh` to preserve OmniRoute Gate 4b (`muse-wire-compat` SSE keepalive normalization) across container recreations.
  - Adopt verified upstream features: Goose `supports_vision: true` in `custom_omniroute.json`, OMP `prewalk.auto: "suggest"` in `config.yml` and `imageCountBudget: 20` on multimodal models in `models.yml`, and Claude Code top-level `minimumVersion: "2.1.302"` and `env.CLAUDE_CODE_RETRY_WATCHDOG_MAX_USAGE_LIMIT_WAIT_MS: "300000"`.

- **MCP Router `0.6.4`, Knowledge Graph, OpenSpec Store & Core Runtime Alignment (`mcp-router-multi-key-load-balancing`, `openspec-runtime-governance`, `workspace-index-freshness`, `gws-agent-skills`, `platform-go-runtime`, `docker-resource-access`)**:
  - Repackage `/Applications/MCP Router.app` (`app.asar`) from `~/Developer/platform/mcp-router` (`package:arm64`) so the live `:3282` service runs the committed `68c047d`/`8550cb9` multi-key pool failover and `safeStorage` encryption build (replacing the Jul 22 `app.asar`), and update `"packageManager": "pnpm@12.14.0"` in `mcp-router/package.json`.
  - Update `openspec-runtime-governance` spec to reflect the OpenSpec `1.14.3` Stores Beta architecture (`openspec-store` registered store and `defaultStore: "openspec-store"`).
  - Update `workspace-index-freshness` to `graphifyy` `0.9.92`, refresh all 5 stale `0.9.74` Graphify platform skills (`agents`, `droid`, `kiro`, `copilot`, `codebuddy`), document the `@agentmemory/agentmemory@0.9.30` `cli.mjs` `embeddingProvider` display bug workaround, and refresh `wiki/entities/{graphify,agentmemory,notion-cli,docker-workstation}.md`.
  - Recover `gws` keyring decryption (`gws auth login` when `encryption_valid: false`).
  - Align all 18 tracked `go.mod` files (and CI/tools.env metadata) in `platform/go-microservices` to `go 1.27.2` and remove obsolete `GOEXPERIMENT=goroutineleakprofile` (GA in Go 1.27).
  - Remediate `tdt/jira-skill/docker-compose.yml` (`jira-skill-data:/app/data` named volume + `127.0.0.1:` port bindings) and non-loopback port bindings in `tdt/bootstrap-nexus`, `tdt/realtime`, `vds/vds-root-assets`, and `ghtk/ghtk-training-cicd` flagged by `docker-standardize-check.sh`.

### Explicit Non-Goals

- Performing unapproved destructive deletions (`rm -rf` or `brew bundle cleanup --force`) or rotating upstream vendor API keys without explicit operator action.
- Auto-upgrading OpenCode from the stable `1.x` track (`1.19.3`) to the breaking `2.x` track (`2.0.32`) before plugin compatibility (`oh-my-opencode`) is separately verified.
- Modifying `platform/openspec-store` archived change directories (archived changes remain strictly immutable).
- Executing live host package mutations, LaunchAgent reloads, or dotfile writes during the OpenSpec planning phase.

### Affected Ownership Boundaries

- **Central OpenSpec Store (`~/Developer/platform/openspec-store`)**: Owns `openspec/changes/reconcile-workstation-dev-tooling-and-upstream-features/*`, `config/{Brewfile,workstation-toolchain-manifest.json,npm-global-tools.json,uv-tools.json,script-provenance-manifest.tsv}`, `docs/mac-development-setup.md`, `scripts/{workstation-daily-update.sh,toolchain_updater_registry.py,inventory-workstation-toolchain.py,reconcile-agent-cli-coverage.py,measure-snapshot-growth.py}`, and `tests/test_portable_workstation_slice_{a,b,c}.py`.
- **External Workspace Repositories (governed via external execution packets)**:
  - `~/Developer/scripts/` & `~/Developer/docs/` (`workstation-daily-update.sh`, `docker-service.sh`, `omniroute-watchdog.sh`, `README.md`)
  - `~/Developer/shb/shb-schedule` (`src/shb_schedule/workflows/workstation_update.py` & `tests/test_workstation_update_workflow.py`)
  - `~/Developer/platform/mcp-router` (`package.json` & `apps/electron` `package:arm64` bundle)
  - `~/Developer/platform/go-microservices` (18 `go.mod` files, `docs/adr/0005-go-1.26-runtime.md`, `tools/templates/Makefile.platform`)
  - `~/Developer/tdt/{jira-skill,bootstrap-nexus,realtime}`, `~/Developer/vds/vds-root-assets`, `~/Developer/ghtk/ghtk-training-cicd` (`docker-compose*.yml`)
  - `~/Developer/wiki` (`entities/*.md` and `log.md`)
  - `~/Omniroute` (`scripts/check-upstream.sh`, `scripts/ensure-muse-wire-compat.sh`, `scripts/update.sh`)
- **Operator Host & User Dotfiles (`$HOME`, governed via operator-authorized apply gates with mode `0600` backups)**:
  - `~/.zshenv`, `~/.zprofile`, `~/.zshrc`, `~/Library/LaunchAgents/*.plist`
  - `~/.claude/`, `~/.codex/`, `~/.omp/agent/`, `~/.config/opencode/`, `~/.copilot/`, `~/.factory/`, `~/.gemini/`, `~/.kimi-code/`, `~/.kimi/`, `~/.config/goose/`, `~/.pi/agent/`, `~/.config/muse/`, `~/.qwen/`, `~/.grok/`, `~/.hermes/`, `~/.agentmemory/snapshots`

## Capabilities

### New Capabilities

*(None — all changes refine and extend existing governed workstation, routing, knowledge, and runtime capabilities.)*

### Modified Capabilities

- `portable-workstation-toolchain`: Add `muse-code`, `googleworkspace-cli`, and `ollama` to `Brewfile`; enforce `typeset -U path PATH`, `/opt/homebrew/bin` vs `~/.npm-global/bin` precedence, `/opt/homebrew/opt/libpq/bin` exposure, and TTY-guarded iTerm2 shell integration; require DBOS `workstation_update.py` to execute Stages 8–10 health reporters and `ntn update`; and remediate LaunchAgent `exit 255`/`exit 78` defects and provenance tracking.
- `workstation-toolchain-inventory`: Reconcile `workstation-toolchain-manifest.json`, `npm-global-tools.json`, `uv-tools.json`, and `inventory-workstation-toolchain.py` ownership declarations for `codex`, `opencode`, `openspec`, `newman`, `hermes`, `qwen`, `qoder`/`qodercli`, `prime-agent`, `cce`, `ruff`, `pytest`, `goose`, `droid`, `copilot-cli`, and `gitnexus` duplicate detection.
- `agent-cli-inventory-coverage`: Unify covered and declared-uncovered agent CLI rosters across `toolchain_updater_registry.py`, `reconcile-agent-cli-coverage.py`, `workstation-daily-update.sh`, and `workstation_update.py` (including `qwen` and `kimi`, and removing `kilo update` from DBOS).
- `snapshot-store-growth-bounds`: Mandate scheduled execution of `measure-snapshot-growth.py` inside the primary DBOS workflow (`workstation_update.py`) and specify non-destructive `git repack -a -d -f` reclamation for `~/.agentmemory/snapshots`.
- `omniroute-agent-cli-routing`: Add Qwen Code (`~/.qwen/settings.json` `$version: 4`) OmniRoute and `mcp-router` routing; harden mode `0644` `MCPR_TOKEN`/provider files to `0600`; reconcile `kimi-code`, `grok`, `pi`, and `opencode` configs; preserve OmniRoute Gate 4b SSE patch (`--profile base` + `ensure-muse-wire-compat.sh`) across container recreates; and adopt upstream CLI features (`supports_vision`, `minimumVersion`, retry watchdog).
- `omp-provider-routing`: Reconcile `modelRoles` (`google-antigravity/gemini-4-argon` for `default`/`smol`), hyphenated `nx/gemini-4-argon`, `nx/deepseek-v4.1-flash` `contextWindow: 900000`, per-model `imageCountBudget` in `models.yml`, `prewalk.auto` in `config.yml`, and `omp completions zsh`.
- `claude-code-provider-routing`: Reconcile `cockpit` (`cockpit/gpt-5.6-luna` on `:20129`) and `omniroute` (`gemini-3.8-flash-high` on `:20128`) profile specifications with live `~/.claude/profiles/*.json`.
- `hermes-runtime-efficiency`: Enforce `tool_loop_guardrails.loop_caps` (`max_web_searches`, `max_subagents`), bounded `delegation.*` parameters, and OmniRoute catalog pruning in `~/.hermes/config.yaml`.
- `mcp-router-multi-key-load-balancing`: Require `/Applications/MCP Router.app` `app.asar` bundle parity (`v0.6.4` multi-key pool build) with `~/Developer/platform/mcp-router` source and `pnpm@12.14.0` `packageManager` metadata alignment.
- `openspec-runtime-governance`: Update runtime topology from legacy `1.7.0` `~/Developer/openspec` symlink traversal to OpenSpec `1.14.3` Stores Beta (`openspec-store` and `defaultStore: "openspec-store"`).
- `workspace-index-freshness`: Upgrade approved Graphify version pin to `0.9.92`, synchronize all 5 platform skill copies (`agents`, `droid`, `kiro`, `copilot`, `codebuddy`), and reconcile `agentmemory` CLI embedding status reporting and wiki entity versions.
- `gws-agent-skills`: Require `googleworkspace-cli` in `config/Brewfile` and keyring re-encryption (`gws auth login`) when `gws auth status` reports `encryption_valid: false`.
- `platform-go-runtime`: Align all 18 `platform/go-microservices` module directives to `go 1.27.2` and replace `GOEXPERIMENT=goroutineleakprofile` with Go 1.27 GA `/debug/pprof/goroutineleak`.
- `docker-resource-access`: Enforce named database volumes (`jira-skill-data:/app/data`) in `tdt/jira-skill/docker-compose.yml` and loopback port bindings across all 5 flagged workspace Compose files.

## Impact

- **Planning & Governance Store**: `~/Developer/platform/openspec-store` (`config/{Brewfile,workstation-toolchain-manifest.json,npm-global-tools.json,uv-tools.json,script-provenance-manifest.tsv}`, `docs/mac-development-setup.md`, `scripts/*.py`, `scripts/workstation-daily-update.sh`, `tests/test_portable_workstation_slice_{a,b,c}.py`, and 14 capability specs).
- **Daily Maintenance & Scheduling**: `~/Developer/scripts/workstation-daily-update.sh` and `~/Developer/shb/shb-schedule` (`workstation_update.py` & `test_workstation_update_workflow.py`).
- **Agent Harnesses & Gateways**: Claude Code, Codex CLI, OMP, Antigravity/Gemini, OpenCode, Copilot CLI, Factory Droid, Kimi Code, Block Goose, Pi, Meta Muse Code, Qwen Code, Grok CLI, Hermes Agent, OmniRoute, and MCP Router.
- **Language Toolchains & Infra**: Go `1.27.2` (`platform/go-microservices` 18 modules), Python `3.14.8`/`3.15.0` (`uv 0.13.1`), TypeScript `7.0.2` (`platform/mcp-router`), Docker Desktop `4.95.0`, `libpq` `18.6`, `agentmemory` `0.9.30` (~11.59 GiB disk reclamation), `graphifyy` `0.9.92`, `ntn` `0.23.20`, and `gws` `0.22.5`.
