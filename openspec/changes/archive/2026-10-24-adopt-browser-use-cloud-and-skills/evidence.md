# Verification Evidence: `adopt-browser-use-cloud-and-skills`

## 1. Task 1.1: Central Store `config/uv-tools.json` & Slice A Pytest

- **File Updated**: `/Users/androidteam/Developer/platform/openspec-store/config/uv-tools.json` (`L18-23`, `"package": "browser-use @ git+https://github.com/browser-use/browser-use.git"`, SHA-256 `a0368455b81df101d4f95b142183561b8a4cf3c52ba0c31f13201f5084b75909`) and `/Users/androidteam/Developer/platform/openspec-store/tests/test_portable_workstation_slice_a.py` (`L139`, `self.assertIn("browser-use", names)`).
- **`config/workstation-toolchain-manifest.json`**: Preserved unchanged (`0` drift in `inventory-workstation-toolchain.py`).
- **Test Execution**:
  ```bash
  uv run --directory /Users/androidteam/Developer/platform/openspec-store pytest /Users/androidteam/Developer/platform/openspec-store/tests/test_portable_workstation_slice_a.py
  # Result: 22 passed in 0.26s (exit code 0)
  ```

## 2. Tasks 2.1 & 2.2: Shared Secret Hygiene (`~/.zshenv`) & Value-Blind Cloud Readiness

- **`/Users/androidteam/.zshenv` (`L34`)**: Normalized `export BROWSER_USE_API_KEY='...'` to single quotes inside `# BEGIN shared-agent-secrets` ... `# END shared-agent-secrets`.
- **File Mode**: `stat -L -f '%04Lp' /Users/androidteam/.zshenv` → `0600`.
- **Value-Blind Secret Audit**:
  - `~/.zshenv`: `True` (value SHA-256 `aa79ba359f0122529d57e4a665090ab677aab6f11aac4793bd1be5129355c956`)
  - `~/.hermes/.env`: `False`
  - `~/.omp/agent/.env`: `False`
  - `~/.tdt/.env`: `False`
  - `~/.shb/.env`: `False`
  - `/Users/androidteam/Developer/**/.env*` (`126` files scanned): `False` (`0` matches)
- **Value-Blind Cloud Readiness Probe (`GET /api/v2/billing/account` & `GET /api/v4/profiles`)**:
  ```json
  {
    "billing_account_http_status": 200,
    "projectId": "fd09dc16-f32b-4b5d-bd64-84b85d984bca",
    "concurrentSessionLimit": 10,
    "activeSessionCount": 0,
    "totalCreditsBalanceUsd": 1.0,
    "isFreeTier": true,
    "profiles_http_status": 200,
    "profiles_totalItems": 1
  }
  ```

## 3. Tasks 3.1 & 3.2: Global `browser-use` CLI (`uv tool`), V4 SDK, and Daily Maintenance Mirror Parity

- **Pre-Install Collision Check**: `which browser-use browseruse bu browser browser-use-tui || true` returned empty (`0` collisions).
- **Installation**:
  ```bash
  uv tool install --upgrade --force 'browser-use @ git+https://github.com/browser-use/browser-use.git'
  ```
  - Installed `browser-use==0.13.13` (`@3df5806a0d097a1546d92c49bcf1b28c9972c3bd`), `browser-use-sdk==3.12.1`, `browser-harness==0.1.13` into `/Users/androidteam/.local/share/uv/tools/browser-use/`.
  - Exposed `/Users/androidteam/.local/bin/{browser-use,browseruse,bu,browser,browser-use-tui}`.
- **CLI & V4 SDK Verification**:
  - `/Users/androidteam/.local/bin/browser-use --version` → `0.1.13`
  - `/Users/androidteam/.local/bin/browser-use auth status` → `{"status": "authenticated", "source": "env", "path": "/Users/androidteam/.config/browser-harness/auth.json"}`
  - `/Users/androidteam/.local/share/uv/tools/browser-use/bin/python -c "import browser_use_sdk; from browser_use_sdk.v4 import BrowserUse; print(browser_use_sdk.__version__, BrowserUse)"` → `3.12.1 <class 'browser_use_sdk.v4.client.BrowserUse'>`
  - Post-`uv tool upgrade browser-use` check → `Nothing to upgrade`; `browser-use-sdk==3.12.1` and `browser_use_sdk.v4` retained via `uv-receipt.toml`.
- **Daily Maintenance Mirror Parity**:
  - Updated `/Users/androidteam/Developer/scripts/workstation-daily-update.sh:787` and `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh:787` (`uv tool upgrade browser-use 2>&1 || true`).
  - Both files have identical SHA-256: `ca84b0155a7445854bc776c445d6ef9dba9b6c8129762a233c2b60edfc1ac0e6`.
  - `bash -n /Users/androidteam/Developer/scripts/workstation-daily-update.sh` → `exit 0`.
  - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py` → `Ran 37 tests in 10.554s — OK` (`exit 0`).

## 4. Tasks 4.1 & 4.2: Hermes Native Browser Use Mode & Hybrid Local Routing

- **`/Users/androidteam/.hermes/config.yaml:256-261`** (`mode 0600`): Removed `backend: false` (leaving `browser.backend` omitted) and set `cloud_provider: browser-use` while preserving `allow_private_urls: true` and dormant `BROWSERBASE_*` keys in `~/.hermes/.env` (`mode 0600`, `4` keys preserved).
- **Hermes Runtime Verification (`/Users/androidteam/.hermes/hermes-agent/.venv/bin/python`)**:
  ```json
  {
    "provider_is_available": true,
    "is_browser_use_cli_mode": true,
    "is_legacy_browser_use_cloud_config": true,
    "local_url_verdict": [null, true],
    "public_url_verdict": [null, false]
  }
  ```

## 5. Tasks 5.1 & 5.2: Canonical Agent Skills, Fanout, MCP Router Audit & Live V4 Cloud Browser Smoke Test

- **Canonical Skill Installation**:
  ```bash
  /opt/homebrew/bin/skills add browser-use/browser-use --skill browser-use cloud open-source qa --agent universal claude-code hermes-agent -y
  ```
  - Verified `/Users/androidteam/Developer/.agents/skills/{browser-use,cloud,open-source,qa}/SKILL.md` present; `remote-browser` and `x402` absent.
- **Manifest Fanout & Snapshot Acceptance**:
  - Added `browser-use`, `cloud`, `open-source`, `qa` to `config/codex-user-skill-manifest.txt:76-80`, `config/claude-user-skill-manifest.txt:33-37`, and `config/hermes-user-skill-manifest.txt:10-14`.
  - `python3 .../sync-workspace-agent-skills.py --accept-refresh` → `accept_refresh=ok`
  - `python3 .../sync-workspace-agent-skills.py` → created 4 user-scope symlinks in each of `~/.agents/skills/`, `~/.claude/skills/`, and `~/.hermes/skills/`
  - `python3 .../sync-workspace-agent-skills.py --check` → `canonical_direct_roots=115 ... malformed_entries=0 ... snapshot_check=ok` (`exit 0`)
- **Live Hermes `browser_exec` Local Sidecar (`http://127.0.0.1:<port>/`) & Public Cloud (`BU_AUTOSPAWN="1"`) Smoke Tests**:
  - Local Loopback Sidecar (`::local`, `cleanup_browser` from `tools.browser_tool_lifecycle` + `stop_harness_daemons` from `tools.browser_use_cli`):
    ```json
    {"success": true, "exit_code": 0, "output": "{\"info\": {\"url\": \"http://127.0.0.1:49719/\", \"title\": \"\\ud83d\\udc34 Hermes Hybrid Local\", \"w\": 1280, \"h\": 577, \"sx\": 0, \"sy\": 0, \"pw\": 1280, \"ph\": 577}, \"h1\": \"Local Sidecar Active\"}\n", "workspace": "/Users/androidteam/.hermes/cache/browser-use/workspace/verify_cloud_task", "session": "verify_cloud"}
    ```
  - Public URL Cloud `BU_AUTOSPAWN="1"` (`new_tab("https://example.com")`, `page_info()`, `js()`, `cdp("Accessibility.getFullAXTree")`, `capture_screenshot()`, `stop_remote_daemon("verify_cloud3")`):
    ```json
    {"success": true, "exit_code": 0, "output": "{\"url\": \"https://example.com/\", \"title\": \"\\ud83d\\udc34 Example Domain\", \"body_snippet\": \"This domain is for use in documentation examples without needing permission. This is not a service; avoid relying on it \", \"ax_nodes\": 38, \"shot_exists\": true}\n", "workspace": "/Users/androidteam/.hermes/cache/browser-use/workspace/verify_cloud_task3", "session": "verify_cloud3"}
    ```
- **Idempotent Skill Update**:
  - `/opt/homebrew/bin/skills update browser-use cloud open-source qa -y` → `✓ All project skills are up to date` (`exit 0`, zero warnings).
- **MCP Router Audit (`~/Library/Application Support/MCP Router/mcprouter.db`)**:
  - Verified active servers (`19` rows total, `14` auto-start); neither `browser-harness-mcp` nor `browser-use --mcp` stdio server is registered.
- **Bounded 1-Minute Cloud Browser V4 Lifecycle Smoke Test (`POST /api/v4/browsers` + `BU_CDP_URL`)**:
  ```text
  Created V4 Cloud Browser session: 37ac7e1c-760f-47cd-a86e-fc5285cc0f55 status: BrowserSessionStatus.active cdp_url_scheme: https
  browser-use CDP page_info output: {'url': 'https://example.com/', 'title': '🐴 Example Domain', 'w': 1536, 'h': 643, 'sx': 0, 'sy': 0, 'pw': 1521, 'ph': 756}
  Stopped V4 Cloud Browser session: 37ac7e1c-760f-47cd-a86e-fc5285cc0f55 status: BrowserSessionStatus.stopped browser_cost: 0.0003333333333333333333333333332 proxy_cost: 0
  ```
- **Live Cloud API V4 Agent Run (`POST /api/v4/runs` with `output_schema`, `proxyCountryCode: None`, `max_cost_usd=0.05`)**:
  ```text
  Created V4 Run: 130b34fa-5940-428e-94dd-7024a33e492d session_id: a42ac3e8-cda6-4932-996e-ffbe8c4b3eb9 status: Status2.queued
  Completed V4 Run status: Status2.completed model: gpt-6-luna total_cost_usd: 0.003091
  V4 Structured Output (summary.output): {"heading": "No h1 found", "link_url": "https://iana.org/help/example-domains"}
  Explicitly stopped V4 session browser: 32677c65-5ec0-405e-9440-3868ee16a5ea status: BrowserSessionStatus.stopped
  V4 Session Cost breakdown: {"session_id":"a42ac3e8-cda6-4932-996e-ffbe8c4b3eb9","num_runs":1,"llm_cost_usd":"0.003091","search_cost_usd":"0.000000","browser_cost_usd":"0.000333","proxy_cost_usd":"0.000000","proxy_used_mb":"0.000000","total_cost_usd":"0.003424"}
  Post-test activeSessionCount: 0 totalCreditsBalanceUsd: 0.9946915431
  ```
