# Proposal: Durable Workstation Toolchain and Application Update Engine

## Why

The development workstation currently relies on a fragmented and partially drifted collection of auto-update mechanisms:
1. **LaunchAgent / Script Fragmentation and Duplication**:
   - `com.developer.workstation-daily-update.plist` triggers a monolithic 800+ line shell script (`~/Developer/scripts/workstation-daily-update.sh`) daily at 08:00 AM.
   - A recorded mirror copy at `platform/openspec-store/scripts/workstation-daily-update.sh` has already drifted from the executed copy (20 lines of un-reconciled diff).
   - Lingering disabled/orphaned LaunchAgents and legacy scripts continue to clutter the system (`com.user.brew-npm-update.plist.disabled` -> `~/.local/bin/brew-npm-update.sh`, `com.microservices.developer-workstation-tool-update.plist.disabled` -> `~/Library/Application Support/...`).
   - A separate LaunchAgent `com.omniroute.update-check.plist` runs every 12h for OmniRoute image checks.
2. **Missing Ecosystem Surfaces & Automation Blind Spots**:
   - **Mac App Store (`mas`)**: `/opt/homebrew/bin/mas` tracks 8 critical applications (`Keynote`, `Numbers`, `Pages`, `Parallels Desktop`, `Perplexity`, `Slack`, `Telegram 2`, `Xcode`), but zero automated checks or upgrades exist in daily maintenance (`mas outdated` / `mas upgrade`).
   - **Bun Global Ecosystem**: Bun `1.4.3` is installed, but `~/.bun/install/global` is uninitialized (`No package.json was found for directory ~/.bun/install/global`), preventing global packages from being discovered or upgraded.
   - **Python / uv Tools**: Currently hardcoded to two specific packages (`graphifyy`, `tavily-cli`) rather than dynamically discovering all installed tools (`uv tool list`).
   - **Homebrew Casks**: Casks are upgraded without verifying whether GUI processes are actively running (`pgrep -x`), risking session disruption.
3. **Lack of Durable Workflow Guarantees & Security Guardrails**:
   - LaunchAgent execution is fragile: a failure at Stage 11 (e.g. transient GitHub rate limit during `skills update`) requires a complete replay of Stages 1–10.
   - Unattended runs lack explicit privilege boundaries (`sudo` / interactive password prompts can stall processes indefinitely).
   - Dynamic discovery loops lack strict argument validation and injection protection.
   - Logs are unstructured plaintext in `~/Library/Logs/workstation-daily-update.log`.
   - No structured run summaries, no automatic retries with exponential backoff, and no notification/alerting to chat destinations (Telegram/Discord) on degraded runs.

The workspace already maintains a durable, DBOS-backed task scheduling ecosystem in `shb-schedule` (`~/Developer/shb/shb-schedule`), using strict declarative YAML manifests (`shb-schedule/v1`), PostgreSQL persistence, step checkpointing, and retry policies. Migrating the workstation update pipeline to `shb-schedule` eliminates script sprawl, prevents copy drift, ensures idempotency, and provides complete ecosystem coverage across Homebrew, NPM, Bun, Mac App Store, UV, and remote skills.

## What Changes

1. **Durable Workflow Execution via `shb-schedule`**:
   - Implement `shb_schedule.workflows.workstation_update:workstation_update_workflow` in `shb-schedule` as a multi-step DBOS workflow:
     - `step_preflight_authority_check`: Evaluates `toolchain_updater_registry.py`, authority status, power states (`pmset -g batt`), lock contention, and `DISABLE_UPDATES` pause policy.
     - `step_homebrew_update`: Executes non-interactive `brew update`, inspects `brew outdated --json=v2`, applies formula upgrades, checks active GUI process locks (`pgrep -x`) before upgrading casks, and runs `brew cleanup -s`. Strictly non-interactive; no `sudo`.
     - `step_mas_update`: Discovers outdated Mac App Store applications via `mas outdated`, sanitizes identifiers, gates upgrades against active processes (`pgrep -x`), and invokes `mas upgrade -- <id>` without elevation.
     - `step_npm_global_update`: Discovers outdated packages via `npm outdated -g --json`, sanitizes package names, filters out pinned/governed coding agents (`codex`, `claude`, `pi`, `kilo`), and updates eligible tools.
     - `step_bun_global_update`: Ensures `~/.bun/install/global/package.json` is initialized with mode `0600`, upgrades Bun runtime via `bun upgrade`, and updates global packages via `bun update -g`.
     - `step_uv_tools_update`: Dynamically queries `uv tool list`, sanitizes identifiers matching `^[A-Za-z0-9._@/+-]+$`, and upgrades all managed tool venvs using discrete argv arguments (`uv tool upgrade -- "$TOOL"`).
     - `step_agent_cli_update`: Iterates over `AGENT_CLI_COVERED` with time bounds (900s), executing static declared vendor update commands and post-update version probes.
     - `step_skills_refresh`: Invokes `skills update -y` with a 1800s bound, classifies 5 drift outcomes, and verifies parity across `.agents/skills/`.
     - `step_integrity_and_store_validation`: Validates script provenance digests against expected store hashes and runs `openspec validate --all --strict --store openspec-store`.
2. **Declarative Schedule Manifest (`shb-schedule/v1`)**:
   - Register `~/.shb/schedules/workstation-daily-update.yaml` under `owner: platform-team`, cron `"0 8 * * *"`, timezone `Asia/Ho_Chi_Minh`, timeout `3600s`, with a 2-attempt retry backoff policy, file mode `0600`.
3. **Migration & Deprecation of Duplicate/Legacy Mechanisms**:
   - Deprecate and remove disabled LaunchAgents under strict allowlist: `com.user.brew-npm-update.plist.disabled` and `com.microservices.developer-workstation-tool-update.plist.disabled` (verifying regular files, non-symlink, and `launchctl bootout` before unlink).
   - Remove legacy script `~/.local/bin/brew-npm-update.sh` and obsolete `~/Library/Application Support/com.microservices.developer-workstation-tool-update/`.
   - Synchronize the recorded script copy `platform/openspec-store/scripts/workstation-daily-update.sh` with the executed script to eliminate detected drift, maintaining a thin LaunchAgent fallback wrapper that invokes `shb-schedule run-now --workflow workstation-daily-update`.
4. **Structured JSON Run Telemetry & Proactive Alerts**:
   - Each run records an immutable summary artifact at `~/Developer/data/updates/YYYY-MM-DD.json` (mode `0600`, directory mode `0700`).
   - Degraded runs or failures dispatch notifications to the designated Telegram home channel (`Home` `88d95325258b`) carrying stage names and counts, strictly isolating secrets and omitting raw stderr.

## Capabilities

### Modified Capabilities
- `portable-workstation-toolchain`: Extended to govern Mac App Store (`mas`) automation, Bun global package manifest initialization, durable step-level workflow execution, process-lock safety checks, strict non-interactive privilege boundaries, input sanitization, and structured JSON telemetry.

## Non-Goals

- Replacing or migrating service daemons managed via `brew services` or separate LaunchAgents (`com.omniroute.update-check.plist`, `com.developer.index-refresh.plist`).
- Modifying upstream agent binaries or removing developer data/caches.
- Automating updates on unmanaged/quarantined credentials or dotfiles.
