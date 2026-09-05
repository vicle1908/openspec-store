## Why

A few workspace-root projects are missing consistent Git hygiene, and one complete Python package (`wiki-mcp-server`) lacks a repository. Normalize ignores, initialize the missing repo, and record retention decisions so future cleanup passes stop revisiting the same files.

## What Changes

- Initialize `wiki-mcp-server` as a local Git repository with a standard Python `.gitignore` (including `.claude/`).
- Add `.claude/` ignore coverage to `ntu-keynote` and `workspace-python-template`.
- Retain reviewed root evidence/docs rather than delete them, and document this decision.
- No remotes, no publishing, and no deletion of active projects or retained evidence.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none)

## Impact

Affects workspace-root repository hygiene only: `wiki-mcp-server`, `ntu-keynote`, `workspace-python-template`, and workspace documentation/ownership notes.
