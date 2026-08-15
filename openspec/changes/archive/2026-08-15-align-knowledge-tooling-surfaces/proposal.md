# Align Knowledge Tooling Surfaces

## Why

The workspace implementation now uses Graphify-Labs `graphifyy` 0.9.42, GitNexus 1.6.9, OpenSpec 1.9.0, and the central inventory-driven refresh contract. Several current repository documents, tests, merge attributes, and skill metadata still describe older Graphify versions, obsolete `.graphify/graph.json` paths, duplicate merge drivers, or a nonexistent weekly cron.

These are documentation and tooling-surface drift defects. The runtime refresh implementation is already complete; this change makes current guidance and regression fixtures describe the implementation that actually runs.

## What Changes

- Update go-microservices knowledge-tool docs, version metadata, and fixture expectations.
- Remove obsolete `.graphify/graph.json` merge attributes and retain the active `graphify-out/graph.json` Graphify merge driver across inventoried repositories.
- Align current OpenSpec prose with `graphify-out/`, central post-merge dispatch, and the LaunchAgent contract.
- Update workspace skill guidance and OpenSpec workflow guidance to remove stale weekly-cron and obsolete provider claims while preserving historical migration references.
- Preserve unrelated dirty work, generated Graphify output, and historical/archive evidence.

This is a documentation/tooling reconciliation only; no new runtime capability or provider cutover is introduced.
