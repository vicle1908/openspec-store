# Proposal: Setup TDT Python Workspace

## Why

16 Python repos live on Google Drive (`gdrive-tdt:TDT/`). They need to be
pulled as workspace peers at `~/Developer/<repo>/` — matching the existing
multi-repo layout alongside `go-microservices/` and `mcp-router/`.

GDrive repos are file-only copies (no `.git`). Each needs:
- Git initialization with proper `.gitignore`
- Python environment via `uv sync`
- Bidirectional sync with GDrive via `rclone bisync`
- Workspace-level `AGENTS.md` for agent discovery

## What Changes

1. **Git init** — initialize git in each of the 16 pulled repos
2. **`.gitignore`** — add Python-specific ignores (`.venv/`, `__pycache__/`, etc.)
3. **`rclone bisync`** — set up bidirectional sync per repo with filters
4. **`uv sync`** — create Python environments
5. **Workspace `AGENTS.md`** — add `~/Developer/AGENTS.md` as workspace-level guide

## Non-Goals

- No code changes to any Python repo
- No CI/CD setup
- No Android/iOS repos (separate concern)

## Compatibility

Additive only. New repos appear at workspace root level.

## Rollback

Remove each `~/Developer/<repo>/` directory and bisync state.
