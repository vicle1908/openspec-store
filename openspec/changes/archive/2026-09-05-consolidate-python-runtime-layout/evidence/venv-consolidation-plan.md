# Python Virtual Environment Consolidation Plan

## 1. Executive Summary & Governance

- **Change Name**: `consolidate-python-runtime-layout`
- **Store Root**: `/Users/androidteam/Developer/openspec-store`
- **Date**: 2026-09-05
- **Operational Scope**: **EXPLICIT NO-DELETION AUDIT**. In accordance with OpenSpec change policy and repository safety guidelines, this plan performs analysis and policy recommendations only. Zero virtual environments, binary interpreters, or deployment files have been removed or modified.
- **Total Environments Evaluated**: 17 environment paths across 3 target categories:
  - Repo-local developer environments (`~/Developer/*/.venv`): 11 (10 on-disk, 1 active unlinked)
  - Legacy centralized environments (`~/.tdt/venvs/*`): 4
  - Service deployment environments (`~/.tdt/deployments/*/app/.venv`): 2 (1 on-disk, 1 active unlinked)
- **Total Current On-Disk Footprint**: ~5.93 GB across all audited environments.
- **Identified Stale / Duplicate Candidates**: 5 candidates consuming **~2.06 GB** of reclaimable space.

---

## 2. Environment Classification & Inventory Summary

| Path | Size | Classification | Owner / Service | Python Interpreter Status | Active Process |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/Users/androidteam/.tdt/deployments/ai-review/app/.venv` | 876M | **live** | `com.tdt.ai-review` | Python 3.14.5 (uv 0.12.10) - Valid | PID 66918 (`uvicorn ai_review.api.app:app:8090`) |
| `/Users/androidteam/.tdt/deployments/webhook-receiver/app/.venv` | 0B (unlinked) | **live** | `com.tdt.webhook-receiver` | Missing on disk; runs in memory/inode | PID 667 (`uvicorn webhook_receiver:8080`) |
| `/Users/androidteam/Developer/wiki-mcp-server/.venv` | 0B (unlinked) | **live** | `MCP Router` (wiki server) | Missing on disk; runs in memory/inode | PID 4409 (`wiki_mcp_server/server.py`) |
| `/Users/androidteam/Developer/agent-docs-sync/.venv` | 791M | **developer-owned** | `agent-docs-sync` | Python 3.14.5 (uv 0.12.9) - Valid | None |
| `/Users/androidteam/Developer/agent-harness/.venv` | 800M | **developer-owned** | `agent-harness` | Python 3.14.5 (uv 0.12.9) - Valid | None |
| `/Users/androidteam/Developer/ai-harness-skills/.venv` | 114M | **developer-owned** | `ai-harness-skills` | Python 3.14.5 (uv 0.12.9) - Valid | None |
| `/Users/androidteam/Developer/browser-cli/.venv` | 321M | **developer-owned** | `browser-cli` | Python 3.14.5 (uv 0.12.9) - Valid | None |
| `/Users/androidteam/Developer/code-daily-scan/.venv` | 834M | **developer-owned** | `code-daily-scan` | Python 3.14.5 (uv 0.12.9) - Valid | None |
| `/Users/androidteam/Developer/jira-kanban-from-spreadsheet/.venv` | 267M | **developer-owned** | `jira-kanban` | Python 3.14.5 (uv 0.12.9) - Valid | None |
| `/Users/androidteam/Developer/openspec-store/.venv` | 33M | **developer-owned** | `openspec-store` | Python 3.14 (uv 0.12.5) - Valid | None |
| `/Users/androidteam/Developer/tdt-core/.venv` | 192M | **developer-owned** | `tdt-core` | Python 3.14.5 (uv 0.12.5) - Valid | None |
| `/Users/androidteam/Developer/tdt-sheets/.venv` | 256M | **developer-owned** | `tdt-sheets` | Python 3.14.5 (uv 0.12.9) - Valid | None |
| `/Users/androidteam/.tdt/venvs/ai-review` | 841M | **duplicate** | Legacy TDT runtime | Broken (`/Users/lekhanhvinh/...`) | None |
| `/Users/androidteam/.tdt/venvs/jira-daily-reports` | 321M | **duplicate** | Legacy TDT runtime | Broken (`/Users/lekhanhvinh/...`) | None |
| `/Users/androidteam/.tdt/venvs/tdt-observability` | 437M | **duplicate** | Legacy TDT runtime | Broken (`/Users/lekhanhvinh/...`) | None |
| `/Users/androidteam/.tdt/venvs/webhook-receiver` | 330M | **duplicate** | Legacy TDT runtime | Broken (`/Users/lekhanhvinh/...`) | None |
| `/Users/androidteam/Developer/hermes-webui/.venv` | 127M | **duplicate** | `hermes-webui` | Broken (`/opt/homebrew/.../python3.13`) | None (Service runs via hermes-agent venv PID 685) |

---

## 3. High-Priority Operational Findings: Active Unlinked Environments

During the runtime process mapping, two critical active services were identified whose virtual environments were deleted from disk (unlinked) while their processes remain running:

1. **`webhook-receiver` Service (PID 667)**:
   - **Launchd Job**: `com.tdt.webhook-receiver`
   - **WorkingDirectory**: `/Users/androidteam/.tdt/deployments/webhook-receiver/app`
   - **Current Executable**: `/Users/androidteam/.tdt/deployments/webhook-receiver/app/.venv/bin/python`
   - **Finding**: Process 667 holds open unlinked file descriptors (from previous cleanup into `.Trash`). If PID 667 terminates or the machine restarts, launchd will fail to restart the service because `.venv/bin/uvicorn` is missing from the deployment path.
   - **Action Required Prior to Any Service Restart**: Re-create the deployment venv in `/Users/androidteam/.tdt/deployments/webhook-receiver/app` using `uv sync --frozen` from the deployment `uv.lock`.

2. **`wiki-mcp-server` Service (PID 4409)**:
   - **Parent Process**: MCP Router (PID 704)
   - **Registered Executable**: `/Users/androidteam/Developer/wiki-mcp-server/.venv/bin/python` (stored in `/Users/androidteam/Library/Application Support/MCP Router/mcprouter.db`)
   - **Finding**: Process 4409 holds open unlinked file descriptors. If MCP Router restarts, the wiki tool server will fail to launch because `/Users/androidteam/Developer/wiki-mcp-server/.venv` does not exist on disk.
   - **Action Required Prior to Any MCP Router Restart**: Re-create the virtual environment in `/Users/androidteam/Developer/wiki-mcp-server` using `uv sync` from its canonical `pyproject.toml` and `uv.lock`.

---

## 4. Detailed Candidate Analysis for Future Consolidation

The following 5 virtual environments are confirmed **non-live, duplicate, or broken**. They represent candidates for removal in a future, explicitly approved retirement change.

### Candidate 1: `~/.tdt/venvs/ai-review`
- **Path**: `/Users/androidteam/.tdt/venvs/ai-review`
- **Reclaimable Disk Space**: 841 MB
- **Affected Service**: `ai-review`
- **Current Status**: Broken symlink. Points to `/Users/lekhanhvinh/.local/share/uv/python/cpython-3.14.5-macos-aarch64-none/bin/python3.14` (non-existent username from prior workstation state).
- **Consolidation Rationale**: Duplicate runtime. The authoritative live deployment runs out of `/Users/androidteam/.tdt/deployments/ai-review/app/.venv` (PID 66918, LaunchAgent `com.tdt.ai-review.plist`).
- **Deletion Prerequisites**:
  1. Verify `launchctl list | grep com.tdt.ai-review` confirms PID running from `~/.tdt/deployments/ai-review/app/.venv`.
  2. Verify no active process has open file handles to `~/.tdt/venvs/ai-review`: `lsof +D /Users/androidteam/.tdt/venvs/ai-review` returns zero matches.
  3. Ensure explicit user/owner confirmation of the specific removal path.
- **Rollback Path**: Rebuildable in `< 30s` via `cd ~/Developer/ai-review && uv sync`.
- **Required Owner Approval**: TDT Platform / AI Review Service Maintainer.

### Candidate 2: `~/.tdt/venvs/jira-daily-reports`
- **Path**: `/Users/androidteam/.tdt/venvs/jira-daily-reports`
- **Reclaimable Disk Space**: 321 MB
- **Affected Service**: `jira-daily-reports`
- **Current Status**: Broken symlink to `/Users/lekhanhvinh/...`. No LaunchAgent plist references this path; no running processes.
- **Consolidation Rationale**: Abandoned legacy runtime directory. Source repository `~/Developer/jira-daily-reports` uses repo-local uv invocation (`uv run`).
- **Deletion Prerequisites**:
  1. Confirm `lsof +D /Users/androidteam/.tdt/venvs/jira-daily-reports` returns zero matches.
  2. Confirm no launchd plist in `~/Library/LaunchAgents/` references `~/.tdt/venvs/jira-daily-reports`.
- **Rollback Path**: `cd ~/Developer/jira-daily-reports && uv sync`.
- **Required Owner Approval**: TDT Platform / Jira Automation Lead.

### Candidate 3: `~/.tdt/venvs/tdt-observability`
- **Path**: `/Users/androidteam/.tdt/venvs/tdt-observability`
- **Reclaimable Disk Space**: 437 MB
- **Affected Service**: `tdt-observability`
- **Current Status**: Broken symlink to `/Users/lekhanhvinh/...`. No active process.
- **Consolidation Rationale**: The active LaunchAgent `com.tdt-observability.qemu9p.plist` drives Colima VM execution (`/opt/homebrew/bin/colima -p tdt-observability-qemu-9p start`), not this host Python venv.
- **Deletion Prerequisites**:
  1. Confirm `lsof +D /Users/androidteam/.tdt/venvs/tdt-observability` returns zero matches.
  2. Verify `com.tdt-observability.qemu9p.plist` and `com.tdt-observability.qemu9p-ports.plist` configurations remain unmodified and decoupled from this path.
- **Rollback Path**: `cd ~/Developer/tdt-observability && uv sync`.
- **Required Owner Approval**: TDT Observability Lead.

### Candidate 4: `~/.tdt/venvs/webhook-receiver`
- **Path**: `/Users/androidteam/.tdt/venvs/webhook-receiver`
- **Reclaimable Disk Space**: 330 MB
- **Affected Service**: `webhook-receiver`
- **Current Status**: Broken symlink to `/Users/lekhanhvinh/...`. Not used by launchd.
- **Consolidation Rationale**: The official deployment path is `/Users/androidteam/.tdt/deployments/webhook-receiver/app/.venv` (defined in `com.tdt.webhook-receiver.plist`). `~/.tdt/venvs/webhook-receiver` is an orphaned duplicate.
- **Deletion Prerequisites**:
  1. Confirm `lsof +D /Users/androidteam/.tdt/venvs/webhook-receiver` returns zero matches.
  2. Complete restoration of the live deployment venv in `/Users/androidteam/.tdt/deployments/webhook-receiver/app/.venv` before removing this duplicate path.
- **Rollback Path**: `cd ~/Developer/webhook-receiver && uv sync`.
- **Required Owner Approval**: Webhook Platform Owner.

### Candidate 5: `~/Developer/hermes-webui/.venv`
- **Path**: `/Users/androidteam/Developer/hermes-webui/.venv`
- **Reclaimable Disk Space**: 127 MB
- **Affected Service**: `hermes-webui`
- **Current Status**: Broken interpreter link pointing to missing Homebrew Python 3.13 (`/opt/homebrew/Cellar/python@3.13/3.13.15/...`).
- **Consolidation Rationale**: Duplicate/stale repo-local venv. The service is launched via `com.victory1908.hermes-webui.plist` running `start.sh`, which calls `bootstrap.py`. Per `bootstrap.py` line 281, the live server preferentially runs using the agent venv at `/Users/androidteam/.hermes/hermes-agent/venv/bin/python` (PID 685) to ensure access to Hermes Agent libraries.
- **Deletion Prerequisites**:
  1. Confirm `lsof +D /Users/androidteam/Developer/hermes-webui/.venv` returns zero matches.
  2. Verify `HERMES_WEBUI_PYTHON` or `~/.hermes/hermes-agent/venv/bin/python` continues serving PID 685 successfully.
- **Rollback Path**: `cd ~/Developer/hermes-webui && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
- **Required Owner Approval**: Hermes Maintainer.

---

## 5. Developer-Owned Environments Policy & Retention

All 9 active developer-owned environments under `~/Developer/*/.venv`:
- `agent-docs-sync` (791 MB)
- `agent-harness` (800 MB)
- `ai-harness-skills` (114 MB)
- `browser-cli` (321 MB)
- `code-daily-scan` (834 MB)
- `jira-kanban-from-spreadsheet` (267 MB)
- `openspec-store` (33 MB)
- `tdt-core` (192 MB)
- `tdt-sheets` (256 MB)

**Policy**:
1. **Developer Ownership**: These environments are strictly developer-owned and managed by `uv`. They provide instantaneous execution for testing (`uv run pytest`), linting (`uv run ruff`), and interactive development without re-sync latency.
2. **Preservation**: They **MUST NOT** be pruned or unified into a single global environment, as each repository pins specific dependency sets and tool versions compliant with `workspace-python-template`.
3. **Reproducibility**: Each environment has a verified `pyproject.toml` and `uv.lock`. If a developer wishes to reclaim space locally, they can run `rm -rf .venv && uv sync` in that specific repository at their own discretion.

---

## 6. Credential & Security Verification

- **Credential Scan Summary**: All 17 environment paths were exhaustively traversed for `.env`, credentials, or secret configuration files.
- **Zero Secrets Recorded**: Zero `.env` files and zero credential-bearing configuration files exist within any virtual environment.
- **Privacy Compliance**: All entries in `evidence/venv-inventory.json` and this document contain strictly filesystem metadata, process IDs, and non-sensitive service identifiers.

---

## 7. Verification of No-Deletion Constraint

- **Pre-Audit & Post-Audit Directory Invariant**:
  - All 10 on-disk Developer repository `.venv` directories remain completely intact.
  - All 4 legacy `~/.tdt/venvs/*` directories remain completely intact.
  - The live deployment at `~/.tdt/deployments/ai-review/app/.venv` remains completely intact and operating.
- **Git Status**: Zero files modified or deleted across all workspace code repositories.
