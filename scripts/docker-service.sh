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
export HOME="${HOME:-/Users/androidteam}"

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

is_socket_helper_up() {
  local target_user="${USER:-$(id -un)}"
  [[ -f "/Library/LaunchDaemons/com.docker.socket.plist" ]] && \
  grep -q "<string>${target_user}</string>" "/Library/LaunchDaemons/com.docker.socket.plist" 2>/dev/null && \
  [[ -x "/Library/PrivilegedHelperTools/com.docker.socket" ]] && \
  [[ -L "/var/run/docker.sock" ]] && [[ "$(readlink /var/run/docker.sock 2>/dev/null)" == "${socket_path}" ]]
}

ensure_helpers() {
  local install_bin="/Applications/Docker.app/Contents/MacOS/install"
  local app_socket="/Applications/Docker.app/Contents/MacOS/com.docker.socket"
  local target_user="${USER:-$(id -un)}"
  [[ -x "$install_bin" ]] || return 0
  if ! is_socket_helper_up || \
     ! sudo -n cmp -s "$app_socket" "/Library/PrivilegedHelperTools/com.docker.socket" 2>/dev/null; then
    log "Provisioning Docker Desktop privileged helper (com.docker.socket) via sudo non-interactively..."
    sudo -n "$install_bin" remove-vmnetd >/dev/null 2>&1 || true
    sudo -n "$install_bin" config --user "$target_user" >/dev/null 2>&1 || true
    sudo -n "$install_bin" socket-symlink-on-startup --user "$target_user" >/dev/null 2>&1 || true
    sudo -n launchctl kickstart -p system/com.docker.socket >/dev/null 2>&1 || true
    sudo -n ln -sfn "$socket_path" /var/run/docker.sock >/dev/null 2>&1 || true
  fi
  local priv_dir
  for priv_dir in /tmp/docker-desktop-privileged*; do
    [[ -d "$priv_dir" ]] || continue
    if pgrep -f "$priv_dir" >/dev/null 2>&1; then
      echo 0 > "$priv_dir/exitcode.txt" 2>/dev/null || true
      pkill -f "$priv_dir" 2>/dev/null || true
      sleep 1
    fi
    rm -f "$priv_dir/exitcode.txt" "$priv_dir/cmd" 2>/dev/null || true
    rmdir "$priv_dir" 2>/dev/null || true
  done
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

  local helpers_socket="false"
  is_socket_helper_up && helpers_socket="true"
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

  printf '{"status":"%s","session_id":"%s","socket_exists":%s,"socket_path":"%s","context":"desktop-linux","helpers":{"socket":%s},"stacks":%s}\n' \
    "${status}" "${session_id}" "${socket_exists}" "${socket_path}" "${helpers_socket}" "${stacks_json}"
}

cmd_start() {
  local timeout_sec="${1:-$DOCKER_TIMEOUT_SEC}"
  log "Starting Docker Desktop..."
  ensure_helpers
  if is_daemon_up; then
    echo "✓ Daemon already running."
    return 0
  fi

  echo "Starting Docker Desktop... (timeout ${timeout_sec}s)"
  log "Invoking: docker desktop start --timeout $timeout_sec"
  if ! docker desktop start --timeout "$timeout_sec"; then
    if ! pgrep -x com.docker.backend >/dev/null 2>&1 && ! is_daemon_up; then
      echo "✗ Failed to start Docker Desktop within ${timeout_sec}s."
      log "Start failed after ${timeout_sec}s."
      return 1
    fi
    log "com.docker.backend is active; continuing to wait for socket reachability..."
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
    (cd "$stack_dir" && docker compose ${profile_args[@]+"${profile_args[@]}"} --project-directory . down --timeout "$timeout_sec")
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
    (cd "$stack_dir" && docker compose ${profile_args[@]+"${profile_args[@]}"} --project-directory . up -d)
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
  ensure_helpers
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

    local socket_proc="down"
    if is_socket_helper_up; then
      if [[ -L "/var/run/docker.sock" ]] && [[ "$(readlink /var/run/docker.sock 2>/dev/null)" == "${socket_path}" ]]; then
        socket_proc="active (symlink verified)"
      else
        socket_proc="up"
      fi
    fi
    printf 'Docker Desktop Status:\n'
    printf '  Status: %s\n' "$status"
    printf '  Session ID: %s\n' "$session_id"
    printf '  Socket: %s (exists=%s)\n' "$socket_path" "${socket_exists}"
    printf '  Context: desktop-linux\n'
    printf '  Helpers:\n'
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
    if [[ "$socket_proc" == "down" ]]; then
      echo "Helper Remediation: sudo -n /Applications/Docker.app/Contents/MacOS/install config --user ${USER:-$(id -un)}"
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
