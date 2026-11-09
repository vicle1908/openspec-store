# Proposal: Unpin Dev Tooling and Harden Unattended Privilege-Free Execution

## Why

Scheduled background maintenance workflows across `shb-schedule` and `launchd` must run unattended without human intervention. An architectural review of current maintenance cycles revealed two systemic issues:
1. **Tool Pinning Inflexibility**: Tools declared with exact versions (e.g. `graphifyy` pinned to `0.9.95` in `config/uv-tools.json`) cause `uv tool upgrade` to silently no-op with `Nothing to upgrade (hint: ... is pinned)`. This keeps developer tooling stale until manual intervention unpins them. The workspace requires an unpinned policy where all standalone tools continuously track `@latest` with automatic unpin recovery.
2. **Interactive & Privilege-Gated Operations**: Scheduled runs currently degrade or risk stalling on privilege and interactive gates. Specifically, `mas upgrade 747648890` (Telegram) fails daily with `Failed to find app folder URL in installer output` because `/Applications/Telegram.app` is already managed by Homebrew Cask, violating single-authority rules and risking interactive Apple ID prompts. Furthermore, unattended daemons must never invoke `sudo`, must enforce non-interactive environment flags, and must preserve macOS TCC permissions across version bumps via invariant code signing (`client_type = 0`).

## What Changes

1. **Unpin Developer Tooling Across Workspace**:
   - Standardize `platform/openspec-store/config/uv-tools.json` and `npm-global-tools.json` to declare `"version": "latest"` across all tools.
   - Update `shb_schedule.workflows.workstation_update` and `workstation-daily-update.sh` so `step_uv_tools_update` detects pinned hints and automatically unpins via `uv tool install --upgrade <tool>@latest`.
   - Update OpenSpec specifications to replace hard equality pins (`pinned at X`) with modern capability baselines (`>=`).
2. **Eliminate Authority Collisions & Interactive Prompts**:
   - In `step_mas_update`, query installed Homebrew casks (`brew list --cask`) and skip any application managed by Cask (such as `Telegram`), eliminating package manager collisions and installer receipt errors.
   - Enforce headless non-interactive environment variables (`NONINTERACTIVE=1`, `CI=1`, `DEBIAN_FRONTEND=noninteractive`, `HOMEBREW_NO_INTERVENTIONS=1`, `HOMEBREW_NO_AUTO_UPDATE=1`, `PIP_NO_INPUT=1`, `NPM_CONFIG_YES=true`) with stdin redirected from `/dev/null`.
   - Strict zero-sudo rule: all tools must install into sanctioned user-writable paths; operations requiring root must fail fast rather than stalling background runners.
3. **Preserve TCC Grants Across Binary Rotations**:
   - Re-sign updated agent executables immediately post-upgrade using the persistent local certificate `Developer Agent Code Signing` under `client_type = 0` supervisor bundle delegation (`org.python.python`, `com.stablyai.orca`, `com.trycua.driver`, etc.), ensuring Designated Requirement invariance without interactive prompts.

## Capabilities

### Modified Capabilities
- `portable-workstation-toolchain`: Mandate unpinned `@latest` tracking for standalone tools with automatic unpin recovery, authority-gated MAS skipping for Cask-managed apps, and non-interactive zero-sudo execution.

## Impact

- **Affected Components**: `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`, `scripts/workstation-daily-update.sh`, `platform/openspec-store/config/uv-tools.json`, `platform/openspec-store/scripts/workstation-daily-update.sh`.
- **Breaking Changes**: None. Enhances resilience and guarantees zero-prompt automated maintenance.
