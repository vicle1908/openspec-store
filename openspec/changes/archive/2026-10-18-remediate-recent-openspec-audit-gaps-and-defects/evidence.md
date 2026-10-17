# Verification Evidence: `remediate-recent-openspec-audit-gaps-and-defects`

- **Date**: `2026-10-17`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Change**: `remediate-recent-openspec-audit-gaps-and-defects`
- **Discipline**: Strictly value-blind (SHA-256 digests, permissions, exit codes, and structural metadata only; zero secrets or raw tokens).

---

## 1. OmniRoute Muse Code Container Durability, Host CLI Bridge & Goose Wire Docs (Tasks 1.1–1.3)

### Task 1.1 — OmniRoute Container Entrypoint Compatibility & Clean Upstream Worktree
- **Clean Upstream Git Worktree**:
  - Reverted `/Users/androidteam/Omniroute/scripts/dev/peer-stamp.mjs` and `/Users/androidteam/Omniroute/open-sse/utils/sseHeartbeat.ts` to `HEAD`.
  - Command: `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no`
  - Exit Code: `0` (empty output; 0 modified tracked files).
- **Container Entrypoint Wrapper & Compose Override**:
  - `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (`mode 0755`, SHA-256: `4e4fdbe012b87e9fc181e389828bcdd3f52d65b192c6d3f42ea10f492b8a69bf`)
  - `/Users/androidteam/Omniroute/docker-compose.override.yml` (SHA-256: `f49e26176deb3b1fffd0f41f84e016e1b54db19c16a6a22686e673770024f395`)
  - `/Users/androidteam/Omniroute/scripts/update.sh` (SHA-256: `6f94da47f5d7299cd538fb9543160d29184b368535e2964d5cee059353114b66`)
- **Full Container Recreation & Live Smoke Proof**:
  - Command: `cd /Users/androidteam/Omniroute && docker compose --profile base down && docker compose --profile base up -d` → Exit Code: `0` (container healthy).
  - `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:20128/v1/muse-code/models` → `200`
  - `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:20128/muse-code/models` → `200`
  - `muse exec --disable-approval --no-session-log "Reply with PONG"` → Exit Code: `0`, Output: `PONG`.

### Task 1.2 — Host CLI Bridge Loopback Normalization & Per-Invocation Ephemeral `DATA_DIR`
- **Target File**: `/Users/androidteam/.local/bin/omniroute` (`mode 0755`)
  - Pre-apply SHA-256: `4213493675fd60cad2497409429879e949b06203d6ae77b076da38fda182f8be`
  - Post-apply SHA-256: `25c33fef3739f5526c3a239e9dea4b4dc42faf88b50a7603f58c8976befd79e8`
- **Host Orphan SQLite Preservation (`/Users/androidteam/.omniroute/storage.sqlite`)**:
  - Pre-apply mtime: `1792031065` | SHA-256: `01102201746998b6e921966847720056febb965011883ce915c798bf6afcb0e1`
  - Post-apply mtime: `1792031065` | SHA-256: `01102201746998b6e921966847720056febb965011883ce915c798bf6afcb0e1` (unchanged)
- **Live Verification**:
  - `~/.local/bin/omniroute keys list --output json | jq '.keys | length'` → Exit Code: `0`, Output: `0`.
  - `ls -d /tmp/omniroute-cli-bridge* /var/folders/*/*/T/omniroute-cli-bridge* 2>/dev/null` → `0` leftover directories.

### Task 1.3 — 21 `cli-*` Skills Reference & Goose Wire Protocol Documentation
- **Updated Artifacts**:
  - `/Users/androidteam/Developer/docs/omniroute-agent-skills.md` (SHA-256: `da6adbdfe3645a1bc8190290d49c555231d68064d52997fa6fc027d48eff05c0`) — Added Section 4 covering all 21 `cli-*` skills (`cli-a2a`, `cli-backup-sync`, `cli-batches`, `cli-chat`, `cli-compression`, `cli-contexts`, `cli-cost-usage`, `cli-eval`, `cli-health`, `cli-keys`, `cli-mcp`, `cli-models`, `cli-plugins-skills`, `cli-policy-audit`, `cli-providers`, `cli-resilience`, `cli-routing`, `cli-serve`, `cli-setup`, `cli-skill-collector`, `cli-tunnel`).
  - `/Users/androidteam/Developer/wiki/entities/omniroute.md` (SHA-256: `84b4795dc7b7963c86e6f9242c931eab2004afce1c5320bafb834e16fe09db14`) — Updated line 76/91 to reflect active host CLI bridge governance (`~/.local/bin/omniroute`).
  - `/Users/androidteam/Developer/wiki/entities/goose.md` (SHA-256: `b4bb7b9c45818879b0bc463d6457f88dfda1c2ef75c369ff684e7e8c607e9e94`) — Updated line 20/23 to record `/v1/chat/completions` (`OPENAI_BASE_PATH: chat/completions`); `grep -c '/v1/responses' wiki/entities/goose.md` → `0`.

---

## 2. OMP Routing Reconciliation, Shell Startup Hardening & Kimi Toolchain Coverage (Tasks 2.1–2.3)

### Task 2.1 — OMP Role & Fallback-Chain Verification
- `/Users/androidteam/.omp/agent/config.yml` (`mode 0600`, SHA-256: `ee266cb3319c470c9688d191e67b9615447b6e8bff4fe04b7bead72fdf3cbfb2`): `modelRoles.default` and `modelRoles.smol` bound to `google-antigravity/gemini-4-argon`; `retry.fallbackChains['omniroute/gemini-4-argon']` bound to `['omniroute/gemini-3.8-flash-high', 'google-antigravity/gemini-3.8-flash:high']`.
- `/Users/androidteam/.omp/agent/models.yml` (`mode 0644`, SHA-256: `98798996502cba3ec18c81c3fe78647b7514eaf54ff5d3d34c1c87fb4f6141a4`): `gemini-4-argon` and `nx/gemini-4-argon` present under `providers.omniroute.models`.
- `omp models --json` → Exit Code: `0`, resolves both `google-antigravity/gemini-4-argon` and `omniroute/gemini-4-argon`.

### Task 2.2 — Interactive Zsh Startup Hardening & `AddressBookSourceSync` Suppression
- **Target File**: `/Users/androidteam/.zshrc` (`mode 0600`)
  - Backup: `/Users/androidteam/.zshrc.pre-cce-lazyload` (`mode 0600`, SHA-256: `661f2c6565c4170af7d8d057b05d4ed43843912c46a118411313f0bb65b078d2`)
  - Post-apply SHA-256: `1c77171e0d52480730d5dd9842d94f1014b0e49711d427a8cce034e8a237f1fa`
- **Verification**:
  - `zsh -n /Users/androidteam/.zshrc` → Exit Code: `0`.
  - 5-run timing (`TERM=xterm-256color /usr/bin/time -p zsh -i -c exit`): `160ms`, `120ms`, `110ms`, `130ms`, `120ms` → **Median `120ms`** (`< 200ms` target; down from `860ms`).
  - `launchctl disable gui/502/com.apple.AddressBook.SourceSync` + killed runaway PID `32709`/`84144`; `ps aux | grep AddressBookSourceSync` → `0` active processes.

### Task 2.3 — Kimi Code Coverage in Fallback Shell Runner & Toolchain Inventory
- **Target Files**:
  - `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` (SHA-256: `8d3eac4bfc2c7a160f23154f05a98864867a2edcc72308b10b86ee2f54c86925`)
  - `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh` (SHA-256: `8d3eac4bfc2c7a160f23154f05a98864867a2edcc72308b10b86ee2f54c86925` — 100% byte-for-byte mirror parity)
  - `/Users/androidteam/Developer/platform/openspec-store/scripts/inventory-workstation-toolchain.py` (SHA-256: `db66ad14af3a64e46e7320129813672038e6c16ea1c54d684c88343a88f67319`)
- **Verification**:
  - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/inventory-workstation-toolchain.py` → `kimi -> authority: vendor_download (writer: kimi, verb: 'kimi update', dispatch: native) [CLEAN]`; `Unknown Tools: 0`.
  - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py` → `Ran 26 tests in 1.593s — OK` (Exit Code: `0`).

---

## 3. Workstation TCC Post-Upgrade Provenance & Hermes CUA Driver Persistence (Tasks 3.1–3.3)

### Task 3.1 — Active Mach-O Realpath Enrollment in `TCC.db` & `replayd` Suppression
- **Enrolled Active Mach-O Realpaths (`auth_value = 2` in `kTCCServiceAccessibility` and `kTCCServiceScreenCapture`)**:
  ```text
  kTCCServiceAccessibility|/Users/androidteam/.kimi-code/bin/kimi|2
  kTCCServiceScreenCapture|/Users/androidteam/.kimi-code/bin/kimi|2
  kTCCServiceAccessibility|/Users/androidteam/.local/share/claude/versions/2.1.302|2
  kTCCServiceScreenCapture|/Users/androidteam/.local/share/claude/versions/2.1.302|2
  kTCCServiceAccessibility|/opt/homebrew/Cellar/block-goose-cli/1.55.0/bin/goose|2
  kTCCServiceScreenCapture|/opt/homebrew/Cellar/block-goose-cli/1.55.0/bin/goose|2
  kTCCServiceAccessibility|/opt/homebrew/Cellar/node/26.12.0/bin/node|2
  kTCCServiceScreenCapture|/opt/homebrew/Cellar/node/26.12.0/bin/node|2
  kTCCServiceAccessibility|/opt/homebrew/Cellar/omp/18.11.3/bin/omp|2
  kTCCServiceScreenCapture|/opt/homebrew/Cellar/omp/18.11.3/bin/omp|2
  kTCCServiceAccessibility|/opt/homebrew/Cellar/opencode/1.19.3/bin/opencode|2
  kTCCServiceScreenCapture|/opt/homebrew/Cellar/opencode/1.19.3/bin/opencode|2
  ```
- **ScreenCaptureKit Reminder Suppression**:
  - Updated `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` so all client entries carry `kScreenCapturePrivacyHintDate = "3026-01-01 00:00:00 +0000"` and `kScreenCaptureApprovalLastAlerted = "3026-01-01 00:00:00 +0000"`.

### Task 3.2 — Post-Upgrade TCC Provenance Verification in `shb-schedule` & `workstation-daily-update.sh`
- **Target Files**:
  - `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (SHA-256: `11a6b06374b11c288eb6d746fcb1fa8008926b8064da0fadd4879f5b24017003`)
  - `/Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py` (SHA-256: `b47ba058cba3e43555c6ea16bbedfb4fc2f677fe60873ada74165cd0e267e68f`)
- **Live & Unit Test Verification**:
  - Live `verify_tcc_provenance()` output:
    `{'status': 'CLEAN', 'verified_binaries': ['/opt/homebrew/Cellar/omp/18.11.3/bin/omp', '/opt/homebrew/Cellar/node/26.12.0/bin/node', '/opt/homebrew/Cellar/opencode/1.19.3/bin/opencode', '/opt/homebrew/Cellar/block-goose-cli/1.55.0/bin/goose', '/Users/androidteam/.local/share/claude/versions/2.1.302', '/Users/androidteam/.kimi-code/bin/kimi'], 'missing_binaries': []}`
  - `uv run --no-sync --directory /Users/androidteam/Developer/shb/shb-schedule pytest -q` → `98 passed in 109.60s` (Exit Code: `0`).

### Task 3.3 — Hermes CUA Driver Persistence
- `/Users/androidteam/.hermes/.env` (`mode 0600`, SHA-256: `2b756fe735fdc16d2abb1f5c7900ba72a5af12d88ec43e1fc28e3015911af2b9`)
- `/Users/androidteam/.zshenv` (`mode 0600`, SHA-256: `c22d4efca930947db9670d18f58704a74e058c14b7f6d7d58dfe2c1d102e1132`)
- `zsh -c 'echo $HERMES_CUA_DRIVER_CMD'` → `/Applications/CuaDriver.app/Contents/MacOS/cua-driver` (`cua-driver 0.28.2`).

---

## 4. SHB Scheduler Container Trigger Guard (Task 4.1)

- **Target Files**:
  - `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/server/health.py` (SHA-256: `13fdc7292c3a4a4817fe52bea94c7a9638b9f6ca3e921e4c0f72242bbef2483e`)
  - `/Users/androidteam/Developer/shb/shb-schedule/tests/test_server.py` (SHA-256: `62456fb8bf4cc35e11451c3bea85b57433b25eeeed3b45780d87eedb1684bae3`)
- **Verification**:
  - `GET /scheduler/schedules` and `GET /scheduler/schedules/{name}` expose `execution_target` and `persisted` fields.
  - `POST /scheduler/schedules/{name}/trigger` returns HTTP `409 Conflict` (`{"persisted": false, "triggered": false}`) when `should_persist(manifest)` is `False`.
  - `uv run --no-sync --directory /Users/androidteam/Developer/shb/shb-schedule pytest -q` → `98 passed` (Exit Code: `0`).

---

## 5. Temporal Go Microservices Heartbeating, Validator & Toolchain Pin Parity (Tasks 5.1–5.3)

- **Modified Files & SHA-256 Digests (`/Users/androidteam/Developer/platform/go-microservices`)**:
  - `services/order-service/internal/adapters/temporal/workflow.go`: `393cbb25a3d223d973ceb4e7c2ff23808ed33dc6c3edb3d3683b340be0a51017`
  - `services/order-service/internal/adapters/temporal/activities.go`: `2fd643716caabc5f2a5142a8be65203a4c366e98905b871973bf5fdb308e48c5`
  - `services/inventory-service/internal/adapters/temporal/workflow.go`: `6fca4dc32cdbdf8efc880d18117b011a9921ad483914ddd952aaa642270910eb`
  - `services/inventory-service/internal/adapters/temporal/activities.go`: `1f00de983536e39f73f51a533a4b864ca143a0000a29928ce7aa8dd4d96cb8c9`
  - `services/reporting-service/internal/adapters/temporal/worker.go`: `fa0dd8a65b07d44a75b6c965206c708981ab25c523bc9f86d2a1feb37da2b148`
  - `services/reporting-service/internal/application/orchestration/rollup_activity.go`: `1b904499cf498619cf0677fbde9fdedd0ff3c6d8bcfb0b8da52f74ff40612b67`
  - `scripts/validate-temporal-inventory.rb`: `f3d6160c8899093aba86613684952d295af63a5ea1d23b25b0876888a4c87c15`
  - `services/catalog-service/verification/tools.env`: `4d207f1d5a1e3767e3cd64cee9e0128d795d367196f643e29f7cccced163b997`
  - `services/notification-service/verification/tools.env`: `a1c255a853188930b4935162d8f0789c96ba3c3295528b073192a463647b9441`
  - `tests/platform/go.mod`: `3bea670d289be5b3415d9d14287cf462cc7b0c950a7dc760ad4b4712b3194882`
  - `verification/fixtures/temporal-determinism/nondeterministic/go.mod`: `52c5d598ad041dcfeba3a81b3044650bbbfea4542f28c5a2185f2f54a0ca185d`
- **Verification**:
  - `go test ./...` in `services/order-service` → `23 packages ok` (Exit Code: `0`).
  - `go test ./...` in `services/inventory-service` → `11 packages ok` (Exit Code: `0`).
  - `go test ./...` in `services/reporting-service` → `17 packages ok` (Exit Code: `0`).
  - `ruby scripts/validate-temporal-inventory.rb --self-test` → `5 negative controls passed`, `valid (8 services, 9 task queues)` (Exit Code: `0`).
  - `bash scripts/verify-go-modules.sh --root . --manifest verification/go-module-roots.txt` → `18/18 passed, 0 failed` (Exit Code: `0`).
  - `bash scripts/test-temporal-determinism-negative.sh` → `both gates rejected the negative controls` (Exit Code: `0`).

---

## 6. OpenSpec Store Archive Readiness Gate & Forward Archive Reconciliation Ledger (Tasks 6.1–6.2)

### Task 6.1 — Range Audit Date-Cutover Enforcement in `validate-archive-readiness.py`
- **Target Files**:
  - `/Users/androidteam/Developer/platform/openspec-store/scripts/validate-archive-readiness.py` (SHA-256: `6e89b48841f8b2302ba4da5daf1ffb7b8b02d320bb7038b47b6dfba1a7faf437`)
  - `/Users/androidteam/Developer/platform/openspec-store/tests/test_validate_archive_readiness.py` (SHA-256: `df3bceffcc1ebf88fa8830c3f7dbe5608823ea03413b62c7f7e2f1a9e5be3a74`)
- **Verification**:
  - `uv run --directory /Users/androidteam/Developer/platform/openspec-store pytest tests/test_validate_archive_readiness.py` → `8 passed in 0.04s` (Exit Code: `0`).
  - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/validate-archive-readiness.py --range HEAD~10..HEAD` → `Range audit PASSED: all newly archived changes satisfy readiness criteria.` (Exit Code: `0`).

### Task 6.2 — Forward Verification Ledger for Pre-Gate Archives (`openspec/changes/archive/` Untouched)
Per `cleanup-archive-verification` Requirement `Immutable archive history is preserved` and `Scenario: Forward reconciliation of scheduling archives missing evidence.md`:
- `git -C /Users/androidteam/Developer/platform/openspec-store diff --name-only HEAD -- openspec/changes/archive` → **empty (`0` files modified in `openspec/changes/archive/`)**.
- Forward verification records for historical archives audited in this change:
  - `2026-10-15-align-temporal-go-microservices-patterns`: Remediated forward via Tasks `5.1`–`5.3` (`order-service`, `inventory-service`, `reporting-service` heartbeats, `validate-temporal-inventory.rb`, and `tools.env`/`go.mod` parity).
  - `2026-10-15-harden-terminal-and-shell-resilience`: Remediated forward via Task `2.2` (`~/.zshrc` `cce` lazy-load achieving `120ms` median startup and `AddressBookSourceSync` disablement).
  - `2026-10-15-workstation-tcc-permission-provisioning`: Remediated forward via Tasks `3.1`–`3.3` (active Mach-O realpath enrollment in `TCC.db` with `auth_value = 2`, `verify_tcc_provenance()`, and `HERMES_CUA_DRIVER_CMD`).
  - `2026-10-15-introduce-omniroute-cli-bridge` & `2026-10-15-standardize-goose-omniroute-runtime`: Remediated forward via Tasks `1.2`–`1.3` (`~/.local/bin/omniroute` per-invocation `fs.mkdtempSync` cleanup + `127.0.0.1` normalization, 21 `cli-*` skill recipes in `docs/omniroute-agent-skills.md`, and `/v1/chat/completions` attribution in `wiki/entities/goose.md`).
  - `2026-10-17-onboard-muse-code-cli-with-omniroute-combo`: Remediated forward via Task `1.1` (compose-mounted `container-entrypoint-compat.sh` surviving `docker compose down/up` and clean `~/Omniroute` git worktree).
