# Verification Evidence: `persist-agent-tcc-provenance-and-auto-upgrade`

- **Date**: `2026-10-24`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Change**: `persist-agent-tcc-provenance-and-auto-upgrade`
- **Discipline**: Strictly value-blind (SHA-256 digests, permissions, exit codes, and structural metadata only; zero secrets or raw tokens).

---

## 1. Local Code-Signing Authority, Symlink Alignment & 9-Identity TCC Provenance (Tasks 2.1–2.3)

- **Code-Signing Authority**:
  - `CN=Developer Agent Code Signing`, SHA-1 leaf anchor `H"65340d85afd298131c682d8463087891292a2b59"` trusted in `~/Library/Keychains/login.keychain-db`.
- **`goose` Cellar Symlink & Code Signing**:
  - `brew unlink block-goose-cli && brew link --overwrite block-goose-cli` → `/opt/homebrew/bin/goose -> ../Cellar/block-goose-cli/1.56.0/bin/goose`.
  - Signed `/opt/homebrew/Cellar/block-goose-cli/1.56.0/bin/goose` (`--identifier com.block.goose`), `/opt/homebrew/Cellar/python@3.15/3.15.0_1/Frameworks/Python.framework/Versions/3.15/Resources/Python.app` (`--identifier org.python.python --deep`, after verifying `Contents/Info.plist` `CFBundleIdentifier = org.python.python`), and `/opt/homebrew/Cellar/python@3.15/3.15.0_1/Frameworks/Python.framework/Versions/3.15/bin/python3.15` (`--identifier org.python.python3`) with `Developer Agent Code Signing`.
- **9-Identity Native `SecStaticCodeCheckValidity` Verification (`python3 scripts/tcc_provenance.py --json`, strictly read-only `mode=ro`)**:
  - Exit Code: `0` (`"status": "CLEAN"`, `"missing_binaries": []`, `"errors": []`).
  - Verified identities (`9/9`):
    - `/opt/homebrew/Cellar/omp/18.12.6/bin/omp` (`Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`)
    - `/opt/homebrew/Cellar/node/26.12.1/bin/node` (`Accessibility`, `ScreenCapture`)
    - `/opt/homebrew/Cellar/opencode/1.19.4/bin/opencode` (`Accessibility`, `ScreenCapture`)
    - `/opt/homebrew/Cellar/block-goose-cli/1.56.0/bin/goose` (`Accessibility`, `ScreenCapture`)
    - `/Users/androidteam/.local/share/claude/versions/2.1.310` (`Accessibility`, `ScreenCapture`)
    - `/Users/androidteam/.kimi-code/bin/kimi` (`Accessibility`, `ScreenCapture`)
    - `/opt/homebrew/Cellar/herdr/0.9.5/bin/herdr` (`Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`)
    - `/opt/homebrew/Cellar/python@3.15/3.15.0_1/Frameworks/Python.framework/Versions/3.15/bin/python3.15` (`Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`)
    - `org.python.python` (`/opt/homebrew/Cellar/python@3.15/3.15.0_1/Frameworks/Python.framework/Versions/3.15/Resources/Python.app`: `Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`)

---

## 2. Workspace Skill Surface Pruning & Snapshot Manifest Refresh (Tasks 3.1–3.2)

- **Target File**: `/Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` (SHA-256: `45f74c0c275bd5a5bcff01cde9dff621ba0516a41c001670b183a6ea74d5d7bb`)
- **Verification**:
  - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --bootstrap-snapshot` → `bootstrap_snapshot=ok` (Exit Code: `0`).
  - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` → `malformed_entries=0`, `snapshot_check=ok`, `0` `surface_violations` (Exit Code: `0`).
  - `"description_raw_bytes"` count in `.agents/.skill-snapshots/{current,previous}/manifest.json` → `0` in both files.
  - **End-to-End Pruning Smoke Test (Default Mode & `--accept-refresh`)**: Created unallowlisted `/Users/androidteam/Developer/data/skills/_default_mode_probe/SKILL.md` and `/Users/androidteam/Developer/agent/skills/_default_mode_probe/SKILL.md`, ran `python3 scripts/sync-workspace-agent-skills.py` (default mode, no flags), verified both unallowlisted directories were automatically pruned (`not (ws / "data/skills").exists()` and `not (ws / "agent").exists()`), and confirmed subsequent `--check` exited `0`.

---

## 3. Dual-Runner Post-Upgrade Signing, `data/skills` Pruning, Single-Pass Stage 9 Reconciliation & `Python.app` LaunchAgent Supervision (Tasks 4.1–4.3)

- **Changed Files & SHA-256 Digests**:
  ```text
  60b9ce65aa088e61014b01326c5a2da8d3986f7ffe2382ea3a9ea2a06d3cb8f9  /Users/androidteam/Developer/scripts/workstation-daily-update.sh
  60b9ce65aa088e61014b01326c5a2da8d3986f7ffe2382ea3a9ea2a06d3cb8f9  /Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh
  fd2d8b313fc9688703e595f23245c1bf14d7b40004ab947725baa1fc597ea4e3  /Users/androidteam/Developer/platform/openspec-store/scripts/inventory-workstation-toolchain.py
  45f74c0c275bd5a5bcff01cde9dff621ba0516a41c001670b183a6ea74d5d7bb  /Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py
  8a96d1725bc7404e22e6690b9e2d98a01c59477ff800b2909281517f2b050563  /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py
  c689bd96af8f482fb534cb33ebc1f2ae3db3bbdf7547765ffa3b751c63d58fa9  /Users/androidteam/Developer/platform/openspec-store/pyproject.toml
  848bb7eaa15c87ba32be75e38e73bcb02a5cd3de9e8e8a5b3af3168c92f87010  /Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py
  6a46244679dc5fba28b00ce16beaac61f7d21396854be53be202fc345d66eadb  /Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py
  eaad46d78c355ffc7146131e9f58e80df203dc8b1b80b9e5ad444f3f307a1712  /Users/androidteam/Developer/tdt/tdt-core/pyproject.toml
  aafe65fc24cecef20be80d23e5df8ab0ff93921df997fd1a0f252d96ac153bbd  /Users/androidteam/Developer/ai-tooling/workspace-python-template/pyproject.toml
  9b40024df19987af0166e52f36624a233abc0a2f647cc807dd9556f7827941ef  /Users/androidteam/Developer/ai-tooling/wiki-mcp-server/pyproject.toml
  9209695647ac0242ee3b310e288986245216b60eb07901c8d69eca9197014a3b  /Users/androidteam/Library/LaunchAgents/com.developer.workstation-daily-update.plist
  ```
- **End-to-End Runtime Feature Verification**:
  - **LaunchAgent `Python.app` (`org.python.python`) Execution under `launchd` (`gui/502`)**:
    - `plutil -lint ~/Library/LaunchAgents/com.developer.workstation-daily-update.plist` → `OK` (`ProgramArguments[0] = "/opt/homebrew/opt/python@3.15/Frameworks/Python.framework/Versions/3.15/Resources/Python.app/Contents/MacOS/Python"`).
    - **Full Live LaunchAgent Daily Update Trigger (`launchctl kickstart -k gui/502/com.developer.workstation-daily-update`, `MODE=apply`)**:
      - Completed in `174.924s` with `last exit code = 0` (`Execution completed successfully: workflow=workstation-daily-update status=SUCCESS`).
      - Persisted `/Users/androidteam/Developer/data/updates/2026-10-24.json` (`timestamp: "2026-10-24T10:45:57.790338+00:00"`, `status: "SUCCESS"`, `errors: []`):
        - `preflight.status`: `"SUCCESS"`
        - `homebrew.status`: `"SUCCESS"` (`errors: []`)
        - `mas.status`: `"SUCCESS"` (`updated: ["Telegram 2 (747648890)"]`, `errors: []`)
        - `bun.status`: `"SUCCESS"` (`errors: []`)
        - `uv_tools.status`: `"SUCCESS"` (`tools_updated: ["browser-use", "graphifyy", "infinity-emb", "tavily-cli"]`, `errors: []`)
        - `npm.status`: `"SUCCESS"` (`errors: []`)
        - `agent_clis.status`: `"SUCCESS"` (`errors: []`)
        - `skills.status`: `"SUCCESS"` (`drift: 13`, `refreshed: 13`, `already_current: 51`, `failed: 0`, `parity_valid: true`, `errors: []`, `data/skills` pruned automatically)
        - `integrity.status`: `"SUCCESS"` (`script_drift: false`, `openspec_valid: true`, `tcc_provenance.status: "CLEAN"` with all `9/9` binaries verified under `launchd`, `snapshot_growth.status: "SUCCESS"`, `agent_cli_coverage.status: "SUCCESS"`, `errors: []`)
  - **Live macOS TCC Runtime Feature Probes (`ScreenCapture`, `Accessibility`, `SystemPolicyAllFiles`)**:
    - Executed `CGDisplayCreateImage(CGMainDisplayID())`, `AXIsProcessTrusted()`, and `sqlite3.connect('file:/Library/Application Support/com.apple.TCC/TCC.db?mode=ro', uri=True)` under both `/opt/homebrew/Cellar/python@3.15/3.15.0_1/Frameworks/Python.framework/Versions/3.15/bin/python3.15` and `Python.app/Contents/MacOS/Python`:
      - `captured_screen_dimensions`: `"5120x2880"` (`display_id: 1`)
      - `ax_trusted`: `true`
      - `fda_tcc_authorized_rows`: `297` (`14` rows across sampled target identities)
    - `orca computer permissions --json` → `accessibility: "granted"`, `screenshots: "granted"`.

---

## 4. `uv` Python `3.14.9` Standardization, Legacy Python Cleanup & `pyproject.toml` / `uv.lock` Verification (Tasks 6.1–6.4)

- **`uv` Managed Python & `uv tool` Alignment**:
  - `uv python upgrade` → Installed and linked `cpython-3.14.9-macos-aarch64-none` (`/Users/androidteam/.local/share/uv/python/cpython-3.14-macos-aarch64-none/bin/python3.14`).
  - `uv tool install --reinstall --python 3.14 tavily-cli` → All 4 installed `uv` tools (`browser-use`, `graphifyy`, `infinity-emb`, `tavily-cli`) resolve to `/Users/androidteam/.local/share/uv/python/cpython-3.14.9-macos-aarch64-none/bin/python3.14`.
  - Uninstalled unused `uv` Python `3.11`/`3.12` (`rm -f ~/.local/bin/python3.11`) and zero-dependent Homebrew legacy Python formulae (`brew uninstall python@3.10 python@3.11 python@3.12`).
  - `python3 scripts/inventory-workstation-toolchain.py --json` → `manifest_reconciliation`: `{"status": "aligned", "obsolete_candidate_count": 0, "reconciled_authority_status": "reconciled"}`.
- **`pyproject.toml` Clean-Break `>=3.14` & `uv lock --check` Across All 35 Workspace Repositories**:
  - Updated `pyproject.toml` (`requires-python = ">=3.14"`, `[tool.uv]` with `python-preference = "only-managed"` and `package = false` on non-package repos) and ran `uv lock --upgrade && uv sync` across `platform/openspec-store` (`ruff 0.17.2`, `pluggy 1.7.0`, `iniconfig 2.3.1`), `shb/shb-schedule` (`ruff 0.17.2`, `coverage 7.17.0`, `certifi 2026.10.23`), `tdt/tdt-core` (`dbos 3.3.0`, `fastapi 0.162.0`, `pydantic 2.14.1`, `ruff 0.17.2`, `mypy 2.4.0`), `ai-tooling/workspace-python-template`, and `ai-tooling/wiki-mcp-server` (`pydantic 2.14.1`, `starlette 1.9.0`).
  - `uv lock --check` across all 35 workspace `pyproject.toml` repositories → `35/35` passed (`0` failed).
- **Test Suites & Unmasked `workstation-daily-update.sh --check`**:
  - `uv run --directory ~/Developer/platform/openspec-store pytest tests/test_portable_workstation_slice_a.py tests/test_portable_workstation_slice_b.py tests/test_portable_workstation_slice_c.py scripts/test-version-authority-governance.py -q` → `105 passed, 2 skipped in 17.85s` (Exit Code: `0`).
  - `uv run --directory ~/Developer/shb/shb-schedule pytest tests/test_workstation_update_workflow.py -q` → `42 passed in 44.75s` (Exit Code: `0`).
  - `uv run --directory ~/Developer/tdt/tdt-core pytest -q` → `564 passed, 6 skipped` (Exit Code: `0`).
  - Unmasked `bash /Users/androidteam/Developer/scripts/workstation-daily-update.sh --check` → Exit Code: `0` (`Complete [MODE=check]`, `SCRIPT_DRIFT=0`, `TCC_DRIFT=0` `9/9` verified, `Reconciled Authority Status: RECONCILED`, `obsolete_candidate_count: 0`).
  - Verified all 7 `security authorizationdb` rights retain default `authenticate-user = true` rules (`0` `allow` overrides).
