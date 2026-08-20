# Proposal: Workspace Repo Alignment

## Problem

Consistency check on 2026-08-20 found 2 active Python git repos that exist on disk but are not documented in AGENTS.md or included in GDrive sync:

1. **claude-code-provider-adapter** — Anthropic Messages → OpenAI Responses adapter for Claude Code multi-provider routing. Active git repo with recent commits.
2. **hermes-webui** — Hermes web UI. Active git repo with recent commits.

Two other repos were investigated and excluded:
- **wiki-mcp-server** — Not a git repo (local package only)
- **workspace-python-template** — Template repo ("my-project"), not a workspace member

## Solution

Add both repos to:
1. AGENTS.md workspace layout (Python repos section)
2. GDrive sync REPOS list

## Out of Scope

- No spec changes (skip_specs: true)
- No code changes
- No new skills or MCP tools
