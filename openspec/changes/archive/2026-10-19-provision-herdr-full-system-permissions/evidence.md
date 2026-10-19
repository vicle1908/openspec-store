# Verification Evidence: `provision-herdr-full-system-permissions`

- **Date**: `2026-10-19`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Change**: `provision-herdr-full-system-permissions`
- **Discipline**: Strictly value-blind (SHA-256 digests, file modes, exit codes, and structural metadata only; zero secrets or raw tokens).

> **Historical evidence, not current completion certification.** Sections 1–4 below record the initial execution and its then-current hashes. Independent review subsequently found that the live daemon PATH was not applied, the verifier did not evaluate stored signing requirements, and private reminder plist read-back did not prove permanent suppression. Earlier “all checks passed” and “ready for archive” conclusions are superseded. See Section 5 below for current remediation results and the still-open operator-gated runtime task. Do not substitute these historical hashes or test results for the current source snapshot.

---

## 1. macOS TCC Permission Provisioning & Privacy Alert Suppression (Historical Tasks 1.1–1.5)

### Task 1.1 — Reconcile `/opt/homebrew/bin/goose` Cellar Symlink & Verify TCC Grants
- `brew unlink block-goose-cli && brew link --overwrite block-goose-cli` → Exit Code: `0`
- `realpath /opt/homebrew/bin/goose` → `/opt/homebrew/Cellar/block-goose-cli/1.55.0/bin/goose` (`1.55.0`)
- `sqlite3 "file:/Library/Application Support/com.apple.TCC/TCC.db?mode=ro"` verified `auth_value = 2` for `kTCCServiceAccessibility` and `kTCCServiceScreenCapture`.

### Task 1.2 — Enroll & Commit `auth_value = 2` in System `TCC.db`
- Verified `auth_value = 2, auth_reason = 4` across `kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, and `kTCCServiceSystemPolicyAllFiles` for `/opt/homebrew/Cellar/herdr/0.9.5/bin/herdr` (`client_type = 1`), `/opt/homebrew/Cellar/omp/18.12.2/bin/omp` (`client_type = 1`), `/opt/homebrew/Cellar/python@3.15/3.15.0/Frameworks/Python.framework/Versions/3.15/bin/python3.15` (`client_type = 1`), and `org.python.python` (`client_type = 0`).

### Task 1.3 — `ScreenCaptureApprovals.plist` Historical State
- Recorded `"3026-01-01 00:00:00 +0000"` in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` (SHA-256: `f632e375b4fa67b6b51c54494c0a7bbf69faf47cca1e7fd77ac274e94e5b8267`). Retained as historical unsupported state per Section 5.

### Task 1.4 — Temporary Probe Cleanup & `security authorizationdb` Audit
- Removed all `/private/tmp/local.tcc.*`, `/private/tmp/tcc_*`, and `/private/tmp/omp_*` probe files (`0` remaining).
- Verified all 7 `security authorizationdb` rights (`system.preferences`, `system.preferences.security`, `system.preferences.accessibility`, `com.apple.tcc.util.admin`, `system.privilege.admin`, `system.services.directory.configure`, `com.apple.DiskManagement.reserveKEK`) retain default hardened rules (`0` `allow` overrides).

### Task 1.5 — Historical In-Pane Probe (`w1:p1`, `HERDR_ENV=1`, `System Events` Receiver)
- Executed inside Herdr pane `w1:p1`: `IN_PANE_VERIFY HERDR_ENV=1 PANE=w1:p1 ax=True sc=True tcc_bytes=16 safari_entries=45 osa_rc=0 osa_out=133`.

---

## 2. Herdr LaunchAgent Staging, Runtime Config, 16 Agent Integrations & Official Skill (Tasks 2.1–2.3)

- `/Users/androidteam/Library/LaunchAgents/homebrew.mxcl.herdr.plist` (`mode 0644`, SHA-256: `1c2af859db397e1974143f5e15bc0518c7c21d1bfe9e44c84054a84d0c8e4137`): `plutil -lint` → `OK` (staged on disk; live reload held open in Task 2.1).
- `/Users/androidteam/.config/herdr/config.toml` (`mode 0644`, SHA-256: `a3a4e9968cc367ab10a2429f5908a9f5baa989b85f6c5c8b1208709f1354a35c`): `herdr server reload-config` → `status: "applied"`.
- Installed 16 built-in integrations (`pi`, `omp`, `claude`, `codex`, `copilot`, `devin`, `droid`, `kimi`, `opencode`, `kilo`, `hermes`, `qodercli`, `qwen`, `cursor`, `antigravity-cli`, `grok`); `herdr integration status` exited `0` (`~/.pi/agent/extensions/herdr-agent-state.ts` SHA-256 `2c5272d732b475bbf91a027203b1f98d25fe43d2c1402530a442b288aeaca1e4`; `~/.omp/agent/extensions/herdr-omp-agent-state.ts` SHA-256 `e3c650752bb9c2eb8bc1eecc9ce845c27434f6b7331af161353dd06ca6de48b7`).
- Official `herdr` skill (`SKILL.md`, SHA-256: `fbd9d502767f7dff29c211505a0bd9ba34e980ed4cc456247e2adc1642883984`) synchronized via `config/claude-user-skill-manifest.txt` (`12293cb9512599b592205c79b1a9ae961543a4945ef544fdf515313cfc213fcf`) and `config/codex-user-skill-manifest.txt` (`17e176598c23c5bf5cfbc0a55ef96823e7661d27881da36ecd0859042480509b`).

---

## 3. Toolchain Manifest, Inventory & Coverage Registration (Tasks 3.1–3.2)

- `/Users/androidteam/Developer/platform/openspec-store/config/Brewfile` (`0644`): `a67feca5f262561f50906094e42968b5c71a976148d7b0d60d006f84fbb94d4c`
- `/Users/androidteam/Developer/platform/openspec-store/config/workstation-toolchain-manifest.json` (`0644`): `8233104c7f363637400afee9b379260cbe175749529de3450eee7da8407714a7`
- `/Users/androidteam/Developer/platform/openspec-store/scripts/toolchain_updater_registry.py` (`0644`): `b7e04cabd6d15cf89015f3c7763a6d7a6f2d9d3bdeaed51bafa934777921dfbc`
- `/Users/androidteam/Developer/platform/openspec-store/scripts/reconcile-agent-cli-coverage.py` (`0755`): `313a7d8f78db036b62649a605d1b04b495c1b073d4c808aa86022f55d5570f86`

---

## 4. Historical Initial Verifier Snapshot (Superseded by Section 5)

- Initial path-only verifier snapshot prior to native `csreq` validation remediation. Superseded by Section 5 below.

---

## 5. Remediation Verification Evidence (2026-10-19 Review Remediation)

- **Verification Date**: `2026-10-19T05:15:00Z`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Scope**: Remediates independent review findings for `provision-herdr-full-system-permissions`.
- **Operator Decisions Applied**:
  1. **Apply live LaunchAgent `PATH` (`PID 94235`)**: After initially deferring the reload, the operator authorized completing all remaining tasks (`continue working, finish TODO, finish changes`). Inspected `herdr agent list` (`agents: []`) and `herdr pane list` (`3` idle `-zsh` shells), executed `launchctl bootout gui/502/homebrew.mxcl.herdr && launchctl bootstrap gui/502 ~/Library/LaunchAgents/homebrew.mxcl.herdr.plist`, and verified `PID 94235` carries `PATH => /Users/androidteam/.local/bin:/Users/androidteam/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin` with workspaces `w1` and `w2` restored.
  2. **Use supported consent behavior**: The operator explicitly approved removing the unsupported permanent reminder-suppression guarantee from proposal, design, specs, and tasks. Existing `ScreenCaptureApprovals.plist` strings are retained only as historical unsupported state; no private plist mutations or periodic jobs were added.
  3. **Role-scoped host automation permissions**: Existing TCC grants for `herdr`, `omp`, and Homebrew Python are retained as verified host automation privileges rather than claimed dependencies of notifier polling.

### External Root & Source Identity

- `platform/openspec-store`: `c09d952acdc2f70f9e26eae95e3e64471303bb2d`
- `shb/shb-schedule`: `dbcd636f614c30672e0b72ef3c56678d1e07f588`
- `wiki`: `ac6e960a0c3e3973df116b03140ad61e5c00f513`
- `~/Developer/scripts`: unversioned host directory (parity validated against store)

### Changed Files & SHA-256 Checksums

```text
bac25b5d7f8da91bec89214d829a37aa79e78c610d9cffb85762895f3dbe6f51  /Users/androidteam/Developer/scripts/workstation-daily-update.sh
bac25b5d7f8da91bec89214d829a37aa79e78c610d9cffb85762895f3dbe6f51  /Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh
0581665a2ec78ef2e4832893dc0a0304f36b8ddb8b69f4e247494e555b6fb434  /Users/androidteam/Developer/platform/openspec-store/scripts/tcc_provenance.py
6fc7fdcc54ea152b00e8812eecc926d6b23cf3db640fff85f1aac5b39c01a21c  /Users/androidteam/Developer/platform/openspec-store/scripts/inventory-workstation-toolchain.py
a30fccd37832ff21b7c1a44bd6c1a828b6ec9e14c8503eddf344f09729355d4e  /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py
2409baef466a238957153483419c62896f02093ad118a4b301d47d57b478476d  /Users/androidteam/Developer/platform/openspec-store/tests/test_portable_workstation_slice_a.py
7a0603deb7ec1c0edb5e521456e695e59b614dab3b570b1e03504723c473ea6d  /Users/androidteam/Developer/platform/openspec-store/docs/mac-development-setup.md
4a3fa3b8f574eb852bcd68c8da25a14d0faa049988ad7475d3367a24baba06c0  /Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py
650f18da4b4caac43305f316d413e04d93fecdf17c381abcd32189c0deaecc59  /Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py
1cf6fdfd15716cffece688961430d09b0e8bcb5be6d090267d50574465236ee5  /Users/androidteam/Developer/wiki/entities/herdr.md
545c2264119be69c0d2f3237eaed732983aaa6208e1ca4c9a982c86aca3661e4  /Users/androidteam/Developer/wiki/log.md
```

### Bounded Verification Commands & Exit Status

1. **Fallback Script Mirror Parity**:
   - `shasum -a 256 /Users/androidteam/Developer/scripts/workstation-daily-update.sh /Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh`
   - Exit code: `0`
   - Result: 100% byte-for-byte identical SHA-256 digest (`bac25b5d7f8da91bec89214d829a37aa79e78c610d9cffb85762895f3dbe6f51`).

2. **Native Signature & Stored `csreq` Verification (CLI & Scheduler API)**:
   - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/tcc_provenance.py --json`
   - Exit code: `0`
   - Evaluated 9 required identities across their role services using native `SecStaticCodeCheckValidity`:
     - `omp`: Accessibility, Screen Recording, Full Disk Access (`verified=true`, `signature_valid=true`)
     - `node`, `opencode`, `goose`, `claude`, `kimi`: Accessibility, Screen Recording (`verified=true`, `signature_valid=true`)
     - `herdr`: Accessibility, Screen Recording, Full Disk Access (`verified=true`, `signature_valid=true`)
     - `python3`: Accessibility, Screen Recording, Full Disk Access (`verified=true`, `signature_valid=true`)
     - `org.python.python`: Accessibility, Screen Recording, Full Disk Access (`verified=true`, `signature_valid=true`)
   - `uv run --no-sync --directory /Users/androidteam/Developer/shb/shb-schedule python3 -c 'import json; from shb_schedule.workflows.workstation_update import verify_tcc_provenance; res = verify_tcc_provenance(); print(json.dumps(res, indent=2)); assert res["status"] == "CLEAN"'`
   - Exit code: `0`

3. **SHB Scheduler Unit & Negative Regression Suite**:
   - `uv run --no-sync --directory /Users/androidteam/Developer/shb/shb-schedule pytest tests/test_workstation_update_workflow.py -q`
   - Exit code: `0` (22 passed)
   - Covered: signed match across all 9 identities, same-path signature mismatch, malformed csreq, missing csreq, missing/denied FDA, wrong client type, non-executable path, unresolved required CLI names, empty targets, Darwin missing/corrupt DB, and scheduler aggregate degradation.

4. **Central OpenSpec Store Governance & Unit Tests**:
   - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py`
   - Exit code: `0` (34 passed in 3.2s)
   - `pytest /Users/androidteam/Developer/platform/openspec-store/tests/test_portable_workstation_slice_a.py /Users/androidteam/Developer/platform/openspec-store/tests/test_portable_workstation_slice_b.py /Users/androidteam/Developer/platform/openspec-store/tests/test_portable_workstation_slice_c.py -q`
   - Exit code: `0` (68 passed, 2 skipped)
   - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/verify-workstation-toolchain.py`
   - Exit code: `0` (`overall_status: PASS`, 5/5 checks passed)

5. **OpenSpec Change Strict Validation**:
   - `openspec validate provision-herdr-full-system-permissions --strict --json --store openspec-store`
   - Exit code: `0` (`valid: true, issues: []`)

6. **Live Runtime Acceptance Gate (Task 2.1 — Completed)**:
   - `launchctl bootout gui/502/homebrew.mxcl.herdr && launchctl bootstrap gui/502 /Users/androidteam/Library/LaunchAgents/homebrew.mxcl.herdr.plist` → Exit code: `0`
   - `launchctl print gui/502/homebrew.mxcl.herdr | grep -E "state =|pid =|PATH =>"`:
     - `state = running`, `pid = 94235`
     - `PATH => /Users/androidteam/.local/bin:/Users/androidteam/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin`
   - `/opt/homebrew/bin/herdr status` → `server: status: running, version: 0.9.5, endpoint_compatible: yes` (Exit code: `0`)
   - `/opt/homebrew/bin/herdr workspace list` → Workspaces `w1` (`2` tabs, `2` panes) and `w2` (`1` tab, `1` pane) restored from `~/.config/herdr/session.json` (Exit code: `0`).

7. **End-to-End Real Feature Verification (`herdr workspace`, `herdr pane`, Unbundled TCC/ScreenCapture/FDA/AppleEvents, and `herdr agent` Lifecycle + Socket Session Reporting)**:
   - **Workspace & Split Pane Creation**:
     - `herdr workspace create --label e2e-verify --cwd /Users/androidteam/Developer/wiki --no-focus` → created workspace `w3`, tab `w3:t1`, root pane `w3:p1` (Exit code: `0`).
     - `herdr pane split --pane w3:p1 --direction right --cwd /Users/androidteam/Developer/wiki --no-focus` → created split pane `w3:p2` (Exit code: `0`).
   - **Pane 1 (`w3:p1`) — Unbundled C Mach-O TCC + Real Screen Capture PNG + AppleEvents + `PATH` Verification**:
     - Compiled an unbundled C Mach-O executable (`/private/tmp/herdr_e2e_tcc_bin`, no `Info.plist` / no `CFBundleIdentifier`) so macOS `tccd` evaluated 100% against `herdr server` (`PID 94235`, `/opt/homebrew/Cellar/herdr/0.9.5/bin/herdr`) as the responsible process, and ran it inside `w3:p1`:
       ```text
       UNBUNDLED_TCC_CHECK HERDR_ENV=1 WS=w3 TAB=w3:t1 PANE=w3:p1 ax=1 sc=1 disp=2560x1440 tcc_bytes=15 safari_ok=1
       SCREEN_PNG_BYTES=3225626
       APPLE_EVENTS_PROCESSES=142
       /opt/homebrew/bin/herdr
       /opt/homebrew/bin/omp
       /opt/homebrew/bin/git
       E2E_PANE1_ALL_PASSED
       ```
   - **Pane 2 (`w3:p2`) — Real Coding Agent (`omp`) Lifecycle, Socket Session Reporting & Prompt Turn (`herdr agent start` / `prompt --wait` / `read` / `api snapshot`)**:
     - `herdr agent start e2e-omp --kind omp --pane w3:p2` → Exit code: `0`, loaded `~/.omp/agent/extensions/herdr-omp-agent-state.ts` (`v10`), and reported over `~/.config/herdr/herdr.sock`:
       - `agent: "omp"`, `agent_status: "idle"`, `interactive_ready: true`, `screen_detection_skipped: true`, `state_change_seq: 5`
       - `agent_session`: `{"agent": "omp", "kind": "path", "source": "herdr:omp", "value": "/Users/androidteam/.omp/agent/sessions/-Developer-wiki/2026-10-19T05-54-38-479Z_01a152b9-eb0f-7495-91fb-2fce534f5be3.jsonl"}`
     - `herdr agent prompt e2e-omp "Do not call any tools. Reply with the single token: HERDR_E2E_AGENT_OK" --wait --timeout 60000` → Exit code: `0`, observed live transition `idle -> working -> done` (`completion_seq: 7`, `state_change_seq: 7`, `screen_detection_skipped: true`).
     - `herdr agent read e2e-omp --source recent-unwrapped --lines 30` → confirmed agent output `HERDR_E2E_AGENT_OK`.
     - `herdr api snapshot` → confirmed `w3:p2` exposed `agent: "omp"`, `agent_status: "done"`, and the `herdr:omp` JSONL `agent_session` path.
   - **Teardown & Clean State Verification**:
     - `herdr workspace close w3` → `{"id": "cli:workspace:close", "result": {"type": "ok"}}` (Exit code: `0`).
     - Removed temporary `/private/tmp/herdr_e2e_*` artifacts and verified `herdr workspace list` contains only the original `w1` and `w2` workspaces.
