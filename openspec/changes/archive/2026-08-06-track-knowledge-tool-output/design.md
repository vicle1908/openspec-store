# track-knowledge-tool-output — Design

## Decision: What to Track

| Directory | Size | Track? | Rationale |
|-----------|------|--------|-----------|
| `graphify-out/` (total) | 88MB | ✅ YES | Agents need graphs on clone. 88MB is manageable. |
| `graphify-out/graph.json` | ~5-18MB each | ✅ Core file | Knowledge graph — most important |
| `graphify-out/GRAPH_REPORT.md` | ~10-50KB each | ✅ Report | Audit trail, useful for agents |
| `graphify-out/graph.html` | ~200KB-4MB each | ✅ Visual | Interactive graph for humans |
| `graphify-out/manifest.json` | ~10KB each | ✅ Metadata | Incremental rebuild tracking |
| `graphify-out/.graphify_labels.json` | ~10KB each | ✅ Labels | Community labels for graphify |
| `graphify-out/cache/` | varies | ❌ SKIP | Regenerable, per-machine |
| `graphify-out/.graphify_*` | varies | ❌ SKIP | Internal state, regenerable |
| `graphify-out/2026-*/` | 43MB total | ❌ SKIP | Historical snapshots, not needed |
| `.gitnexus/` | 1.5GB total | ❌ SKIP | Too large for git. Re-index on demand. |
| `wiki/` | 296KB | ✅ Already | Just initialized git tracking. |

## Corrected Size Analysis

- **graph.json total**: 79.3MB (the core data)
- **graph.html total**: 27MB (interactive visualizations)
- **graphify-out/ total (excl snapshots)**: 88MB
- **graphify-out/ total (incl snapshots)**: 1895MB — date-stamped subdirs must be excluded

## .gitignore Pattern

Replace current `graphify-out/` blanket ignore with selective pattern:

```gitignore
# graphify internal state (regenerable)
graphify-out/cache/
graphify-out/.graphify_*
graphify-out/needs_update
graphify-out/.graphify_root
graphify-out/20*/

# graphify-out/ IS tracked (graph.json, reports, HTML, labels)

# GitNexus (too large for git, 1.5GB)
.gitnexus/

# graphify internal directory
.graphify/
```

## Additional Fixes Required

1. **Add `.gitnexus/` to .gitignore** in 16 repos (was missing from agent-core, agent-docs-sync, etc.)
2. **Remove duplicate `graphify-out/`** in jira-kanban-from-spreadsheet .gitignore
3. **Exclude date-stamped subdirs** (`graphify-out/2026-*/`) — historical snapshots, not needed

## Rollback

If tracking causes issues:
1. Re-add `graphify-out/` to .gitignore
2. `git rm -r --cached graphify-out/`
3. Commit removal

## Risk

Low. graphify-out/ is non-sensitive (code structure labels only, no actual secrets or source code). 88MB one-time addition is manageable. No app source code changes. Date-stamped snapshots excluded to prevent bloat.
