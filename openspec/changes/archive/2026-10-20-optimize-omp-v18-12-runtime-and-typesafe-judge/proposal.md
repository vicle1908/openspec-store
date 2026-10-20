# Proposal

## Why

OMP (`v18.12.2`) currently suffers from 63 daily `HTTP 402` judgment failures because `judge` resolves to an unfunded `openrouter` credential instead of the funded `TYPESAFE_API_KEY` (`typesafe/jev-1.14.0`), while non-login/GUI-spawned OMP processes (`zsh -fc`, Orca, Herdr) lack active provider keys in `~/.omp/agent/.env` (currently mode `0644` with empty keys, causing `models.yml` providers to fall back to literal env-var strings as Bearer tokens), alongside degraded subagent/advisor settings (`isolation.backend: rcopy`, `externalThinking: true`, missing `cockpit/*` wildcard fallback and reasoning metadata), 15 dead `sh/*` entries and inflated `contextWindow` overrides in `~/.omp/agent/models.yml`, a broken `@AGENTS.md` relative import in `/Users/androidteam/Developer/.claude/CLAUDE.md`, and missing `omp` registration in the workstation toolchain manifest. Reconciling OMP's `judge` role, non-login credential store, `v18.12.2` runtime configuration, custom model catalog, context import path, and toolchain governance eliminates judgment/advisor failures, activates APFS copy-on-write isolation and Apple Silicon MLX acceleration, prevents premature context overflow, and brings `/opt/homebrew/bin/omp` under full declarative toolchain tracking.

## What Changes

- **TypeSafe `jev-1.14.0` Native Judge Integration, Non-Login `.env` Persistence & OpenRouter `402` Remediation**:
  - Bind `modelRoles.judge: typesafe/jev-1.14.0` and `retry.fallbackChains.judge: [typesafe/jev-latest, typesafe/jev-preview]` in `~/.omp/agent/config.yml` so `find` (`find.enabled: auto`), `prewalk.auto: suggest`, `ttsr.judge: auto`, and `eval` `judge()`/`judge_batch()` deterministically route to TypeSafe System One (`https://api.typesafe.ai/v1/systemone`).
  - Persist all 5 active provider credentials (`TYPESAFE_API_KEY`, `OMNIROUTE_API_KEY`, `HERMES_CUSTOM_COCKPIT_API_KEY`, `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_PHANMEMVIP_API_KEY`) in `~/.omp/agent/.env` (`mode 0600`, removing retired empty `HERMES_CUSTOM_GIAODUC_API_KEY` and `HERMES_CUSTOM_OMNIROUTE_API_KEY` entries) and enroll `typesafe` (`credential_type: "api_key"`, `data: {"key": "...", "source": "login"}`) in `~/.omp/agent/agent.db:auth_credentials` while deleting the unfunded `openrouter` credential (`id=1`) from `auth_credential_blocks` (`WHERE credential_id IN (...) OR provider_key GLOB ...`) and `auth_credentials`, commenting out `OPENROUTER_API_KEY` in `~/.zshenv`, and adding `disabledProviders: [openrouter, lm-studio, llama.cpp, vscode]` in `~/.omp/agent/config.yml`.
- **OMP `v18.12.2` Runtime, Advisor, and Apple Silicon Optimization (`~/.omp/agent/config.yml`)**:
  - Switch `isolation.backend` from `rcopy` to `apfs` so isolated `task` subagents on macOS arm64 use instantaneous APFS `clonefile(2)` copy-on-write clones instead of full recursive directory copies.
  - Set `externalThinking: false` to restore native provider reasoning tokens on Gemini 4 Argon, Gemini 3.8 Flash, and Cockpit GPT-6.1-Sol, and set `providers.tinyModelDevice: mlx` to enable Apple Silicon 4-bit MLX local inference acceleration.
  - Replace model-specific `cockpit/gpt-6-astra` with wildcard `cockpit/*: [google-antigravity/gemini-4-argon:high, omniroute/gemini-3.8-flash-high, google-antigravity/gemini-3.8-flash:high]` in `retry.fallbackChains` to cover `modelRoles.advisor: cockpit/gpt-6.1-sol:xhigh` and all Cockpit models without YAML duplication, and replace unauthenticated `google/*` and `google-vertex/*` wildcard hops in `retry.fallbackChains['google-antigravity/*']` with `google-antigravity/gemini-3.8-flash:high`.
  - Remove superseded legacy keys from `~/.omp/agent/config.yml` (`memories.enabled`, `renderMermaid.enabled`, `calc.enabled`, and `bashInterceptor.redirects`) while retaining `memory.backend: local`, `bashInterceptor.enabled: true`, and `tui.renderMermaid: true`.
- **Custom Model Catalog Hygiene & Context-Window Alignment (`~/.omp/agent/models.yml`)**:
  - Prune the 14 retired `sh/*` model entries (including duplicate `sh/codex-x`) from `providers.omniroute.models` (leaving the 11 active live models) and remove the retired `omniroute-chat` (`sh/codex-x`) provider block that no longer exist in live OmniRoute (`http://127.0.0.1:20128/v1/models`).
  - Align `contextWindow` declarations with live upstream limits for OMP `v18.12.0+` catalog precedence: set `nx/deepseek-v4.1-flash` `contextWindow: 128000` (from `900000`) and `omniroute-anthropic` (`pm/Claude-Fable`, `pm/Claude-Opus`, `pm/Claude-Sonnet`) `contextWindow: 200000` (from `900000`) so automatic compaction fires before upstream context overflow.
  - Enrich `providers.cockpit.models` (`gpt-6-astra`, `gpt-6.1-sol`, `gpt-5.6-luna`, `gpt-5.6-sol`, `gpt-5.6-terra`) with `reasoning: true`, `thinking: { mode: effort, efforts: [low, medium, high, xhigh], defaultLevel: high }`, `supportsTools: true`, and `imageCountBudget: 20`.
- **Workspace Context Hygiene & Declarative Toolchain Ownership for `omp`**:
  - Update the trailing `@AGENTS.md` import in `/Users/androidteam/Developer/.claude/CLAUDE.md:L153` to `@../AGENTS.md` (so `/Users/androidteam/Developer/AGENTS.md` remains imported without `@-import: file not found` warnings) and remove the duplicate `~/.omp/agent/skills/herdr` symlink.
  - Register `omp` (`can1357/tap/omp`, `/opt/homebrew/bin/omp`, `authoritative_owner: "brew-formula"`) with full schema fields and shadow-path verification across `config/workstation-toolchain-manifest.json`, `config/Brewfile`, `docs/mac-development-setup.md`, `scripts/toolchain_updater_registry.py`, `scripts/inventory-workstation-toolchain.py`, `scripts/reconcile-agent-cli-coverage.py`, `scripts/workstation-daily-update.sh` (plus `/Users/androidteam/Developer/scripts/workstation-daily-update.sh`), and unit tests in `scripts/test-version-authority-governance.py` and `tests/test_portable_workstation_slice_a.py`.

### Non-Goals

- Changing OMP's active primary chat or advisor role bindings (`default`, `smol`, `tiny`, `vision`, `slow`, `plan`, `commit`, `task`, `advisor: cockpit/gpt-6.1-sol:xhigh`).
- Modifying OmniRoute container combos or upstream provider accounts in `http://127.0.0.1:20128` (already governed by `configure-omniroute-gemini-4-argon-tier-combos`).
- Modifying the SHB Python `shb_core.jev` SDK integration (governed separately by `agent-core-integrate-jev-system-one`).

### Ownership Boundaries

- **OMP Agent Configuration & State (`~/.omp/agent/config.yml`, `~/.omp/agent/models.yml`, `~/.omp/agent/.env`, `~/.omp/agent/agent.db`, `~/.omp/agent/skills/`)**: Owns OMP role bindings, fallback chains, runtime settings, custom model metadata, and non-login credential resolution.
- **User Shell & Workspace Context (`~/.zshenv`, `/Users/androidteam/Developer/.claude/CLAUDE.md`, `/Users/androidteam/Developer/scripts/workstation-daily-update.sh`)**: Owns login-shell environment exports, workspace context file imports, and synchronized host maintenance scripts.
- **Central OpenSpec Governance & Toolchain Manifest (`/Users/androidteam/Developer/platform/openspec-store`)**: Owns canonical specifications (`omp-provider-routing`, `omp-fresh-shell-contract`, `workstation-toolchain-inventory`, `agent-cli-inventory-coverage`), `config/workstation-toolchain-manifest.json`, `config/Brewfile`, and toolchain inventory/reconciliation scripts and tests.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `omp-provider-routing`: Add requirements for native TypeSafe `jev-1.14.0` `judge` role routing and fallback chains, `disabledProviders` hygiene, `cockpit` reasoning metadata and `cockpit/*` wildcard fallback coverage, pruning retired `sh/*` models and aligning `contextWindow` limits in `models.yml`, and `v18.12.2` runtime settings (`isolation.backend: apfs`, `externalThinking: false`, `providers.tinyModelDevice: mlx`, legacy key removal).
- `omp-fresh-shell-contract`: Add requirements governing `TYPESAFE_API_KEY`, `OMNIROUTE_API_KEY`, and `HERMES_CUSTOM_{COCKPIT,SHOPAPIKEY,PHANMEMVIP}_API_KEY` availability across login shells (`zsh -lic`) and non-login/GUI (`zsh -fc`) processes via `~/.omp/agent/.env` (`0600`) and `agent.db` without secret exposure, `@../AGENTS.md` context resolution, and supersession of legacy `phanmemvip/gpt-5.6-sol:max` default-role assertions.
- `workstation-toolchain-inventory`: Add requirements registering `omp` (`can1357/tap/omp`, `/opt/homebrew/bin/omp`) under `brew-formula` ownership with dynamic Cellar source verification and shadow-path scanning in `config/workstation-toolchain-manifest.json`, `config/Brewfile`, `scripts/toolchain_updater_registry.py`, and `scripts/inventory-workstation-toolchain.py`.
- `agent-cli-inventory-coverage`: Add requirements registering `omp` in `scripts/reconcile-agent-cli-coverage.py` (with registry-verified `uncovered_declared` evaluation) and `AGENT_CLI_KNOWN_UNCOVERED` in `workstation-daily-update.sh`.

## Impact

- **OMP Runtime (`~/.omp/agent/`)**: Eliminates `HTTP 402` judgment failures on `find`, `prewalk.auto`, and `ttsr.judge`; enables sub-second `typesafe/jev-1.14.0` System One judgments (~600 ms) in both login and `zsh -fc`/GUI environments; prevents literal env-var Bearer token `HTTP 401` failures on custom providers; restores native model reasoning tokens; speeds up isolated `task` spawns via APFS `clonefile(2)`; and prevents context overflow on `nx/deepseek-v4.1-flash` and `pm/Claude-*`.
- **Workstation Toolchain Governance (`platform/openspec-store`)**: Ensures `omp` is audited alongside peer Homebrew-formula agent CLIs (`herdr`, `qwen`, `goose`) with active shadow-path detection and zero drift in `inventory-workstation-toolchain.py --json` and `reconcile-agent-cli-coverage.py`.
