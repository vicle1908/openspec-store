# Proposal: Ecosystem Reference Cleanup

## Why

After consolidating openspec/ from individual repos into the shared store,
stale references remained in code comments, docs, and AGENTS.md files across
the workspace. These reference paths like `openspec/changes/...` that no
longer exist locally.

## What Changes

1. Updated `docs/openspec-setup.md` with current store stats and git tracking
2. Fixed 7 code comment references in Python repos (agent-core, tdt-core, jira-skill)
3. Verified ai-harness-skills resolves openspec/schemas/ correctly (local dependency)
4. Verified agent-docs-sync path matching works with store layout

## Non-Goals

- No spec content changes
- No functional code changes
- No Python repo structural changes
