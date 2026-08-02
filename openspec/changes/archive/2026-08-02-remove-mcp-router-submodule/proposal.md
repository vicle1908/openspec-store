# Remove mcp-router Submodule

## Why

The mcp-router submodule was added to the repository but is an independent project maintained separately. It caused:
- CI failures when the submodule directory was missing
- Agentguide validation errors for missing guides
- Confusion about repository boundaries

## What Changes

- Remove mcp-router from git tracking (submodule deinit + git rm)
- Update CI workflow to handle missing mcp-router directory
- Update agentguide validator to skip mcp-router validation when directory doesn't exist
- Remove mcp-router reference from root AGENTS.md
- Keep mcp-router in .gitignore to prevent accidental re-tracking

## Goals

- Clean separation between microservices repo and mcp-router
- CI passes without mcp-router being present
- Agentguide validator is tolerant of missing optional directories

## Non-Goals

- Modifying mcp-router code or configuration
- Changing mcp-router's own CI/CD setup
- Removing mcp-router from the local filesystem (it stays as a standalone clone)

## Affected Boundaries

- `.github/workflows/verify.yml` - CI workflow
- `tools/agentguide/validator.go` - Agent guidance validator
- `AGENTS.md` - Root agent instructions
- `.gitmodules` - Submodule configuration (emptied)
- `.gitignore` - Added mcp-router/
