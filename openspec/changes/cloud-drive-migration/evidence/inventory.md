# Pre-action inventory: cloud-drive-migration

Recorded: 2026-09-06T06:22:00+07:00

## Read-only verification

- No deletion or move commands were run.
- No mutation tasks were marked complete.
- Checksums were omitted for large trees because sizes, timestamps, and git metadata were sufficient for an approval gate.

## iCloud candidates

| Path | Status | Local size | Modified |
|---|---:|---:|---|
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/vds` | exists | 8.0G | 2026-08-24 |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/microservices` | exists | 604M | 2026-02-20 |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/compileDebugKotlin` | missing | - | - |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/compileKotlin` | missing | - | - |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/ksp` | missing | - | - |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/sparse` | missing | - | - |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/inventory` | missing | - | - |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/com 2` | missing | - | - |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/camunda` | exists | 12K | 2026-05-03 |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/camunda7` | exists | 40K | 2026-05-03 |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/camunda-async` | exists | 0B | 2025-12-15 |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/airbridge` | exists | 12K | 2026-05-03 |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/tmz` | exists | 8K | 2026-05-03 |

Notes:
- `vds` is a git worktree with no `.git` directory detected locally.
- `microservices` is a git repo; git status did not complete cleanly in the captured run.

## Google Drive candidates

| Path | Status | Local size | Notes |
|---|---:|---:|---|
| `~/My Drive/tdt` | exists | 6.1G | Local root for the mixed code/docs folder |
| `~/My Drive/tdt/TDT (1)` | missing | - | Not found locally; earlier remote listing snapshot did not match current local scan |
| `~/My Drive/tdt/VinID` | missing | - | Not found locally; earlier remote listing snapshot did not match current local scan |
| `~/My Drive/tdt/tdt-meta` | exists | 300M | Keep-listed documentation |
| `~/My Drive/tdt/poems-mobile3-docs` | exists | 225M | Keep-listed documentation |
| `~/My Drive/tdt/tdt-python-source-package` | exists | 20M | Keep-listed source package |
| `~/My Drive/tdt/tdt-python-source-package.zip` | exists | 10M | Keep-listed source archive |
| `~/My Drive/tdt/git-remotes` | exists | 12M | Keep-listed metadata |
| `~/My Drive/tdt/git-bundles` | exists | 8.4M | Keep-listed rollback bundles |
| `~/My Drive/tdt/data` | exists | 22M | Keep-listed data |
| `~/My Drive/tdt/reports` | exists | 696K | Keep-listed documentation |
| `~/My Drive/tdt/workflow-dag` | exists | - | Keep-listed documentation |
| `~/My Drive/tdt/mcp-router` | missing | - | Representative code-mirror candidate |
| `~/My Drive/tdt/agent-core` | missing | - | Representative code-mirror candidate |
| `~/My Drive/tdt/jira-skill` | missing | - | Representative code-mirror candidate |

Notes:
- Rclone remote listing snapshots previously showed `TDT (1)` and `VinID` at remote root level, but current local filesystem scans do not find them under `~/My Drive/tdt/`. That mismatch must be resolved before any deletion approval.

## Desktop/Documents candidates

| Path | Status | Local size | Notes |
|---|---:|---:|---|
| `~/Desktop` | exists | 184K | Personal-looking root; protected by default |
| `~/Desktop/tdt-python-source-package.zip` | exists | ~10M | Migration stub candidate |
| `~/Desktop/tdt-documentation-package.zip` | exists | ~213K | Migration stub candidate |
| `~/Documents` | exists | 104K | Personal-looking root; protected by default |

Current `~/Desktop` contents are small and mostly look like sync artifacts or migration leftovers. Current `~/Documents` contains substantial personal and document files; only exact approved paths should be touched.

## Developer bundle candidate

| Path | Status | Local size | Notes |
|---|---:|---:|---|
| `~/Developer/go-microservices-cleanup-20260817.bundle` | exists | 3.3M | Current local stat size differs from design estimate |

## Current destination note

- `~/Developer/vds` does not exist.
- `~/Developer/microservices` does not exist.
