#!/usr/bin/env bash
# workspace-worktree-scan.sh — Report worktree, dirty-path, and trash status.
# Usage: workspace-worktree-scan.sh

set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/Users/androidteam/Developer}"

# Explicit, approved ecosystem repository list; do not recursively traverse the workspace.
REPOSITORIES=(
  "agent-core"
  "agent-docs-sync"
  "agent-harness"
  "ai-harness-skills"
  "ai-review"
  "ai-training-materials"
  "browser-cli"
  "claude-code-provider-adapter"
  "code-daily-scan"
  "go-microservices"
  "goose-docs"
  "hermes-webui"
  "jira-daily-reports"
  "jira-epic-report"
  "jira-kanban-from-spreadsheet"
  "jira-skill"
  "mcp-router"
  "ntu-keynote"
  "openspec-store"
  "ops-automation-suite"
  "prime-agent"
  "realtime"
  "tdt-core"
  "tdt-observability"
  "tdt-scheduler"
  "tdt-sheets"
  "webhook-receiver"
  "wiki"
  "wiki-mcp-server"
  "workspace-python-template"
)

printf 'Workspace worktree scan: %s\n' "$WORKSPACE_ROOT"
printf '%s\n' '----------------------------------------'
SEEN_GIT_COMMON_DIRS=()
SEEN_OWNER_PATHS=()

canonical_repo_count=0
canonical_worktree_count=0
canonical_extra_count=0
canonical_dirty_count=0
canonical_trash_count=0
canonical_prunable_count=0
linked_path_count=0

for repository in "${REPOSITORIES[@]}"; do
  repo_path="${WORKSPACE_ROOT}/${repository}"
  if [[ ! -d "$repo_path" ]]; then
    printf '%-32s MISSING (not a directory)\n' "$repo_path"
    continue
  fi
  if ! git_common_dir="$(git -C "$repo_path" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"; then
    printf '%-32s SKIP (not a Git repository)\n' "$repo_path"
    continue
  fi
  linked_repo_index=''
  for index in "${!SEEN_GIT_COMMON_DIRS[@]}"; do
    if [[ "${SEEN_GIT_COMMON_DIRS[$index]}" == "$git_common_dir" ]]; then
      linked_repo_index="$index"
      break
    fi
  done
  if [[ -n "$linked_repo_index" ]]; then
    linked_owner="${SEEN_OWNER_PATHS[$linked_repo_index]}"
    linked_path_count=$((linked_path_count + 1))
  else
    linked_owner=''
    SEEN_GIT_COMMON_DIRS+=("$git_common_dir")
    SEEN_OWNER_PATHS+=("$repo_path")
    canonical_repo_count=$((canonical_repo_count + 1))
  fi

  worktree_output=''
  if [[ -z "$linked_owner" ]]; then
    if ! worktree_output="$(git -C "$repo_path" worktree list --porcelain 2>/dev/null)"; then
      printf '%-32s ERROR (unable to inspect worktrees)\n' "$repo_path"
      continue
    fi
    worktree_count="$(printf '%s\n' "$worktree_output" | awk '$1 == "worktree" { count++ } END { print count + 0 }')"
    extra_count=$((worktree_count > 0 ? worktree_count - 1 : 0))
    prunable_count="$(printf '%s\n' "$worktree_output" | awk '$1 == "prunable" { count++ } END { print count + 0 }')"
    canonical_worktree_count=$((canonical_worktree_count + worktree_count))
    canonical_extra_count=$((canonical_extra_count + extra_count))
    canonical_prunable_count=$((canonical_prunable_count + prunable_count))
  fi

  dirty_output=''
  if ! dirty_output="$(git -C "$repo_path" status --porcelain --untracked-files=all 2>/dev/null)"; then
    printf '%-32s ERROR (unable to inspect status)\n' "$repo_path"
    continue
  fi
  dirty_count="$(printf '%s\n' "$dirty_output" | awk 'NF { count++ } END { print count + 0 }')"
  if [[ -z "$linked_owner" ]]; then
    canonical_dirty_count=$((canonical_dirty_count + dirty_count))
  fi

  trash_count=0
  while IFS= read -r trash_dir; do
    [[ -n "$trash_dir" ]] || continue
    if [[ -n "$(find "$trash_dir" -mindepth 1 -print -quit 2>/dev/null)" ]]; then
      trash_count=$((trash_count + 1))
    fi
  done < <(find "$repo_path" -type d -name '.orca-worktree-trash' -print 2>/dev/null)
  if [[ -z "$linked_owner" ]]; then
    canonical_trash_count=$((canonical_trash_count + trash_count))
  fi

  if [[ -n "$linked_owner" ]]; then
    printf '%-32s LINKED (status checked; counts owned by %s) dirty_paths=%d trash_nonempty=%d\n' \
      "$repo_path" "$linked_owner" "$dirty_count" "$trash_count"
  else
    printf '%-32s worktrees=%d extra=%d dirty_paths=%d trash_nonempty=%d prunable=%d\n' \
      "$repo_path" "$worktree_count" "$extra_count" "$dirty_count" "$trash_count" "$prunable_count"
  fi
done

printf '%s\n' '----------------------------------------'
printf 'Canonical repositories=%d worktrees=%d extras=%d dirty_paths=%d trash_nonempty=%d prunable=%d linked_paths=%d\n' \
  "$canonical_repo_count" "$canonical_worktree_count" "$canonical_extra_count" \
  "$canonical_dirty_count" "$canonical_trash_count" "$canonical_prunable_count" "$linked_path_count"
