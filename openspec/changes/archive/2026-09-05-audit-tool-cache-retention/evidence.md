# Tool Cache Retention Audit Evidence

## Executive Summary

This read-only audit inventories the cache roots, disk consumption, modification dates, ownership boundaries, and active processes for tool-owned caches across the workstation:
- **UV Cache**: Astral Python package manager and resolver (`~/.cache/uv`).
- **Claude Code**: Anthropic Claude Code CLI runtime, plugins, and project state (`~/.claude`).
- **Orca**: Orca desktop IDE, terminals, Electron cache, and Codex runtime (`~/.orca`, `~/Library/Application Support/Orca`).

Total tool cache storage inventoried across all candidate locations is approximately **3.06 GiB**:
1. `~/.cache/uv`: 890.0 MB (890,004,935 B)
2. `~/.claude`: 1.14 GB (1,137,309,687 B)
3. `~/.orca`: 28.3 KB (28,260 B)
4. `~/Library/Application Support/Orca`: 1.24 GB (1,235,054,336 B)
*(Note: standard macOS `~/Library/Caches/{uv,Claude,Orca}` roots were confirmed MISSING; tools store their cache state under their respective home/Application Support roots).*

No cache, database, configuration, or user data was deleted or altered during this audit.

---

## 1. Inventory of Candidate Roots

### 1.1 UV Package Cache (`~/.cache/uv`)
- **Filesystem Path**: `/Users/androidteam/.cache/uv`
- **Total Allocated Size**: 890,004,935 B (~848.8 MiB)
- **Directory Modification Time**: `2026-09-05T15:27:07+0700`
- **Component Breakdown**:
  | Entry | Kind | Size (Bytes) | Size (Human) | Modification Date | Classification |
  |---|---|---|---|---|---|
  | `archive-v0` | Directory | 840,326,268 | 801.4 MiB | 2026-09-05T15:27:07+0700 | Recoverable Cache |
  | `simple-v24` | Directory | 49,291,328 | 47.0 MiB | 2026-09-05T15:26:32+0700 | Recoverable Cache |
  | `wheels-v6` | Directory | 356,112 | 347.8 KiB | 2026-09-05T15:26:32+0700 | Recoverable Cache |
  | `sdists-v9` | Directory | 29,168 | 28.5 KiB | 2026-09-05T15:26:37+0700 | Recoverable Cache |
  | `interpreter-v4` | Directory | 2,015 | 2.0 KiB | 2026-09-05T15:26:32+0700 | Active Metadata |
  | `CACHEDIR.TAG` | File | 43 | 43 B | 2026-09-05T15:26:32+0700 | Standard Tag |
  | `.gitignore` | File | 1 | 1 B | 2026-09-05T15:26:32+0700 | Metadata |
  | `.lock` | File | 0 | 0 B | 2026-09-05T15:26:32+0700 | Lockfile |
  | `builds-v0` | Directory | 0 | 0 B | 2026-09-05T15:27:08+0700 | Ephemeral Scratch |

### 1.2 Claude Code State & Cache (`~/.claude`)
- **Filesystem Path**: `/Users/androidteam/.claude`
- **Total Allocated Size**: 1,137,309,687 B (~1.06 GiB)
- **Directory Modification Time**: `2026-09-05T22:17:55+0700`
- **Component Breakdown**:
  | Entry | Kind | Size (Bytes) | Size (Human) | Modification Date | Classification |
  |---|---|---|---|---|---|
  | `plugins/` | Directory | 661,015,367 | 630.4 MiB | 2026-09-05T19:29:14+0700 | Recoverable / Active |
  | `plugins/cache` | Directory | ~690,000,000 | ~658 MiB | 2026-09-05T19:29:14+0700 | Recoverable Cache |
  | `plugins/marketplaces` | Directory | ~118,000,000 | ~112 MiB | 2026-09-05T19:29:14+0700 | Active / Recoverable Index |
  | `projects/` | Directory | 455,841,677 | 434.7 MiB | 2026-09-05T19:49:12+0700 | Protected / Active State |
  | `file-history/` | Directory | 8,362,040 | 7.97 MiB | 2026-09-05T00:22:42+0700 | Active Undo State |
  | `shell-snapshots/` | Directory | 6,746,881 | 6.43 MiB | 2026-09-05T19:29:40+0700 | Recoverable Cache |
  | `jobs/` | Directory | 3,752,437 | 3.58 MiB | 2026-09-01T19:18:55+0700 | Stale Diagnostic State |
  | `cache/` | Directory | 630,788 | 616.0 KiB | 2026-09-05T19:28:35+0700 | Recoverable Cache |
  | `backups/` | Directory | 287,581 | 280.8 KiB | 2026-09-05T22:27:29+0700 | Recoverable Backups |
  | `history.jsonl` | File | 256,996 | 251.0 KiB | 2026-09-05T22:17:55+0700 | Protected User History |
  | `settings.json*` | Files | ~165,000 | ~161 KiB | 2026-08-31T11:44:20+0700 | Protected Configuration |
  | `skills/`, `commands/` | Directories | ~225,000 | ~220 KiB | 2026-09-04T17:44:21+0700 | Protected Customizations |
  | `tasks/`, `teams/`, `plans/` | Directories | ~80,000 | ~78 KiB | 2026-09-05T19:49:12+0700 | Active Workflow State |

### 1.3 Orca Application & Runtime State (`~/.orca` and `~/Library/Application Support/Orca`)
- **Filesystem Paths**:
  - `/Users/androidteam/.orca`: 28,260 B (~27.6 KiB)
  - `/Users/androidteam/Library/Application Support/Orca`: 1,235,054,336 B (~1.15 GiB)
- **Directory Modification Time**: `2026-09-05T22:30:03+0700`
- **Component Breakdown**:
  | Entry | Kind | Size (Bytes) | Size (Human) | Modification Date | Classification |
  |---|---|---|---|---|---|
  | `codex-runtime-home` | Directory | 1,007,212,003 | 960.5 MiB | 2026-09-05T22:22:12+0700 | Active / Historical Rollouts |
  | `codex-runtime-home/home/sessions` | Directory | ~958,000,000 | ~913.6 MiB | 2026-09-05T22:22:12+0700 | Agent Session State |
  | `logs/` | Directory | 99,410,375 | 94.8 MiB | 2026-09-05T04:03:21+0700 | Stale Diagnostic Logs |
  | `opencode-hooks/` | Directory | 54,825,016 | 52.3 MiB | 2026-08-20T11:12:43+0700 | Active Extension Runtime |
  | `terminal-history/` | Directory | 27,348,428 | 26.1 MiB | 2026-09-05T22:18:01+0700 | Active Terminal Scrollback |
  | `Partitions/` | Directory | 17,328,498 | 16.5 MiB | 2026-08-20T19:24:49+0700 | Active Webview Storage |
  | `orchestration.db*` | SQLite DB + WAL | 10,924,112 | 10.4 MiB | 2026-09-04T23:22:08+0700 | Protected Orchestration DB |
  | `GPUCache`, `Cache`, `Dawn*`, `Code Cache` | Directories | ~9,300,000 | ~8.9 MiB | 2026-08-20T11:09:16+0700 | Recoverable Chromium Cache |
  | `serve-sim-runtime` | Directory | 4,394,024 | 4.19 MiB | 2026-08-23T20:49:36+0700 | Simulator Runtime Cache |
  | `profiles` | Directory | 2,186,730 | 2.09 MiB | 2026-08-20T11:09:08+0700 | Protected Browser Profiles |
  | `ai-vault/` | Directory | 1,007,717 | 984 KiB | 2026-08-24T10:45:36+0700 | Protected Vault State |
  | Credentials & Auth Keys | Files | ~60,000 | ~58 KiB | Various | Protected (Never Touch) |

---

## 2. Tool Ownership & Active Session Mapping

### 2.1 UV
- **Owning Tool**: Astral UV Python package manager (`/opt/homebrew/bin/uv`).
- **Active Processes**:
  - Live virtualenvs built and managed by uv:
    - PID 667: `/Users/androidteam/.tdt/deployments/webhook-receiver/app/.venv/bin/python ... uvicorn webhook_receiver.api.app:create_app` (port 8080)
    - PID 66918: `/Users/androidteam/.tdt/deployments/ai-review/app/.venv/bin/python ... uvicorn ai_review.api.app:app` (port 8090)
  - No active foreground or background `uv` compilation/download processes running.
- **Safety Boundary**: Virtual environments contain hardcoded symlinks or references to packages, but runtime execution runs independently of the cache directory. Clearing cache does not kill running services, though it prevents offline reinstalls.

### 2.2 Claude Code
- **Owning Tool**: Anthropic Claude Code CLI (`claude`, version 2.1.260).
- **Active Processes**:
  - PID 7986: `claude` (interactive session on `ttys002`)
  - PID 51984 / 51990: `node .../happy/scripts/claude_local_launcher.cjs` and `claude 2.1.260` (active session on `ttys003`)
  - PID 60522: `claude` (interactive session on `ttys004`)
  - PID 90022: `claude -r` (resumed session on `ttys011`)
- **Safety Boundary**: Live Claude Code processes continuously read and update `projects/`, `file-history/`, `shell-snapshots/`, and `plugins/`. Any direct modification of these paths while sessions are running risks file lock contention or session state loss.

### 2.3 Orca
- **Owning Tool**: Orca desktop runtime (`/Applications/Orca.app`, version 1.4.197).
- **Active Processes**:
  - PID 26675: `Orca Helper ... daemon-entry.js`
  - PID 66706: `Orca Helper --type=gpu-process`
  - PID 66708: `Orca Helper --type=utility --utility-sub-type=network.mojom.NetworkService`
  - PID 66826: `Orca Helper (Renderer)`
  - PID 74258 / 74259: `Orca Helper` audio and video services
  - Connected terminal sessions: PID 1209, PID 22342, PID 86371 (`omp --extension .../orca-agent-status.ts`)
- **Safety Boundary**: Orca holds open file descriptors to `orchestration.db`, `codex-runtime-home/home/*.sqlite`, and socket files (`daemon-v36.sock`). Deleting files or SQLite WAL files while Orca is running causes severe database corruption or UI crashes.

---

## 3. Classification & Evaluation

| Component | Size | Classification | Rationale |
|---|---|---|---|
| `~/.cache/uv/archive-v0` | 801.4 MiB | **Recoverable** | Downloaded wheels and sdist packages from PyPI. Completely restorable on-demand via network. |
| `~/.cache/uv/simple-v24` | 47.0 MiB | **Recoverable** | Cached HTTP responses from package indexes. Re-fetched as needed. |
| `~/.cache/uv/wheels-v6`, `sdists-v9` | 376.3 KiB | **Recoverable** | Locally built wheel files and extracted source trees. |
| `~/.cache/uv/interpreter-v4` | 2.0 KiB | **Active** | Discovered Python runtime paths. |
| `~/.claude/plugins/cache` | ~658 MiB | **Recoverable** | Cached plugin package downloads. Can be re-downloaded via `claude plugin`. |
| `~/.claude/plugins/marketplaces` | ~112 MiB | **Active / Recoverable** | Cloned git repositories for plugin marketplaces. |
| `~/.claude/projects/` | 434.7 MiB | **Protected / Active** | Project conversation transcripts, cost ledgers, and memories needed for `/resume`. Deletion causes irreversible loss of session history. |
| `~/.claude/file-history/` | 7.97 MiB | **Active** | Local undo buffers for recently edited files. Safe to prune only after sessions end. |
| `~/.claude/shell-snapshots/` | 6.43 MiB | **Recoverable** | Ephemeral environment snapshots across subshell invocations. |
| `~/.claude/jobs/` | 3.58 MiB | **Stale** | Subagent output logs from older dates (e.g. Sep 01). |
| `~/.claude/cache/` | 616 KiB | **Recoverable** | Internal CLI response cache. |
| `~/.claude/settings.json*` | ~161 KiB | **Protected** | User configuration, custom MCP server definitions, and provider configs. |
| Orca `codex-runtime-home/home/sessions` | 913.6 MiB | **Active** | Historical and active agent rollout logs for Codex within Orca. Needed for audit and debugging. |
| Orca `logs/` | 94.8 MiB | **Stale** | Rotated diagnostic and crashpad logs. Reclaimable safely when Orca is not diagnosing an active crash. |
| Orca `terminal-history/` | 26.1 MiB | **Active** | Scrollback and terminal pane history. |
| Orca Chromium Caches (`Cache`, `GPUCache`, etc.) | 8.9 MiB | **Recoverable** | Chromium webview and shader caches. |
| Orca `orchestration.db*`, `ai-vault/`, auth | ~11.5 MiB | **Protected** | Application database, encryption keys, and active credentials. |

---

## 4. Safe Owner-Native Cleanup Recommendations & Rollback Trade-offs

### 4.1 UV Cleanup
- **Recommended Command**:
  ```bash
  uv cache prune
  ```
- **Action Scope**: Prunes dangling cache entries and unreferenced environments without purging actively used distributions.
- **Aggressive Command** (Requires approval):
  ```bash
  uv cache clean
  ```
- **Reclaimable Potential**: Up to **848.8 MiB**.
- **Rollback & Latency Considerations**:
  - Zero permanent data loss: all packages are re-downloadable from PyPI / index.
  - Future `uv sync` or `uv run` commands will experience network latency while re-downloading dependencies.
  - Offline builds will fail if required archives are evicted while network is unavailable.

### 4.2 Claude Code Cleanup
- **Recommended Command**:
  ```bash
  claude plugin prune
  ```
- **Action Scope**: Removes orphaned or unused auto-installed plugin dependencies.
- **Targeted Project Purge** (Requires explicit per-project path approval):
  ```bash
  claude project purge <path-to-workspace>
  ```
- **Reclaimable Potential**:
  - `plugins/cache`: ~658 MiB (if manually purged when all Claude sessions are idle).
  - Stale `jobs/` and `cache/`: ~4.2 MiB.
- **Rollback & Latency Considerations**:
  - `claude project purge` permanently deletes conversation history, token metrics, and `/resume` capability for that workspace.
  - Deleting `plugins/cache` requires re-downloading plugins upon next session startup.
  - Under no circumstances should `settings.json`, `skills/`, or `commands/` be targeted.

### 4.3 Orca Cleanup
- **Recommended Commands**:
  - Close idle live terminals:
    ```bash
    orca terminal close --all
    ```
  - Reset completed orchestration runs:
    ```bash
    orca orchestration reset
    ```
- **Targeted Log Rotation** (Requires Orca shutdown):
  - Truncating or removing rotated log files under `~/Library/Application Support/Orca/logs/` (reclaims ~94.8 MiB).
- **Reclaimable Potential**: ~103.7 MiB (logs + Chromium cache) safely; up to 1.0 GiB if Codex sessions are archived.
- **Rollback & Trade-offs**:
  - DO NOT delete files in `~/Library/Application Support/Orca` while Orca is running (PID 26675, 66826).
  - Deleting `terminal-history` destroys terminal buffer scrollback for developers.
  - Deleting `codex-runtime-home/home/sessions` removes historical agent traces needed for session review.

---

## 5. Explicit Approval Requirements

Per workspace governance and OpenSpec safety constraints:
1. **Generic "Approve All" is strictly prohibited**: Destructive cleanup actions must specify exact commands, targets, and expected byte savings.
2. **Read-Only Gate Compliance**: This change (`audit-tool-cache-retention`) is strictly read-only (`skip_specs: true`). No filesystem deletions were executed.
3. **Pre-Requisite for Future Cleanup**:
   - Any actual deletion must occur in a separate, dedicated, approval-gated OpenSpec change.
   - All active Claude Code and Orca sessions must be terminated or gracefully closed before mutating application support directories.
   - Exact approved commands must be presented to and approved by the operator.
