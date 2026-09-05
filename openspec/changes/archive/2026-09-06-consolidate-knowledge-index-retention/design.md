# Design: Knowledge Index Retention Audit

## Approach

Single-pass read-only audit. For each index found on disk:
1. Determine which repo it belongs to (canonical path vs worktree/symlink)
2. Check if the repo is on the approved inventory (knowledge-refresh-inventory.tsv)
3. Compare last git commit with index metadata to assess freshness
4. Record disk size and classification

## Index Types

| Index | Location | Provider | Refresh Method |
|-------|----------|----------|----------------|
| GitNexus | `.gitnexus/` | MCP server | Nightly LaunchAgent + post-merge hook |
| Graphify | `graphify-out/` | PyPI `graphifyy` | Post-commit hook + manual `graphify update .` |

## Classification Schema

- **current**: On approved inventory, index exists, repo is active
- **historical**: Repo exists but not on approved inventory, or index is stale
- **duplicate**: Index exists in a worktree/symlink that maps to a canonical repo
- **unapproved**: Repo not in workspace layout at all

## Evidence Outputs

- `evidence/index-inventory.json` — structured inventory of all indexes
- `evidence/index-retention-plan.md` — human-readable classification and recommendations
