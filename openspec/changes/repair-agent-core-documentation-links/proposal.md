# Proposal: Repair agent-core documentation links

## Why

`docs-sync validate` reports 2 broken Markdown links in agent-core:

1. `docs/README.md` line 19 links to `model-resolution.md` — file does not exist. The
   model resolution content lives in `docs/architecture.md` (lines 78–80).
2. `docs/extending.md` line 269 links to `docs/scheduling.md` — resolves to
   `docs/docs/scheduling.md` (double-path). The file exists at `docs/scheduling.md`.
   Line 267 also references nonexistent `docs/scheduler/ARCHITECTURE.md`.

Both are documentation-only defects. No application code changes are required.

## What Changes

- `docs/README.md`: redirect Model Resolution link from `model-resolution.md` to
  `architecture.md` (no anchor — architecture.md has no Model Resolution heading).
- `docs/extending.md`: replace two scheduling paragraphs with one truthful link
  `scheduling.md`, removing the nonexistent `docs/scheduler/ARCHITECTURE.md` reference.

## Non-Goals

- No application code changes.
- No graphify index refresh.
- No new documentation files.
