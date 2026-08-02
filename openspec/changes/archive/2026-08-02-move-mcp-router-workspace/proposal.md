# Proposal: Move mcp-router to Root Workspace

## Why

`mcp-router/` is a standalone git repo (own `.git`, own remote) sitting
nested inside `go-microservices/mcp-router/`. It was previously a submodule
but was removed. The nested location causes:

1. **Confusion** — agents treating it as part of the microservices monorepo
2. **Dead CI code** — verify.yml copies an AGENTS.md that no longer exists
3. **Stale ignores** — .gitignore, .gitnexusignore, .graphifyignore still
   reference the nested path
4. **Agentguide validator bloat** — 12+ lines of mcp-router-specific logic
   for a repo that's no longer nested

Moving to `~/Developer/mcp-router/` makes it a workspace peer alongside
`go-microservices/`, matching the multi-repo workspace design.

## What Changes

- `mv go-microservices/mcp-router ~/Developer/mcp-router`
- Remove dead CI step from verify.yml (copies deleted file)
- Remove mcp-router from .gitignore, .gitnexusignore, .graphifyignore
- Remove mcp-router-specific code from agentguide validator
- Deploy AGENTS.md to ~/Developer/mcp-router/

## Non-Goals

- No changes to mcp-router's own code or CLAUDE.md
- No changes to mcp-router's git history or remote

## Compatibility

Backward compatible. mcp-router was already ignored by go-microservices git.
Moving it out only removes dead references.

## Rollback

Move back: `mv ~/Developer/mcp-router go-microservices/mcp-router`
