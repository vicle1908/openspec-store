#!/usr/bin/env bash
# install-hooks.sh — Install managed post-merge dispatcher in all inventoried repos
#
# This script installs a lightweight post-merge hook that dispatches to the
# central refresh-knowledge-indexes.sh script. The hook itself contains no
# logic — all validation, branch checking, and locking happens centrally.
#
# Idempotent: checks for the managed block marker before inserting.
#
# Usage:
#   ./install-hooks.sh          # Install in all inventoried repos
#   ./install-hooks.sh --dry-run # Show what would be done

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INVENTORY="${SCRIPT_DIR}/knowledge-refresh-inventory.tsv"
DRY_RUN=false

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

# Parse args
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

# Validate inventory exists
if [[ ! -f "$INVENTORY" ]]; then
  echo "ERROR: Inventory not found at $INVENTORY" >&2
  exit 1
fi

# Counters
updated=0
skipped=0
errors=0
repos_processed=0

echo "=== Post-merge hook installer ==="
echo "Inventory: $INVENTORY"
echo "Dry run:   $DRY_RUN"
echo ""

# Read inventory (skip comments and blank lines)
while IFS=$'\t' read -r repo_path default_branch gitnexus_enabled graphify_enabled; do
  # Skip comments and empty lines
  [[ "$repo_path" =~ ^#.*$ || -z "$repo_path" ]] && continue

  repos_processed=$((repos_processed + 1))
  hook_path="${repo_path}/.git/hooks/post-merge"

  # Verify the repo exists
  if [[ ! -d "$repo_path/.git" ]]; then
    echo "  SKIP  $repo_path (no .git directory)"
    skipped=$((skipped + 1))
    continue
  fi

  # Ensure hooks directory exists
  hooks_dir="$(dirname "$hook_path")"
  if [[ ! -d "$hooks_dir" ]]; then
    if $DRY_RUN; then
      echo "  WOULD CREATE  $hooks_dir"
    else
      mkdir -p "$hooks_dir"
    fi
  fi

  # Check if hook file exists
  if [[ -f "$hook_path" ]]; then
    # Check if managed block already exists
    if grep -q "$BLOCK_START" "$hook_path" 2>/dev/null; then
      echo "  EXISTS  $repo_path (managed block already present)"
      skipped=$((skipped + 1))
      continue
    fi

    # Hook exists but no managed block — append it
    echo "  APPEND  $repo_path (hook exists, adding managed block)"
    if $DRY_RUN; then
      echo "  [dry-run] Would append managed block to $hook_path"
    else
      {
        echo ""
        echo "$DISPATCHER_BLOCK"
      } >> "$hook_path"
      chmod +x "$hook_path"
    fi
    updated=$((updated + 1))
  else
    # No hook file — create it with shebang and managed block
    echo "  CREATE  $repo_path (new hook)"
    if $DRY_RUN; then
      echo "  [dry-run] Would create $hook_path"
    else
      {
        echo "#!/usr/bin/env bash"
        echo ""
        echo "$DISPATCHER_BLOCK"
      } > "$hook_path"
      chmod +x "$hook_path"
    fi
    updated=$((updated + 1))
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
