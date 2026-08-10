# repair-knowledge-output-tracking — Tasks

## 1. Repair ignore rules

- [x] 1.1 Remove broad `graph.json` and `GRAPH_REPORT.md` rules from go-microservices
- [x] 1.2 Add label negations after `.graphify_*` in all 17 repos
- [x] 1.3 Verify caches, internal state, locks, dated snapshots, and `.gitnexus/` remain ignored

## 2. Track missing outputs

- [x] 2.1 Track go-microservices graph.json and GRAPH_REPORT.md
- [x] 2.2 Track `.graphify_labels.json` and `.graphify_labels.json.sig` in all 17 repos
- [x] 2.3 Verify no unrelated source or pre-existing worktree files are staged

## 3. Agent verification

- [x] 3.1 Run graphify query from go-microservices without rebuilding
- [x] 3.2 Run graphify query from one Python repo using committed label artifacts
- [x] 3.3 Verify GitNexus remains ignored and available for on-demand indexing

## 4. Closure

- [x] 4.1 Validate the successor OpenSpec change
- [x] 4.2 Commit each repository's scoped repair
- [x] 4.3 Archive the successor change and commit only its store artifacts
