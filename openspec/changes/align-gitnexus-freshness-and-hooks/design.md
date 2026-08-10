# align-gitnexus-freshness-and-hooks — Design

## Reindex Strategy

All 14 stale repos will be reindexed with `--index-only --skip-agents-md --skip-skills`:
- `--index-only`: rebuilds graph/symbols/relationships/commit-hash metadata in `.gitnexus/` without touching AGENTS.md, CLAUDE.md, or skill files
- `--skip-agents-md`: preserves our custom AGENTS.md content beyond the GitNexus block
- `--skip-skills`: preserves our custom skill files

The 4 already-fresh repos (agent-core, agent-docs-sync, agent-harness, go-microservices) are skipped.

```bash
REPOS="ai-harness-skills ai-review browser-cli code-daily-scan jira-daily-reports jira-epic-report jira-kanban-from-spreadsheet jira-skill mcp-router ops-automation-suite tdt-core tdt-observability tdt-sheets webhook-receiver"
for repo in $REPOS; do
  cd ~/Developer/$repo
  gitnexus analyze --index-only --skip-agents-md --skip-skills
done
```

## Pre-commit Hook: Keep Existing --repo "$root" Logic

**Critical finding from review**: The existing hook at `go-microservices/scripts/knowledge-pre-commit.sh` already passes `--repo "$root"` (full path). The comment in the hook explains why: *"Use repo path (not basename) — GitNexus derives name from git remote, which may differ from the directory name."*

**Do NOT replace with `basename "$root"`** — the existing code is correct.

The actual issue is **performance**, not correctness: `detect-changes` takes 30+ seconds, which is too slow for a pre-commit hook. Fix:

1. Run `detect-changes` in the background with a timeout
2. If it completes within 5s, include the advisory output
3. If it times out, skip silently (advisory-only, not blocking)

```bash
# In knowledge-pre-commit.sh, replace the detect-changes block with:
root="$(git rev-parse --show-toplevel 2>/dev/null || exit 0)"
timeout 5 gitnexus detect-changes --scope staged --repo "$root" 2>&1 ||
  printf 'knowledge: staged impact check skipped (timeout or unavailable); commit remains advisory-only\n' >&2
```

The `timeout 5` ensures the hook completes in under 5 seconds. If `detect-changes` is slow (common with large repos), the hook degrades gracefully.

## Illegal Instruction Fix

The `Illegal instruction: 4` is an arm64 ONNX native addon issue. Investigation steps:
1. Check if `node -e "require('@ladybugdb/core')"` works from the hook context
2. Check if the hook runs in a different arch context (e.g., via `arch -x86_64`)
3. If confirmed, add `arch -arm64` prefix or use `arch` detection
4. If root cause is unclear, the `timeout 5` fallback handles this gracefully

## Cron Freshness Check Update

The cron should use `gitnexus status` for GitNexus freshness instead of file-mtime comparison. Update the weekly-graphify-freshness cron prompt:

```
For GitNexus freshness in each repo:
  status_output=$(cd <repo> && gitnexus status 2>&1)
  if echo "$status_output" | grep -q "stale"; then
    echo "STALE: <repo> — needs gitnexus analyze"
  fi
```

The cron agent should report staleness but NOT auto-reindex (too slow for a cron job). It should recommend manual reindex.

**PATH note**: The cron runs with the agent's full environment, which includes `~/.npm-global/bin` on PATH. `gitnexus` is at `~/.npm-global/bin/gitnexus` and will be found.

## No Rollback Needed

`.gitnexus/` is gitignored in all repos. Reindexing only changes local index data. If a reindex produces bad results, simply re-run `gitnexus analyze --index-only` to rebuild. No git history involved.

## Global Graph Impact

GitNexus indexes are per-repo and local to `.gitnexus/`. No global graph changes needed.
