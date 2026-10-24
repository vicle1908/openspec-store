# Proposal

## Why

The workstation and `~/Developer` ecosystem lack a unified, governed cloud stealth browser and CLI 3.0 workflow across coding agents, while Hermes Agent currently has its native `browser-harness` (`browser_exec`) disabled (`browser.backend: false`, `browser.cloud_provider: browserbase`) due to historical Browserbase CDP incompatibilities. Adopting Browser Use Cloud (API V4 + CDP Browser Infrastructure), the `browser-use` CLI (`uv tool`), and the four core `browser-use/browser-use` skills activates Hermes's first-class `browser_exec` + `BU_AUTOSPAWN` runtime and gives all workstation agents $0/month pay-as-you-go stealth browsers ($0.02/hr, 90.5% Stealth Bench V2, free CAPTCHA solving, 10 concurrent sessions) without paying LLM orchestration markups when paired with local OmniRoute (`127.0.0.1:20128`).

## What Changes

- **Shared-Tier Credential Governance (`~/.zshenv`)**: Standardize `BROWSER_USE_API_KEY` inside the `# BEGIN shared-agent-secrets` ... `# END shared-agent-secrets` block of `/Users/androidteam/.zshenv` (mode `0600`, single-quoted export) without duplicating it in `~/.hermes/.env` or repository `.env` files, and verify account/profile readiness via a value-blind probe (`GET /api/v2/billing/account` and `GET /api/v4/profiles`).
- **Hermes Native `browser-use` Backend Activation (`~/.hermes/config.yaml`)**: Remove `browser.backend: false` (leaving `browser.backend` unset so `is_browser_use_cli_mode()` and `is_legacy_browser_use_cloud_config()` both evaluate to `True`) and switch `browser.cloud_provider` from `browserbase` to `browser-use` (retaining `BROWSERBASE_*` in `~/.hermes/.env` as a dormant fallback), enabling Hermes's bundled `browser-harness==0.1.13` (`browser_exec`) with `BU_AUTOSPAWN="1"` for public URLs and automatic local Chromium sidecar (`::local`, `BU_CDP_WS`) routing for `localhost`/`127.0.0.1`/RFC1918 targets.
- **Workstation CLI & Cloud API V4 SDK Ownership (`uv tool`)**: Install `browser-use` via `uv tool install --upgrade --force 'browser-use @ git+https://github.com/browser-use/browser-use.git'` at `~/.local/bin/browser-use` (tracking `0.13.13+` with `browser-use-sdk>=3.10.0,<4`, resolving `3.12.1+` and `browser_use_sdk.v4` without being downgraded by `uv tool upgrade`), declare `browser-use` in `platform/openspec-store/config/uv-tools.json`, and register `uv tool upgrade browser-use` in both `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` and its recorded mirror `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh` (keeping both copies byte-identical per `config/script-provenance-manifest.tsv`).
- **Canonical Agent Skills Adoption (`~/Developer/.agents/skills/`)**: Install the four high-value upstream skills (`browser-use`, `cloud`, `open-source`, `qa`) from `browser-use/browser-use` via `/opt/homebrew/bin/skills add` (excluding `x402` and redundant `remote-browser`, and prohibiting unmanaged `browser-use skill install`), fan them out via `config/{codex,claude,hermes}-user-skill-manifest.txt`, and verify snapshot and symlink integrity with `sync-workspace-agent-skills.py --accept-refresh`, `sync-workspace-agent-skills.py`, and `sync-workspace-agent-skills.py --check`.
- **Cloud Spend, Teardown & MCP Bloat Guardrails**: Enforce explicit cloud browser teardown (`PATCH /api/v4/browsers/{id}` `{"action":"stop"}` / `stop_remote_daemon`), default `proxyCountryCode: null` ($0.20/GB direct egress vs. $5.00/GB residential proxy when residential IP unblocking is not needed), per-run `maxCostUsd` caps on V4 runs, and exclusion of the 23-tool `browser-harness-mcp` / 16-tool `browser-use --mcp` stdio servers from `MCP Router` (`localhost:3282`).

### Non-Goals

- **No Replacement of Local OmniRoute or Bright Data Scraping Pipelines**: Single-page scraping, SERP queries, and 40+ structured platform pipelines remain on `brightdata` (`bdata`), `tvly`, and `exa`; local LLM inference for Python agents remains routed through local OmniRoute (`http://127.0.0.1:20128/v1`) at $0 orchestration markup.
- **No Unmanaged `browser-use skill install` Execution**: Never run `browser-use skill install`, which writes raw untracked `SKILL.md` files directly into `~/.claude/skills/`, `~/.codex/skills/`, and `~/.agents/skills/` and breaks `sync-workspace-agent-skills.py`.
- **No Local Browser MCP Schema Bloat in `MCP Router`**: Do not mount the 23-tool `browser-harness-mcp` or 16-tool `browser-use --mcp` stdio servers in `mcprouter.db`, preserving the 21-agent MCP tool budget and avoiding duplication with `chrome-devtools-mcp`.
- **No Deletion of Dormant Browserbase Credentials**: Existing `BROWSERBASE_*` keys in `~/.hermes/.env` and the `hermes-browserbase` spec remain preserved for rollback.

## Capabilities

### New Capabilities
- `browser-use-workstation-integration`: Governs shared-tier `BROWSER_USE_API_KEY` placement and value-blind verification, Hermes `browser-use` backend/cloud provider activation with hybrid local sidecar routing, `uv tool` ownership of `browser-use` + `browser-use-sdk` V4, canonical installation and user-scope fanout of the `browser-use`, `cloud`, `open-source`, and `qa` skills, and cloud browser cost/teardown/MCP guardrails.

### Modified Capabilities
<!-- None: existing hermes-browserbase, portable-workstation-toolchain, and ponytail-agent-skills specs remain canonically preserved without mutating existing requirement blocks. -->

## Impact

- **Planning & Governance Store (`~/Developer/platform/openspec-store` — central store root)**:
  - `config/uv-tools.json` (declares `browser-use` in the `uv-tools` layered profile alongside `graphifyy` and `tavily-cli`)
  - `config/codex-user-skill-manifest.txt`, `config/claude-user-skill-manifest.txt`, `config/hermes-user-skill-manifest.txt` (adds `browser-use`, `cloud`, `open-source`, `qa`)
  - `scripts/workstation-daily-update.sh` (synchronized byte-for-byte with `~/Developer/scripts/workstation-daily-update.sh` for Stage 7 provenance parity)
- **External Workstation & Workspace Surfaces (require operator-authorized apply phase)**:
  - `/Users/androidteam/.zshenv` (`0600`, `# BEGIN/END shared-agent-secrets` single-quote normalization for `BROWSER_USE_API_KEY`)
  - `/Users/androidteam/.hermes/config.yaml` (`0600`, `browser.backend` unset, `browser.cloud_provider: browser-use`)
  - `/Users/androidteam/.local/bin/browser-use` & `/Users/androidteam/.local/share/uv/tools/browser-use/` (`uv tool` environment tracking `browser-use` `0.13.13+` and `browser-use-sdk>=3.10.0,<4`, resolving `3.12.1+`)
  - `/Users/androidteam/Developer/.agents/skills/{browser-use,cloud,open-source,qa}/`, `~/Developer/skills-lock.json`, `~/Developer/.agents/skills-lock.json`, `~/Developer/.agents/.skill-snapshots/`, and user-scope symlinks under `~/.agents/skills/`, `~/.claude/skills/`, and `~/.hermes/skills/`
  - `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` (Stage 4 `uv tool upgrade browser-use`)
