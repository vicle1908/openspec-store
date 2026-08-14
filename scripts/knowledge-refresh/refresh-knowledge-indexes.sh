#!/usr/bin/env bash
#
# Central knowledge index refresh script.
# Iterates the approved inventory, refreshing GitNexus and Graphify indexes
# for each repository (including eligible worktrees).
#
# Status values: success, fresh_noop, skipped_dirty, skipped_merge_state,
#   skipped_uninitialized, provider_missing, lock_busy, watcher_active,
#   timeout, failed, superseded
set -euo pipefail
export PATH="/Users/androidteam/.npm-global/bin:/Users/androidteam/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
readonly SCRIPT_DIR="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
)"
readonly OPENSPEC_ROOT="${SCRIPT_DIR}/../.."
readonly INVENTORY_FILE="${SCRIPT_DIR}/knowledge-refresh-inventory.tsv"
readonly APPROVAL_FILE="${SCRIPT_DIR}/knowledge-refresh-approval.sha256"
readonly STATE_DIR="${HOME}/Developer/.knowledge-refresh"
readonly LOG_FILE="${STATE_DIR}/refresh.log"
readonly LOCK_DIR="${STATE_DIR}/locks"
readonly GITNEXUS_TIMEOUT=300   # 5 minutes per target
readonly GITNEXUS_INDEX_EMBEDDING_DIMS=768  # nomic-embed-text local endpoint
readonly GRAPHIFY_TIMEOUT=300
readonly OVERALL_TIMEOUT=7200   # 2 hours
readonly MAX_LOG_LINES=1000
readonly WORKTREE_MAX_AGE_DAYS=30
# Return codes for process_target()
readonly RC_SUCCESS=0      # success / fresh no-op
readonly RC_SKIP=10        # policy skip (dirty, transition, uninitialized)
readonly RC_FAILURE=1      # provider or validation failure
readonly EPHEMERAL_PATH=".claude/worktrees/"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log_init() {
  mkdir -p "$STATE_DIR"
  touch "$LOG_FILE"
}

log_rotate() {
  if [[ -f "$LOG_FILE" ]]; then
    local lines
    lines="$(wc -l < "$LOG_FILE" | tr -d ' ')"
    if (( lines > MAX_LOG_LINES )); then
      local tail_count=$(( MAX_LOG_LINES / 2 ))
      local tmp
      tmp="$(mktemp "${LOG_FILE}.rotating.XXXXXX")"
      tail -n "$tail_count" "$LOG_FILE" > "$tmp"
      mv "$tmp" "$LOG_FILE"
      log_line root rotation "log_rotated" 0 "rotated from ${lines} to ${tail_count} lines"
    fi
  fi
}

log_line() {
  local repo="$1" tool="$2" status="$3" duration="${4:-0}" extra="${5:-}"
  printf '[%s] [%s] [%s] [%s] [%s] %s\n' \
    "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    "$repo" "$tool" "$status" "${duration}s" "$extra" \
    >> "$LOG_FILE"
}

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
die() { printf 'refresh: error: %s\n' "$*" >&2; exit 1; }
warn() { printf 'refresh: warning: %s\n' "$*" >&2; }
note() { printf 'refresh: %s\n' "$*"; }

redact() {
  sed -E \
    -e 's/(MCPR_TOKEN|AGENTMEMORY_URL|AGENTMEMORY_SECRET|GITNEXUS_EMBEDDING_API_KEY|GITNEXUS_MCP_AUTH_TOKEN|GITNEXUS_WIKI_API_KEY|GITHUB_TOKEN|GEMINI_API_KEY|GOOGLE_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|NEO4J_PASSWORD|FALKORDB_PASSWORD|GRAPHIFY_POSTGRES_DSN)=[^[:space:]]+/\1=REDACTED/g' \
    -e 's/((api[_-]?key|auth[_-]?token|bearer[_-]?token|password|secret|token)=)[^[:space:]]+/\1REDACTED/Ig' \
    -e 's#(https?://)[^/@[:space:]]+:[^/@[:space:]]+@#\1REDACTED@#g'
}

elapsed() {
  local start="$1"
  echo $(( $(date +%s) - start ))
}

repo_name() {
  basename "$1"
}

# PID-aware timeout: macOS-native alternative to GNU timeout.
# Usage: run_with_timeout <seconds> <command> [args...]
# Returns: child exit status, or 124 on timeout.
run_with_timeout() {
  local seconds="$1"
  shift

  local output pid elapsed=0 rc=0
  output="$(mktemp "${TMPDIR:-/tmp}/knowledge-refresh-timeout.XXXXXX")"

  "$@" >"$output" 2>&1 &
  pid=$!

  while kill -0 "$pid" 2>/dev/null; do
    if (( elapsed >= seconds )); then
      kill -TERM "$pid" 2>/dev/null || true
      sleep 5
      kill -KILL "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
      cat "$output"
      rm -f "$output"
      return 124
    fi
    sleep 1
    elapsed=$((elapsed + 1))
  done

  wait "$pid" || rc=$?
  cat "$output"
  rm -f "$output"
  return "$rc"
}

# ---------------------------------------------------------------------------
# Inventory validation
# ---------------------------------------------------------------------------
validate_inventory() {
  [[ -f "$INVENTORY_FILE" ]] || die "inventory not found: ${INVENTORY_FILE}"
  [[ -f "$APPROVAL_FILE" ]] || die "approval digest not found: ${APPROVAL_FILE}"

  local actual_digest
  actual_digest="$(shasum -a 256 "$INVENTORY_FILE" | awk '{print $1}')"
  local expected_digest
  expected_digest="$(head -1 "$APPROVAL_FILE" | awk '{print $1}')"

  if [[ "$actual_digest" != "$expected_digest" ]]; then
    die "inventory SHA-256 mismatch (expected=${expected_digest} actual=${actual_digest}); inventory is not approved"
  fi

  local root branch gitnexus_enabled graphify_enabled canonical_root
  while IFS=$'\t' read -r root branch gitnexus_enabled graphify_enabled; do
    [[ "$root" =~ ^#.*$ || -z "$root" ]] && continue
    case "$root" in
      "$HOME/Developer"/*) ;;
      *) die "inventory path is outside approved workspace: ${root}" ;;
    esac
    [[ -d "$root" ]] || die "inventory repository missing: ${root}"
    is_repo "$root" || die "inventory path is not a Git repository: ${root}"
    canonical_root="$(cd "$root" 2>/dev/null && pwd)" || die "cannot canonicalize inventory path: ${root}"
    [[ "$canonical_root" == "$root" ]] || die "inventory path is not canonical: ${root} (canonical=${canonical_root})"
    [[ -n "$branch" ]] || die "inventory default branch missing: ${root}"
    git -C "$root" show-ref --verify --quiet "refs/heads/${branch}" || \
      die "inventory default branch not found: ${root} (${branch})"
  done < "$INVENTORY_FILE"
  note "inventory approved (${actual_digest:0:12}...)"
}

# ---------------------------------------------------------------------------
# Git state checks
# ---------------------------------------------------------------------------
is_repo() {
  git -C "$1" rev-parse --is-inside-work-tree >/dev/null 2>&1
}

is_dirty() {
  [[ -n "$(git -C "$1" status --porcelain=v1 --untracked-files=all 2>/dev/null)" ]]
}

is_merge_state() {
  [[ -f "$1/.git/MERGE_HEAD" ]] || \
    [[ -f "$(git -C "$1" rev-parse --git-path MERGE_HEAD 2>/dev/null)" ]] 2>/dev/null
}

is_rebase_state() {
  local git_dir
  git_dir="$(git -C "$1" rev-parse --git-dir 2>/dev/null)"
  [[ -d "${git_dir}/rebase-merge" ]] || [[ -d "${git_dir}/rebase-apply" ]]
}

# ---------------------------------------------------------------------------
# Lock management (PID-aware, never steal live locks)
# ---------------------------------------------------------------------------
lock_id() {
  local canonical_root="$1"
  printf '%s' "$canonical_root" | shasum -a 256 | awk '{print $1}'
}

acquire_lock() {
  local name="$1"
  local lock_dir="${LOCK_DIR}/${name}"

  mkdir -p "$LOCK_DIR"
  if mkdir "$lock_dir" 2>/dev/null; then
    printf '%s\t%s\t%s\t%s\n' "$$" "${USER:-unknown}" \
      "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$name" > "${lock_dir}/owner"
    return 0
  fi

  # Lock exists -- check if owner is still alive
  if [[ -f "${lock_dir}/owner" ]]; then
    local active_pid
    active_pid="$(head -1 "${lock_dir}/owner" | cut -f1)"
    if [[ "$active_pid" =~ ^[0-9]+$ ]] && kill -0 "$active_pid" 2>/dev/null; then
      # Live process holds the lock
      return 1
    fi
    # Stale lock -- remove and retry
    warn "removing stale lock: ${name}"
    rm -f "${lock_dir}/owner"
    rmdir "$lock_dir" 2>/dev/null || true
    if mkdir "$lock_dir" 2>/dev/null; then
      printf '%s\t%s\t%s\t%s\n' "$$" "${USER:-unknown}" \
        "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$name" > "${lock_dir}/owner"
      return 0
    fi
  fi
  return 1
}

release_lock() {
  local name="$1"
  local lock_dir="${LOCK_DIR}/${name}"
  rm -f "${lock_dir}/owner" 2>/dev/null || true
  rmdir "$lock_dir" 2>/dev/null || true
}

# ---------------------------------------------------------------------------
# GitNexus refresh
# ---------------------------------------------------------------------------
gitnexus_refresh() {
  local root="$1" branch="$2" name="$3"
  local start_ts status
  local lock_name="gitnexus-$(lock_id "$root")"
  local target_head="" indexed_rev="" final_head=""
  start_ts="$(date +%s)"

  # Check gitnexus availability
  if ! command -v gitnexus >/dev/null 2>&1; then
    status="provider_missing"
    note "  GitNexus: not installed for ${name}"
    log_line "$name" gitnexus "$status" "$(elapsed "$start_ts")"
    return 0
  fi

  # Check .gitnexus/ exists
  if [[ ! -d "${root}/.gitnexus" ]]; then
    status="skipped_uninitialized"
    note "  GitNexus: .gitnexus/ missing for ${name}, skipping"
    log_line "$name" gitnexus "$status" "$(elapsed "$start_ts")"
    return 0
  fi

  # Acquire workspace lock (atomic mkdir)
  if ! acquire_lock "$lock_name"; then
    status="lock_busy"
    note "  GitNexus: workspace lock busy for ${name}"
    log_line "$name" gitnexus "$status" "$(elapsed "$start_ts")"
    return 0
  fi

  start_ts="$(date +%s)"
  trap 'release_lock $lock_name' RETURN

  # Check if index is already current
  target_head="$(git -C "$root" rev-parse --verify HEAD 2>/dev/null || true)"
  if [[ -z "$target_head" ]]; then
    status="skipped_uninitialized"
    note "  GitNexus: no HEAD for ${name}"
    log_line "$name" gitnexus "$status" "$(elapsed "$start_ts")"
    release_lock $lock_name
    trap - RETURN
    return 0
  fi

  note "  GitNexus: analyzing ${name} (branch=${branch})"

  local analyze_status=0
  (
    cd "$root"
    GITNEXUS_EMBEDDING_DIMS="$GITNEXUS_INDEX_EMBEDDING_DIMS" \
    run_with_timeout "$GITNEXUS_TIMEOUT" \
      gitnexus analyze . \
        --index-only \
        --default-branch "$branch" \
        --name "$name"
  ) 2>&1 | redact || analyze_status=$?

  local dur
  dur="$(elapsed "$start_ts")"

  if [[ "$analyze_status" -eq 124 ]]; then
    status="timeout"
    warn "  GitNexus: analysis timed out for ${name} after ${GITNEXUS_TIMEOUT}s"
    log_line "$name" gitnexus "$status" "$dur" \
      "target=${target_head};indexed=${indexed_rev};final=${final_head}"
    release_lock $lock_name
    trap - RETURN
    return 0
  elif [[ "$analyze_status" -ne 0 ]]; then
    status="failed"
    warn "  GitNexus: analysis failed for ${name} (exit=${analyze_status})"
    log_line "$name" gitnexus "$status" "$dur" \
      "target=${target_head};indexed=${indexed_rev};final=${final_head}"
    release_lock $lock_name
    trap - RETURN
    return 1
  fi

  # Verify indexed revision from GitNexus metadata. The installed CLI's
  # `status` command is current-repository-only and has no --repo/--json API.
  indexed_rev="$(python3 - "${root}/.gitnexus/meta.json" \
    "${root}/.gitnexus/gitnexus.json" <<'PY'
import json
import sys
from pathlib import Path

for raw in sys.argv[1:]:
    path = Path(raw)
    if not path.is_file():
        continue
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        continue
    value = data.get("lastCommit") or data.get("current_commit") or data.get("revision")
    if isinstance(value, str) and value:
        print(value)
        break
PY
  )"

  final_head="$(git -C "$root" rev-parse --verify HEAD 2>/dev/null || true)"

  status="success"
  if [[ -n "$final_head" && "$final_head" != "$target_head" ]]; then
    status="superseded"
    warn "  GitNexus: ${name} HEAD changed during refresh (${target_head:0:12} -> ${final_head:0:12})"
  elif [[ -n "$indexed_rev" && -n "$target_head" && "$indexed_rev" == "$target_head" ]]; then
    note "  GitNexus: ${name} indexed at ${target_head:0:12}"
  elif [[ -n "$indexed_rev" && -n "$target_head" && "$indexed_rev" != "$target_head" ]]; then
    status="superseded"
    warn "  GitNexus: ${name} indexed revision ${indexed_rev:0:12} != HEAD ${target_head:0:12}"
  else
    status="fresh_noop"
    note "  GitNexus: ${name} refreshed (could not verify revision)"
  fi

  log_line "$name" gitnexus "$status" "$dur" \
      "target=${target_head};indexed=${indexed_rev};final=${final_head}"
  release_lock $lock_name
  trap - RETURN
  return 0
}

# ---------------------------------------------------------------------------
# Graphify refresh
# ---------------------------------------------------------------------------
snapshot_graph_outputs() {
  local root="$1" snapshot_dir="$2"
  local output
  mkdir -p "$snapshot_dir"
  for output in graph.json manifest.json .graphify_analysis.json GRAPH_REPORT.md; do
    if [[ -f "${root}/graphify-out/${output}" ]]; then
      cp -p "${root}/graphify-out/${output}" "${snapshot_dir}/${output}"
    fi
  done
}

restore_graph_outputs() {
  local root="$1" snapshot_dir="$2"
  local output
  for output in "$snapshot_dir"/*; do
    [[ -f "$output" ]] || continue
    cp -p "$output" "${root}/graphify-out/$(basename "$output")"
  done
}

graphify_refresh() {
  local root="$1" name="$2"
  local start_ts status
  local lock_name="graphify-$(lock_id "$root")"
  start_ts="$(date +%s)"

  # Check graphify availability
  if ! command -v graphify >/dev/null 2>&1; then
    status="provider_missing"
    note "  Graphify: not installed for ${name}"
    log_line "$name" graphify "$status" "$(elapsed "$start_ts")"
    return 0
  fi

  # Check graphify-out/ exists
  if [[ ! -d "${root}/graphify-out" ]]; then
    status="skipped_uninitialized"
    note "  Graphify: graphify-out/ missing for ${name}, skipping"
    log_line "$name" graphify "$status" "$(elapsed "$start_ts")"
    return 0
  fi

  # Check for active graphify watch process (lsof -p PID)
  local watcher_pid
  if pgrep -f "graphify watch.*${root}" >/dev/null 2>&1; then
    watcher_pid="$(pgrep -f "graphify watch.*${root}" 2>/dev/null | head -1)"
    if [[ -n "$watcher_pid" ]] && [[ "$watcher_pid" =~ ^[0-9]+$ ]]; then
      if lsof -p "$watcher_pid" >/dev/null 2>&1; then
        status="watcher_active"
        note "  Graphify: watcher_active for ${name} (PID=${watcher_pid}), skipping"
        log_line "$name" graphify "$status" "$(elapsed "$start_ts")"
        return 0
      fi
    fi
  fi

  # Acquire owner lock (atomic mkdir)
  if ! acquire_lock "$lock_name"; then
    status="lock_busy"
    note "  Graphify: lock busy for ${name}"
    log_line "$name" graphify "$status" "$(elapsed "$start_ts")"
    return 0
  fi

  start_ts="$(date +%s)"
  trap 'release_lock "$lock_name"' RETURN

  # Snapshot all usable Graphify outputs before refresh
  local backup_dir
  backup_dir="$(mktemp -d "${TMPDIR:-/tmp}/graphify-backup-${name}.XXXXXX")"
  snapshot_graph_outputs "$root" "$backup_dir"
  local had_graph=0
  if [[ -f "${backup_dir}/graph.json" ]] && \
    ! python3 -c 'import json, sys; json.load(open(sys.argv[1]))' \
      "${backup_dir}/graph.json" >/dev/null 2>&1; then
    rm -f "${backup_dir}/graph.json"
  fi
  [[ -f "${backup_dir}/graph.json" ]] && had_graph=1

  note "  Graphify: refreshing ${name}"

  local graphify_status=0
  (
    cd "$root"
    GRAPHIFY_VIZ_NODE_LIMIT=0 run_with_timeout "${GRAPHIFY_TIMEOUT}" \
      graphify update . 2>&1 | redact
  ) >> "${LOG_FILE}" 2>&1 || graphify_status=$?

  local dur
  dur="$(elapsed "$start_ts")"

  if [[ "$graphify_status" -eq 124 ]]; then
    status="timeout"
    warn "  Graphify: refresh timed out for ${name} after ${GRAPHIFY_TIMEOUT}s"
    # Restore on failure
    if [[ "$had_graph" -eq 1 ]]; then
      restore_graph_outputs "$root" "$backup_dir"
      note "  Graphify: restored output snapshot for ${name}"
    fi
    rm -rf "$backup_dir"
      log_line "$name" graphify "$status" "$dur"
    release_lock "$lock_name"
    trap - RETURN
    return 0
  elif [[ "$graphify_status" -ne 0 ]]; then
    warn "  Graphify: update failed for ${name} (exit=${graphify_status}); trying code-only repair"
    graphify_status=0
    local repair_dir
    repair_dir="$(mktemp -d "${TMPDIR:-/tmp}/graphify-repair-${name}.XXXXXX")"
    (
      cd "$root"
      GRAPHIFY_VIZ_NODE_LIMIT=0 run_with_timeout "${GRAPHIFY_TIMEOUT}" \
        graphify extract . --code-only --out "$repair_dir" 2>&1 | redact
    ) >> "${LOG_FILE}" 2>&1 || graphify_status=$?
    dur="$(elapsed "$start_ts")"

    if [[ "$graphify_status" -eq 0 ]] && \
      [[ -f "${repair_dir}/graphify-out/graph.json" ]] && \
      python3 -c 'import json, sys; json.load(open(sys.argv[1]))' \
        "${repair_dir}/graphify-out/graph.json" >/dev/null 2>&1; then
      cp -R "${repair_dir}/graphify-out/." "${root}/graphify-out/"
    elif [[ "$graphify_status" -eq 0 ]]; then
      graphify_status=1
    fi
    rm -rf "$repair_dir"

    if [[ "$graphify_status" -eq 124 ]]; then
      status="timeout"
      warn "  Graphify: repair timed out for ${name} after ${GRAPHIFY_TIMEOUT}s"
      if [[ "$had_graph" -eq 1 ]]; then
        restore_graph_outputs "$root" "$backup_dir"
      fi
      rm -rf "$backup_dir"
      log_line "$name" graphify "$status" "$dur"
      release_lock "$lock_name"
      trap - RETURN
      return 0
    elif [[ "$graphify_status" -ne 0 ]]; then
      status="failed"
      warn "  Graphify: repair failed for ${name} (exit=${graphify_status})"
      if [[ "$had_graph" -eq 1 ]]; then
        restore_graph_outputs "$root" "$backup_dir"
        note "  Graphify: restored output snapshot for ${name}"
      fi
      rm -rf "$backup_dir"
      log_line "$name" graphify "$status" "$dur"
      release_lock "$lock_name"
      trap - RETURN
      return 1
    fi
  fi

  if [[ ! -f "${root}/graphify-out/graph.json" ]] || \
    ! python3 -c 'import json, sys; json.load(open(sys.argv[1]))' \
      "${root}/graphify-out/graph.json" >/dev/null 2>&1; then
    status="failed"
    warn "  Graphify: graph.json missing or invalid for ${name}"
    if [[ "$had_graph" -eq 1 ]]; then
      restore_graph_outputs "$root" "$backup_dir"
      note "  Graphify: restored output snapshot for ${name}"
    fi
    rm -rf "$backup_dir"
      log_line "$name" graphify "$status" "$dur"
    release_lock "$lock_name"
    trap - RETURN
    return 1
  fi

  status="success"
  note "  Graphify: ${name} refreshed"
  log_line "$name" graphify "$status" "$dur"

  # Cleanup backup
  rm -rf "$backup_dir"

  release_lock "$lock_name"
  trap - RETURN
  return 0
}

# ---------------------------------------------------------------------------
# Worktree enumeration
# ---------------------------------------------------------------------------
is_ephemeral_worktree() {
  local wt_path="$1"
  [[ "$wt_path" == *"$EPHEMERAL_PATH"* ]]
}

is_stale_worktree() {
  local wt_path="$1"
  local age_days
  age_days=$(( ($(date +%s) - $(stat -f %m "$wt_path" 2>/dev/null || echo 0)) / 86400 ))
  (( age_days > WORKTREE_MAX_AGE_DAYS ))
}

has_knowledge_index() {
  local wt_path="$1"
  [[ -d "${wt_path}/.gitnexus" ]] || [[ -d "${wt_path}/graphify-out" ]]
}

refresh_worktrees() {
  local canonical_root="$1" branch="$2" name="$3"
  local gitnexus_enabled="$4" graphify_enabled="$5"

  local worktree_list
  worktree_list="$(git -C "$canonical_root" worktree list --porcelain 2>/dev/null)" || return 0

  local current_wt="" current_head="" current_branch="" detached=0
  while IFS= read -r line; do
    case "$line" in
      worktree\ *)
        current_wt="${line#worktree }"
        current_head=""
        current_branch=""
        detached=0
        ;;
      HEAD\ *)
        current_head="${line#HEAD }"
        ;;
      branch\ refs/heads/*)
        current_branch="${line#branch refs/heads/}"
        ;;
      detached)
        detached=1
        ;;
      "")
        # End of one worktree entry -- evaluate it
        if [[ -n "$current_wt" && -n "$canonical_root" ]]; then
          local wt_name
          wt_name="$(repo_name "$current_wt")-wt-$(lock_id "$current_wt" | cut -c1-8)"

          # Skip main checkout
          if [[ "$current_wt" == "$canonical_root" || "$current_wt" == "$canonical_root/" ]]; then
            current_wt=""
            continue
          fi

          # Skip detached HEAD
          if [[ "$detached" -eq 1 ]]; then
            log_line "$wt_name" worktree "skipped_detached" "0" "skipped detached HEAD"
            current_wt=""
            continue
          fi

          # Skip ephemeral worktrees
          if is_ephemeral_worktree "$current_wt"; then
            log_line "$wt_name" worktree "skipped_ephemeral" "0" "skipped ephemeral worktree"
            current_wt=""
            continue
          fi

          # Skip stale worktrees
          if is_stale_worktree "$current_wt"; then
            log_line "$wt_name" worktree "skipped_stale" "0" "skipped worktree > ${WORKTREE_MAX_AGE_DAYS} days"
            current_wt=""
            continue
          fi

          # Only refresh worktrees with existing indexes
          if ! has_knowledge_index "$current_wt"; then
            log_line "$wt_name" worktree "skipped_uninitialized" "0" "no .gitnexus/ or graphify-out/"
            current_wt=""
            continue
          fi

          note "Worktree: refreshing ${wt_name} at ${current_wt}"
          local wt_start
          wt_start="$(date +%s)"

          if [[ "$gitnexus_enabled" == "yes" ]] && [[ -d "${current_wt}/.gitnexus" ]]; then
            gitnexus_refresh "$current_wt" "${current_branch:-$branch}" "$wt_name"
          fi
          if [[ "$graphify_enabled" == "yes" ]] && [[ -d "${current_wt}/graphify-out" ]]; then
            graphify_refresh "$current_wt" "$wt_name"
          fi

          log_line "$wt_name" worktree "success" "$(elapsed "$wt_start")" "worktree refresh complete"
        fi
        current_wt=""
        ;;
    esac
  done <<< "$worktree_list"
}

# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# process_target — refresh a single inventoried repository
#
# Called by process_inventory (batch) and main() (--repo dispatch).
# Returns 0 on success, 1 on failure. Caller decides whether to abort.
# ---------------------------------------------------------------------------
process_target() {
  local canonical_root="$1"
  local branch="${2:-main}"
  local gitnexus_enabled="${3:-yes}"
  local graphify_enabled="${4:-yes}"
  local trigger="${5:-unknown}"

  local name
  name="$(repo_name "$canonical_root")"
  note "[trigger=$trigger] Processing ${name} (${canonical_root})"

  # --- Guards ---------------------------------------------------------------
  if [[ ! -d "$canonical_root" ]]; then
    warn "  Repository directory missing: ${canonical_root}"
    log_line "$name" "$trigger" "failed" "0" "directory not found"
    return $RC_SKIP
  fi

  if ! is_repo "$canonical_root"; then
    warn "  Not a git repository: ${canonical_root}"
    log_line "$name" "$trigger" "skipped_uninitialized" "0" "not a git repo"
    return $RC_SKIP
  fi

  if is_dirty "$canonical_root"; then
    note "  Skipping ${name}: working tree is dirty"
    log_line "$name" "$trigger" "skipped_dirty" "0" "uncommitted changes"
    return $RC_SKIP
  fi

  if is_merge_state "$canonical_root" || is_rebase_state "$canonical_root"; then
    note "  Skipping ${name}: merge or rebase in progress"
    log_line "$name" "$trigger" "skipped_merge_state" "0" "merge/rebase active"
    return $RC_SKIP
  fi

  local target_head
  target_head="$(git -C "$canonical_root" rev-parse --verify HEAD 2>/dev/null || true)"
  if [[ -z "$target_head" ]]; then
    note "  Skipping ${name}: no HEAD"
    log_line "$name" "$trigger" "skipped_uninitialized" "0" "no HEAD"
    return $RC_SKIP
  fi

  # --- Refresh --------------------------------------------------------------
  local target_start
  target_start="$(date +%s)"
  local target_failed=0

  if [[ "$gitnexus_enabled" == "yes" ]]; then
    gitnexus_refresh "$canonical_root" "$branch" "$name" || target_failed=1
  fi

  if [[ "$graphify_enabled" == "yes" ]]; then
    graphify_refresh "$canonical_root" "$name" || target_failed=1
  fi

  # Refresh eligible worktrees
  refresh_worktrees "$canonical_root" "$branch" "$name"     "$gitnexus_enabled" "$graphify_enabled"

  if [[ "$target_failed" -ne 0 ]]; then
    log_line "$name" "$trigger" "failed" "$(elapsed "$target_start")" "provider error"
    return $RC_FAILURE
  fi

  log_line "$name" "$trigger" "success" "$(elapsed "$target_start")"     "canonical+worktrees refresh complete"
  return 0
}

process_inventory() {
  local overall_start line_count
  overall_start="$(date +%s)"
  line_count=0
  local failed=0
  local refreshed=0 skipped=0

  while IFS=$'\t' read -r canonical_root branch gitnexus_enabled graphify_enabled; do
    # Skip comments and header lines
    [[ "$canonical_root" == \#* ]] && continue
    [[ -z "$canonical_root" ]] && continue
    [[ -z "$branch" ]] && branch="main"

    line_count=$(( line_count + 1 ))

    # Enforce overall timeout
    local elapsed_total
    elapsed_total=$(( $(date +%s) - overall_start ))
    if (( elapsed_total >= OVERALL_TIMEOUT )); then
      warn "overall timeout reached (${OVERALL_TIMEOUT}s); ${line_count} targets processed"
      log_line "SYSTEM" overall "timeout" "0" "elapsed=${elapsed_total}s"
      break
    fi

    # Delegate to process_target
    if process_target "$canonical_root" "$branch" "$gitnexus_enabled" "$graphify_enabled" "batch"; then
      refreshed=$(( refreshed + 1 ))
    else
      local ret=$?
      if [[ $ret -eq $RC_SKIP ]]; then
        skipped=$(( skipped + 1 ))
      else
        failed=$(( failed + 1 ))
      fi
    fi

  done < "$INVENTORY_FILE"

  local total_elapsed
  total_elapsed="$(elapsed "$overall_start")"
  note ""
  note "=== Refresh complete ==="
  note "Processed: ${line_count} targets"
  note "Refreshed: ${refreshed}"
  note "Skipped:   ${skipped}"
  note "Failed:    ${failed}"
  note "Duration:  ${total_elapsed}s"
  log_line "SYSTEM" overall "success" "$total_elapsed" \
    "targets=${line_count} refreshed=${refreshed} skipped=${skipped} failed=${failed}"
}

# ---------------------------------------------------------------------------
# Entry point
usage() {
  cat <<'EOF'
Usage: refresh-knowledge-indexes.sh [options]

Options:
  --repo <path>       Refresh a single inventoried repository
  --trigger <type>    Trigger type: post-merge, manual, launchd, test
  --dry-run           Validate inventory without refreshing
  --status            Show recent log entries
  --rotate            Rotate the refresh log
  --help, -h          Show this help

Without arguments, performs a full batch refresh of all inventoried repos.
EOF
}

process_single_repo() {
  local repo_path="$1"
  local trigger="${2:-manual}"

  log_init
  log_rotate

  # Canonicalize and validate
  local canonical
  canonical="$(cd "$repo_path" 2>/dev/null && pwd)" || { warn "Directory not found: $repo_path"; return 0; }

  # Validate git repo (handles worktree .git files)
  if ! git -C "$canonical" rev-parse --git-dir >/dev/null 2>&1; then
    warn "Not a git repository: $canonical"
    log_line "$(repo_name "$canonical")" "$trigger" "skipped_uninitialized" "0" "not a git repo"
    return 0
  fi

  # Lookup in inventory (exact canonical match required)
  local inv_branch="main" inv_gn="yes" inv_gf="yes" found=false
  while IFS=$'\t' read -r i_root i_branch i_gn i_gf; do
    [[ "$i_root" == \#* || -z "$i_root" ]] && continue
    local i_canonical
    i_canonical="$(cd "$i_root" 2>/dev/null && pwd)" 2>/dev/null || continue
    if [[ "$i_canonical" == "$canonical" ]]; then
      inv_branch="${i_branch:-main}"
      inv_gn="${i_gn:-yes}"
      inv_gf="${i_gf:-yes}"
      found=true
      break
    fi
  done < "$INVENTORY_FILE"

  if ! $found; then
    note "  Skipping $(repo_name "$canonical"): skipped_unlisted (not in inventory)"
    log_line "$(repo_name "$canonical")" "$trigger" "skipped_unlisted" "0" "not in inventory"
    return 0
  fi

  # For post-merge: require current branch matches inventory default
  if [[ "$trigger" == "post-merge" ]]; then
    local current_branch
    current_branch="$(git -C "$canonical" symbolic-ref --short HEAD 2>/dev/null)" || return 0
    if [[ "$current_branch" != "$inv_branch" ]]; then
      log_line "$(repo_name "$canonical")" "$trigger" "skipped_wrong_branch" "0" \
        "branch=$current_branch expected=$inv_branch"
      return 0
    fi
    # Graphify handled by existing hook
    inv_gf="no"
  fi

  # Advisory: hook must never block git operations
  if process_target "$canonical" "$inv_branch" "$inv_gn" "$inv_gf" "$trigger"; then
    return 0
  else
    local rc=$?
    log_line "$(repo_name "$canonical")" "$trigger" "failed" "0" "exit=$rc"
    return 0
  fi
}

main() {
  local mode="batch"
  local repo_path=""
  local trigger="manual"

  while (($#)); do
    case "$1" in
      --repo)
        (($# >= 2)) || die "--repo requires a path"
        repo_path="$2"
        mode="single"
        shift 2
        ;;
      --trigger)
        (($# >= 2)) || die "--trigger requires a value"
        trigger="$2"
        shift 2
        ;;
      --dry-run) mode="dry-run"; shift ;;
      --status) mode="status"; shift ;;
      --rotate) mode="rotate"; shift ;;
      --help|-h) usage; return 0 ;;
      *) usage >&2; return 2 ;;
    esac
  done

  case "$mode" in
    single)
      validate_inventory
      process_single_repo "$repo_path" "$trigger"
      ;;
    dry-run)
      note "Dry run -- validating inventory only"
      validate_inventory
      note "Inventory validation passed"
      while IFS=$'\t' read -r canonical_root branch gitnexus_enabled graphify_enabled; do
        [[ "$canonical_root" == \#* ]] && continue
        [[ -z "$canonical_root" ]] && continue
        local name
        name="$(repo_name "$canonical_root")"
        local exists="missing"
        [[ -d "$canonical_root" ]] && exists="present"
        printf '  %-30s  git=%s  graph=%s  dir=%s\n' \
          "$name" "$gitnexus_enabled" "$graphify_enabled" "$exists"
      done < "$INVENTORY_FILE"
      ;;
    status)
      validate_inventory
      log_rotate
      if [[ -f "$LOG_FILE" ]]; then
        note "Recent log entries:"
        tail -20 "$LOG_FILE"
      else
        note "No log file found at ${LOG_FILE}"
      fi
      ;;
    rotate)
      log_rotate
      note "Log rotated"
      ;;
    batch)
      validate_inventory
      log_init
      log_rotate
      local batch_status=0
      run_with_timeout "$OVERALL_TIMEOUT" process_inventory || batch_status=$?
      if [[ "$batch_status" -eq 124 ]]; then
        log_line "SYSTEM" overall "timeout" "$OVERALL_TIMEOUT" "batch timeout"
        return 0
      fi
      return "$batch_status"
      ;;
  esac
}
main "$@"
