# repair-knowledge-output-tracking

## Why

A post-archive audit of `track-knowledge-tool-output` found two tracking gaps:

1. `go-microservices/.gitignore` has broad `graph.json` and `GRAPH_REPORT.md` rules, so its canonical `graphify-out/graph.json` and report are still ignored.
2. All 17 repos use `graphify-out/.graphify_*`, which also ignores `.graphify_labels.json` and its signature even though community labels are part of the committed graph output contract.

As a result, a clone of go-microservices lacks the graph itself, and cloned repositories lose curated community labels.

## What Changes

- Remove the broad `graph.json` and `GRAPH_REPORT.md` ignore rules from go-microservices.
- Add explicit negation rules for `graphify-out/.graphify_labels.json` and `.graphify_labels.json.sig` in all 17 repos.
- Track the missing go-microservices `graph.json` and `GRAPH_REPORT.md`.
- Track label and signature artifacts in all 17 repos.
- Preserve ignores for caches, internal state, rebuild locks, and dated snapshots.
- Verify coding-agent graphify queries work from the tracked outputs without rebuilding.

This is a retrospective configuration/artifact repair; no product behavior or normative spec changes are introduced.
