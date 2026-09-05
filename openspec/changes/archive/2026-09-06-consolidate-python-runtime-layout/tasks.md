# Tasks: consolidate-python-runtime-layout

## Purpose
Audit and inventory all Python virtual environments across the workspace to understand runtime layout, identify consolidation opportunities, and classify each environment as live/developer-owned/duplicate/unknown.

## Scope
READ-ONLY audit. No deletions or modifications to existing environments.

## Tasks

### Task 1: Find all .venv directories in workspace repos
- [x] Scan `/Users/androidteam/Developer/` for `.venv` directories (max depth 3)
- [x] Record path, size, and associated repo
- [x] Write results to `evidence/workspace-venvs.json`

### Task 2: Find .tdt venvs
- [x] Inventory `/Users/androidteam/.tdt/venvs/` directory
- [x] Record each venv name, size, and creation date
- [x] Write results to `evidence/tdt-venvs.json`

### Task 3: Find deployment venvs
- [x] Scan `/Users/androidteam/.tdt/deployments/*/app/.venv`
- [x] Record each deployment venv path, size, and associated deployment
- [x] Write results to `evidence/deployment-venvs.json`

### Task 4: Map venvs to LaunchAgents
- [x] Find all LaunchAgents referencing venvs: `grep -l "venv" ~/Library/LaunchAgents/com.tdt.*.plist`
- [x] For each LaunchAgent, extract the venv path and associated service
- [x] Write results to `evidence/launchagent-venvs.json`

### Task 5: Get comprehensive size report
- [x] Run `du -sh` on all discovered venv directories
- [x] Calculate total disk usage
- [x] Write results to `evidence/venv-sizes.json`

### Task 6: Classify each environment
- [x] Review all inventory data from Tasks 1-5
- [x] Classify each venv as: live (actively used by a service), developer-owned (local dev), duplicate (redundant copy), or unknown
- [x] Write consolidated inventory to `evidence/venv-inventory.json`

### Task 7: Create consolidation plan
- [x] Based on classification, identify consolidation opportunities
- [x] Document which venvs could be shared, which are redundant, which are needed as-is
- [x] Write plan to `evidence/venv-consolidation-plan.md`
- [x] Plan must be REVIEW-ONLY - no actual deletions
