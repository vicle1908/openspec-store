# Design

## Context

See `proposal.md` — Why, and `specs/browser-use-workstation-integration/spec.md` for normative requirements.

Live read-only verification against Browser Use Cloud (`https://api.browser-use.com`) and the workstation filesystem established the following baseline:
1. **Account & Credit State**: `BROWSER_USE_API_KEY` is present in `/Users/androidteam/.zshenv` (`0600`) inside `# BEGIN shared-agent-secrets` (currently double-quoted on line 34). In-process probing of `GET /api/v2/billing/account` and `GET /api/v4/profiles` returned HTTP `200` for project `Default Project` (`fd09dc16-f32b-4b5d-bd64-84b85d984bca`) with `$1.00 USD` balance (`isFreeTier: true`), `concurrentSessionLimit: 10`, `activeSessionCount: 0`, and 1 pre-created profile (`Personal Profile`, `5632534c-d795-4a43-984a-c7349f77b137`).
2. **Hermes Runtime State**: `/Users/androidteam/.hermes/hermes-agent/.venv` (Python 3.14.5) already bundles `browser-harness==0.1.13`, `cdp-use==1.4.5`, and `fetch-use==0.4.0`. With `BROWSER_USE_API_KEY` exported in the environment, `browser-harness auth status` reports `{"status": "authenticated", "source": "env"}` and `BrowserUseBrowserProvider().is_available()` returns `True`. However, `/Users/androidteam/.hermes/config.yaml` still has `browser.backend: false` and `browser.cloud_provider: browserbase` from `2026-08-12-enable-hermes-browserbase`.
3. **PyPI Version & Dependency Pin Constraint**: On PyPI, `browser-use==0.13.11` hard-pins `browser-use-sdk==3.4.2` (which predates the `browser_use_sdk.v4` module introduced in `browser-use-sdk>=3.10.0`), whereas `browser-use-sdk` on PyPI is at `3.12.1` and `browser-use` `main` (`0.13.13`) relaxes the constraint to `browser-use-sdk>=3.10.0,<4`.
4. **Skill & MCP Governance**: `browser-use/browser-use` ships 6 skills (`browser-use`, `cloud`, `open-source`, `qa`, `remote-browser`, `x402`). Running `browser-use skill install` directly writes unmanaged files into `~/.claude/skills/`, `~/.codex/skills/`, and `~/.agents/skills/`, violating `sync-workspace-agent-skills.py`.

## Goals / Non-Goals

**Goals:**
- Provide a zero-drift, single-owner installation of the `browser-use` CLI (`~/.local/bin/browser-use`) and `browser_use_sdk.v4` under `uv` authority.
- Enable Hermes's first-class `browser_exec` (`browser-harness`) + `BU_AUTOSPAWN` cloud browser workflow while guaranteeing that `localhost`/`127.0.0.1`/RFC1918 URLs route to the free local Chromium sidecar (`::local`).
- Expose `browser-use`, `cloud`, `open-source`, and `qa` skills across Claude Code, Codex, OMP, and Hermes via canonical `.agents/skills/` lockfile and snapshot governance.
- Protect the project's credit balance through explicit browser stop semantics, `proxyCountryCode: null` default guidance, and `maxCostUsd` run caps.

**Non-Goals:**
- Adding local stdio MCP servers (`browser-harness-mcp` or `browser-use --mcp`) to `MCP Router` (`mcprouter.db`).
- Routing local Python `browser-use` OSS `Agent` LLM calls through Browser Use Cloud's paid LLM proxy when local OmniRoute (`http://127.0.0.1:20128/v1`) is available at $0 orchestration markup.

## Decisions

### Decision 1: Hybrid Architecture (Cloud Stealth Browsers + Local OmniRoute / CLI 3.0)

```
+-----------------------------------------------------------------------------------+
|                WORKSTATION BROWSER USE INTEGRATION ARCHITECTURE                   |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  ~/.zshenv (0600, # BEGIN shared-agent-secrets)                                   |
|  export BROWSER_USE_API_KEY='...'                                                 |
|         |                                                                         |
|         +---------------------------+---------------------------+                 |
|         |                           |                           |                 |
|         v                           v                           v                 |
|  [Hermes Agent]              [Global uv Tool CLI]        [Shared Agent Skills]    |
|  ~/.hermes/config.yaml       ~/.local/bin/browser-use    ~/Developer/.agents/     |
|  backend: (omitted/default)  - browser-use==0.13.13+       skills/{browser-use,   |
|  cloud_provider: browser-use - browser-use-sdk>=3.12.1     cloud,open-source,qa}  |
|  - Public URL -> BU_AUTOSPAWN- Local Chrome CDP or       Fanned out via           |
|  - Private URL -> ::local      Cloud start_remote_daemon   sync-workspace-skills  |
+-----------------------------------------------------------------------------------+
```

- **Choice**: Use Browser Use Cloud primarily as an elastic **Stealth Browser Infrastructure (`POST /api/v4/browsers` / `start_remote_daemon`)** and selective **V4 Agent (`POST /api/v4/runs` with `gpt-6-luna`)** layer, while keeping coding-agent control on the **`browser-use` CLI 3.0 (`browser-harness`)** and local Python `Agent` LLM calls on **OmniRoute (`127.0.0.1:20128`)**.
- **Rationale**: At `$0.02/browser-hour` with `proxyCountryCode: null` (`$0.20/GB` direct egress), `$1.00` funds ~40–50 hours of stealth + auto-CAPTCHA browser compute with 10 concurrent sessions. By contrast, routing LLM tokens through Cloud BYOK incurs a 0.2× token orchestration fee and leaving `proxyCountryCode: "us"` enabled by default charges `$5.00/GB` (~$0.37 per 75 MB session).
- **Hermes `browser.backend` Omission Invariant (`tools/browser_use_cli.py:248, 528-530, 824`)**: In Hermes, setting **both** `browser.backend: "browser-use"` and `browser.cloud_provider: "browser-use"` causes `_resolve_backend_cdp()` (`L528-530`) to leave `BU_CDP_WS`/`BU_CDP_URL` unset on public URLs (expecting `BU_AUTOSPAWN=1`), while `is_legacy_browser_use_cloud_config()` (`L248`) returns `False` whenever `browser.backend` is truthy—leaving `BU_AUTOSPAWN` unset at `L824` and dropping `browser_harness` into local desktop Chrome discovery (`DevToolsActivePort`). By **omitting `browser.backend`** (removing `backend: false`) and setting **`browser.cloud_provider: browser-use`**, `is_browser_use_cli_mode()` (`L271`) and `is_legacy_browser_use_cloud_config()` (`L244`) both evaluate to `True`: public URLs export `BU_AUTOSPAWN="1"` (provisioning a Browser Use Cloud session via `start_remote_daemon(NAME)` at `browser_harness/run.py:394`), while private/loopback URLs (`localhost`/`127.0.0.1`/RFC1918) set `BU_CDP_WS` to Hermes's local headless `Google Chrome for Testing` sidecar (`::local`, `_local_default`), which suppresses `BU_AUTOSPAWN` (`not _explicit_cdp_configured()` at `run.py:390`).
- **Alternatives Considered**:
  - *Keep Hermes on Browserbase (`backend: false`)*: Rejected because Browserbase costs `$20/mo` + `$0.12/hr`, gates Verified Stealth behind Enterprise plans, and forced Hermes to disable `browser_exec`.
  - *Set explicit `browser.backend: browser-use` alongside `browser.cloud_provider: browser-use`*: Rejected because `is_legacy_browser_use_cloud_config()` returns `False` when `backend` is truthy (`tools/browser_use_cli.py:248`, pinned by `test_explicit_backend_does_not_set_bu_autospawn`), breaking `BU_AUTOSPAWN` on public URLs.
  - *Register 23-tool `browser-harness-mcp` in MCP Router*: Rejected because it duplicates `chrome-devtools-mcp` and adds 23 tool schemas to every turn across all 21 agents, whereas the `browser-use` CLI + skill costs 0 MCP schema tokens.
### Decision 2: Resolving the `browser-use==0.13.11` vs. `browser-use-sdk>=3.12.1` Pin Conflict

- **Choice**: Install `browser-use` via `uv tool install --upgrade --force 'browser-use @ git+https://github.com/browser-use/browser-use.git'` (creating `~/.local/share/uv/tools/browser-use` and linking `~/.local/bin/{browser-use,browseruse,bu,browser,browser-use-tui}`), and register `browser-use` in `config/uv-tools.json` (not in `config/workstation-toolchain-manifest.json`).
- **Rationale**: `browser-use==0.13.11` on PyPI hard-pins `browser-use-sdk==3.4.2`, which lacks `browser_use_sdk.v4`. If `browser-use-sdk` is upgraded manually with `uv pip install` inside a PyPI `0.13.11` tool venv, the next daily `uv tool upgrade browser-use` (`shb-schedule` `step_uv_tools_update` or `workstation-daily-update.sh`) re-locks against `0.13.11` metadata and downgrades `browser-use-sdk` back to `3.4.2`. By contrast, upstream `main` (`0.13.13`, recommended by `docs.browser-use.com/open-source/browser-use-cli.md`) already specifies `browser-use-sdk>=3.10.0,<4` in `pyproject.toml`, so `uv` records the git source in `uv-receipt.toml` and preserves `browser-use-sdk>=3.12.1` across all future `uv tool upgrade` runs. Additionally, `inventory-workstation-toolchain.py` (`reconcile_with_manifest`) has no `elif owner == "uv":` branch for symlinked `~/.local/share/uv/tools/*` binaries, so `uv tool` packages (`graphifyy`, `tavily-cli`, `browser-use`) belong exclusively in `config/uv-tools.json`.
- **Alternatives Considered**:
  - *Install `browser-use==0.13.11` from PyPI + manual `uv pip install --upgrade browser-use-sdk`*: Rejected because daily `uv tool upgrade browser-use` overwrites manual `uv pip` overrides back to `3.4.2`.

### Decision 3: Canonical Skill Selection (`browser-use`, `cloud`, `open-source`, `qa`)

- **Choice**: Install exactly 4 of the 6 skills from `browser-use/browser-use` (`browser-use`, `cloud`, `open-source`, `qa`) using `/opt/homebrew/bin/skills add browser-use/browser-use --skill browser-use cloud open-source qa --agent universal claude-code hermes-agent -y` from `/Users/androidteam/Developer`, and add all 4 slugs to `config/{codex,claude,hermes}-user-skill-manifest.txt`.
- **Rationale**:
  - `browser-use` covers CLI 3.0 local & remote daemon execution.
  - `cloud` provides 11 API V4/V3/V2 & SDK reference docs so agents use V4 endpoints and proper `stop` semantics.
  - `open-source` covers local Python `Agent`/`Browser`/`Tools` customization with custom LLMs (OmniRoute).
  - `qa` provides automated localhost-tunneled Cloud QA scoring.
  - `remote-browser` is a strict subset of `browser-use`, and `x402` is for keyless crypto wallets (unneeded since `BROWSER_USE_API_KEY` is configured).

## Risks / Trade-offs

- **[Risk] Unstopped Cloud Browsers Continue Billing (`$0.02/hr` + `keepAlive: 120s`)** → **Mitigation**: Enforce `try ... finally: client.browsers.stop(session.id)` / `PATCH /api/v4/browsers/{id}` `{"action":"stop"}` / `stop_remote_daemon("<name>")` in all smoke checks and skill workflows, and verify `activeSessionCount: 0` via `GET /api/v2/billing/account` after any cloud smoke test.
- **[Risk] Default Residential Proxy (`proxyCountryCode: "us"`) Drains `$1.00` Credit on Media-Heavy Sites (`$5.00/GB`)** → **Mitigation**: Pass `proxyCountryCode: null` (`None`) by default ($0.20/GB direct egress) and enable country-specific residential proxies only when target sites block datacenter IPs.
- **[Risk] `workstation-daily-update.sh` Mirror Provenance Drift in Stage 7** → **Mitigation**: `config/script-provenance-manifest.tsv` (line 21) is a 3-column TSV (`<executed_path>\t<recorded_path>\t<authority>`) with no hash column; Stage 7 (`detect_script_drift`), `shb-schedule` (`step_integrity_and_store_validation`), and `test-version-authority-governance.py` (`L591-601`) compute live SHA-256 digests on both `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` and `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh`. Whenever Stage 4 is edited to add `uv tool upgrade browser-use`, copy the file immediately to the store mirror so both digests remain identical.

## Migration Plan

1. **Central Store Declarations (`platform/openspec-store`)**:
   - Add `browser-use` to `config/uv-tools.json`.
2. **External Host & Workspace Execution (Apply Phase)**:
   - Normalize `export BROWSER_USE_API_KEY='...'` to single quotes in `~/.zshenv` (`0600`) and verify absence from `~/.hermes/.env`.
   - Verify no PATH collision for `browser-use`, `browseruse`, `bu`, `browser`, `browser-use-tui`, then install via `uv tool install --upgrade --force 'browser-use @ git+https://github.com/browser-use/browser-use.git'`.
   - Update `~/.hermes/config.yaml` (`0600`) to remove `browser.backend: false` (leaving `browser.backend` omitted) and set `browser.cloud_provider: browser-use`.
   - Install the 4 skills via `/opt/homebrew/bin/skills add` in `/Users/androidteam/Developer`, add the 4 slugs to `config/{codex,claude,hermes}-user-skill-manifest.txt`, run `sync-workspace-agent-skills.py --accept-refresh` and `sync-workspace-agent-skills.py`, and verify with `--check`.
   - Update `~/Developer/scripts/workstation-daily-update.sh` Stage 4 and synchronize its recorded mirror in `platform/openspec-store/scripts/workstation-daily-update.sh`.
3. **Rollback Strategy**:
   - Revert `~/.hermes/config.yaml` to `browser.backend: false` and `browser.cloud_provider: browserbase` (credentials in `~/.hermes/.env` remain intact).
   - Run `uv tool uninstall browser-use` and revert manifest entries in `platform/openspec-store`.
