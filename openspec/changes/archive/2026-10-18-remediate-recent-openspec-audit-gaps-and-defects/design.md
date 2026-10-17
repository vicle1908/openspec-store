# Design

## Context

See `proposal.md - Why` for motivation. An audit of OpenSpec changes archived between `2026-10-15` and `2026-10-17` identified three structural failure modes across the workspace:

1. **Ephemeral Runtime Mutations vs. Lifecycle Recreations**:
   - `2026-10-17-onboard-muse-code-cli-with-omniroute-combo` patched `/app/peer-stamp.mjs` and `/app/.build/next/server/chunks/20286.js` inside the running `omniroute` container's writable layer via `Gate 4b` in `~/Omniroute/scripts/update.sh:185-224` and dirtied git-tracked `~/Omniroute/scripts/dev/peer-stamp.mjs` and `~/Omniroute/open-sse/utils/sseHeartbeat.ts`. However, `~/Developer/scripts/docker-service.sh:140,162` and `~/Developer/scripts/omniroute-watchdog.sh:46` recreate the container directly from `diegosouzapw/omniroute:latest` (`docker compose down` / `docker compose up -d`) without calling `update.sh`, wiping the writable layer.
   - `2026-10-15-workstation-tcc-permission-provisioning` enrolled versioned Homebrew Cellar realpaths in `/Library/Application Support/com.apple.TCC/TCC.db`; subsequent `brew upgrade` and `claude update` runs deleted old Cellar paths (`omp 18.11.0`, `node 26.11.1_1`, `opencode 1.19.0`, `goose 1.54.0`, `claude 2.1.300`) and left active binaries (`omp 18.11.3`, `node 26.12.0`, `opencode 1.19.3`, `goose`, `claude 2.1.302`) and `~/.pi/agent/bin/pi` without `TCC.db` entries.
2. **Incomplete Implementation of Checked Tasks**:
   - `2026-10-15-align-temporal-go-microservices-patterns` left `order-service` (`StartToClose = 5m` at `services/order-service/internal/adapters/temporal/workflow.go:15`) and `inventory-service` without `HeartbeatTimeout` or `activity.RecordHeartbeat(ctx)` because `scripts/validate-temporal-inventory.rb:197-200` only checked `RecordHeartbeat` if `Heartbeat:` was already present.
   - `2026-10-15-harden-terminal-and-shell-resilience` checked off Task 2.3 (`cce` deferral) without modifying `~/.zshrc:170-215`, where `__cce_apply_current_provider` still forks synchronously on every interactive shell start.
   - `2026-10-15-introduce-omniroute-cli-bridge` pinned a shared static `/tmp/omniroute-cli-bridge` directory in `~/.local/bin/omniroute:47-50` instead of a per-invocation temporary directory, left `localhost` unnormalized, and omitted the 21 `cli-*` skill recipes in `docs/omniroute-agent-skills.md`.
   - `2026-10-17-reconcile-scheduler-and-workstation-update-governance` left `POST /scheduler/schedules/{name}/trigger` in `shb/shb-schedule` unguarded for `execution_target: host` manifests on Linux containers.
3. **Append-Only Spec Contradictions & Range Audit Exemption**:
   - `openspec/specs/omniroute-agent-cli-routing/spec.md:112` prohibits Next.js bundle hotfixes in the same file that requires Muse Code compatibility (`:555-558`).
   - `openspec/specs/omp-provider-routing/spec.md:105-112` forbids `omniroute` in `modelRoles` and `fallbackChains` in the same file that mandates `omniroute/gemini-4-argon` (`:441-465`), while live `~/.omp/agent/config.yml:2,9` was updated on `2026-10-17` to `google-antigravity/gemini-4-argon`.
   - `scripts/validate-archive-readiness.py:135,146,219` passes `is_range_audit=True` for `--range`, bypassing `evidence.md` checks even for newly committed archives.

## Goals / Non-Goals

**Goals:**
- Make all runtime compatibility layers, TCC authorizations, and shell startup optimizations durable across `docker compose down/up`, `brew upgrade`, and `launchd` cycles.
- Eliminate every verified spec-vs-code discrepancy across `shb/shb-schedule`, `platform/go-microservices`, and `platform/openspec-store`.
- Preserve 100% immutability of `platform/openspec-store/openspec/changes/archive/` (`git diff --name-only HEAD -- openspec/changes/archive` MUST remain empty).

**Non-Goals:**
- Editing any file under `openspec/changes/archive/` or re-opening archived changes.
- Modifying any repository under `tdt/` (`tdt/agent-core`, `tdt/tdt-core`, `tdt/webhook-receiver`, `tdt/ai-review`) or implementing `agent-core-integrate-jev-system-one`.
- Modifying SQLite WAL volume persistence (`omniroute-data` or `shb_scheduler`).

## Decisions

### Decision 1: Compose-Mounted Startup Wrapper for OmniRoute Muse Code Compatibility
- **Choice**: Reuse the existing `~/Omniroute/docker-compose.override.yml` deployment infrastructure pattern (already used for Hub image pinning, Redis port reset, and `omniroute-data` named volume override) to mount an untracked startup wrapper script (`~/Omniroute/scripts/container-entrypoint-compat.sh`) that idempotently applies the `/muse-code` path rewrite in `/app/peer-stamp.mjs` and non-null `resp_keepalive` ID across `/app/.build/next/server/chunks/*.js` inside the container (running as `node` UID 1000) before `exec /app/check-permissions.sh "$@"` (which launches `node dev/run-standalone.mjs` -> `server-ws.mjs`) on every container start, and revert tracked `~/Omniroute/scripts/dev/peer-stamp.mjs` and `~/Omniroute/open-sse/utils/sseHeartbeat.ts` to `HEAD`.
- **Rationale**: `docker-service.sh` and `omniroute-watchdog.sh` run `docker compose --profile base up -d` from `~/Omniroute`, which always loads `docker-compose.override.yml`. Applying the idempotent compatibility shim in the container entrypoint guarantees survival across `docker compose down` and `up -d` without dirtying git-tracked upstream files or building a custom Docker image.
- **Alternatives Considered**: Calling `~/Omniroute/scripts/update.sh` from `docker-service.sh` and `omniroute-watchdog.sh` (rejected: `update.sh` performs image pulls and SQLite backups inappropriate for fast watchdog recovery).

### Decision 2: Per-Invocation `fs.mkdtempSync` with `process.on("exit")` Cleanup in `~/.local/bin/omniroute`
- **Choice**: Replace `path.join(os.tmpdir(), "omniroute-cli-bridge")` in `~/.local/bin/omniroute:47-50` with `fs.mkdtempSync(path.join(os.tmpdir(), "omniroute-cli-bridge-"))`, register idempotent cleanup (`fs.rmSync(ephemeralDir, { recursive: true, force: true })`) on `child.on("close")`, `child.on("error")`, `process.on("exit")`, `SIGINT`, `SIGTERM`, and `stdout` `EPIPE` (because `spawn()` at line 63 is asynchronous), remove any leftover `/tmp/omniroute-cli-bridge` directory, and replace `localhost` with `127.0.0.1` in `baseUrl`.
- **Rationale**: Satisfies `omniroute-agent-skills/spec.md` per-invocation empty `DATA_DIR` isolation and eliminates `/tmp` state accumulation across runs.
- **Alternatives Considered**: Deleting files inside a shared `/tmp/omniroute-cli-bridge` directory (rejected: race condition when concurrent subagents run `omniroute` CLI skills simultaneously).

### Decision 3: TCC Realpath Reconciliation Script Integrated into Workstation Maintenance
- **Choice**: Because SIP (`csrutil status: enabled`) prevents direct SQLite writes to `/Library/Application Support/com.apple.TCC/TCC.db` and `tccutil reset` only accepts bundle identifiers (`client_type = 0`), enroll the active upgraded Mach-O realpaths (`omp`, `node`, `opencode`, `goose`, `claude`, and `kimi`) into `kTCCServiceAccessibility` and `kTCCServiceScreenCapture` (`auth_value = 2`) using the SIP-compliant one-shot `launchctl bootstrap gui/502` probe + System Settings AX checkbox toggle (`skill://macos-tcc-permission-provisioning`) and refresh `ScreenCaptureApprovals.plist` to `3026-01-01`. Note that `~/.pi/agent/bin/pi` is a `#!/bin/sh` wrapper that `exec`s `node`, so `tccd` attributes its TCC provenance to `/bin/sh` and the resolved `node` Mach-O binary. Add a read-only `verify_tcc_provenance()` helper using Python stdlib `sqlite3` (`mode=ro`) called inside `step_integrity_and_store_validation()` in `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (preserving the 9-step workflow structure in `test_plain_workstation_update_workflow_aggregates_steps`) and in `~/Developer/scripts/workstation-daily-update.sh`. Also export `HERMES_CUA_DRIVER_CMD="/Applications/CuaDriver.app/Contents/MacOS/cua-driver"` in `~/.hermes/.env` and `~/.zshenv` (outside `# BEGIN/END shared-agent-secrets`).
- **Rationale**: Follows the established workstation maintenance pipeline pattern so future `brew upgrade` runs never leave CLI binaries without TCC provenance.
- **Alternatives Considered**: Replacing Homebrew symlinks with static wrapper binaries (rejected: violates Homebrew single-owner PATH authority in `portable-workstation-toolchain`).

### Decision 4: Lazy-Loaded `cce` Wrapper in `~/.zshrc` and `AddressBookSourceSync` Throttling
- **Choice**: Mirror the existing `_load_nvm()` lazy-load pattern in `~/.zshrc:101-114` for `cce`: remove the eager `__cce_apply_current_provider` call at `~/.zshrc:212` and instead populate static default environment variables or invoke `__cce_apply_current_provider` lazily on first `cce` / `claude` invocation. Disable/unload the runaway `com.apple.AddressBook.SourceSync` launchd agent when idle so interactive `zsh -i -c exit` runs in `<200ms`.
- **Rationale**: Reuses the exact lazy-load idiom already proven in `~/.zshrc` while preserving `cce use <provider>` interactive switching.

### Decision 5: Host-Target Guard on `shb-schedule` HTTP Control Plane
- **Choice**: In `shb/shb-schedule/src/shb_schedule/server/health.py:216-275`, include `execution_target` and `persisted: state.reconciler.should_persist(manifest)` in `GET /scheduler/schedules` and `GET /scheduler/schedules/{name}`, and in `POST /scheduler/schedules/{name}/trigger` check `if not state.reconciler.should_persist(resolved.manifest): return JSONResponse(status_code=409, ...)` before calling `DBOS.trigger_schedule(name)`.
- **Rationale**: Eliminates the HTTP 500 error when triggering a host-only schedule (`workstation-daily-update`) on the Linux container while keeping `shb-schedule` aligned with `shb-schedule-engine/spec.md`.

### Decision 6: Temporal Converse Heartbeat Validation and Service Activity Heartbeats
- **Choice**:
  - In `platform/go-microservices/scripts/validate-temporal-inventory.rb:197-205`, resolve file-scoped duration constants (such as `const activityStartToClose = 5 * time.Minute` in `order-service`) and inspect each `MustSDKActivityOptions` call block individually, requiring `Heartbeat:` whenever resolved `StartToClose >= 60s` and requiring both `activity.RecordHeartbeat` and `ctx.Err()` / `<-ctx.Done()` in the service's `internal/adapters/temporal/` Go files.
  - Add `Heartbeat: 30 * time.Second`, `if err := ctx.Err(); err != nil`, and `if activity.IsActivity(ctx) { activity.RecordHeartbeat(ctx, ...) }` (guarding against Temporal Go SDK panics when unit tests pass `context.Background()`) to `order-service` (`StartToClose = 5m`), `inventory-service`, and `reporting-service`, and synchronize `TEMPORAL_CLI_VERSION=1.9.1` and `go.temporal.io/sdk v1.49.0` / `go.temporal.io/api v1.63.7` (with `go mod tidy`) across all remaining `tools.env` and `go.mod` files.

### Decision 7: Date-Cutover Enforcement for `--range` Archive Audits in `validate-archive-readiness.py`
- **Choice**: In `platform/openspec-store/scripts/validate-archive-readiness.py`, parse the `<YYYY-MM-DD>-` date prefix of archived change directories during `audit_git_range()`. For archives dated `<= 2026-10-17`, keep historical grandfathering (`is_range_audit=True`); for archives dated `> 2026-10-17` (or undated), enforce `.openspec.yaml` (if present before archive) and non-empty `evidence.md` when `task_summary.total > 0`.

### Transaction Boundaries
- **TCC / SIP Boundary**: `TCC.db` mutations are performed exclusively by macOS `tccd` via `launchctl bootstrap gui/502` probes and System Settings AX interactions; automated verification opens `/Library/Application Support/com.apple.TCC/TCC.db` strictly read-only (`mode=ro`).
- **SHB Scheduler**: `POST /scheduler/schedules/{name}/trigger` performs the `should_persist(manifest)` check in-memory prior to opening any DBOS schedule trigger transaction.
- **Cross-Repo Git Commits**: Each repository (`~/Omniroute`, `shb/shb-schedule`, `platform/go-microservices`, `wiki`, `platform/openspec-store`) commits its changes atomically on its own branch before central OpenSpec archive sync.

## Risks / Trade-offs

- **[Risk] Compose-mounted entrypoint script for OmniRoute could fail if Next.js chunk filenames change in a future OmniRoute image upgrade** → Mitigation: Use a glob/pattern search across `/app/.build/next/server/chunks/*.js` in `container-entrypoint-compat.sh` with a fail-open warning log if upstream has already fixed the keepalive `id` field, and verify in `~/Omniroute/scripts/update.sh` Gate 4b.
- **[Risk] Modifying `~/.zshrc` or `~/.omp/agent/config.yml` could disrupt interactive terminal sessions** → Mitigation: Create timestamped pre-apply backups, validate syntax (`zsh -n ~/.zshrc`, `omp models --json`), and roll back immediately on any check failure.

## Migration Plan

1. Apply and test changes in external repositories (`shb/shb-schedule` and `platform/go-microservices`) and run their respective test suites.
2. Apply workstation runtime remediations (`~/Omniroute/docker-compose.override.yml` + `container-entrypoint-compat.sh`, `~/.local/bin/omniroute`, `~/.zshrc`, `TCC.db` provenance script, `~/.hermes/.env`, `workstation-daily-update.sh` + store mirror) with pre/post SHA-256 verification.
3. Update documentation (`docs/omniroute-agent-skills.md`, `wiki/entities/omniroute.md`, `wiki/entities/goose.md`) and store governance scripts (`scripts/validate-archive-readiness.py`, `scripts/inventory-workstation-toolchain.py`).
4. Record complete value-blind verification outputs in `evidence.md`, run `openspec validate remediate-recent-openspec-audit-gaps-and-defects --strict --json --store openspec-store`, and verify `git diff --name-only HEAD -- openspec/changes/archive` is empty.
- **Rollback**: Restore any host config file from its pre-apply backup; revert `docker-compose.override.yml` and run `docker compose --profile base up -d --force-recreate omniroute-base` in `~/Omniroute`; `git revert` per-repository commits if any regression occurs.
