# Design: Durable Workstation Toolchain and Application Update Engine

## Overview

This design unifies fragmented, overlapping, and partially drifted maintenance mechanisms across macOS packages, applications, and CLI skills into a single, durable orchestration model powered by `shb-schedule` (DBOS durable execution) and governed by OpenSpec capability `portable-workstation-toolchain`.

---

## 1. Subsystem Architecture & Migration Matrix

The development workstation currently has multiple competing and abandoned update mechanisms. This design establishes a single authoritative execution path and safely cleans up obsolete artifacts under an explicit allowlist:

| Mechanism / Artifact | Current State | Target State | Migration Action & Safety Boundary |
| :--- | :--- | :--- | :--- |
| `~/Developer/scripts/workstation-daily-update.sh` | Monolithic 800+ line bash script executed daily at 08:00 AM via launchd | Retained as modular thin CLI runner / fallback invoker | Reconcile copy drift with store mirror; delegate stages to modular workflow functions |
| `platform/openspec-store/scripts/workstation-daily-update.sh` | Recorded mirror copy drifted by 20 lines | Authoritative version-controlled mirror | Sync bytes with executed script; regenerate SHA-256 provenance digest in `script-provenance-manifest.tsv` |
| `~/Library/LaunchAgents/com.user.brew-npm-update.plist.disabled` | Legacy disabled launchd agent | Obsolete | Verify non-symlink regular file; run `launchctl bootout gui/$UID/com.user.brew-npm-update` if loaded; delete plist |
| `~/.local/bin/brew-npm-update.sh` | Legacy uncoordinated brew/npm updater | Obsolete duplicate | Verify non-symlink regular file; delete script |
| `~/Library/LaunchAgents/com.microservices.developer-workstation-tool-update.plist.disabled` | Legacy disabled launchd agent | Obsolete | Verify non-symlink regular file; run `launchctl bootout gui/$UID/com.microservices.developer-workstation-tool-update` if loaded; delete plist |
| `~/Library/Application Support/com.microservices.developer-workstation-tool-update/` | Obsolete shell updater scripts | Obsolete duplicate | Verify directory; remove directory tree |
| `~/Library/LaunchAgents/com.omniroute.update-check.plist` | Specialized LaunchAgent (every 12h) checking OmniRoute Docker digest | Independent daemon | Preserve; outside workstation toolchain scope |
| `~/Developer/shb/shb-schedule/` | DBOS-backed durable workflow engine with Postgres persistence | **Primary Workflow Engine** | Host `workstation_update_workflow` with durable checkpoints |
| `~/.shb/schedules/workstation-daily-update.yaml` | Non-existent | **Authoritative Schedule Manifest** | Declare cron `0 8 * * *` with 2 retry attempts; permissions mode `0600` |

---

## 2. Multi-Stage Workflow Architecture

Under `shb-schedule`, the update pipeline executes as discrete DBOS transactional steps. Each step persists its completion state to PostgreSQL, preventing cascading re-runs upon transient network failures.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   shb-schedule / DBOS Workflow                         │
│                    workstation_update_workflow                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
[Step 1: Preflight]          [Step 2: Homebrew]               [Step 3: Mac App Store]
- Verify noninteractive      - HOMEBREW_NO_AUTO_UPDATE=1      - mas outdated (sanitized regex)
- CI=1, NONINTERACTIVE=1     - Formula upgrade                - Check active GUI locks (pgrep -x)
- Check DISABLE_UPDATES      - Check GUI process locks        - mas upgrade -- <id> (no sudo)
- Check battery (>50% on bat)- Cask upgrade & brew cleanup
    │                               │                               │
    └───────────────────────────────┼───────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
[Step 4: Global NPM & Bun]   [Step 5: Python / uv]            [Step 6: Agent CLIs]
- npm outdated -g --json     - Dynamic uv tool list           - Static AGENT_CLI_COVERED map
- Sanitize package names     - Validate identifier regex      - 900s timeout bound
- Exclude governed agents    - uv tool upgrade -- <tool>      - Post-update version probe
- Ensure Bun global JSON                                      - Discrete argv execution
- bun upgrade && bun update -g
    │                               │                               │
    └───────────────────────────────┼───────────────────────────────┘
                                    │
    ┌───────────────────────────────┴───────────────────────────────┐
    ▼                                                               ▼
[Step 7: Remote Skills]                                      [Step 8: Store Validation]
- skills update -y (1800s bound)                             - Script provenance hash check
- Classify 5 drift outcomes                                  - openspec validate --all --strict
- sync-workspace-agent-skills.py --check                     - Output JSON report (mode 0600)
```

---

## 3. Subsystem Implementation & Safety Specifications

### 3.1 Non-Interactive & Privilege Boundaries
* **Strictly No `sudo`**: The maintenance engine SHALL never invoke `sudo`, request password prompts, or query interactive Keychain dialogs.
* **Fail-Fast Elevation**: If a package or application requires root elevation or interactive authentication, the runner immediately records it as `SKIPPED (requires elevation)` and proceeds without stalling.
* **Environment Sentinels**:
  - `CI=1`
  - `NONINTERACTIVE=1`
  - `HOMEBREW_NO_AUTO_UPDATE=1` (during inspection phases)
* **PATH Normalization**: In LaunchAgent and background contexts, explicitly construct and export the comprehensive path:
  `/opt/homebrew/bin:/opt/homebrew/sbin:/Users/androidteam/.npm-global/bin:/Users/androidteam/.local/bin:/Users/androidteam/.bun/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin`

### 3.2 Pre-flight Power & Lock Safety
* **Power Check**: Before resource-intensive builds or downloads, query `pmset -g batt`. If running on battery with charge < 50%, skip non-essential heavy updates.
* **Lock Contention**: Check for active Homebrew locks (`/tmp/homebrew.*.lock`) and active coding agent sessions. If locked, defer step.

### 3.3 Mac App Store (`mas`) Safety Gate
`mas upgrade` can force restart or crash running applications.
* Workflow executes `mas outdated` returning lines formatted as `<id> <name> (<current> -> <latest>)`.
* Parse application names and validate against character class `^[A-Za-z0-9._@/+-]+$`.
* Check if the application is running using `pgrep -x "$APP_NAME"` (strictly excluding updater subprocesses).
* If running: Log as `SKIPPED (active application process: $APP_NAME)` without sending signals or disrupting the process.
* If idle: Execute `mas upgrade -- "$APP_ID"` non-interactively without elevation.

### 3.4 Dynamic Discovery Loop Injection Protection
All dynamic iteration loops (NPM, Bun, UV, Agent CLIs) enforce strict argument sanitization:
* Validate every discovered identifier against regex: `^[A-Za-z0-9._@/+-]+$`. Any string with spaces, semicolons, shell metacharacters, or unescaped control codes is immediately rejected.
* Pass arguments as discrete `argv` elements in subprocess execution arrays, preceded by `--` to prevent argument injection:
  `["uv", "tool", "upgrade", "--", tool_name]`
* Pinned Agent CLIs: Executed commands are resolved exclusively from a hardcoded static configuration dictionary keyed by the discovered binary name—never from dynamic user/package strings.

### 3.5 Bun Global Ecosystem Normalization
* Verify directory `~/.bun/install/global` exists with mode `0700`.
* Verify `~/.bun/install/global/package.json` exists. If missing, write empty dependencies object `{"dependencies": {}}` with mode `0600`.
* Execute `bun upgrade` followed by `bun update -g` non-interactively.

### 3.6 Secret Isolation & File Mode Permissions
* **Permissions**:
  - Directory `~/Developer/data/updates/` created with mode `0700`.
  - Telemetry run reports written with file mode `0600`.
  - Manifest directory `~/.shb/schedules/` created with mode `0700` and manifest files with mode `0600`.
* **Credential Isolation**:
  - Notification webhook and Telegram bot tokens are dynamically read from `~/.shb/.env` at execution time.
  - Secret values SHALL NEVER be written to DBOS PostgreSQL step checkpoints, telemetry JSON files, or log streams.
  - Failure notifications dispatched to the Telegram channel carry only structured counts and stage names, strictly omitting raw stderr buffers that could echo credentials.

### 3.7 Deletion Allowlist Boundary
Uninstallation and removal of deprecated artifacts is strictly restricted to an exact allowlist:
1. `~/Library/LaunchAgents/com.user.brew-npm-update.plist.disabled`
2. `~/Library/LaunchAgents/com.microservices.developer-workstation-tool-update.plist.disabled`
3. `~/.local/bin/brew-npm-update.sh`
4. `~/Library/Application Support/com.microservices.developer-workstation-tool-update/`
* Rules: No globbing (`rm -rf *.disabled` is strictly prohibited). Each path must be verified as existing and non-symlink before unlinking. For LaunchAgents, execute `launchctl bootout` if loaded before removal.

---

## 4. Telemetry & Observability Schema

Every completed, degraded, or failed run persists an immutable JSON run record to `~/Developer/data/updates/YYYY-MM-DD.json` (mode `0600`):

```json
{
  "timestamp": "2026-10-13T08:00:00+07:00",
  "status": "completed|degraded|failed",
  "duration_seconds": 142.5,
  "steps": {
    "preflight": { "status": "success", "power": "AC", "global_pause": false },
    "homebrew": { "formulae_updated": ["omp"], "casks_updated": [], "casks_skipped_running": [] },
    "mas": { "updated": [], "skipped_running": ["Slack"] },
    "npm": { "updated": ["@brightdata/cli", "codexuse-cli"], "governed_skipped": ["codex", "pi"] },
    "bun": { "runtime_version": "1.4.3", "packages_updated": [] },
    "uv_tools": { "updated": ["graphifyy"], "current": ["tavily-cli"] },
    "agent_clis": { "updated": [], "verified": ["claude", "codex", "pi"] },
    "skills": { "drift": 0, "refreshed": 0, "already_current": 42, "path_ambiguous": 0, "failed": 0 },
    "store_validation": { "status": "valid", "specs_checked": 434 }
  },
  "errors": []
}
```

If `status != "completed"`, a notification payload containing summary counts and stage names is dispatched to the Telegram `Home` channel (`88d95325258b`).
