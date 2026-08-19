## Why

The nightly knowledge index refresh (`refresh-knowledge-indexes.sh`) fails for 13 of 20 inventoried repos every cycle with no self-healing. The root cause (verified by tech-verifier): the `incrementalInProgress` flag is set in 12 repos from a previously interrupted analysis run, and 1 repo (tdt-core) has FTS index corruption. The refresh script has no fallback mechanism — when `gitnexus analyze --index-only` fails, it logs the failure and moves on. Next night, the same repos fail again. Additionally, the graphify skill is stale across 7 of 8 agent platforms (only Claude was updated today), causing spurious warnings on every `graphify --version` call and preventing other agents from using the latest graphify features.

## What Changes

- **Add FTS repair fallback to `gitnexus_refresh()`**: When `gitnexus analyze --index-only` fails, attempt `gitnexus analyze --repair-fts` before giving up. This fixes the FTS corruption issue in ~1 repo without a full re-index.
- **Add force re-index fallback to `gitnexus_refresh()`**: When repair-fts also fails (or for duplicate primary key errors), fall back to `gitnexus analyze --force --index-only --default-branch <branch> --name <name>` for a clean rebuild. This fixes the duplicate primary key issue in 11 Python repos.
- **Update graphify skills across all platforms**: Run `graphify install --platform <P>` for codex, hermes, pi, copilot, opencode, gemini, and agents to sync them to 0.9.46.
- **Fix `knowledge-status.sh` version detection**: The `tool_version()` function captures stderr warnings mixed with version output, corrupting the graphify version string. Use `2>/dev/null` on stderr separately.

## Capabilities

### New Capabilities

_(none — pure tooling fix, no spec-level behavior changes)_

### Modified Capabilities

_(none — refresh script is infrastructure, not spec-governed behavior)_

**skip_specs: true** — This change modifies refresh script internals and updates skill files. No spec-governed behavior changes.

## Impact

- **Files touched**: `scripts/knowledge-refresh/refresh-knowledge-indexes.sh`, `scripts/knowledge-refresh/knowledge-status.sh`
- **Skill directories updated**: `~/.codex/skills/graphify/`, `~/.hermes/skills/graphify/`, `~/.pi/agent/skills/graphify/`, `~/.copilot/skills/graphify/`, `~/.config/opencode/skills/graphify/`, `~/.gemini/skills/graphify/`, `~/Developer/.agents/skills/graphify/`
- **Repos affected**: All 13 failing repos will self-heal on next nightly refresh
- **Risk**: LOW — refresh script changes are advisory (never block git operations); skill updates are file copies
- **Precedent**: Builds on `2026-08-19-fix-dev-tooling-refresh-mechanism` which fixed dirty-tree skipping and WAL threshold but did not address the fallback gap
