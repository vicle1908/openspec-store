# Proposal

## Why

The workspace previously relied on fragile custom Python wrappers (`google_api.py`, `setup.py`) and ad-hoc markdown notes that suffered from silent token invalidation, scope mismatches, and zero discovery across Codex, Claude Code, and other workspace agents. Adopting the official Google Workspace CLI (`gws`) and its official agent skills catalog via the standard `npx skills` manager provides an encrypted keyring-backed, upstream-synchronized, and multi-agent discoverable foundation across `.agents/` and `.claude/` with continuous update support (`npx skills update`).

## What Changes

- Use `npx skills add https://github.com/googleworkspace/cli/tree/main/skills/<skill-name> -y` to install official Google Workspace Agent Skills (`gws-calendar`, `gws-drive`, `gws-gmail`, `gws-docs`, `gws-sheets`, `gws-tasks`) into canonical workspace roots (`~/Developer/.agents/skills/`).
- Wire symlinks automatically into `~/Developer/.claude/skills/` for Claude Code and register entries in `~/Developer/.agents/skills-lock.json` for deterministic tracking.
- Enable automated continuous upstream maintenance using `npx skills update [skills...]` to track upstream Google Workspace CLI skill revisions without manual drift.
- Register adopted `gws-*` skills in `codex-user-skill-manifest.txt` and `claude-user-skill-manifest.txt` for user-scope cross-repository discovery.
- Deprecate custom Python wrappers (`google_api.py`, `setup.py`) in favor of native `/opt/homebrew/bin/gws` subcommands with structured JSON output (`--format json`).
- Establish runtime verification and diagnostics via `gws auth status` to validate credentials without invoking live mutating API calls.

## Capabilities

### New Capabilities

- `gws-agent-skills`: Standardized execution contract, parameter formatting, structured JSON output, and `npx skills update` lifecycle for official Google Workspace agent skills via `gws` CLI.

### Modified Capabilities

- `workspace-openspec-skill-discovery`: Incorporates official Google Workspace agent skills into canonical shared skill roots (`.agents/`), Claude Code native roots (`.claude/`), and user-scope discovery synchronization.

## Impact

- Canonical skills: Managed entries in `~/Developer/.agents/skills/` and symlinks in `~/Developer/.claude/skills/`.
- Lockfile: `~/Developer/.agents/skills-lock.json` tracks upstream sources, revisions, and content hashes.
- Lifecycle: Skills support `npx skills update` for recurring maintenance.
- Discovery manifests: `~/Developer/platform/openspec-store/config/codex-user-skill-manifest.txt` and `claude-user-skill-manifest.txt`.
- Synchronization: Verified via `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check`.
- CLI dependency: `/opt/homebrew/bin/gws` with OS keyring authentication.
