# Proposal

## Why

Several OpenSpec changes archived between 2026-10-15 and 2026-10-17 introduced implementation drift, ephemeral runtime hotfixes that do not survive container or package-manager lifecycles, unfulfilled task checkboxes, and internal specification contradictions that must be remediated forward without mutating immutable archive directories. Closing these verified gaps restores end-to-end alignment between canonical specifications in `platform/openspec-store` and live code, scripts, and workstation configurations across OmniRoute, OMP, SHB Scheduler, Go Microservices, and macOS toolchain governance.

## What Changes

- **Durable OmniRoute Muse Code Compatibility & Clean Upstream Worktree (`omniroute-agent-cli-routing`)**:
  - Replace the ephemeral in-container writable-layer hotfix (`Gate 4b` in `~/Omniroute/scripts/update.sh` and uncommitted edits to tracked `~/Omniroute/scripts/dev/peer-stamp.mjs` and `~/Omniroute/open-sse/utils/sseHeartbeat.ts`) with a compose-mounted startup/override mechanism in `~/Omniroute/docker-compose.override.yml` so the `/muse-code` URL rewrite and non-null `resp_keepalive` ID survive `docker-service.sh stop|restart|drain` and `omniroute-watchdog.sh` container recreations while restoring `git -C ~/Omniroute status` to clean.
  - Reconcile the conflicting `Scenario: vendor bundle hotfix is prohibited` clause in `openspec/specs/omniroute-agent-cli-routing/spec.md` and correct Goose wire-protocol documentation (`wiki/entities/goose.md`) to reflect `/v1/chat/completions`.
- **OmniRoute Host CLI Bridge Per-Invocation Isolation & Documentation Parity (`omniroute-agent-skills`)**:
  - Update `~/.local/bin/omniroute` to create and clean up a unique per-invocation empty temporary `DATA_DIR` (`fs.mkdtempSync`) and normalize `localhost` to `127.0.0.1` as documented.
  - Restore the dropped `Scenario: Container unreachable fails closed without touching host SQLite` in `openspec/specs/omniroute-agent-skills/spec.md`, document the 21 `cli-*` skill subcommands in `docs/omniroute-agent-skills.md`, and remove stale deferral prose in `wiki/entities/omniroute.md`.
- **OMP Provider Routing Spec & Live Role Reconciliation (`omp-provider-routing`)**:
  - Reconcile `openspec/specs/omp-provider-routing/spec.md` with the live `~/.omp/agent/config.yml` `modelRoles.default` and `modelRoles.smol` assignments (`google-antigravity/gemini-4-argon` with `omniroute/gemini-4-argon` combo retained in `models.yml` and `retry.fallbackChains`), and retire superseded pre-OmniRoute clauses (`Scenario: no role points at OmniRoute`, `Scenario: no fallback chain references OmniRoute`).
- **Post-Upgrade TCC Provenance Reconciliation & Hermes CUA Driver Configuration (`workstation-remote-and-agent-permissions`)**:
  - Re-enroll active upgraded Mach-O CLI binaries (`omp`, `node` covering `pi`, `opencode`, `goose`, `claude`, `kimi`) in macOS `TCC.db` (`kTCCServiceAccessibility` and `kTCCServiceScreenCapture`) via SIP-compliant `launchctl` probes and System Settings AX commit, hook read-only TCC provenance verification into scheduled workstation maintenance, and persist `HERMES_CUA_DRIVER_CMD` for `/Applications/CuaDriver.app`.
- **Shell Startup Hardening, Kimi Fallback Coverage & Provenance Spec Alignment (`portable-workstation-toolchain`)**:
  - Complete the unapplied Task 2.3 from `2026-10-15-harden-terminal-and-shell-resilience` by deferring synchronous `cce` initialization (`__cce_apply_current_provider`) in `~/.zshrc` and disabling/throttling runaway `AddressBookSourceSync` launchd respawns so interactive `zsh -i -c exit` meets the `<200ms` latency target.
  - Add `kimi` (`~/.kimi-code/bin`) to the fallback shell runner (`~/Developer/scripts/workstation-daily-update.sh` and its store mirror) and `inventory-workstation-toolchain.py`.
  - Align `openspec/specs/portable-workstation-toolchain/spec.md` with the dynamic paired-file SHA-256 comparison used by `config/script-provenance-manifest.tsv` and the `"paused"` alert-suppression status in `workstation_update.py`.
- **SHB Scheduler Host-Target Trigger Guard (`shb-schedule-engine`)**:
  - Guard `POST /scheduler/schedules/{name}/trigger` and `GET /scheduler/schedules` in `shb/shb-schedule` (`src/shb_schedule/server/health.py`) with `execution_target` / `should_persist()` checks so triggering a host-only schedule (`workstation-daily-update`) on the Linux container returns a structured HTTP 409 Conflict response rather than calling `DBOS.trigger_schedule` on an unpersisted schedule (HTTP 500).
- **Temporal Go Microservices Heartbeating & Toolchain Pin Parity (`temporal-service-orchestration-alignment`)**:
  - Configure `HeartbeatTimeout`, `ctx.Err()` cancellation checks, and `if activity.IsActivity(ctx) { activity.RecordHeartbeat(ctx, ...) }` guards (preventing `getActivityOutboundInterceptor` panics on `context.Background()` unit tests) in `platform/go-microservices/services/order-service` (`StartToClose = 5m`), `inventory-service`, and `reporting-service`.
  - Update `platform/go-microservices/scripts/validate-temporal-inventory.rb` to resolve file-scoped duration constants per `MustSDKActivityOptions` block and fail when any activity with `StartToClose >= 60s` omits `Heartbeat:` or when `internal/adapters/temporal/` omits `activity.RecordHeartbeat` and `ctx.Err()` / `<-ctx.Done()`.
  - Align `TEMPORAL_CLI_VERSION=1.9.1` and `go.temporal.io/sdk v1.49.0` / `go.temporal.io/api v1.63.7` across `catalog-service/verification/tools.env`, `notification-service/verification/tools.env`, `tests/platform/go.mod`, and `verification/fixtures/temporal-determinism/nondeterministic/go.mod`.
- **Archive Readiness Range Gate Hardening (`cleanup-archive-verification`)**:
  - Update `platform/openspec-store/scripts/validate-archive-readiness.py` so `--range` git range audits enforce `.openspec.yaml` and non-empty `evidence.md` for changes archived after `2026-10-17` (while grandfathered pre-gate archives remain exempt) and align status codes and docstrings with `cleanup-archive-verification/spec.md`.

### Non-Goals

- Modifying, adding, deleting, or moving any file inside `platform/openspec-store/openspec/changes/archive/` (all historical archives remain strictly immutable).
- Implementing or modifying any TDT repository (`tdt/*`, including `tdt/agent-core`, `tdt/tdt-core`, `tdt/webhook-receiver`, and `tdt/ai-review`), which are actively developed under separate changes.
- Switching OmniRoute `/app/data` away from its named Docker volume `omniroute-data` or building a custom fork of the `diegosouzapw/omniroute` Docker Hub image.
- Exposing or logging raw API keys, OAuth tokens, or database credentials in any OpenSpec artifact or evidence file.

### Ownership Boundaries

- **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Owns `proposal.md`, `design.md`, `tasks.md`, `evidence.md`, canonical specs under `openspec/specs/`, and store governance scripts (`scripts/validate-archive-readiness.py`, `scripts/inventory-workstation-toolchain.py`, `scripts/workstation-daily-update.sh`). `openspec/changes/archive/` is strictly read-only.
- **External Implementation Roots (governed via explicit cross-root execution and verification gates)**:
  - `/Users/androidteam/Omniroute` (untracked `docker-compose.override.yml` and `scripts/update.sh`; tracked upstream files reverted to clean HEAD).
  - `/Users/androidteam/Developer/shb/shb-schedule` (scheduler trigger endpoint and reloader metadata).
  - `/Users/androidteam/Developer/platform/go-microservices` (Temporal activity heartbeating, Ruby validator, and `tools.env` / `go.mod` pins).
  - Workstation host surfaces (`~/.local/bin/omniroute`, `~/.zshrc`, `~/.omp/agent/config.yml`, `~/.hermes/`, `/Library/Application Support/com.apple.TCC/TCC.db`, `~/Developer/scripts/workstation-daily-update.sh`, `~/Developer/docs/omniroute-agent-skills.md`, `~/Developer/wiki/entities/{omniroute,goose}.md`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `omniroute-agent-cli-routing`: Replace ephemeral in-container bundle hotpatching with compose-durable mount/startup wiring, clean upstream `~/Omniroute` git status, reconcile the vendor bundle hotfix specification clause, and align Goose wire-protocol documentation.
- `omniroute-agent-skills`: Enforce per-invocation ephemeral `DATA_DIR` creation/cleanup and `127.0.0.1` loopback normalization in `~/.local/bin/omniroute`, restore the dropped unreachable-container scenario, and document all 21 `cli-*` skills in `docs/omniroute-agent-skills.md` and `wiki/entities/omniroute.md`.
- `omp-provider-routing`: Reconcile live `~/.omp/agent/config.yml` `modelRoles` (`default` and `smol`) with `omp-provider-routing/spec.md` and retire contradictory pre-OmniRoute prohibition clauses.
- `workstation-remote-and-agent-permissions`: Re-enroll upgraded Mach-O CLI binaries (`omp`, `node` covering `pi`, `opencode`, `goose`, `claude`) in `TCC.db`, add post-upgrade TCC provenance verification, and persist `HERMES_CUA_DRIVER_CMD`.
- `portable-workstation-toolchain`: Defer synchronous `cce` initialization in `~/.zshrc`, suppress `AddressBookSourceSync` CPU runaway, add `kimi` to the fallback shell updater and toolchain inventory, and align provenance manifest and `"paused"` alert specifications.
- `shb-schedule-engine`: Enforce `execution_target` / `should_persist()` guards on `POST /scheduler/schedules/{name}/trigger` and schedule listing in containerized runtimes.
- `temporal-service-orchestration-alignment`: Add `activity.IsActivity(ctx)`-guarded activity heartbeats and `ctx.Err()` checks in `order-service`, `inventory-service`, and `reporting-service`, enforce constant-aware `StartToClose >= 60s` heartbeat validation in `validate-temporal-inventory.rb`, and synchronize lagging `tools.env` and auxiliary `go.mod` pins.
- `cleanup-archive-verification`: Enforce `evidence.md` and `.openspec.yaml` on post-2026-10-17 archives during `--range` audits in `validate-archive-readiness.py` and align status reporting with the canonical spec.

## Impact

- **Repositories & Services**: `platform/openspec-store`, `platform/go-microservices`, `shb/shb-schedule`, `wiki`, `docs`, and `~/Omniroute`.
- **Workstation Runtime & Configs**: `~/.local/bin/omniroute`, `~/.zshrc`, `~/.omp/agent/config.yml`, `~/.hermes/.env`, `/Library/Application Support/com.apple.TCC/TCC.db`, and `~/Developer/scripts/workstation-daily-update.sh`.
- **Verification Gates**: `openspec validate --strict`, `pytest` across `openspec-store` and `shb-schedule`, `ruby scripts/validate-temporal-inventory.rb` + `go test` in `go-microservices`, and value-blind live workstation probes.
