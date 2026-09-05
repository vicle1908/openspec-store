# Deployment Provenance Inventory & Reconciliation Evidence

- **Change:** `reconcile-runtime-deployment-provenance`
- **Audit Timestamp (UTC):** `2026-09-05T15:32:00Z`
- **Auditor:** Automated worker agent under OpenSpec governance
- **Credential Verification:** Both deployment manifests and launchd plist configurations were verified to contain **zero credential, password, secret, token, or private key values**.

---

## 1. Inventory of Provenance Artifacts

| Artifact Path | Owner | Mode | Size | Last Modified (UTC) |
|---|---|---|---|---|
| `~/.tdt/deployments/ai-review/state/deployment-manifest.json` | `androidteam:staff` | `-rw-r--r--` | 1649 B | 2026-09-05 08:24:46 |
| `~/.tdt/deployments/webhook-receiver/state/deployment-manifest.json` | `androidteam:staff` | `-rw-r--r--` | 2825 B | 2026-08-24 05:05:32 |
| `~/Library/LaunchAgents/com.tdt.ai-review.plist` | `androidteam:staff` | `-rw-r--r--` | 1477 B | 2026-09-05 08:38:30 |
| `~/Library/LaunchAgents/com.tdt.webhook-receiver.plist` | `androidteam:staff` | `-rw-r--r--` | 1235 B | 2026-08-27 05:57:27 |

All 4 artifacts exist, are owned by `androidteam:staff`, and are readable/writable.

---

## 2. Comparison with Live Processes and Ports

### 2.1 Service `com.tdt.ai-review`
- **LaunchAgent Label:** `com.tdt.ai-review`
- **Launchd PID:** `66918` (exit status 0)
- **Live Process Command:** `/Users/androidteam/.tdt/deployments/ai-review/app/.venv/bin/python /Users/androidteam/.tdt/deployments/ai-review/app/.venv/bin/uvicorn ai_review.api.app:app --host 127.0.0.1 --port 8090 --log-level info`
- **Listening Port:** `8090` (LISTEN, verified with `lsof -iTCP:8090 -sTCP:LISTEN -nP`)
- **Health Check:** `http://127.0.0.1:8090/health` → `200 OK` (`{"status":"ok"}`)
- **Manifest Comparisons:**
  - `port`: 8090 (matches)
  - `process_command`: matches live executable path (`~/.tdt/deployments/ai-review/...`)
  - `deployment_root`: `~/.tdt/deployments/ai-review` (matches)
  - `installed_plist`: `~/Library/LaunchAgents/com.tdt.ai-review.plist` (matches)
  - `pid`: Manifest records `28405`; live is `66918` (stale from pre-migration process).
  - `source_root`: Manifest records `/Users/androidteam/Developer/ai-review-deploy-source-c35ee68` (path does not exist; canonical source is `/Users/androidteam/Developer/ai-review`).

### 2.2 Service `com.tdt.webhook-receiver`
- **LaunchAgent Label:** `com.tdt.webhook-receiver`
- **Launchd PID:** `667` (exit status 0)
- **Live Process Command:** `/Users/androidteam/.tdt/deployments/webhook-receiver/app/.venv/bin/python /Users/androidteam/.tdt/deployments/webhook-receiver/app/.venv/bin/uvicorn webhook_receiver.api.app:create_app --factory --host 127.0.0.1 --port 8080 --log-level info`
- **Listening Port:** `8080` (LISTEN, verified with `lsof -iTCP:8080 -sTCP:LISTEN -nP`)
- **Manifest Comparisons:**
  - `port`: 8080 (matches)
  - `process_command`: matches live executable path (`~/.tdt/deployments/webhook-receiver/...`)
  - `deployment_root`: `~/.tdt/deployments/webhook-receiver` (matches)
  - `installed_plist`: `~/Library/LaunchAgents/com.tdt.webhook-receiver.plist` (matches)
  - `source_root`: `/Users/androidteam/Developer/webhook-receiver` (matches canonical external source)
  - `pid`: Manifest records `661`; live is `667` (stale PID from earlier launch).
  - `workspace_root`: Manifest records `/Users/androidteam/Developer/tdt` (retired in `root-cleanup-residual`; governed workspace root is `/Users/androidteam/.tdt`).

---

## 3. Discrepancies Summary

| Service | Field | Manifest Value | Live / Reconciled Value | Reason / Classification |
|---|---|---|---|---|
| `ai-review` | `pid` | `28405` | `66918` | Stale PID from before migration to `~/.tdt` |
| `ai-review` | `source_root` | `/Users/androidteam/Developer/ai-review-deploy-source-c35ee68` | `/Users/androidteam/Developer/ai-review` | Temporary deployment source directory removed post-deploy; canonical source is `~/Developer/ai-review` |
| `webhook-receiver` | `pid` | `661` | `667` | Stale PID from earlier launchd restart |
| `webhook-receiver` | `workspace_root` | `/Users/androidteam/Developer/tdt` | `/Users/androidteam/.tdt` | `~/Developer/tdt` was retired in `root-cleanup-residual`; governed workspace is `~/.tdt` |

---

## 4. Reconciled Plan

Only stale, non-secret provenance fields will be updated:
1. In `~/.tdt/deployments/ai-review/state/deployment-manifest.json`:
   - Update `"pid": 66918`
   - Update `"source_root": "/Users/androidteam/Developer/ai-review"`
2. In `~/.tdt/deployments/webhook-receiver/state/deployment-manifest.json`:
   - Update `"pid": 667`
   - Update `"workspace_root": "/Users/androidteam/.tdt"`
3. Verify both files parse as valid JSON and contain zero secrets.
4. Verify both live services remain active, healthy, and undisturbed on ports 8090 and 8080.
