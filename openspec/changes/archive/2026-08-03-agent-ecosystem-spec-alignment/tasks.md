## 1. Standardize Naming

- [x] 1.1 Rename `docs-sync-memory` → `agent-docs-sync-memory`
- [x] 1.2 Rename `docs-sync-memory-wiring` → `agent-docs-sync-memory-wiring`
- [x] 1.3 Rename `docs-sync-observability` → `agent-docs-sync-observability`
- [x] 1.4 Rename `docs-sync-parallel-multi-repo` → `agent-docs-sync-parallel-multi-repo`
- [x] 1.5 Rename `docs-sync-resilience` → `agent-docs-sync-resilience`
- [x] 1.6 Rename `docs-sync-validation-dedup` → `agent-docs-sync-validation-dedup`
- [x] 1.7 Rename `harness-workflow-architecture` → `agent-harness-workflow-architecture`
- [x] 1.8 Add `# Title Specification` lines to all 7 renamed specs

## 2. Separate Standalone Specs

- [x] 2.1 Move `harness-workflow` to `_standalone/harness-workflow`
- [x] 2.2 Move `harness-integration` to `_standalone/harness-integration`
- [x] 2.3 Move `harness-compaction` to `_standalone/harness-compaction`
- [x] 2.4 Move `harness-media` to `_standalone/harness-media`
- [x] 2.5 Move `harness-runtime-authoring` to `_standalone/harness-runtime-authoring`
- [x] 2.6 Move `harness-artifact-integrity` to `_standalone/harness-artifact-integrity`
- [x] 2.7 Move `agent-docs-harness` to `_standalone/agent-docs-harness`
- [x] 2.8 Move `agent-planning` to `_standalone/agent-planning`

## 3. Fix Purpose Text

- [x] 3.1 Update purpose for `agent-core-budget-enforcement`
- [x] 3.2 Update purpose for `agent-core-cli-extraction`
- [x] 3.3 Update purpose for `agent-core-dead-code-cleanup`
- [x] 3.4 Update purpose for `agent-core-docker-local-development`
- [x] 3.5 Update purpose for `agent-core-memory-enhancement`
- [x] 3.6 Update purpose for `agent-core-memory-lifecycle`
- [x] 3.7 Update purpose for `agent-core-resilience-utility`
- [x] 3.8 Update purpose for `agent-core-tool-resilience`
- [x] 3.9 Update purpose for `agent-docs-sync-code-intelligence`
- [x] 3.10 Update purpose for `agent-docs-sync-memory`
- [x] 3.11 Update purpose for `agent-docs-sync-memory-wiring`
- [x] 3.12 Update purpose for `agent-docs-sync-observability`
- [x] 3.13 Update purpose for `agent-docs-sync-parallel-multi-repo`
- [x] 3.14 Update purpose for `agent-docs-sync-project-scaffold`
- [x] 3.15 Update purpose for `agent-docs-sync-resilience`
- [x] 3.16 Update purpose for `agent-docs-sync-validation-dedup`

## 4. Ownership Catalogs

- [x] 4.1 Create `SPEC_INDEX.md` in agent-core (13 specs, 25 docs)
- [x] 4.2 Create `SPEC_INDEX.md` in agent-docs-sync (9 specs, 9 docs)
- [x] 4.3 Create `SPEC_INDEX.md` in agent-harness (5 specs, 7 docs)

## 5. Store Context

- [x] 5.1 Update `openspec/config.yaml` context with agent ecosystem section

## 6. Validation

- [x] 6.1 Validate all 25 renamed/updated agent-ecosystem specs
- [x] 6.2 Validate all 8 standalone specs in `_standalone/`
- [x] 6.3 Run full `openspec validate --strict --all` (349/349 pass)

## 7. Commit

- [x] 7.1 Commit store changes (77a61c8)
- [x] 7.2 Commit agent-core SPEC_INDEX.md (45158e2)
- [x] 7.3 Commit agent-docs-sync SPEC_INDEX.md (5c71274)
- [x] 7.4 Commit agent-harness SPEC_INDEX.md (16ba8c0)
