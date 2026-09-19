# Proposal

## Why

The Developer multi-repo workspace maintains rich architectural knowledge across local tools (LLM Wiki, OpenSpec specs, GitNexus, Graphify, and AgentMemory), but lacks an automated, fail-closed mechanism to sanitize and synchronize this ecosystem knowledge into the external Notion knowledge hub via the `ntn` CLI. Without a unified publishing bridge, external team members and cross-workspace agents cannot access compiled architecture blueprints, component definitions, or freshness audit metrics without local filesystem access.

## What Changes

- Create a standalone knowledge synchronization script `scripts/knowledge-refresh/sync-notion-knowledge.sh` tracked in `openspec-store/scripts/knowledge-refresh/` and installed to `Developer/scripts/knowledge-refresh/`.
- Establish a four-section sub-page hierarchy under the Notion Knowledge root (`3d7c4b21-deb4-8100-99c0-cfe30ef437ee`):
  1. *Ecosystem Concepts & Architecture* (Go platform patterns, Python agent ecosystem, MCP transport, OpenSpec lifecycle, Knowledge Graph architecture).
  2. *Ecosystem Component Entities* (12 service/runtime entities from `wiki/entities/`).
  3. *OpenSpec Architecture & Specifications* (Domain catalog grouping 409 specifications and active change status).
  4. *Knowledge Health & Freshness Matrix* (Nightly audit metrics from `knowledge-status.sh`).
- Implement fail-closed content sanitization: regex-based credential scrubbing (API keys, tokens, passwords) and absolute path normalization (`/Users/androidteam/` to `~/Developer/`).
- Implement local idempotency manifest (`~/.knowledge-refresh/notion-sync-manifest.json`) tracking source file SHA-256 digests and Notion page IDs to ensure safe in-place updates via `ntn pages edit` and skip unmodified content (`fresh_noop`).
- Implement hybrid triggering support: manual CLI execution (`--dry-run`, `--section <name>`, `--force`, `--all`) and automated execution as a post-refresh step in `refresh-knowledge-indexes.sh`.

## Capabilities

### New Capabilities

- `notion-knowledge-sync`: Automated fail-closed, idempotent synchronization of workspace wiki, OpenSpec specifications catalog, and index freshness matrices into Notion sub-pages via `ntn` CLI.

### Modified Capabilities

None.

## Impact

### Affected Ownership Boundaries
- `openspec-store/scripts/knowledge-refresh/`: Version-controlled source for synchronization scripts and inventory approval digests.
- `Developer/scripts/knowledge-refresh/`: Installed runtime scripts for LaunchAgent execution.
- `Developer/.knowledge-refresh/`: Runtime lockfiles, logs, and `notion-sync-manifest.json`.

### Non-Goals
- Bi-directional synchronization: This capability is strictly one-way publishing from authoritative local Git repositories and wiki pages into Notion; editing in Notion does not write back to local Git.
- Raw file dumps: We do not dump thousands of raw code files or uncompiled git logs into Notion; only curated wiki articles, spec catalogs, and audit summaries are synchronized.
- Modifying core Python `agent-docs-sync` CLI package dependencies or `mcp-router` databases.
- Managing Notion workspace user permissions or organization-level Notion billing.
