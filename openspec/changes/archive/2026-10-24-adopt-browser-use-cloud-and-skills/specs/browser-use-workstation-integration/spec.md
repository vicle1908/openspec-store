# browser-use-workstation-integration Specification

## Purpose

Defines the workstation-wide integration contract for Browser Use Cloud (API V4 and CDP Browser Infrastructure), the `browser-use` CLI (`uv tool`), Hermes Agent's native `browser-use` backend and hybrid routing, and the official `browser-use/browser-use` Agent Skills across `/Users/androidteam/Developer`.

## ADDED Requirements

### Requirement: Shared-Tier Credential Storage and Value-Blind Verification

The workstation SHALL store `BROWSER_USE_API_KEY` exclusively in `/Users/androidteam/.zshenv` (`0600`) inside the `# BEGIN shared-agent-secrets` ... `# END shared-agent-secrets` block and MUST verify account readiness using value-blind probes that never emit raw or masked secret substrings.

#### Scenario: Shared secret file permissions and single-source-of-truth placement
- **WHEN** `BROWSER_USE_API_KEY` is configured on the workstation
- **THEN** `/Users/androidteam/.zshenv` SHALL have mode `0600` (`stat -L -f '%04Lp' ~/.zshenv`) and export `BROWSER_USE_API_KEY` inside the `# BEGIN shared-agent-secrets` block
- **AND** `BROWSER_USE_API_KEY` MUST NOT be duplicated in `~/.hermes/.env`, `~/.omp/agent/.env`, `~/.tdt/.env`, `~/.shb/.env`, or any repository `.env` file

#### Scenario: Value-blind account and profile readiness probe succeeds
- **WHEN** a readiness check queries `GET /api/v2/billing/account` and `GET /api/v4/profiles` on `https://api.browser-use.com` using `X-Browser-Use-API-Key` from `~/.zshenv`
- **THEN** the probe SHALL emit only status codes, `projectId`, `concurrentSessionLimit`, `activeSessionCount`, `totalCreditsBalanceUsd`, `isFreeTier`, and profile counts
- **AND** raw key strings, prefixes, or masked substrings MUST NOT appear in output, logs, or evidence

#### Scenario: Missing or unauthorized credential fails closed
- **WHEN** `BROWSER_USE_API_KEY` is absent or `GET https://api.browser-use.com/api/v2/billing/account` returns HTTP `401` or `403`
- **THEN** the verification check SHALL exit non-zero and report an authentication failure without exposing header payloads

### Requirement: Hermes Native Browser Use Mode and Hybrid Local Routing

Hermes Agent (`/Users/androidteam/.hermes/config.yaml`) SHALL omit `browser.backend` (removing `backend: false`) and set `browser.cloud_provider: browser-use` so public web automation executes via Hermes's bundled `browser-harness` (`browser_exec` with `BU_AUTOSPAWN="1"`) while private and loopback URLs route automatically to the local Chromium sidecar (`::local`).

#### Scenario: Public URLs enable Browser Use CLI mode and BU_AUTOSPAWN
- **WHEN** `~/.hermes/config.yaml` omits `browser.backend` and sets `browser.cloud_provider: browser-use` with `BROWSER_USE_API_KEY` present in `~/.zshenv`
- **THEN** `BrowserUseBrowserProvider().is_available()`, `is_browser_use_cli_mode()`, and `is_legacy_browser_use_cloud_config()` SHALL all evaluate to `True`
- **AND** `browser-harness auth status` SHALL report `"status": "authenticated"` with `"source": "env"`

#### Scenario: Private and loopback URLs route to local Chromium sidecar
- **WHEN** `browser_exec` evaluates code referencing `localhost`, `127.0.0.1`, or an RFC1918 address while `browser.allow_private_urls` is `true` and `BROWSER_USE_API_KEY` is present
- **THEN** Hermes SHALL route execution to the local Chromium sidecar (`_code_url_verdict` returning `blocked=None` and `local_sidecar=True` vs `local_sidecar=False` for public URLs)
- **AND** `_resolve_backend_cdp` SHALL export `BU_CDP_WS` for the local sidecar so `browser_harness` suppresses cloud autospawn

#### Scenario: Dormant Browserbase credentials remain preserved for rollback
- **WHEN** Hermes transitions to `browser.cloud_provider: browser-use` with `browser.backend` omitted
- **THEN** existing `BROWSERBASE_*` entries in `~/.hermes/.env` (`0600`) SHALL remain untouched to permit immediate rollback

### Requirement: Single-Owner uv Toolchain Authority for browser-use CLI and V4 SDK

The workstation SHALL install the `browser-use` CLI via `uv tool` (`uv tool install --upgrade --force 'browser-use @ git+https://github.com/browser-use/browser-use.git'`) at `~/.local/bin/browser-use` (backed by `~/.local/share/uv/tools/browser-use`) with `browser-use-sdk>=3.12.1` (`browser_use_sdk.v4`) and SHALL declare `browser-use` in `platform/openspec-store/config/uv-tools.json`.

#### Scenario: Declarative uv-tools profile registration without manifest drift
- **WHEN** `browser-use` is registered in `platform/openspec-store`
- **THEN** `config/uv-tools.json` SHALL include `browser-use` under `tools[]` alongside `graphifyy` and `tavily-cli`
- **AND** `config/workstation-toolchain-manifest.json` SHALL NOT add an unaligned `owner: "uv"` entry that would trigger false drift in `inventory-workstation-toolchain.py`

#### Scenario: CLI entrypoint and Cloud API V4 SDK import verification
- **WHEN** `~/.local/bin/browser-use --version` and `~/.local/share/uv/tools/browser-use/bin/python -c "from browser_use_sdk.v4 import BrowserUse"` are executed
- **THEN** both commands SHALL exit with status code `0`
- **AND** `browser-use auth status` SHALL report `"status": "authenticated"` from the `~/.zshenv` environment variable

#### Scenario: Daily maintenance script and recorded store mirror remain byte-identical
- **WHEN** `~/Developer/scripts/workstation-daily-update.sh` Stage 4 adds `uv tool upgrade browser-use`
- **THEN** `platform/openspec-store/scripts/workstation-daily-update.sh` SHALL be updated to match the exact SHA-256 digest of `~/Developer/scripts/workstation-daily-update.sh`
- **AND** `test-version-authority-governance.py` SHALL pass mirror parity verification with exit code `0`

### Requirement: Canonical Browser Use Agent Skills Installation and Multi-Agent Fanout

The workspace SHALL install the four official `browser-use/browser-use` skills (`browser-use`, `cloud`, `open-source`, `qa`) under `~/Developer/.agents/skills/` via `/opt/homebrew/bin/skills add` and SHALL synchronize user-scope symlinks through `sync-workspace-agent-skills.py` without running `browser-use skill install`.

#### Scenario: Canonical installation of selected skills without unmanaged file writes
- **WHEN** `/opt/homebrew/bin/skills add browser-use/browser-use --skill browser-use cloud open-source qa --agent universal claude-code hermes-agent -y` runs in `/Users/androidteam/Developer`
- **THEN** `~/Developer/.agents/skills/` SHALL contain `browser-use`, `cloud`, `open-source`, and `qa`, each with an unmodified uppercase `SKILL.md` whose YAML `description` is <= 1,024 UTF-8 bytes
- **AND** `remote-browser` and `x402` SHALL NOT be installed, and `browser-use skill install` MUST NOT be run

#### Scenario: User-scope manifest fanout and snapshot acceptance pass cleanly
- **WHEN** the 4 skills are added to `config/{codex,claude,hermes}-user-skill-manifest.txt` and `sync-workspace-agent-skills.py` runs with `--accept-refresh`, default sync, then `--check` in sequence
- **THEN** `sync-workspace-agent-skills.py --check` SHALL exit `0` with `malformed_entries=0`, `surface_violations=0`, `conflicts=0`, `broken=0`, and `snapshot_check=ok`
- **AND** `~/.agents/skills/<name>`, `~/.claude/skills/<name>`, and `~/.hermes/skills/<name>` for all 4 skills SHALL resolve as symlinks to `~/Developer/.agents/skills/<name>`

#### Scenario: Idempotent upstream skill refresh
- **WHEN** `/opt/homebrew/bin/skills update browser-use cloud open-source qa -y` executes in `/Users/androidteam/Developer`
- **THEN** the command SHALL exit with status code `0` and emit zero `Multiple current paths match` warnings

### Requirement: Cloud Spend, Explicit Browser Teardown, and MCP Surface Guardrails

All workstation and agent integrations with Browser Use Cloud MUST enforce explicit browser session termination, default to direct egress (`proxyCountryCode: null`) when residential IP unblocking is unnecessary, and preserve the 21-agent MCP Router tool budget by excluding local `browser-harness-mcp` and `browser-use --mcp` stdio servers.

#### Scenario: Explicit stop terminates Cloud Browser billing
- **WHEN** a Cloud Browser session is created via `POST /api/v4/browsers` (`client.browsers.create(proxy_country_code=None)`) or `start_remote_daemon` and attached over `BU_CDP_URL` / `BU_CDP_WS`
- **THEN** the caller MUST stop the browser via `PATCH /api/v4/browsers/{id}` `{"action": "stop"}` (`client.browsers.stop(id)` or `stop_remote_daemon`) in a `finally` block instead of relying on CDP disconnect
- **AND** `GET /api/v2/billing/account` SHALL report `activeSessionCount: 0` after teardown

#### Scenario: Free-tier model and proxy cost guardrails
- **WHEN** a Cloud Browser or V4 Agent run is invoked on a Free-Tier project (`isFreeTier: true`) or without geo-unblocking requirements
- **THEN** browser settings SHALL pass `proxyCountryCode: null` ($0.20/GB direct egress instead of $5.00/GB residential proxy) unless residential IP unblocking is required
- **AND** V4 Agent runs (`POST /api/v4/runs`) SHALL specify an eligible model (default `gpt-6-luna`) and a bounded `maxCostUsd` cap

#### Scenario: MCP Router excludes duplicate local browser stdio servers
- **WHEN** `~/Library/Application Support/MCP Router/mcprouter.db` active servers are audited
- **THEN** neither the 23-tool `browser-harness-mcp` nor the 16-tool `browser-use --mcp` stdio server SHALL be registered in `mcprouter.db`
- **AND** coding agents SHALL invoke Browser Use via the `browser-use` CLI/skills or Hermes `browser_exec` while retaining `chrome-devtools-mcp` for local DevTools inspection
