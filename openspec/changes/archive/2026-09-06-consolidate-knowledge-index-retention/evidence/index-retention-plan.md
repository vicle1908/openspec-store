# Knowledge Index Retention Plan

## Current State

- 21 `.gitnexus/` directories (~1.8GB total)
- 20 `graphify-out/` directories (~1.0GB total)
- 20 repos approved in knowledge-refresh-inventory.tsv
- 2 unapproved index paths (root `.gitnexus/`, test artifact)

## Classification

### Current (retain)
All 20 approved repos with both gitnexus and graphify indexes — these are actively refreshed by post-merge hooks and scheduled jobs.

### Historical/Redundant (review candidates)
- `openspec-store/graphify-out/` — inventory says `graphify_enabled=no`, but directory exists (184M). Review if this was a one-time generation.
- Root `.gitnexus/` (764K) — workspace-level index, not repo-specific. Review purpose.
- `.knowledge-refresh-test-s1lr2rxj/` (3M) — test artifact, safe to remove.

### No Deletion Recommended Yet
The refresh hooks regenerate indexes from source. Aggressive pruning risks stale navigation state. Recommended next step: define freshness thresholds per index type and prune only verified-stale entries through an approved retirement change.

## Owner-Native Cleanup
- GitNexus: `npx gitnexus clean` (when available)
- Graphify: `graphify clean` (when available)
- Never delete manually — use tool-native commands
