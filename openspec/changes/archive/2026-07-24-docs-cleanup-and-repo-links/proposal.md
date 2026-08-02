## Why

The TDT workspace `docs/` directory has accumulated stale directories, empty files, and one-time investigation reports that clutter the documentation surface. Meanwhile, 8+ repos have rich `docs/` directories that are not discoverable from the central index — a new contributor wouldn't know where to look. The workspace needs cleanup and a simple way to find repo-level documentation.

## What Changes

- Archive stale investigation reports (crashlytics PDFs, coverage assessments) to `docs/archive/`
- Relocate thin single-file directories (configuration, ecosystem-reports, ecc-harness, features) into appropriate parent directories
- Delete the empty `DOCUMENTATION-INDEX.md` (0 bytes, `INDEX.md` serves this role)
- Add a "Repository Documentation" section to `INDEX.md` linking to each repo's `docs/` directory with brief descriptions

## Capabilities

### New Capabilities
- `repo-doc-index`: Central index linking to repository-level documentation across the workspace

### Modified Capabilities
- (none — no existing specs are modified by this change)

## Impact

- **Files modified:** `docs/INDEX.md` (add repo links section)
- **Files moved:** ~8 files across stale directories → archive or parent directories
- **Directories removed:** 4 empty directories after relocation (configuration, ecosystem-reports, ecc-harness, features)
- **No code changes** — documentation only
- **No breaking changes** — all links are additive
