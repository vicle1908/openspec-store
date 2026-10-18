#!/bin/bash
# docker-service.sh — Official Docker Desktop lifecycle wrapper for this macOS workstation.
# 
# Usage:
#   ./docker-service.sh start [--timeout SECONDS]     # Start daemon if down
#   ./docker-service.sh stop [-f|--force]             # Stop daemon (drain stacks first)
#   ./docker-service.sh restart                       # Restart daemon (drain -> restart)
#   ./docker-service.sh status [--json]               # Print daemon status
#   ./docker-service.sh drain                         # Drain registered compose stacks only
#
# Environment:
#   DOCKER_TIMEOUT_SEC  Defaults to 90 for start/restart, 65 for stop/drain
#   LOG_DIR             Defaults to ~/Library/Logs/docker-service

set -euo pipefail

SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCKER_TIMEOUT_SEC="${DOCKER_TIMEOUT_SEC:-90}"
LOG_DIR="${HOME}/Library/Logs/docker-service"
COMPOSE_STACKS=(
  "/Users/androidteam/Omniroute"
  "/Users/androidteam/Developer/shb/shb-schedule"
)

mkdir -p "$LOG_DIR"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_DIR/service.log"; }
usage() {
  cat <<EOF
Usage: $SCRIPT_NAME <command> [options]
Commands:
  start     Start Docker Desktop daemon if not already running
  stop      Stop Docker Desktop (drains known compose stacks before shutdown)
  restart   Restart Docker Desktop (drains stacks then restarts)
  status    Report Docker Desktop health and helper state
  drain     Drain all registered compose stacks without stopping Docker Desktop
  up        Bring up all registered compose stacks
Options:
  --timeout SEC       Override timeout in seconds (default: ${DOCKER_TIMEOUT_SEC})
  -f, --force         Force stop on graceful stop timeout
  --json              Output JSON instead of human-readable status
EOF
  exit "${1:-0}"
}

socket_path="${HOME}/.docker/run/docker.sock"
is_daemon_up() {
  docker info >/dev/null 2>&1
}

status_json() {
  local session_id="-" status="stopped"
  local json_status
  if json_status=$(docker desktop status --format json 2>/dev/null) && [[ -n "$json_status" ]]; then
    session_id=$(echo "$json_status" | tr -d '\n' | sed -n 's/.*"SessionID"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    status=$(echo "$json_status" | tr -d '\n' | sed -n 's/.*"Status"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    [[ -z "$session_id" ]] && session_id="-"
    [[ -z "$status" ]] && status="stopped"
  fi

  local helpers_vmnetd="false" helpers_socket="false"
  pgrep -x com.docker.vmnetd >/dev/null 2>&1 && helpers_vmnetd="true"
  if [[ -L "/var/run/docker.sock" ]] && [[ "$(readlink /var/run/docker.sock 2>/dev/null)" == *"${socket_path}"* ]]; then
    helpers_socket="true"
  elif pgrep -x com.docker.socket >/dev/null 2>&1; then
    helpers_socket="true"
  fi
  local socket_exists=false
  [[ -S "$socket_path" ]] && socket_exists=true

  local daemon_up=false
  is_daemon_up && daemon_up=true

  local stacks_json="["
  local first=true
  for stack_dir in "${COMPOSE_STACKS[@]}"; do
    local stack_exists=false
    local running_count=0
    if [[ -d "$stack_dir" ]]; then
      stack_exists=true
      if [[ "$daemon_up" == "true" ]]; then
        running_count=$(docker compose --project-directory "$stack_dir" ps -q 2>/dev/null | wc -l | tr -d ' ')
        [[ -z "$running_count" ]] && running_count=0
      fi
    fi
    if [[ "$first" == "true" ]]; then
      first=false
    else
      stacks_json="${stacks_json},"
    fi
    stacks_json="${stacks_json}{\"path\":\"$stack_dir\",\"exists\":$stack_exists,\"running_containers\":$running_count}"
  done
  stacks_json="${stacks_json}]"

  printf '{"status":"%s","session_id":"%s","socket_exists":%s,"socket_path":"%s","context":"desktop-linux","helpers":{"vmnetd":%s,"socket":%s},"stacks":%s}\n' \
    "${status}" "${session_id}" "${socket_exists}" "${socket_path}" "${helpers_vmnetd}" "${helpers_socket}" "${stacks_json}"
}

cmd_start() {
  local timeout_sec="${1:-$DOCKER_TIMEOUT_SEC}"
  log "Starting Docker Desktop..."
  if is_daemon_up; then
    echo "✓ Daemon already running."
    return 0
  fi

  echo "Starting Docker Desktop... (timeout ${timeout_sec}s)"
  log "Invoking: docker desktop start --timeout $timeout_sec"
  if ! docker desktop start --timeout "$timeout_sec"; then
    echo "✗ Failed to start Docker Desktop within ${timeout_sec}s."
    log "Start failed after ${timeout_sec}s."
    return 1
  fi

  log "Waiting for socket reachability..."
  local waited=0
  while ((waited < timeout_sec)); do
    if is_daemon_up; then
      echo "✓ Docker daemon started successfully."
      return 0
    fi
    sleep 5
    ((waited += 5))
  done

  echo "✗ Timeout: Docker daemon did not become responsive within ${timeout_sec}s."
  log "Timeout waiting for daemon after docker desktop start."
  return 1
}

cmd_drain() {
  local timeout_sec="${1:-65}"
  log "Draining compose stacks with timeout ${timeout_sec}s..."
  local drained_any=false
  for stack_dir in "${COMPOSE_STACKS[@]}"; do
    if [[ ! -d "$stack_dir" ]]; then
      echo "⚠ Stack directory missing: $stack_dir (skipping)"
      log "Stack directory missing: $stack_dir"
      continue
    fi
    echo "Draining stack at $stack_dir..."
    local profile_args=()
    if [[ "$stack_dir" == *"/Omniroute"* ]]; then
      profile_args=(--profile base)
    fi
    log "Running: docker compose ${profile_args[*]:-} --project-dir $stack_dir down --timeout $timeout_sec"
    (cd "$stack_dir" && docker compose "${profile_args[@]}" --project-directory . down --timeout "$timeout_sec")
    drained_any=true
  done
  if $drained_any; then
    echo "✓ All registered stacks drained."
  else
    echo "✓ No stacks active or configured."
  fi
}
cmd_up() {
  log "Starting registered compose stacks..."
  local up_any=false
  for stack_dir in "${COMPOSE_STACKS[@]}"; do
    if [[ ! -d "$stack_dir" ]]; then
      echo "⚠ Stack directory missing: $stack_dir (skipping)"
      log "Stack directory missing: $stack_dir"
      continue
    fi
    echo "Bringing up stack at $stack_dir..."
    local profile_args=()
    if [[ "$stack_dir" == *"/Omniroute"* ]]; then
      profile_args=(--profile base)
    fi
    log "Running: docker compose ${profile_args[*]:-} --project-dir $stack_dir up -d"
    (cd "$stack_dir" && docker compose "${profile_args[@]}" --project-directory . up -d)
    if [[ "$stack_dir" == *"/Omniroute"* ]] && [[ -x "$stack_dir/scripts/ensure-muse-wire-compat.sh" ]]; then
      log "Running: $stack_dir/scripts/ensure-muse-wire-compat.sh"
      "$stack_dir/scripts/ensure-muse-wire-compat.sh" || log "WARNING: ensure-muse-wire-compat.sh returned non-zero"
    fi
    up_any=true
  done
  if $up_any; then
    echo "✓ All registered stacks up."
  else
    echo "✓ No stacks active or configured."
  fi
}


cmd_stop() {
  local force="${1:-false}"
  local timeout_sec="${2:-65}"
  log "Stopping Docker Desktop... (draining first)"
  cmd_drain "$timeout_sec"
  echo "Stopping Docker Desktop..."
  log "Invoking: docker desktop stop --timeout $timeout_sec"
  if ! docker desktop stop --timeout "$timeout_sec"; then
    if [[ "$force" == "true" ]]; then
      echo "⚠ Graceful stop timed out; forcing..."
      log "Forcing stop via docker desktop stop --force"
      docker desktop stop --force
    else
      echo "✗ Stop timed out; use --force if needed."
      return 1
    fi
  fi

  log "Verifying socket closure..."
  sleep 2
  if [[ -S "$socket_path" ]] || is_daemon_up; then
    echo "✗ Docker daemon still appears active; verify manually."
    return 1
  fi
  echo "✓ Docker Desktop stopped."
  return 0
}

cmd_restart() {
  local timeout_sec="${1:-90}"
  log "Restarting Docker Desktop..."
  cmd_drain 65
  echo "Restarting Docker Desktop..."
  log "Invoking: docker desktop restart --timeout $timeout_sec"
  docker desktop restart --timeout "$timeout_sec"
  if is_daemon_up; then
    echo "✓ Docker Desktop restarted."
    cmd_up
    return 0
  else
    echo "✗ Docker daemon not reachable after restart."
    return 1
  fi
}

cmd_status() {
  local as_json="${1:-false}"
  if [[ "$as_json" == "--json" ]]; then
    status_json
  else
    local json_data session_id status
    json_data=$(docker desktop status --format json 2>/dev/null || echo '{"Status":"unknown"}')
    session_id=$(echo "$json_data" | tr -d '\n' | sed -n 's/.*"SessionID"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    status=$(echo "$json_data" | tr -d '\n' | sed -n 's/.*"Status"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    [[ -z "$session_id" ]] && session_id="-"
    [[ -z "$status" ]] && status="stopped"

    local socket_exists=false
    [[ -S "$socket_path" ]] && socket_exists=true

    local vmnetd="down" socket_proc="down"
    pgrep -x com.docker.vmnetd >/dev/null 2>&1 && vmnetd="up"
    if [[ -L "/var/run/docker.sock" ]] && [[ "$(readlink /var/run/docker.sock 2>/dev/null)" == *"${socket_path}"* ]]; then
      socket_proc="active (symlink verified)"
    elif pgrep -x com.docker.socket >/dev/null 2>&1; then
      socket_proc="up"
    fi
    printf 'Docker Desktop Status:\n'
    printf '  Status: %s\n' "$status"
    printf '  Session ID: %s\n' "$session_id"
    printf '  Socket: %s (exists=%s)\n' "$socket_path" "${socket_exists}"
    printf '  Context: desktop-linux\n'
    printf '  Helpers:\n'
    printf '    com.docker.vmnetd: %s\n' "$vmnetd"
    printf '    com.docker.socket: %s\n' "$socket_proc"

    printf '  Registered Stacks:\n'
    local daemon_up=false
    is_daemon_up && daemon_up=true
    for stack_dir in "${COMPOSE_STACKS[@]}"; do
      local running_count=0
      if [[ -d "$stack_dir" ]] && [[ "$daemon_up" == "true" ]]; then
        running_count=$(docker compose --project-directory "$stack_dir" ps -q 2>/dev/null | wc -l | tr -d ' ')
        [[ -z "$running_count" ]] && running_count=0
      fi
      if [[ ! -d "$stack_dir" ]]; then
        printf '    %s: missing\n' "$stack_dir"
      else
        printf '    %s: %s running\n' "$stack_dir" "$running_count"
      fi
    done
    if [[ "$status" != "running" ]] || [[ "$socket_exists" == "false" ]]; then
      echo "Remediation: run '$SCRIPT_NAME start'"
    fi
  fi
}

case "${1:-help}" in
  start)
    shift; cmd_start "${1:-$DOCKER_TIMEOUT_SEC}" ;;
  stop)
    shift; force="false"; timeout_sec=65
    while [[ $# -gt 0 ]]; do case "$1" in -f|--force) force="true"; shift;; *) timeout_sec="$1"; shift;; esac; done
    cmd_stop "$force" "$timeout_sec" ;;
  restart)
    shift; cmd_restart "${DOCKER_TIMEOUT_SEC}" ;;
  status)
    shift; cmd_status "${1:-""}" ;;
  drain)
    shift; cmd_drain "${1:-65}" ;;
  up)
    shift; cmd_up ;;
  help|--help|-h|*) usage ;;
esac
