## Why

The knowledge refresh script (`refresh-knowledge-indexes.sh`) skips repos with dirty working trees. While this prevents conflicts, the `is_dirty()` function has blind spots: it excludes untracked `graphify-out/` files but NOT tracked graphify-out modifications (created by the graphify post-commit hook). This causes 7 repos to be perpetually skipped despite having only harmless generated-file changes. Additionally, there's no way to force-refresh a dirty repo, and no monitoring to detect when repos go stale.

## What Changes

- **Fix `is_dirty()` exclusions**: Add patterns for tracked graphify-out modifications, `.omp/`, `AGENTS.md`, `CLAUDE.md`, and gitnexus-generated skill directories
- **Add `--force` flag**: Bypass dirty check for `--repo` mode only (batch mode still skips dirty repos for safety)
- **Add freshness monitoring**: Simple wrapper that reports stale repos with actionable status

## Capabilities

### New Capabilities

_(none — pure infrastructure improvement)_

### Modified Capabilities

_(none — script internals, not spec-governed)_

**skip_specs: true** — Script behavior changes only.

## Impact

- **File modified**: `scripts/knowledge-refresh/refresh-knowledge-indexes.sh`
- **Repos affected**: 7 repos that were previously skipped will now refresh
- **Risk**: LOW — exclusions only affect generated files; --force is manual-only
- **Precedent**: Builds on `fix-gitnexus-refresh-fallback-and-graphify-skill-sync` and `fix-dev-tooling-refresh-mechanism`
