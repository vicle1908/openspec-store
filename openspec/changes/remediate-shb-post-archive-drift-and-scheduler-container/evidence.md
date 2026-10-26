# Evidence: remediate-shb-post-archive-drift-and-scheduler-container

**Date:** 2026-10-26  
**Change Directory:** `/Users/androidteam/Developer/platform/openspec-store/openspec/changes/remediate-shb-post-archive-drift-and-scheduler-container`  
**Status:** Completed & 100% Verified  

---

## 1. Live `shb-schedule-scheduler-1` Container Verification (`D1`)

### Container Health & Image Status
Command: `docker ps --filter "name=shb-schedule" --format "table {{.Names}}	{{.Image}}	{{.Status}}	{{.Ports}}"`  
Output:
```
NAMES                      IMAGE                  STATUS                  PORTS
shb-schedule-scheduler-1   shb-scheduler:latest   Up 21 hours (healthy)   127.0.0.1:9110->9110/tcp
shb-schedule-db-1          postgres:18.6-alpine   Up 3 days (healthy)     5432/tcp
```

### Schedule Schema & Rejection Gate Verification
1. **GET `/scheduler/schedules/workstation-daily-update`**:
   ```bash
   curl -s http://127.0.0.1:9110/scheduler/schedules/workstation-daily-update
   ```
   Output:
   ```json
   {
     "name": "workstation-daily-update",
     "version": "shb-schedule/v1",
     "owner": "platform-team",
     "cron": "0 8 * * *",
     "timezone": "Asia/Ho_Chi_Minh",
     "workflow": "workstation-daily-update",
     "queue": "default",
     "timeout_seconds": 3600,
     "automatic_backfill": false,
     "execution_target": "host",
     "persisted": false,
     "retry": {
       "max_attempts": 2,
       "backoff_seconds": 120
     }
   }
   ```
   - Confirms `execution_target: "host"` and `persisted: false` are exposed.

2. **POST `/scheduler/schedules/workstation-daily-update/trigger`**:
   ```bash
   curl -s -w "\nHTTP_STATUS: %{http_code}\n" -X POST http://127.0.0.1:9110/scheduler/schedules/workstation-daily-update/trigger
   ```
   Output:
   ```json
   {
     "error": "Schedule 'workstation-daily-update' has execution_target='host' and is not persisted in this runtime environment",
     "name": "workstation-daily-update",
     "execution_target": "host",
     "persisted": false,
     "triggered": false
   }
   HTTP_STATUS: 409
   ```
   - Confirms HTTP 409 rejection for host-targeted scheduled jobs.

---

## 2. Working Tree & Knowledge Refresh Verification (`D9`)

### Clean Source Code & Working Trees across SHB Repositories
- Source and test files across all 13 SHB repositories (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`, `shb-tools`, `shb-schedule`, `shb-webhook-receiver`, `shb-browser-cli`, `shb-jira-tools`) are clean and committed.
- Canonical test suites passing: `uv run pytest -v` (e.g. 73 passed in `shb-schedule`, 100% passing across SHB suites).
- Code hygiene: `uv run ruff check` and `uv run mypy src/ tests/` pass with zero errors.

### TDT Agent Core Hygiene
- Reconciled working tree in `/Users/androidteam/Developer/tdt/agent-core`: committed `.gitnexusignore` and `.graphifyignore` (`1d6ac78 chore: reconcile knowledge index ignore and graphify artifacts`).

### Knowledge Freshness Verification across all 13 SHB Repositories
Command: `/Users/androidteam/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh --check | grep "shb-"`  
Output:
```
shb-core                        FRESH         FRESH         7256c44
shb-agent-core                  FRESH         FRESH         d780ceb
shb-browser-cli                 FRESH         FRESH         0d9b3b9
shb-tools                       FRESH         FRESH         79f9488
shb-agent-harness               FRESH         FRESH         2c53f54
shb-ai-harness-skills           FRESH         FRESH         b855f4e
shb-agent-skills                FRESH         FRESH         3cb343c
shb-ai-review                   FRESH         FRESH         12b82ee
shb-webhook-receiver            FRESH         FRESH         e86ad68
shb-jira-tools                  FRESH         FRESH         3d00885
shb-mcp-servers                 FRESH         FRESH         f49ffac
shb-observability               FRESH         FRESH         71a726b
shb-schedule                    FRESH         FRESH         50f15bd
```
- **Result**: 13/13 SHB repositories are **`FRESH`** in both GitNexus (1.6.12) and Graphify (0.9.95).

---

## 3. Archive Range Readiness & Immutability Ledger (`D7` & `D10`)

### Archive Range Validation
Command: `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/validate-archive-readiness.py --range HEAD~35..HEAD --store /Users/androidteam/Developer/platform/openspec-store --strict`  
Output:
```
Range audit: validating 26 archived changes in HEAD~35..HEAD...
Range audit PASSED: all newly archived changes satisfy readiness criteria.
```
- **Exit Code**: `0`.
- All 26 archived changes within the 35-commit range satisfy immutable archive and evidence criteria.

---

## 4. OpenSpec Store Validation
- `openspec validate remediate-shb-post-archive-drift-and-scheduler-container --strict --store openspec-store` → **PASS** (0 errors).
- `openspec validate --all --store openspec-store` → **446 passed, 0 failed**.
