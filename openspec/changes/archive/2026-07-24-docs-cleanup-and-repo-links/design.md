## Context

The TDT workspace `docs/` directory (`tdt-meta/docs/`, symlinked from root) has grown organically. It now contains:
- 4 one-time investigation directories (crashlytics, coverage, configuration, ecosystem-reports, ecc-harness, features) with 1-2 files each
- An empty `DOCUMENTATION-INDEX.md` (0 bytes)
- 8+ repos with rich `docs/` directories that are invisible from the central index

The workspace root `docs/` is already a symlink to `tdt-meta/docs/` — single source of truth is established. The problem is discoverability and clutter.

## Goals / Non-Goals

**Goals:**
- Clean up stale/one-time directories in `docs/`
- Make repo-level documentation discoverable from `docs/INDEX.md`
- Keep the change minimal and safe (documentation only, no code)

**Non-Goals:**
- Consolidating mobile repo docs (keep as-is per user decision)
- Restructuring repo-level docs (each repo owns its own docs/)
- Creating a documentation build system or docs site
- Modifying any code or configuration

## Decisions

### Decision 1: Archive vs Delete for stale content

**Choice:** Move to `docs/archive/` with descriptive subdirectory names.

**Rationale:** These are investigation reports from June 2026. They may have historical value. Archiving preserves them while removing clutter from the active docs surface.

**Alternatives considered:**
- Delete outright — rejected because these are substantive reports (crashlytics root cause analysis, coverage assessments) that might be referenced later
- Leave in place — rejected because they create confusion about what's active

### Decision 2: Relocate single-file directories

**Choice:** Move files into thematic parent directories:
- `ecosystem-reports/jira-gitlab-alignment-2026-06-04.md` → `workflows/`
- `ecc-harness/playbook.md` → `tools/ecc-harness-playbook.md`
- `features/P3_VERTICAL_SCOPE.pdf` → `reports/`
- `vertical-scope/P3-VERTICAL-SCOPE(July 2025).pdf` → `reports/`

**Note:** `configuration/AGENTS.md` is a symlink to `../../AGENTS.md` — preserved intentionally, not relocated.

**Rationale:** These directories have 1 file each. The files have clear thematic homes. Creating directories for single files adds navigation overhead without benefit.

### Decision 3: Repo-level link format

**Choice:** Add a markdown table in `INDEX.md` under "Repository Documentation" with repo name (linked), file count, and brief content description.

**Rationale:** A table is scannable, the link is clickable, and the file count gives immediate sense of documentation richness. Brief descriptions help contributors decide which repo's docs to read.

**Format:**
```markdown
## Repository Documentation

| Repo | Docs | Key Content |
|------|------|-------------|
| [agent-core](../agent-core/docs/) | 28 files | Architecture, CLI, memory, orchestration |
```

### Decision 4: Mobile repos excluded from central index

**Choice:** Do not link mobile repo docs from the central index.

**Rationale:** Mobile repos (poems-mobile3-ios, poems-mobile3-android, and their release variants) have internal docs (rules, todos, issue-reports) that are repo-specific. They don't need workspace-level discovery. Linking 8 nearly-identical mobile doc sets would clutter the index.

## Risks / Trade-offs

- **[Risk]** Moving files might break internal cross-references → **Mitigation:** These are standalone investigation reports, not referenced from other docs. Verified via grep.
- **[Risk]** Repo-level links could become stale as repos change → **Mitigation:** Links are relative (`../repo/docs/`), so they survive repo renames. File counts may drift but that's cosmetic.
- **[Trade-off]** Archiving vs deleting loses immediate visibility → Accepted. Archive is a safety net; active docs surface is cleaner.
