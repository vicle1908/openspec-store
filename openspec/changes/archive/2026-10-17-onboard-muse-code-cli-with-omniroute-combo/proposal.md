# Proposal

## Why

Meta Muse Code (`muse`, Homebrew cask `muse-code`) is not yet installed or governed on this workstation, and unconfigured `muse-spark-1.3` requests to the local OmniRoute gateway fail because no `muse-spark-1.3` combo or Meta upstream credential exists yet. Onboarding Muse Code via the official Homebrew cask (`muse-code`), routing its default `muse-spark-1.3` model through an OmniRoute combo backed by the 15-account `gemini-3.8-flash-high` Antigravity pool, wiring `mcp-router` (`mcpServers` / `mcp_servers`) and workstation skills, and registering `muse` in the workstation toolchain authority and manifest files establishes a zero-account, resilient terminal coding agent that adheres to all workstation and gateway governance invariants.

## What Changes

- Install Meta Muse Code CLI (`v1.4.10-R6427.1`, `muse-aarch64-macos`) via the official Homebrew cask `muse-code` (`/opt/homebrew/bin/muse`), explicitly disambiguating it from the unrelated disabled desktop cask `muse`.
- Register an OmniRoute combo named `muse-spark-1.3` (`POST http://127.0.0.1:20128/api/combos`) with `strategy: "priority"`, `context_length: 1000000`, and `context_cache_protection: true` referencing the `gemini-3.8-flash-high` combo (`combo-ref`) as primary leg and `agy/gemini-3.8-flash-medium` as secondary fallback, so `handleChatImplementation` intercepts bare `"model": "muse-spark-1.3"` requests on `POST /v1/responses` ahead of the unauthenticated static `muse-code` provider (returning expected `COMBO_NAME_SHADOWS_MODEL` warning `#8530`) while preserving `GET /v1/muse-code/models` catalog compatibility.
- Seed `OMNIROUTE_API_KEY` into `~/.config/muse/auth.json` (mode `0600`, supporting both `TBH_CREDENTIAL_BACKEND=file` `schema_version: 1` and canonical macOS Keychain `schema_version: 2` via `muse auth set --provider meta --api-key-stdin`) and configure `~/.config/muse/settings.json` (mode `0600`) with `"schema_version": 1`, `"model": "muse-spark-1.3"`, `"provider": "meta"`, sanctioned `"endpoint_transport": {"base_url": "http://127.0.0.1:20128/v1", "auth": "bearer"}` (preventing Muse CLI $\ge$ 1.0.1 bearer withholding), and `mcpServers.mcp-router` (canonicalized from `mcp_servers`, with `transport: "stdio"`, `mode: "optional"`).
- Verify native skill discovery (`~/.claude/skills` and `~/.agents/skills`) and import workstation skills into Muse Code via `muse skills import --from claude --scope user`.
- Register executable `muse` (and cask alias `muse-code` where applicable) as `brew-cask` (`updater_dispatch="none"`, `supported_verb=None`, `delegating_to="brew"`, `status="uncovered_declared"`) across `platform/openspec-store/scripts/toolchain_updater_registry.py`, `inventory-workstation-toolchain.py`, `config/workstation-toolchain-manifest.json`, `reconcile-agent-cli-coverage.py`, `test-version-authority-governance.py`, and `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`pgrep -x` checks for `muse-code`, `muse`, and `muse-aarch64-macos`).
- Verify end-to-end non-interactive prompt execution and Muse `{"type": "namespace", "name": "muse"}` tool-calling round-trips (`muse exec --disable-approval --no-session-log`) through `http://127.0.0.1:20128/v1/responses`, including fail-closed checks for OmniRoute's 1000ms `response.in_progress` startup keepalive frame and `/v1/muse-code/models` catalog schema.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `omniroute-agent-cli-routing`: Add normative requirements for Muse Code (`muse`) loopback routing through `http://127.0.0.1:20128/v1` with `endpoint_transport` bearer pinning, `muse-spark-1.3` combo interception backed by `gemini-3.8-flash-high`, `mcpServers` (`mcp-router`) stdio integration, and mode `0600` credential/config hygiene.
- `portable-workstation-toolchain`: Add normative requirements for `cask "muse-code"` (`/opt/homebrew/bin/muse`) ownership provenance, manifest/inventory registration (`updater_dispatch="none"`, `delegating_to="brew"`), collision disambiguation from the disabled desktop cask `muse`, and active process exclusion (`muse-code`, `muse`, `muse-aarch64-macos`).

## Impact

- **Ownership Boundaries**:
  - Workstation CLI & User Config (`~/.config/muse/settings.json`, `~/.config/muse/auth.json`, `/opt/homebrew/bin/muse`): Owned by local workstation runtime configuration.
  - OmniRoute Gateway State (`POST /api/combos`, `PUT|DELETE /api/combos/<combo-id>` in Docker volume `omniroute-data`): Owned by local OmniRoute deployment (`~/Omniroute`).
  - Toolchain Authority & Inventory (`platform/openspec-store/scripts/*`, `platform/openspec-store/config/workstation-toolchain-manifest.json`, and `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`): Owned by `platform/openspec-store` and `shb/shb-schedule`.
- **Dependencies**: Homebrew (`homebrew/cask`), running OmniRoute container (`v3.8.51` on `127.0.0.1:20128`), and `mcp-router` (`localhost:3282`).
- **Explicit Non-Goals**:
  - Enrolling or authenticating a direct Meta account (`auth.meta.com` RFC 8628 device OAuth or `META_API_KEY` for upstream `mc/*` / `msw/*` providers) in OmniRoute; that is explicitly deferred to a separate follow-up OpenSpec change.
  - Modifying existing routing configurations for unrelated coding CLIs (`omp`, `claude`, `kimi`, `goose`, `pi`, `codex`).
