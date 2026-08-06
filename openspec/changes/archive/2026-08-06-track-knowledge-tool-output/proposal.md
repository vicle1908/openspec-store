# track-knowledge-tool-output

## Why

Knowledge tool output (graphify-out/, .gitnexus/, wiki/) is currently .gitignored or not tracked, which creates several problems:

1. **No recovery**: If graphify-out/ is deleted, agents lose access to knowledge graphs until rebuilt (30s-2min per repo)
2. **No cross-machine portability**: New clones or other machines must rebuild all graphs from scratch
3. **No audit trail**: Changes to knowledge graphs aren't version-controlled
4. **Agent access gap**: Coding agents that clone a repo don't get graphify-out/ — they must rebuild before using graphify query

The wiki/ directory was just git-tracked (296KB, 21 pages). graphify-out/ (180MB total) is manageable. .gitnexus/ (1.5GB) is too large for git tracking.

## What Changes

### Phase 1: Track graphify-out/ in all repos

- Remove `graphify-out/` from .gitignore in all 17 repos
- Commit existing graphify-out/ directories (graph.json, GRAPH_REPORT.md, graph.html, manifest.json)
- Keep cache/ and internal files (.graphify_*, needs_update) gitignored
- Keep wiki/ subdirectory gitignored (auto-generated, regenerated from graph)

### Phase 2: Keep .gitnexus/ gitignored (too large)

- .gitnexus/ stays gitignored (1.5GB total, not feasible for git)
- GitNexus freshness monitored by weekly cron (detect-only)
- Agents re-index on demand when needed

### Phase 3: Wiki already tracked

- wiki/ is already git-tracked (296KB, committed)
- Weekly wiki-lint cron commits changes automatically

## Non-Goals

- Track .gitnexus/ in git (1.5GB too large)
- Track graphify-out/cache/ (regenerable)
- Change GitNexus indexing mechanism

## Impact

- 17 repos: .gitignore updated, graphify-out/ committed
- ~180MB added to git repos (one-time)
- Agents get immediate graphify access on clone
- Recovery: `git checkout graphify-out/` instead of full rebuild
