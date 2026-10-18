#!/bin/bash
# omniroute-watchdog.sh — Periodic health monitor and auto-recovery for OmniRoute stacks.
# Designed for launchd StartInterval execution (fail-closed, minimal overhead).

set -euo pipefail

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:${HOME}/.local/bin"

OMNIROUTE_DIR="${HOME}/Omniroute"
DOCKER_SERVICE="${HOME}/Developer/scripts/docker-service.sh"
LOG_FILE="${HOME}/.omniroute/watchdog.log"

mkdir -p "$(dirname "$LOG_FILE")"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

# 1. Verify Docker daemon responsiveness
if ! docker info >/dev/null 2>&1; then
  log "WARNING: Docker daemon not responding. Attempting to start via docker-service.sh..."
  if [[ -x "$DOCKER_SERVICE" ]]; then
    "$DOCKER_SERVICE" start >> "$LOG_FILE" 2>&1 || true
  fi
  if ! docker info >/dev/null 2>&1; then
    log "ERROR: Docker daemon remains unreachable. Aborting cycle."
    exit 1
  fi
  log "Docker daemon restored successfully."
fi

# 2. Check OmniRoute healthz endpoint
omni_status=$(docker inspect omniroute --format '{{.State.Status}}' 2>/dev/null || echo "missing")
omni_health=$(docker inspect omniroute --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' 2>/dev/null || echo "none")

if [[ "$omni_status" != "running" ]] || { [[ "$omni_health" != "starting" ]] && ! curl -fsS -m 10 http://127.0.0.1:20128/healthz >/dev/null 2>&1; }; then
  if [[ "$omni_status" == "running" ]]; then
    log "WARNING: OmniRoute (status=$omni_status health=$omni_health) unreachable or unhealthy. Restarting container..."
    if [[ -d "$OMNIROUTE_DIR" ]]; then
      (cd "$OMNIROUTE_DIR" && docker compose restart omniroute-base) >> "$LOG_FILE" 2>&1 || {
        log "ERROR: Failed to restart OmniRoute container."
      }
    fi
  else
    log "WARNING: OmniRoute (status=$omni_status health=$omni_health) not running. Bringing up stack..."
    if [[ -d "$OMNIROUTE_DIR" ]]; then
      (cd "$OMNIROUTE_DIR" && docker compose --profile base up -d) >> "$LOG_FILE" 2>&1 || {
        log "ERROR: Failed to run docker compose up for OmniRoute."
      }
      if [[ -x "$OMNIROUTE_DIR/scripts/ensure-muse-wire-compat.sh" ]]; then
        "$OMNIROUTE_DIR/scripts/ensure-muse-wire-compat.sh" >> "$LOG_FILE" 2>&1 || {
          log "WARNING: ensure-muse-wire-compat.sh returned non-zero"
        }
      fi
    fi
  fi
fi

exit 0
