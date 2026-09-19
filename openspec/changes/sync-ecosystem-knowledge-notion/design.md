# Design

## Context

See `proposal.md - Why` for motivation.

The workspace currently hosts 24 curated markdown wiki pages in `~/Developer/wiki/` (covering concepts, entities, comparisons, and architecture), 409 specifications in `openspec-store/openspec/specs/`, and nightly knowledge graph indices (GitNexus and Graphify) managed by LaunchAgent `com.developer.index-refresh` via `scripts/knowledge-refresh/refresh-knowledge-indexes.sh`.

The Notion CLI (`/Users/androidteam/.local/bin/ntn`, v0.23.7) is authenticated to workspace `Lê Khánh Vinh’s Workspace` with verified access to the Knowledge Root (`3d7c4b21-deb4-8100-99c0-cfe30ef437ee`).

## Goals / Non-Goals

**Goals:**
- Provide a deterministic, standalone synchronization script `sync-notion-knowledge.sh` adhering to existing script infrastructure patterns.
- Organize synchronized knowledge into four clear sub-pages under the Knowledge Root: Concepts & Architecture, Entities, OpenSpec Catalog, and Freshness Matrix.
- Guarantee that no secrets, tokens, or operator-specific paths escape to Notion.
- Ensure idempotent execution using SHA-256 digests in a local state manifest.
- Support both ad-hoc terminal execution and automated integration into the nightly refresh pipeline.

**Non-Goals:**
- Bi-directional sync or syncing changes made in Notion back to Git.
- Uploading uncurated raw source code files or Git commit logs.
- Modifying Notion user roles or workspace access permissions.

## Decisions

### Decision 1: Standalone Script with Dual-Tree Parity
- **Pattern**: Follow existing script layout (`openspec-store/scripts/knowledge-refresh/` as source of truth, copied to `Developer/scripts/knowledge-refresh/` with approval hash verification in `knowledge-refresh-approval.sha256`).
- **Rationale**: Keeps synchronization lightweight, independent of Python virtual environments, and directly invokable by both shell users and macOS LaunchAgents.
- **Alternatives Considered**: Extending `agent-docs-sync` Python CLI. Rejected because `agent-docs-sync` focuses on source-to-doc mapping within individual Git repos, whereas Notion knowledge export is an ecosystem-wide compilation task across multiple repos.

### Decision 2: Four-Section Hierarchical Notion Organization
- **Pattern**: Create 4 parent sub-pages under Knowledge Root (`3d7c4b21-deb4-8100-99c0-cfe30ef437ee`), and place Markdown documents as child pages beneath their respective section.
- **Sections**:
  1. `Ecosystem Concepts & Architecture`: 6 concept docs from `wiki/concepts/`, 1 comparison from `wiki/comparisons/`, and 1 architecture doc from `wiki/architecture/`.
  2. `Ecosystem Component Entities`: 12 entity docs from `wiki/entities/`.
  3. `OpenSpec Architecture & Specifications`: Synthesized domain catalog of 409 specs and active changes ledger.
  4. `Knowledge Health & Freshness Matrix`: Nightly report from `knowledge-status.sh`.
- **Rationale**: Avoids cluttering the Knowledge root or a flat database with dozens of mixed-scope entries, providing a clean table-of-contents navigation experience in Notion UI.

### Decision 3: Idempotency, Transaction Boundaries & Notion CLI Flags
- **State Manifest**: `~/.knowledge-refresh/notion-sync-manifest.json` stores:
  ```json
  {
    "sections": {
      "concepts": "<notion-page-id>",
      "entities": "<notion-page-id>",
      "specs": "<notion-page-id>",
      "freshness": "<notion-page-id>"
    },
    "documents": {
      "wiki/concepts/go-platform-architecture.md": {
        "page_id": "<notion-page-id>",
        "sha256": "<hash>",
        "last_synced": "2026-09-19T05:00:00Z"
      }
    }
  }
  ```
- **Transaction Boundary**: Individual document level. The manifest file is only updated after `ntn pages create` or `ntn pages edit` exits with code 0. If a failure occurs mid-batch, subsequent runs resume cleanly without duplicate page creation.
- **CLI Flag Invariants**:
  - `ntn pages create --parent page:<id> --json < content.md`: Uses `--json` to parse the returned `.id` via `jq -r .id`.
  - `ntn pages edit <page-id> --allow-deleting-content --json < content.md`: Uses `--allow-deleting-content` to allow replacing child blocks without interactive prompts and `--json` for structured status validation.
  - Rate-limit pacing: 500ms sleep delay between consecutive Notion write calls.

### Decision 4: Fail-Closed Sanitization Engine
- **Pattern**: Reuses and extends the regex pattern established in `refresh-knowledge-indexes.sh:75`:
  - Token scrubbing: Replaces matches of `(MCPR_TOKEN|AGENTMEMORY_SECRET|GITHUB_TOKEN|api_key|bearer_token|password)=...` with `REDACTED`.
  - Path normalization: Transforms `/Users/androidteam/Developer/` to `~/Developer/`.
- **Rationale**: Prevents accidental credential leaks to external cloud services and keeps documentation portable.

### Decision 5: Hybrid Triggering Architecture
- **CLI Flags**: `--dry-run` (preview diffs without writing), `--section <name>` (filter by category: `concepts`, `entities`, `specs`, `freshness`), `--force` (bypass SHA check), and `--all` (full run).
- **Nightly Hook**: Appended to `refresh-knowledge-indexes.sh` after repository indexing passes complete.

## Risks / Trade-offs

- **Notion Rate Limiting**: Consecutive rapid `ntn api` calls may trigger HTTP 429. *Mitigation*: Introduce a 500ms pacing delay (`sleep 0.5`) between document sync operations.
- **Local Manifest Loss**: If `notion-sync-manifest.json` is deleted, re-running would risk creating duplicate section pages. *Mitigation*: The bootstrap routine inspects existing child pages of the Knowledge Root using regex pattern `<page url="https://app.notion.com/p/([0-9a-f]+)">([^<]+)</page>` from `ntn pages get` output before creating new section parents.
- **Divergence between Local Wiki and Notion**: Manual edits in Notion would be overwritten by future syncs. *Mitigation*: The header of each synced Notion page includes an automated synchronization banner indicating that the page is managed by automated ecosystem sync.
