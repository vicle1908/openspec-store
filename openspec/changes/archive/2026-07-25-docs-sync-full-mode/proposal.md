## Why

The current `docs-sync` CLI only checks **git diff** (recent changes) for documentation updates. This means documentation gaps — source code that never had docs, broken links across the entire doc set, or Diátaxis violations in existing docs — go undetected until someone manually notices. Full mode should scan **all source code and all docs** comprehensively, not just recent changes.

## What Changes

- Add `docs-sync sync --full` that runs a comprehensive pipeline: scan all source files, classify into Diátaxis, audit all docs, generate missing docs, validate everything, and produce a summary report
- Add `docs-sync audit` command for standalone comprehensive doc audit (read-only, no generation)
- Extend multi-repo support (`sync-all --full`) to run the full pipeline across all TDT repos with aggregated reporting
- Add gap detection: identify source files without documentation, docs with broken links, and Diátaxis violations
- Add comprehensive reporting with statistics (files scanned, docs found, gaps identified, docs generated)

## Capabilities

### New Capabilities

- `docs-sync-full-mode`: Full comprehensive documentation pipeline that scans all code and all docs, detects gaps, generates missing docs, and validates everything

### Modified Capabilities

- `agent-docs-sync`: Extend CLI with `--full` flag on sync command and new `audit` command; add gap detection and comprehensive reporting requirements

## Impact

- **agent-docs-sync**: Main implementation target — new CLI commands, new pipeline composition, enhanced reporting
- **Existing tools**: Reuses ScannerTool, ClassifierTool, CheckLinksTool, EnforcerTool, GitNexusLoaderTool, GraphifyLoaderTool (no changes to these)
- **Discovery pipeline**: Reuses `run_discovery_pipeline` for the discover phase (no changes)
- **Sync pipeline**: Extends `build_sync_pipeline` with full-mode variant
- **Config**: No new config needed — uses existing harness and planning configuration
- **Dependencies**: No new dependencies — all tools already exist

## Non-Goals

- Replacing the existing git-diff-based sync (that stays as the default mode)
- Changing the DiscoveryAgent or ValidationAgent behavior
- Adding new LLM models or providers
- Modifying the pydantic-ai-harness integration
