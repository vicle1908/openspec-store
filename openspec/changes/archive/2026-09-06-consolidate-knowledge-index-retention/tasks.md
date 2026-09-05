# Tasks: Consolidate Knowledge Index Retention

## Phase 1: Inventory

- [x] 1.1 Find all `.gitnexus/` directories and record paths and sizes
- [x] 1.2 Find all `graphify-out/` directories and record paths and sizes
- [x] 1.3 Load approved repo inventory from `knowledge-refresh-inventory.tsv`

## Phase 2: Analysis

- [x] 2.1 For each index, resolve canonical repo path (handle symlinks/worktrees)
- [x] 2.2 Compare each index against approved inventory
- [x] 2.3 Check freshness by comparing last commit with index state
- [x] 2.4 Classify each index (current/historical/duplicate/unapproved)

## Phase 3: Evidence

- [x] 3.1 Write `evidence/index-inventory.json` with structured findings
- [x] 3.2 Write `evidence/index-retention-plan.md` with human-readable recommendations

## Phase 4: Archive

- [x] 4.1 Archive the change
- [x] 4.2 Commit store changes
