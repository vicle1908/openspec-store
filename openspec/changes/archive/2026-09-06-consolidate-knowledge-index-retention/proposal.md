# Proposal: Consolidate Knowledge Index Retention

## Problem

Knowledge indexes (GitNexus `.gitnexus/` and Graphify `graphify-out/`) accumulate
across the workspace. Without a clear inventory and retention policy, indexes may:
- Grow stale without refresh
- Exist for repos no longer on the approved inventory
- Be duplicated across worktrees or symlinks

## Solution

Perform a read-only audit of all knowledge indexes in the workspace:
1. Inventory every `.gitnexus/` and `graphify-out/` directory
2. Compare against the approved 20-repo refresh inventory
3. Classify each index as current/historical/duplicate/unapproved
4. Produce a retention plan (no deletions in this change)

## Out of Scope

- Actual deletion of any index data
- Changes to the knowledge-refresh LaunchAgent or scripts
- Modification of the refresh inventory
