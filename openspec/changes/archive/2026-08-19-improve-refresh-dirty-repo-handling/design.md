## Context

The refresh script's `is_dirty()` function (lines 166-175) checks `git status --porcelain` and skips repos with any output. It currently excludes:
- `?? graphify-out/` (untracked graphify files)
- ` M uv.lock` and `?? uv.lock` (dependency lock changes)

But it does NOT exclude:
- ` M graphify-out/*` (tracked graphify modifications from post-commit hook)
- `?? .omp/` (LSP state files)
- ` M AGENTS.md` / ` M CLAUDE.md` (gitnexus-generated files)
- `?? .claude/skills/gitnexus/` (gitnexus-generated skill directories)

This causes 7 repos to be perpetually skipped. Additionally, there's no `--force` flag for manual override.

See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- Make the refresh script handle generated-file changes automatically
- Provide a `--force` escape hatch for genuinely dirty repos
- Add freshness visibility without requiring manual status checks

**Non-Goals:**
- Auto-stash/restore dirty repos (too complex, error-prone)
- Modify batch mode behavior (still skips dirty repos for safety)
- Add CI/CD integration (separate concern)

## Decisions

### D1: Expand is_dirty() exclusions

**Choice**: Add these exclusion patterns to `is_dirty()`:
```bash
| grep -v '^ M graphify-out/'   # tracked graphify modifications
| grep -v '^M  graphify-out/'   # staged graphify modifications
| grep -v '^?? \.omp/'          # LSP state files
| grep -v 'AGENTS\.md'          # gitnexus-generated (tracked or untracked)
| grep -v 'CLAUDE\.md'          # gitnexus-generated (tracked or untracked)
| grep -v '^?? \.claude/skills/gitnexus/'  # gitnexus-generated skills
```

**Rationale**: All these patterns represent generated files that are expected to change after hooks run. Excluding them makes the dirty check more accurate without compromising safety.

**Alternatives considered**:
- *Only exclude graphify-out tracked*: Partial fix, leaves other generated files
- *Use a .gitignore-based approach*: More complex, doesn't help with tracked files
- *Add all exclusions to .gitignore*: Only works for untracked, not tracked modifications

### D2: Add --force flag for --repo mode

**Choice**: Add `--force` flag that bypasses `is_dirty()` check. Only works with `--repo` (single repo mode), not batch mode. Use a script-level `_FORCE` variable instead of threading through function args.

**Rationale**: Batch mode should always skip dirty repos (safety). But manual `--repo` operations might need to refresh a genuinely dirty repo (e.g., after testing, before committing). Using `_FORCE` avoids adding a 6th positional arg to `process_target()` which already has 5.

**Implementation**: Parse `--force` in main() arg loop, set `_FORCE=true`. In process_target(), check `[[ "${_FORCE:-}" == "true" ]]` to skip is_dirty.

### D3: Add freshness check output

**Choice**: Add a `--check` flag that reports which repos are stale without refreshing. Check BOTH GitNexus (meta.json lastCommit vs HEAD) and Graphify (graph.json built_at_commit vs HEAD). Support `--repo` mode for single-repo checks.

**Rationale**: Provides at-a-glance health visibility. Checking both tools catches cases where one is current but the other is stale (e.g., GitNexus refreshed but Graphify skipped).

**Implementation**: Iterate inventory (or single repo with --repo), compare meta.json lastCommit AND graph.json built_at_commit to git HEAD, report stale repos with tool-specific status.

## Risks / Trade-offs

- **[Risk] Over-excluding in is_dirty()** → Mitigated by keeping exclusions specific to known generated files. The comment block in is_dirty() documents each exclusion's purpose.
- **[Risk] --force on dirty repos might cause issues** → Mitigated by restricting to --repo mode only. Batch mode is never affected.
- **[Trade-off] --force vs stash/restore** → Chose simpler --force. Stash/restore was error-prone (stash pop failures observed during testing).

## Migration Plan

1. Update `is_dirty()` with new exclusions
2. Add `--force` flag parsing and propagation
3. Add `--check` flag for freshness reporting
4. Test on the 7 currently-skipped repos
5. Verify batch mode still skips genuinely dirty repos

## Open Questions

_(none)_
