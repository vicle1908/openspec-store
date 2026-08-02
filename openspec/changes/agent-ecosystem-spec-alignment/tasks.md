## 1. Standardize Naming

- [x] 1.1 Rename `docs-sync-memory` → `agent-docs-sync-memory`
- [x] 1.2 Rename `docs-sync-memory-wiring` → `agent-docs-sync-memory-wiring`
- [x] 1.3 Rename `docs-sync-observability` → `agent-docs-sync-observability`
- [x] 1.4 Rename `docs-sync-parallel-multi-repo` → `agent-docs-sync-parallel-multi-repo`
- [x] 1.5 Rename `docs-sync-resilience` → `agent-docs-sync-resilience`
- [x] 1.6 Rename `docs-sync-validation-dedup` → `agent-docs-sync-validation-dedup`
- [x] 1.7 Rename `harness-workflow-architecture` → `agent-harness-workflow-architecture`
- [x] 1.8 Add `# Title Specification` lines to all 7 renamed specs
  - Evidence: all 7 titles verified — `# Agent Docs Sync * Specification` and `# agent-harness-workflow-architecture Specification`

## 2. Separate Standalone Specs

- [x] 2.1 Move `harness-workflow` to `_standalone/harness-workflow`
- [x] 2.2 Move `harness-integration` to `_standalone/harness-integration`
- [x] 2.3 Move `harness-compaction` to `_standalone/harness-compaction`
- [x] 2.4 Move `harness-media` to `_standalone/harness-media`
- [x] 2.5 Move `harness-runtime-authoring` to `_standalone/harness-runtime-authoring`
- [x] 2.6 Move `harness-artifact-integrity` to `_standalone/harness-artifact-integrity`
- [x] 2.7 Move `agent-docs-harness` to `_standalone/agent-docs-harness`
- [x] 2.8 Move `agent-planning` to `_standalone/agent-planning`
  - Evidence: `ls _standalone/` returns 8 directories; `openspec spec list` returns 0 stray `docs-sync-*` or `harness-*` specs

## 3. Fix Purpose Text

- [x] 3.1 Update purpose for `agent-core-budget-enforcement` — "Define USD cost ceiling enforcement for LLM gateway calls..."
- [x] 3.2 Update purpose for `agent-core-cli-extraction` — "Define the modular CLI architecture for agent-core..."
- [x] 3.3 Update purpose for `agent-core-dead-code-cleanup` — "Define dead code detection and removal across agent-core modules..."
- [x] 3.4 Update purpose for `agent-core-docker-local-development` — "Docker Compose stack for local agent-core development..."
- [x] 3.5 Update purpose for `agent-core-memory-enhancement` — "Define memory system enhancements for agent-core..."
- [x] 3.6 Update purpose for `agent-core-memory-lifecycle` — "Define the memory lifecycle contract..."
- [x] 3.7 Update purpose for `agent-core-resilience-utility` — "Define resilience primitives for agent-core..."
- [x] 3.8 Update purpose for `agent-core-tool-resilience` — "Define tool-level resilience patterns..."
- [x] 3.9 Update purpose for `agent-docs-sync-code-intelligence` — "Define code intelligence capabilities for docs-sync..."
- [x] 3.10 Update purpose for `agent-docs-sync-memory` — "Define the memory layer for docs-sync..."
- [x] 3.11 Update purpose for `agent-docs-sync-memory-wiring` — "Define the memory wiring contract for docs-sync..."
- [x] 3.12 Update purpose for `agent-docs-sync-observability` — "Define observability for docs-sync..."
- [x] 3.13 Update purpose for `agent-docs-sync-parallel-multi-repo` — "Define parallel multi-repository documentation sync..."
- [x] 3.14 Update purpose for `agent-docs-sync-project-scaffold` — "Define the project scaffold capability for docs-sync..."
- [x] 3.15 Update purpose for `agent-docs-sync-resilience` — "Define resilience patterns for docs-sync..."
- [x] 3.16 Update purpose for `agent-docs-sync-validation-dedup` — "Define validation and deduplication for docs-sync..."
  - Evidence: all 16 purpose texts verified via python3 content check; no empty or generic boilerplate remaining

## 4. Ownership Catalogs

- [x] 4.1 Create `SPEC_INDEX.md` in agent-core (13 specs, 12 modules, 25 docs)
- [x] 4.2 Create `SPEC_INDEX.md` in agent-docs-sync (9 specs, 6 modules, 9 docs)
- [x] 4.3 Create `SPEC_INDEX.md` in agent-harness (5 specs, 5 modules, 7 docs)
  - Evidence: each SPEC_INDEX.md maps spec → module(s) → doc(s) with coverage gaps noted

## 5. Store Context

- [x] 5.1 Update `openspec/config.yaml` context with agent ecosystem section
  - Evidence: config.yaml now includes "Agent Ecosystem (Python 3.14, uv)" section with repo descriptions, dependency relationships, and naming conventions

## 6. Validation

- [x] 6.1 Validate all 25 renamed/updated agent-ecosystem specs — all pass
- [x] 6.2 Validate all 8 standalone specs in `_standalone/` — all pass
- [x] 6.3 Run full `openspec validate --strict --all` — 350/350 pass, 0 fail
- [x] 6.4 Validate `agent-ecosystem-spec-alignment` change — valid (skip_specs)
  - Evidence: `Totals: 350 passed, 0 failed (350 items)` at commit 77a61c8

## 7. Commit

- [x] 7.1 Commit store changes — `77a61c8 refactor(specs): standardize agent ecosystem naming, separate standalone harness-skill specs`
- [x] 7.2 Commit agent-core SPEC_INDEX.md — `45158e2 docs: add SPEC_INDEX.md — maps specs to modules and docs`
- [x] 7.3 Commit agent-docs-sync SPEC_INDEX.md — `5c71274 docs: add SPEC_INDEX.md — maps specs to modules and docs`
- [x] 7.4 Commit agent-harness SPEC_INDEX.md — `16ba8c0 docs: add SPEC_INDEX.md — maps specs to modules and docs`
- [x] 7.5 Commit change artifacts + config update — `17002b0 feat: add agent-ecosystem-spec-alignment change + update workspace context`
