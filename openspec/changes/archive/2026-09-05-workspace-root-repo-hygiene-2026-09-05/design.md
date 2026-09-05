## Context

Several workspace-root projects have inconsistent ignores or missing Git setup. One complete Python package (`wiki-mcp-server`) is untracked entirely. See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- Establish consistent local Git hygiene for workspace-root projects.
- Ensure `.claude/` is excluded in reviewed root repos.
- Record retention decisions for evidence/docs items so future cleanup passes stop revisiting them.

**Non-Goals:**
- No remote publishing, no CI setup, no dependency changes, no deletion of active projects or retained evidence.

## Decisions

- Initialize `wiki-mcp-server` as a local Git repository now, rather than leaving it untracked.
- Reuse the standard Python `.gitignore` already used elsewhere, adding `.claude/`.
- Document ownership decisions in workspace docs instead of deleting reviewed items prematurely.

## Risks / Trade-offs

- Local-only Git reduces discoverability for other users → Acceptable because the repo is currently single-user/workspace-local.
- Preserving evidence/docs increases root clutter → Acceptable because deletion requires explicit retention approval.
