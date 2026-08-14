#!/usr/bin/env bash
# install-hooks.sh — Atomic upserter for post-merge dispatchers in all inventoried repos
#
# Each hook is backed up, surgically updated (managed block replaced, Graphify
# and all other content preserved), validated with `bash -n`, and atomically
# renamed into place. Malformed marker states are treated as hard failures.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INVENTORY="${SCRIPT_DIR}/knowledge-refresh-inventory.tsv"
DRY_RUN=false
ROLLBACK=false

# Managed block markers
BLOCK_START="# knowledge-gitnexus-post-merge-start"
BLOCK_END="# knowledge-gitnexus-post-merge-end"

# The dispatcher block to inject
read -r -d '' DISPATCHER_BLOCK << 'BLOCK_EOF' || true
# knowledge-gitnexus-post-merge-start
# Managed by workspace refresh system — do not edit between markers.
knowledge_gitnexus_dispatch() {
  nohup "$HOME/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh" \
    --repo "$(git rev-parse --show-toplevel)" \
    --trigger post-merge \
    >>"$HOME/Developer/.knowledge-refresh/post-merge.log" 2>&1 </dev/null &
}
knowledge_gitnexus_dispatch
# knowledge-gitnexus-post-merge-end
BLOCK_EOF

# --- Parse args ---
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --rollback) ROLLBACK=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

# --- Validate inventory ---
if [[ ! -f "$INVENTORY" ]]; then
  echo "ERROR: Inventory not found at $INVENTORY" >&2
  exit 1
fi

# Counters
updated=0
skipped=0
errors=0
repos_processed=0
hook_changed=0

echo "=== Post-merge hook atomic upserter ==="
echo "Inventory: $INVENTORY"
echo "Dry run:   $DRY_RUN"
echo ""

# --- upsert_hook: replace managed block atomically in a single hook ---
# Usage: upsert_hook <hook_path> <repo_label>
# Exit 0 = no change needed or update succeeded; exit 1 = failure.
upsert_hook() {
  local hook_path="$1"
  local label="$2"
  hook_changed=0

  if $ROLLBACK; then
    local backup_path="${hook_path}.knowledge-refresh.bak"
    if [[ ! -f "$backup_path" ]]; then
      echo "  FAIL   $label (backup not found: $backup_path)"
      return 1
    fi
    local rollback_tmp
    rollback_tmp="$(mktemp "${hook_path}.rollback.XXXXXX")"
    cp -p "$backup_path" "$rollback_tmp"
    if ! bash -n "$rollback_tmp" 2>/dev/null; then
      echo "  FAIL   $label (backup failed bash -n validation)"
      rm -f "$rollback_tmp"
      return 1
    fi
    chmod +x "$rollback_tmp"
    mv "$rollback_tmp" "$hook_path"
    hook_changed=1
    echo "  ROLLBACK $label"
    return 0
  fi

  # --- Count markers in existing hook ---
  local start_count end_count
  start_count="$(grep -c "$BLOCK_START" "$hook_path" 2>/dev/null | tr -cd "[:digit:]")"
  start_count="${start_count:-0}"
  end_count="$(grep -c "$BLOCK_END" "$hook_path" 2>/dev/null | tr -cd "[:digit:]")"
  end_count="${end_count:-0}"

  # --- Malformed marker detection ---
  if (( start_count > 1 || end_count > 1 )); then
    echo "  FAIL   $label (duplicate markers: start=$start_count end=$end_count)"
    return 1
  fi
  if (( start_count == 1 && end_count == 0 )); then
    echo "  FAIL   $label (start marker without end marker)"
    return 1
  fi
  if (( start_count == 0 && end_count == 1 )); then
    echo "  FAIL   $label (end marker without start marker)"
    return 1
  fi

  # --- No markers at all: append the block ---
  if (( start_count == 0 )); then
    echo "  APPEND $label"
    if $DRY_RUN; then return 0; fi
    local tmp
    tmp="$(mktemp "${hook_path}.XXXXXX")"
    {
      cat "$hook_path"
      echo ""
      echo "$DISPATCHER_BLOCK"
    } > "$tmp"
    if ! bash -n "$tmp" 2>/dev/null; then
      echo "  FAIL   $label (bash -n failed on new hook)"
      rm -f "$tmp"
      return 1
    fi
    cp -p "$hook_path" "${hook_path}.knowledge-refresh.bak"
    chmod +x "$tmp"
    mv "$tmp" "$hook_path"
    hook_changed=1
    return 0
  fi

  # --- Markers present: rebuild with single-pass awk (portable, preserves blank lines) ---
  # awk replaces the managed region atomically in one pass, preserving all
  # content outside it byte-for-byte. Uses a temp file for the dispatch block
  # because awk -v splits multi-line strings on newlines.
  local new_hook dispatch_file
  new_hook="$(mktemp "${hook_path}.XXXXXX")"
  dispatch_file="$(mktemp "${hook_path}.dispatch.XXXXXX")"
  printf '%s\n' "$DISPATCHER_BLOCK" > "$dispatch_file"
  awk -v bs="$BLOCK_START" -v be="$BLOCK_END" -v df="$dispatch_file" '
    BEGIN { while ((getline line < df) > 0) { dispatch = (dispatch == "" ? line : dispatch "\n" line) } close(df) }
    $0 ~ bs { print dispatch; skip=1; next }
    $0 ~ be && skip { skip=0; next }
    !skip { print }
  ' "$hook_path" > "$new_hook"
  rm -f "$dispatch_file"

  # --- Validate new hook ---
  if ! bash -n "$new_hook" 2>/dev/null; then
    echo "  FAIL   $label (bash -n failed on updated hook)"
    rm -f "$new_hook"
    return 1
  fi

  # --- Check for actual change ---
  if cmp -s "$new_hook" "$hook_path"; then
    echo "  OK     $label (no change needed)"
    rm -f "$new_hook"
    return 0
  fi

  # --- Atomic replacement ---
  if $DRY_RUN; then
    echo "  WOULD  $label"
    rm -f "$new_hook"
    return 0
  fi

  cp -p "$hook_path" "${hook_path}.knowledge-refresh.bak"
  chmod +x "$new_hook"
  mv "$new_hook" "$hook_path"
  hook_changed=1
  echo "  UPDATE $label"
  return 0
}

# --- Main loop: process each inventoried repo ---
while IFS=$'\t' read -r repo_path default_branch gitnexus_enabled graphify_enabled; do
  [[ "$repo_path" =~ ^#.*$ || -z "$repo_path" ]] && continue

  repos_processed=$((repos_processed + 1))
  hook_path="${repo_path}/.git/hooks/post-merge"

  if [[ ! -d "$repo_path/.git" ]]; then
    echo "  SKIP   $repo_path (no .git directory)"
    skipped=$((skipped + 1))
    continue
  fi

  hooks_dir="$(dirname "$hook_path")"
  mkdir -p "$hooks_dir"

  if [[ ! -f "$hook_path" ]]; then
    if $ROLLBACK; then
      echo "  FAIL   $repo_path (cannot roll back a missing hook)"
      errors=$((errors + 1))
      continue
    fi
    # No hook file — create from scratch
    echo "  CREATE $repo_path"
    if ! $DRY_RUN; then
      {
        echo "#!/usr/bin/env bash"
        echo ""
        echo "$DISPATCHER_BLOCK"
      } > "$hook_path"
      chmod +x "$hook_path"
      updated=$((updated + 1))
    fi
    continue
  fi

  # Hook exists — atomic upsert
  if upsert_hook "$hook_path" "$repo_path"; then
    if (( hook_changed == 1 )); then
      updated=$((updated + 1))
    fi
  else
    errors=$((errors + 1))
  fi

done < "$INVENTORY"

echo ""
echo "=== Summary ==="
echo "  Repos processed: $repos_processed"
echo "  Updated:         $updated"
echo "  Skipped:         $skipped"
echo "  Errors:          $errors"

if $DRY_RUN; then
  echo ""
  echo "  (dry run — no changes made)"
fi

exit $errors
