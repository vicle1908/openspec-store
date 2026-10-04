# Verification Evidence: Govern Workstation Toolchain Consolidation and Snapshot Growth

## Date: 2026-10-04

### 1. Snapshot Store Growth Measurement & Ceilings
- **Command**: `python3 scripts/measure-snapshot-growth.py --json`
- **Output**:
  - Total size: `9.74 GiB` (exceeds declared ceiling `1G`)
  - Loose objects: `9.72 GiB` across 1,365 objects
  - Packed objects: `17.41 MiB` across 1,227 objects in 1 pack
  - Commits: 864 commits (oldest: `2026-08-17`, newest: `2026-10-04`)
  - Reclaimable estimate: `~9.71 GiB`
  - Owner command: `git -C ~/.agentmemory/snapshots repack -a -d -f --depth=250 --window=250`
  - Prohibitions verified: Direct object deletion (`rm -rf .git/objects`) prohibited.

### 2. Prefix Reconciliation & Toolchain Inventory
- **Command**: `python3 scripts/inventory-workstation-toolchain.py`
- **Prefix Reconciliation**:
  - `~/.npmrc` sets `prefix = /Users/androidteam/.npm-global`.
  - `npm config get prefix`: `/Users/androidteam/.npm-global`
  - Maintenance pipeline prefix: `/Users/androidteam/.npm-global`
  - Status: `RECONCILED`
- **Duplication & Authoritative Detection**:
  - `gitnexus`: Resolves to `/Users/androidteam/.npm-global/bin/gitnexus` (authoritative). Duplicates in `~/.local/share/home-toolchain/` (219.91 MiB) and `~/.local/lib/node_modules/` (1017.93 MiB).
  - `codex`: Resolves to `/Users/androidteam/.npm-global/bin/codex` (authoritative). Duplicate in `/opt/homebrew/lib/node_modules/@openai/codex` (317.56 MiB).
  - Name collision: Recorded `grok` formula (deprecated regex tool) vs `grok-build` cask (agent CLI), and `opencode` third-party tap shadowing `homebrew/core`.
  - Policy: `Proposes deletion = False`.

### 3. Agent CLI Coverage Reconciliation
- **Command**: `python3 scripts/reconcile-agent-cli-coverage.py`
- **Roster**: 16 installed agents total.
  - Covered (7): `auggie`, `claude`, `codex`, `kilo`, `opencode`, `pi`, `qoder`.
  - Uncovered Declared (9): `buzz`, `cce`, `cursor-agent`, `droid`, `goose`, `grok`, `happy`, `hermes-agent`, `prime-agent`.
  - Undeclared: 0.

### 4. Daily Maintenance Pipeline Integration
- **Command**: `bash ~/Developer/scripts/workstation-daily-update.sh --check`
- **Results**:
  - `[Stage 7/12] Script Provenance Drift Check: in sync (checked=7 drifted=0 missing_record=0)`
  - `[Stage 8/12] Snapshot Store Growth Bounds`: Reports EXCEEDED `9.74 GiB`.
  - `[Stage 9/12] Toolchain Inventory & Prefix Reconciliation`: Reports RECONCILED.
  - `[Stage 10/12] Agent CLI Coverage Reconciliation`: Reports 0 undeclared.
  - Summary: `DEGRADED: one or more Git snapshot stores exceed declared size ceilings.` (non-fatal, exits 0).
  - OpenSpec Store Strict Validation: `436 passed, 0 failed`.
