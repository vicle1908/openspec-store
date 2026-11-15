# Proposal

## Why

Following archival of `2026-11-15-promote-gemini-4-hydrogen-fleet-default-with-flash-fallback`, four post-cutover defects remain on `iosteam-mac-mini`: banned Antigravity account `62af823b` (`vicgnome19094@gmail.com`) is still referenced across eight Argon/Carbon OmniRoute combos and OMP's `agent.db`, Hydrogen combos use `priority` instead of `quota-weighted` routing (compounding burst `429` disconnects in Codex CLI v0.169.0 alongside an unsupported `service_tier = "ultrafast"` config), live Pi `1.5.2` has drifted from `1.4.0`-pinned specs/docs, and `openspec-store`'s GitNexus index is stale after the archive commit.

Each defect was verified against official upstream documentation and live codebase/runtime state:
- **OmniRoute & Codex CLI (`openai/codex`, OpenAI Responses API, `~/Omniroute`)**: Official Codex source (`codex-rs/core/src/session/mod.rs`) confirms `service_tier = "ultrafast"` is unsupported on `gemini-4-hydrogen` and triggers `unsupported_service_tier_warning`, while `codex-rs/codex-api/src/sse/responses.rs` leaves `response.in_progress` unhandled and turns mid-stream `rate_limit_exceeded` errors (emitted after `withEarlyStreamKeepalive` commits HTTP `200` at `DEFAULT_THRESHOLD_MS = 1000` ms) into `stream closed before response.completed` disconnects and `95s+` retry backoffs. In OmniRoute (`open-sse/services/combo/strategyRegistry.ts`, `quotaStrategies.ts`, `antigravity429Guard.ts`), `priority` always hits `targets[0]` (`9c033d6f`) first, saturating a single account's Antigravity burst/TPM budget and tripping `AG_429_BUDGET` (`2`) + local refusal locks instead of distributing load across all 5 active WTU-Pro accounts via `quota-weighted`.
- **Banned Account Hygiene**: `62af823b` (`is_active = 0, test_status = 'banned'`) remains in `gemini-4-argon*` and `gemini-4-carbon*` (8 combos in `/app/data/storage.sqlite`) and active as `id = 3` (`vicgnome19094@gmail.com`) in `~/.omp/agent/agent.db`.
- **Pi `1.5.2` Drift**: Live Pi (`@earendil-works/pi-coding-agent` `1.5.2`) retains releases `1.5.1` and `1.5.2` (`~/.pi/agent/install/releases/`), while `pi-agent-harness-config/spec.md`, `wiki/entities/pi.md`, `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md`, and `lastChangelogVersion` in `~/.pi/agent/settings.json` still reference `1.4.0`.

## What Changes

- **OmniRoute Combo Cleanup & Strategy Alignment (`/app/data/storage.sqlite` via HTTP API)**:
  - Prune banned `62af823b` from all 8 remaining combos (`gemini-4-argon{,-high,-medium,-low}` and `gemini-4-carbon{,-high,-medium,-low}`), leaving the 2 active Ultra `agy` accounts (`0532bad4`, `338764b8`).
  - Switch `gemini-4-hydrogen-{xhigh,high,medium,low}` (and top-level `gemini-4-hydrogen` config) from `priority` to `quota-weighted` (matching `gemini-3.8-flash-high`, `gemini-4-argon*`, and `gemini-4-carbon*`) with `predictiveTtftMs: 0` across the 5 active WTU-Pro connections (`9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`), and clear resilience cooldowns.
- **OMP Auth Database Hygiene (`~/.omp/agent/agent.db`)**:
  - Prune banned `vicgnome19094@gmail.com` (`id = 3`) from `auth_credentials` (`provider = 'google-antigravity'`), leaving 5 active non-banned OAuth accounts (`id IN (2, 6, 10, 14, 15)`).
- **Codex CLI Config Alignment (`~/.codex/config.toml`)**:
  - Remove unsupported `service_tier = "ultrafast"` from `~/.codex/config.toml` (canonical default behavior per `openai/codex`), preserving `model = "gemini-4-hydrogen"`, `model_reasoning_effort = "high"`, and `stream_idle_timeout_ms >= 300000` default; verify zero `unsupported_service_tier_warning` diagnostics on `codex exec` and `HTTP 200` / `"pong"` protocol-level `/v1/responses` completions against `quota-weighted` `gemini-4-hydrogen`.
- **Pi `1.5.2` Release & Documentation Alignment**:
  - Update `lastChangelogVersion` to `"1.5.2"` in `~/.pi/agent/settings.json` (preserving `models.json` and `1.5.1`/`1.5.2` release layout or pruning superseded releases per policy — explicitly documenting `1.5.2` active + `N-1` `1.5.1` fallback).
  - Update `wiki/entities/pi.md` (+ Notion sync) and `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` from `1.4.0` to `1.5.2`.
- **Knowledge Index & Verification Hygiene**:
  - Verify `openspec-store` GitNexus index refresh (`refresh-knowledge-indexes.sh --repo /Users/androidteam/Developer/platform/openspec-store --force --trigger manual`), leaving unrelated uncommitted changes in `openspec-store` and `wiki` untouched.

### Non-Goals
- Do NOT modify OmniRoute container source code or fork `~/Omniroute` (`RESPONSES_TRANSPORT_KEEPALIVE_ENABLED` stays `"false"`, `DEFAULT_THRESHOLD_MS` stays `1000`).
- Do NOT alter `gemini-3.8-flash-high` fallback chains, OMP `modelRoles`, `~/.pi/agent/models.json`, or `macbook-pro-m5` remote configs.
- Do NOT commit, reset, or disturb another session's uncommitted files in `platform/openspec-store` (`scripts/knowledge-refresh/refresh-knowledge-indexes.sh`, `scripts/workstation-daily-update.sh`, `openspec/changes/standardize-uv-script-execution-and-toolchain-resilience/`) or `wiki` (`entities/tailscale.md`).
- Do NOT push git commits without explicit user approval.

### Ownership Boundaries
- **OmniRoute Gateway**: `/app/data/storage.sqlite` combos (`gemini-4-argon*`, `gemini-4-carbon*`, `gemini-4-hydrogen*`) via `http://127.0.0.1:20128/api/*`.
- **Workstation Host Configs**: `~/.omp/agent/agent.db`, `~/.codex/config.toml`, `~/.pi/agent/settings.json`, `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md`.
- **Knowledge & OpenSpec Stores**: `/Users/androidteam/Developer/wiki/entities/pi.md`, Notion (`sync-notion-knowledge.sh`), AgentMemory mesh (`127.0.0.1:3111` & `100.106.143.78:3111`), and `/Users/androidteam/Developer/platform/openspec-store/`.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `omniroute-compression-and-routing`: Remove banned `62af823b` from `gemini-4-argon*` and `gemini-4-carbon*` (2 active Ultra steps each) and switch `gemini-4-hydrogen*` combos to `quota-weighted` across the 5 active WTU-Pro accounts (`9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`).
- `omp-provider-routing`: Exclude banned `vicgnome19094@gmail.com` (`id = 3`) from `~/.omp/agent/agent.db` (`5` active `google-antigravity` OAuth accounts remain).
- `omniroute-agent-cli-routing`: Omit unsupported `service_tier = "ultrafast"` from `~/.codex/config.toml` per `openai/codex` schema and verify zero `unsupported_service_tier_warning` diagnostics plus protocol-level `/v1/responses` `HTTP 200` / `"pong"` execution against `quota-weighted` `gemini-4-hydrogen`.
- `pi-agent-harness-config`: Align `pi-agent-harness-config` (`spec.md`), `wiki/entities/pi.md`, `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md`, and `~/.pi/agent/settings.json` (`lastChangelogVersion`) to Pi `1.5.2` with `1.5.1`/`1.5.2` (`N-1`) release retention.

## Impact

- **Systems Affected**: OmniRoute combos (`13` combos updated in `storage.sqlite`), OMP SQLite (`~/.omp/agent/agent.db`), Codex CLI (`~/.codex/config.toml`), Pi CLI (`~/.pi/agent/settings.json`), Hermes Pi skill, Wiki/Notion, and `openspec-store` GitNexus index.
- **Rollback**: Pre-mutation backups (`0600`) of `agent.db`, `~/.codex/config.toml`, `~/.pi/agent/settings.json`, `combos-pre.json`, and an OmniRoute SQLite snapshot under `~/.omniroute/backups/reconcile-hydrogen-codex-routing-banned-accounts-and-pi-sync/`.
