#!/bin/bash
# omniroute-watchdog.sh — Periodic health monitor and auto-recovery for OmniRoute stacks.
# Designed for launchd StartInterval execution (fail-closed, minimal overhead).

set -euo pipefail

export PATH="${HOME}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

OMNIROUTE_DIR="${HOME}/Omniroute"
DOCKER_SERVICE="${HOME}/Developer/scripts/docker-service.sh"
LOG_FILE="${HOME}/.omniroute/watchdog.log"
LOCK_FILE="${HOME}/.omniroute/update.lock"
INTEGRITY_MARKER="${HOME}/.omniroute/integrity-last-ok"
INTEGRITY_INTERVAL_SEC=21600

mkdir -p "$(dirname "$LOG_FILE")"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

# 0. Acquire non-blocking maintenance/update lock (~/.omniroute/update.lock)
# Uses macOS native /usr/bin/lockf (BSD flock(2)) on persistent fd 9 held until
# process exit. File contents and mtime are ignored; the lock file is never unlinked.
umask 077
if ! (: >>"$LOCK_FILE") 2>/dev/null; then
  log "ERROR: Cannot open maintenance lock file at $LOCK_FILE. Aborting cycle."
  exit 1
fi
exec 9>>"$LOCK_FILE"
lock_rc=0
/usr/bin/lockf -s -t 0 9 || lock_rc=$?
if [[ "$lock_rc" -ne 0 ]]; then
  if [[ "$lock_rc" -eq 75 ]]; then
    log "INFO: Maintenance lock active at $LOCK_FILE. Skipping watchdog cycle."
    exit 0
  fi
  log "ERROR: Failed to acquire maintenance lock at $LOCK_FILE (rc=$lock_rc). Aborting cycle."
  exit "$lock_rc"
fi

# 1. Verify Docker daemon responsiveness
if ! docker info >/dev/null 2>&1 9>&-; then
  log "WARNING: Docker daemon not responding. Attempting to start via docker-service.sh..."
  if [[ -x "$DOCKER_SERVICE" ]]; then
    "$DOCKER_SERVICE" start >> "$LOG_FILE" 2>&1 9>&- || true
  fi
  if ! docker info >/dev/null 2>&1 9>&-; then
    log "ERROR: Docker daemon remains unreachable. Aborting cycle."
    exit 1
  fi
  log "Docker daemon restored successfully."
fi

# 2. Check OmniRoute healthz endpoint
omni_status=$(docker inspect omniroute --format '{{.State.Status}}' 2>/dev/null 9>&- || echo "missing")
omni_health=$(docker inspect omniroute --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' 2>/dev/null 9>&- || echo "none")

if [[ "$omni_status" != "running" ]] || { [[ "$omni_health" != "starting" ]] && ! curl -fsS -m 10 http://127.0.0.1:20128/healthz >/dev/null 2>&1 9>&-; }; then
  if [[ "$omni_status" == "running" ]]; then
    log "WARNING: OmniRoute (status=$omni_status health=$omni_health) unreachable or unhealthy. Restarting container..."
    if [[ -d "$OMNIROUTE_DIR" ]]; then
      (cd "$OMNIROUTE_DIR" && docker compose restart omniroute-base) >> "$LOG_FILE" 2>&1 9>&- || {
        log "ERROR: Failed to restart OmniRoute container."
      }
    fi
  else
    log "WARNING: OmniRoute (status=$omni_status health=$omni_health) not running. Bringing up stack..."
    if [[ -d "$OMNIROUTE_DIR" ]]; then
      (cd "$OMNIROUTE_DIR" && docker compose --profile base up -d) >> "$LOG_FILE" 2>&1 9>&- || {
        log "ERROR: Failed to run docker compose up for OmniRoute."
      }
      if [[ -x "$OMNIROUTE_DIR/scripts/ensure-muse-wire-compat.sh" ]]; then
        "$OMNIROUTE_DIR/scripts/ensure-muse-wire-compat.sh" >> "$LOG_FILE" 2>&1 9>&- || {
          log "WARNING: ensure-muse-wire-compat.sh returned non-zero"
        }
      fi
    fi
  fi
  exit 0
fi

# Do not run physical DB integrity check during container startup grace period
if [[ "$omni_health" == "starting" ]]; then
  exit 0
fi

# 3. Periodic 6-hour bounded read-only physical SQLite integrity_check
# Substitutes for in-app quick_check skipped via OMNIROUTE_SKIP_DB_HEALTHCHECK=1.
# Host gtimeout (120s) bounds the docker exec client; in-container Node supervisor
# bounds the child sqlite worker (110s SIGKILL) so no container process lingers.
# Note: better-sqlite3 { timeout: 15000 } is SQLite busy_timeout, not wall-clock.
integrity_due=true
if [[ -f "$INTEGRITY_MARKER" ]]; then
  marker_mtime=$(stat -f %m "$INTEGRITY_MARKER" 2>/dev/null || echo "")
  now_epoch=$(date +%s)
  if [[ "$marker_mtime" =~ ^[0-9]+$ ]]; then
    marker_age=$(( now_epoch - marker_mtime ))
    if [[ "$marker_age" -ge 0 ]] && [[ "$marker_age" -lt "$INTEGRITY_INTERVAL_SEC" ]]; then
      integrity_due=false
    fi
  fi
fi

if [[ "$integrity_due" == "true" ]]; then
  integrity_rc=0
  integrity_out=$(gtimeout --signal=TERM --kill-after=5s 120s docker exec omniroute node -e '
const { spawnSync } = require("child_process");
const inner = [
  "const Database = require(\"better-sqlite3\");",
  "const db = new Database(\"/app/data/storage.sqlite\", { readonly: true, fileMustExist: true, timeout: 15000 });",
  "try {",
  "  const rows = db.pragma(\"integrity_check\");",
  "  const ok = Array.isArray(rows) && rows.length > 0 && rows.every((r) => r && r.integrity_check === \"ok\");",
  "  if (!ok) { process.stdout.write(\"FAIL:integrity_check_not_ok\"); process.exit(1); }",
  "  process.stdout.write(\"ok\");",
  "} finally { db.close(); }"
].join(" ");
const res = spawnSync(process.execPath, ["-e", inner], { timeout: 110000, killSignal: "SIGKILL", encoding: "utf8" });
if (res.error && res.error.code === "ETIMEDOUT") {
  process.stdout.write("FAIL:in_container_timeout");
  process.exit(124);
}
if (res.status !== 0 || (res.stdout || "").trim() !== "ok") {
  process.stdout.write((res.stdout || "").trim() || ("FAIL:status=" + res.status));
  process.exit(res.status || 1);
}
process.stdout.write("ok");
' 2>/dev/null 9>&-) || integrity_rc=$?
  if [[ "$integrity_rc" -ne 0 ]] || [[ "$integrity_out" != "ok" ]]; then
    [[ "$integrity_rc" -ne 0 ]] || integrity_rc=1
    log "ERROR: Periodic SQLite physical integrity_check failed (rc=$integrity_rc, summary=${integrity_out:-error}). Leaving running gateway untouched."
    exit "$integrity_rc"
  fi
  : > "$INTEGRITY_MARKER"
  log "INFO: Periodic SQLite physical integrity_check passed (ok). Updated $INTEGRITY_MARKER."
fi

exit 0
