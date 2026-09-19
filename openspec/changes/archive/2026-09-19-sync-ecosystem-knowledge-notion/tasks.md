# Tasks

## 1. Foundation & Manifest Engine

- [x] 1.1 Scaffold manifest infrastructure and state directory
  - Create directory `~/.knowledge-refresh/` and initialize schema for `notion-sync-manifest.json` tracking section IDs and per-document SHA-256 digests.
  - *Verification*: Verify `~/.knowledge-refresh/notion-sync-manifest.json` validates with `jq .` and defines `sections` and `documents` objects.
- [x] 1.2 Implement fail-closed sanitization and path normalization functions
  - Author bash/sed sanitization utility in `scripts/knowledge-refresh/sync-notion-knowledge.sh` redacting credential tokens and normalizing `/Users/androidteam/Developer/` to `~/Developer/`.
  - *Verification*: Run a synthetic test string containing `MCPR_TOKEN=secret` and verify the output contains `MCPR_TOKEN=REDACTED` with zero token leakage.

## 2. Ingestion Adapter & Notion Sub-Page Hierarchy

- [x] 2.1 Implement section bootstrap routine with regex discovery
  - Query Knowledge Root (`3d7c4b21-deb4-8100-99c0-cfe30ef437ee`) via `ntn pages get` to resolve existing or create missing section sub-pages using pattern `<page url="https://app.notion.com/p/([0-9a-f]+)">([^<]+)</page>` (`Ecosystem Concepts & Architecture`, `Ecosystem Component Entities`, `OpenSpec Architecture & Specifications`, `Knowledge Health & Freshness Matrix`).
  - Store resolved section page IDs into `notion-sync-manifest.json`.
  - *Verification*: Run bootstrap and verify all 4 section page IDs are recorded and accessible via `ntn pages get <section-id>`.
- [x] 2.2 Implement idempotent page sync engine with `--allow-deleting-content` and pacing
  - Implement document diffing against manifest SHA-256 with 500ms pacing delay between API calls. If match, output `fresh_noop`. If new, call `ntn pages create --parent page:<section-id> --json`. If changed, call `ntn pages edit <page-id> --allow-deleting-content --json`.
  - Update `notion-sync-manifest.json` after successful exit code 0.
  - *Verification*: Run sync twice on a test document; observe initial creation followed by `fresh_noop` on second run.
- [x] 2.3 Ingest Ecosystem Concepts, Comparisons, Architecture, and Entities into Notion
  - Process all 6 concept docs from `wiki/concepts/`, 1 comparison from `wiki/comparisons/`, 1 architecture doc from `wiki/architecture/`, and 12 entity docs from `wiki/entities/`.
  - *Verification*: Run `sync-notion-knowledge.sh --section concepts && sync-notion-knowledge.sh --section entities` and verify all pages exist in Notion under their respective section parents.
## 3. OpenSpec Catalog & Freshness Matrix Integration

- [x] 3.1 Build OpenSpec specifications domain catalog generator
  - Author script routine scanning `openspec-store/openspec/specs/*/spec.md` to produce a structured Markdown overview table grouped by capability domains.
  - Sync the generated catalog to section `OpenSpec Architecture & Specifications`.
  - *Verification*: Inspect generated catalog in Notion via `ntn pages get <specs-section-page-id>` and confirm all domains and active changes are listed.
- [x] 3.2 Build Knowledge Health & Freshness Matrix publisher
  - Author script routine executing `scripts/knowledge-refresh/knowledge-status.sh --json` to generate an executive freshness matrix.
  - Sync the freshness report to section `Knowledge Health & Freshness Matrix`.
  - *Verification*: Confirm freshness report in Notion displays table matching live GitNexus and Graphify status.

## 4. Automation & Verification

- [x] 4.1 Wire post-refresh trigger into `refresh-knowledge-indexes.sh` with dual-tree parity
  - Add execution of `sync-notion-knowledge.sh --incremental` to `refresh-knowledge-indexes.sh` after repository indexing completes.
  - Copy updated script from `openspec-store/scripts/knowledge-refresh/` to `Developer/scripts/knowledge-refresh/`.
  - *Verification*: Run `scripts/knowledge-refresh/refresh-knowledge-indexes.sh --check` to verify approval digests match.
- [x] 4.2 End-to-end dry-run and live validation
  - Execute `sync-notion-knowledge.sh --dry-run` and confirm 0 side effects.
  - Execute full sync and verify all sections in Notion.
  - *Verification*: Run `openspec validate sync-ecosystem-knowledge-notion --strict --store openspec-store` and ensure 0 errors.
