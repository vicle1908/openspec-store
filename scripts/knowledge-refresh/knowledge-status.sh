#!/usr/bin/env bash
# knowledge-status.sh — Report freshness across all repos in the inventory.
# Usage: knowledge-status.sh [--json] [--repo <name>]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INVENTORY="${SCRIPT_DIR}/knowledge-refresh-inventory.tsv"
STALENESS_THRESHOLD_DAYS=1

# --- Flags ---
JSON_MODE=false
REPO_FILTER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON_MODE=true; shift ;;
    --repo) REPO_FILTER="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: knowledge-status.sh [--json] [--repo <name>]"
      echo ""
      echo "Reports freshness status of GitNexus and Graphify indexes"
      echo "across all repositories listed in the inventory."
      echo ""
      echo "Options:"
      echo "  --json         Output machine-readable JSON"
      echo "  --repo <name>  Filter to a single repository"
      echo "  -h, --help     Show this help"
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ ! -f "$INVENTORY" ]]; then
  echo "Inventory not found: $INVENTORY" >&2
  exit 1
fi

# --- Helpers ---

# Convert epoch seconds to ISO date (YYYY-MM-DD)
epoch_to_date() {
  if command -v gdate &>/dev/null; then
    gdate -d "@$1" '+%Y-%m-%d' 2>/dev/null || echo "unknown"
  else
    date -r "$1" '+%Y-%m-%d' 2>/dev/null || echo "unknown"
  fi
}

# Short SHA from a full SHA
short_sha() {
  echo "${1:0:7}"
}

# Compute staleness: returns FRESH, STALE, or UNKNOWN
# $1 = index timestamp (epoch), $2 = HEAD timestamp (epoch)
classify_freshness() {
  local idx_ts="$1" head_ts="$2"

  if [[ "$idx_ts" == "0" || -z "$idx_ts" ]]; then
    echo "UNKNOWN"
    return
  fi
  if [[ "$head_ts" == "0" || -z "$head_ts" ]]; then
    echo "UNKNOWN"
    return
  fi

  local diff=$(( head_ts - idx_ts ))
  if (( diff <= 0 )); then
    # Index is at or ahead of HEAD — up to date
    echo "FRESH"
  else
    local days=$(( diff / 86400 ))
    if (( days <= STALENESS_THRESHOLD_DAYS )); then
      echo "FRESH"
    else
      echo "STALE"
    fi
  fi
}

# Get epoch of a file, or 0 if missing
file_mtime_epoch() {
  local fpath="$1"
  if [[ ! -f "$fpath" ]]; then
    echo "0"
    return
  fi
  if command -v stat &>/dev/null; then
    # macOS stat
    stat -f '%m' "$fpath" 2>/dev/null || echo "0"
  else
    echo "0"
  fi
}

# Get git HEAD commit timestamp (epoch) for a repo
head_timestamp() {
  local root="$1"
  git -C "$root" log -1 --format='%ct' HEAD 2>/dev/null || echo "0"
}

# Get git HEAD short SHA
head_sha() {
  local root="$1"
  git -C "$root" rev-parse --short=7 HEAD 2>/dev/null || echo "unknown"
}

# Get the index commit SHA recorded by GitNexus
gitnexus_indexed_sha() {
  local root="$1"
  local meta="${root}/.gitnexus/meta.json"
  if [[ -f "$meta" ]]; then
    # Extract lastCommit field (e.g. "lastCommit": "abc1234...")
    grep -o '"lastCommit"[[:space:]]*:[[:space:]]*"[^"]*"' "$meta" 2>/dev/null \
      | head -1 \
      | sed 's/.*"lastCommit"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/'
  fi
}

# Get GitNexus index timestamp (from meta.json lastRefresh or file mtime)
gitnexus_index_timestamp() {
  local root="$1"
  local meta="${root}/.gitnexus/meta.json"
  if [[ ! -f "$meta" ]]; then
    echo "0"
    return
  fi
  # Try lastRefresh field first
  local ts
  ts=$(grep -o '"lastRefresh"[[:space:]]*:[[:space:]]*"[^"]*"' "$meta" 2>/dev/null \
    | head -1 \
    | sed 's/.*"lastRefresh"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
  if [[ -n "$ts" && "$ts" != "" ]]; then
    # Convert ISO to epoch if possible
    if command -v gdate &>/dev/null; then
      gdate -d "$ts" '+%s' 2>/dev/null || echo "0"
      return
    fi
    # Try date parsing
    date -j -f '%Y-%m-%dT%H:%M:%S' "${ts%%Z*}" '+%s' 2>/dev/null || echo "0"
    return
  fi
  # Fallback: use meta.json mtime
  file_mtime_epoch "$meta"
}

# Get Graphify graph.json path and check freshness
graphify_index_timestamp() {
  local root="$1"
  local graph="${root}/graphify-out/graph.json"
  if [[ ! -f "$graph" ]]; then
    graph="${root}/.claude/graphify/graph.json"
  fi
  if [[ ! -f "$graph" ]]; then
    echo "0"
    return
  fi
  file_mtime_epoch "$graph"
}

graphify_indexed_sha() {
  local root="$1"
  local graph="${root}/graphify-out/graph.json"
  if [[ ! -f "$graph" ]]; then
    graph="${root}/.claude/graphify/graph.json"
  fi
  if [[ ! -f "$graph" ]]; then
    echo ""
    return
  fi
  # Try to extract a commit field if present
  grep -o '"commit"[[:space:]]*:[[:space:]]*"[^"]*"' "$graph" 2>/dev/null \
    | head -1 \
    | sed 's/.*"commit"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' || true
}

# Check if a lock file exists for a repo
lock_info() {
  local repo_name="$1"
  local lock_dir="${HOME}/.claude/locks"
  if [[ ! -d "$lock_dir" ]]; then
    echo ""
    return
  fi
  local lock_file="${lock_dir}/${repo_name}.lock"
  if [[ -f "$lock_file" ]]; then
    local owner
    owner=$(cat "$lock_file" 2>/dev/null || echo "unknown")
    echo "$owner"
  else
    echo ""
  fi
}

# Discover worktrees for a repo (excluding main checkout and detached HEAD)
discover_worktrees() {
  local root="$1"
  local default_branch="$2"
  local repo_name
  repo_name=$(basename "$root")

  # Check if it's even a git repo
  if ! git -C "$root" rev-parse --git-dir &>/dev/null; then
    return
  fi

  local wt_list
  wt_list=$(git -C "$root" worktree list --porcelain 2>/dev/null) || return

  local current_wt=""
  local current_branch=""
  local reading_wt=false

  while IFS= read -r line; do
    if [[ "$line" == worktree\ * ]]; then
      current_wt="${line#worktree }"
      reading_wt=true
    elif [[ "$line" == branch\ * ]]; then
      current_branch="${line#branch }"
      # Strip refs/heads/ prefix
      current_branch="${current_branch#refs/heads/}"
    elif [[ -z "$line" ]]; then
      # End of entry
      if $reading_wt; then
        # Skip the main checkout (bare worktree is the main checkout)
        if [[ "$current_wt" == "$root" ]]; then
          :
        # Skip detached HEAD (no branch line)
        elif [[ -z "$current_branch" ]]; then
          :
        # Skip default branch checkout (already counted as main)
        elif [[ "$current_branch" == "$default_branch" ]]; then
          :
        else
          # Output: path|branch
          echo "${current_wt}|${current_branch}"
        fi
      fi
      current_wt=""
      current_branch=""
      reading_wt=false
    fi
  done <<< "$wt_list"

  # Handle last entry (no trailing blank line)
  if $reading_wt && [[ -n "$current_wt" ]]; then
    if [[ "$current_wt" != "$root" ]] && [[ -n "$current_branch" ]] && [[ "$current_branch" != "$default_branch" ]]; then
      echo "${current_wt}|${current_branch}"
    fi
  fi
}

# --- Collect results ---

declare -a RESULTS=()
declare -a JSON_ITEMS=()

process_repo() {
  local root="$1"
  local default_branch="$2"
  local gn_enabled="$3"
  local gf_enabled="$4"
  local repo_name
  repo_name=$(basename "$root")

  local head_sha_val head_ts lock_owner
  head_sha_val=$(head_sha "$root")
  head_ts=$(head_timestamp "$root")
  head_date=$(epoch_to_date "$head_ts")
  lock_owner=$(lock_info "$repo_name")

  # --- GitNexus status ---
  if [[ "$gn_enabled" == "yes" ]]; then
    local gn_idx_sha gn_idx_ts gn_status
    gn_idx_sha=$(gitnexus_indexed_sha "$root")
    gn_idx_ts=$(gitnexus_index_timestamp "$root")

    if [[ "$gn_idx_ts" == "0" ]]; then
      gn_status="UNINITIALIZED"
    elif [[ -z "$gn_idx_sha" ]]; then
      # No indexed SHA — compare timestamps only
      gn_status=$(classify_freshness "$gn_idx_ts" "$head_ts")
    else
      # Compare indexed SHA with HEAD
      if [[ "$gn_idx_sha" == "$head_sha_val" ]]; then
        gn_status="FRESH"
      else
        gn_status=$(classify_freshness "$gn_idx_ts" "$head_ts")
      fi
    fi

    local gn_idx_date
    gn_idx_date=$(epoch_to_date "$gn_idx_ts")
    local gn_indexed_sha_short
    gn_indexed_sha_short=$(short_sha "$gn_idx_sha")

    RESULTS+=("$(printf '%-32s %-10s %-12s %-15s %s' "$repo_name" "GitNexus" "$gn_status" "$gn_idx_date" "$head_sha_val")")

    local lock_json="null"
    if [[ -n "$lock_owner" ]]; then
      lock_json="\"${lock_owner}\""
    fi

    JSON_ITEMS+=("{\"repo\":\"${repo_name}\",\"tool\":\"GitNexus\",\"status\":\"${gn_status}\",\"lastRefresh\":\"${gn_idx_date}\",\"indexedSha\":\"${gn_indexed_sha_short}\",\"headSha\":\"${head_sha_val}\",\"lockOwner\":${lock_json}}")
  fi

  # --- Graphify status ---
  if [[ "$gf_enabled" == "yes" ]]; then
    local gf_idx_ts gf_status
    gf_idx_ts=$(graphify_index_timestamp "$root")

    if [[ "$gf_idx_ts" == "0" ]]; then
      gf_status="UNINITIALIZED"
    else
      gf_status=$(classify_freshness "$gf_idx_ts" "$head_ts")
    fi

    local gf_idx_date
    gf_idx_date=$(epoch_to_date "$gf_idx_ts")

    RESULTS+=("$(printf '%-32s %-10s %-12s %-15s %s' "$repo_name" "Graphify" "$gf_status" "$gf_idx_date" "$head_sha_val")")

    local lock_json="null"
    if [[ -n "$lock_owner" ]]; then
      lock_json="\"${lock_owner}\""
    fi

    JSON_ITEMS+=("{\"repo\":\"${repo_name}\",\"tool\":\"Graphify\",\"status\":\"${gf_status}\",\"lastRefresh\":\"${gf_idx_date}\",\"indexedSha\":\"\",\"headSha\":\"${head_sha_val}\",\"lockOwner\":${lock_json}}")
  fi

  # --- Worktrees ---
  while IFS='|' read -r wt_path wt_branch; do
    [[ -z "$wt_path" ]] && continue
    local wt_sha
    wt_sha=$(git -C "$wt_path" rev-parse --short=7 HEAD 2>/dev/null || echo "unknown")
    RESULTS+=("$(printf '%-32s %-10s %-12s %-15s %s' "${repo_name}/*" "Worktree" "ACTIVE" "-" "$wt_sha (${wt_branch})")")

    JSON_ITEMS+=("{\"repo\":\"${repo_name}\",\"tool\":\"Worktree\",\"status\":\"ACTIVE\",\"lastRefresh\":\"-\",\"indexedSha\":\"\",\"headSha\":\"${wt_sha}\",\"worktree\":\"${wt_path}\",\"worktreeBranch\":\"${wt_branch}\",\"lockOwner\":null}")
  done < <(discover_worktrees "$root" "$default_branch")
}

# --- Main ---

while IFS=$'\t' read -r root branch gn gf; do
  # Skip comments and blank lines
  [[ "$root" =~ ^#.*$ || -z "$root" ]] && continue

  # Trim whitespace
  root=$(echo "$root" | xargs)
  branch=$(echo "$branch" | xargs)
  gn=$(echo "$gn" | xargs)
  gf=$(echo "$gf" | xargs)

  # Filter by repo name if --repo given
  if [[ -n "$REPO_FILTER" ]]; then
    local_repo_name=$(basename "$root")
    if [[ "$local_repo_name" != "$REPO_FILTER" ]]; then
      continue
    fi
  fi

  # Skip if directory doesn't exist
  if [[ ! -d "$root" ]]; then
    repo_name=$(basename "$root")
    RESULTS+=("$(printf '%-32s %-10s %-12s %-15s %s' "$repo_name" "-" "NOT_FOUND" "-" "-")")
    JSON_ITEMS+=("{\"repo\":\"${repo_name}\",\"tool\":\"-\",\"status\":\"NOT_FOUND\",\"lastRefresh\":\"-\",\"indexedSha\":\"\",\"headSha\":\"-\",\"lockOwner\":null}")
    continue
  fi

  process_repo "$root" "$branch" "$gn" "$gf"

done < "$INVENTORY"

# --- Output ---

if $JSON_MODE; then
  echo "{"
  echo "  \"generated\": \"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\","
  echo "  \"inventory\": \"${INVENTORY}\","
  echo "  \"stalenessThresholdDays\": ${STALENESS_THRESHOLD_DAYS},"
  echo "  \"repos\": ["
  for i in "${!JSON_ITEMS[@]}"; do
    if (( i < ${#JSON_ITEMS[@]} - 1 )); then
      echo "    ${JSON_ITEMS[$i]},"
    else
      echo "    ${JSON_ITEMS[$i]}"
    fi
  done
  echo "  ]"
  echo "}"
else
  echo "Knowledge Index Status"
  echo "Inventory: ${INVENTORY}"
  echo "Threshold: ${STALENESS_THRESHOLD_DAYS} day(s)"
  echo "Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo ""
  printf '%-32s %-10s %-12s %-15s %s\n' "Repository" "Tool" "Status" "Last Refresh" "HEAD"
  printf '%-32s %-10s %-12s %-15s %s\n' "----------------------------" "--------" "----------" "---------------" "-------"
  for result in "${RESULTS[@]}"; do
    echo "$result"
  done

  # Summary
  echo ""
  total=0; fresh=0; stale=0; uninit=0; unknown=0
  for result in "${RESULTS[@]}"; do
    total=$((total + 1))
    case "$result" in
      *FRESH*)     fresh=$((fresh + 1)) ;;
      *STALE*)     stale=$((stale + 1)) ;;
      *UNINIT*)    uninit=$((uninit + 1)) ;;
      *UNKNOWN*)   unknown=$((unknown + 1)) ;;
    esac
  done
  echo "Total: ${total}  FRESH: ${fresh}  STALE: ${stale}  UNINITIALIZED: ${uninit}  UNKNOWN: ${unknown}"
fi
