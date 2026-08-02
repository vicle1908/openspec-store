## Why

The current `agent-docs-sync` documentation synchronization tool relies on a static, manually-maintained `doc-mapping.yaml` file that maps source files to documentation targets. This approach has critical limitations:

1. **No auto-discovery**: New source files are silently ignored unless manually added to the mapping
2. **No deployment support**: Docker, compose, launchd, CI/CD files are read by tools but never mapped to documentation
3. **No Diátaxis structure**: Documentation is flat (reference/explanation only), missing tutorials and how-to guides
4. **No coverage reporting**: No visibility into which source files lack documentation or which Diátaxis quadrants are underpopulated
5. **No multi-language support**: Only Python files are mapped; Swift, Kotlin, TypeScript, Go, Rust are ignored

The TDT ecosystem has grown to 15+ repositories with 100K+ symbols across iOS, Android, Python, and Go codebases. Manual mapping cannot scale. GitNexus and Graphify already provide structural analysis, community detection, and change tracking — but this intelligence is not leveraged for documentation discovery.

## What Changes

- **New Discovery Engine**: Replace static `doc-mapping.yaml` with a hybrid discovery system that combines gitnexus (symbol analysis, ast_hash change detection), graphify (community detection, god nodes, isolated nodes), and file system scanning (deployment artifacts, config files, skills)

- **Diátaxis Classification**: Auto-classify documentation into four quadrants (tutorial, how-to, explanation, reference) using rule-based classification with LLM fallback for ambiguous cases

- **Soft Enforcement**: Validate generated documentation against Diátaxis rules with thresholds (70% required sections, 150% max words, hard block for forbidden elements)

- **Override System**: Human-readable overrides in `.docs-sync-overrides.yaml` (gitignored) that take precedence over auto-discovery, with conflict logging

- **State Management**: `.docs-sync-state.yaml` (committed) tracking discovery results, classification history, coverage gaps, and cache invalidation keys

- **Standalone `discover` Command**: New CLI command that runs discovery independently, with integration into the existing `sync` workflow

- **Multi-Platform Deployment Detection**: Recognize Docker, compose, launchd, systemd, GitHub Actions, GitLab CI, Procfile, Vercel, Netlify and map to appropriate how-to documentation

## Capabilities

### New Capabilities

- `hybrid-discovery`: Core discovery engine that combines gitnexus structural analysis, graphify community detection, and file system scanning to auto-generate source-to-documentation mappings without manual configuration

- `diataxis-classification`: Rule-based classification system that assigns documentation to Diátaxis quadrants (tutorial, how-to, explanation, reference) with LLM fallback for ambiguous cases, including enforcement rules with configurable thresholds

- `override-system`: Human override mechanism allowing per-machine, per-repo customization of discovery results, stored in gitignored files with conflict detection and resolution

- `discovery-state`: State management system for caching discovery results, tracking classification history, detecting coverage gaps, and managing cache invalidation via git commit hashes and gitnexus/graphify manifest timestamps

### Modified Capabilities

(No existing capabilities modified — this is a new subsystem)

## Impact

### Affected Code
- `src/agent_docs_sync/workflows/sync_pipeline.py`: Add discover step, replace doc-mapping.yaml lookup with auto_mapping
- `src/agent_docs_sync/config.py`: Add state/override loading, deprecate doc-mapping.yaml
- `src/agent_docs_sync/cli.py`: Add `discover` command, add `--discover` flag to `sync`
- `src/agent_docs_sync/multi_repo.py`: Replace hardcoded DOC_MAPPING with discovery results

### New Code
- `src/agent_docs_sync/discovery/__init__.py`: Discovery engine entry point
- `src/agent_docs_sync/discovery/scanner.py`: File system artifact scanner
- `src/agent_docs_sync/discovery/gitnexus_loader.py`: GitNexus index loader (file hashes, symbols)
- `src/agent_docs_sync/discovery/graphify_loader.py`: Graphify manifest loader (communities, god nodes, gaps)
- `src/agent_docs_sync/discovery/classifier.py`: Diátaxis rule-based classifier
- `src/agent_docs_sync/discovery/state.py`: State management (.docs-sync-state.yaml)
- `src/agent_docs_sync/discovery/overrides.py`: Override resolution system
- `src/agent_docs_sync/discovery/enforcer.py`: Diátaxis enforcement with thresholds

### Dependencies
- No new external dependencies (gitnexus and graphify are CLI tools, not Python packages)
- Existing: `ruamel.yaml`, `pydantic`, `git` (GitPython)

### Systems Affected
- `agent-docs-sync` CLI tool (new command, enhanced workflow)
- All TDT repositories that use `docs-sync sync` (automatic, backward-compatible)
- Documentation generation prompts (Diátaxis-aware)
- CI/CD pipelines using `docs-sync validate` (new enforcement rules)
