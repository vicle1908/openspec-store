## 1. Freeze the Repair Baseline

- [ ] 1.1 Confirm `upgrade-openspec-1-7-runtime` has recorded the installed OpenSpec version and final comparison baseline; do not edit a main spec before that checkpoint.
- [ ] 1.2 From `tdt-meta/`, record branch and `git status --short`; stop if any of the 66 target spec paths has unrelated dirty work.
- [ ] 1.3 Add `docs/tools/openspec-main-spec-baseline-repair.md` with the runtime version, 66-id/error-class baseline, batch ledger, evidence sources, validation results, rollback notes, and topology invariant.
- [ ] 1.4 Programmatically compare the six design batches with the strict-validation failure set and require exactly 66 unique ids with no omission or duplicate.
- [ ] 1.5 For every target file, record SHA-256, requirement headers, scenario headers, and current findings before edits; do not copy secrets or unrelated spec content into the ledger.

## 2. Establish Purpose and Semantic-Preservation Evidence

- [ ] 2.1 For each of the 64 missing-Purpose specs, record the selected evidence source in priority order: current requirements, archived OpenSpec history, then canonical repository documentation.
- [ ] 2.2 Draft each Purpose as capability-specific descriptive text with no SHALL/MUST behavior, placeholder, volatile repository list, private endpoint, or unsupported claim.
- [ ] 2.3 Review the before inventories and evidence map; remove and escalate any spec whose Purpose cannot be supported before starting its batch.

## 3. Repair Batch 1 — Agent Platform

- [ ] 3.1 Recheck dirty-state ownership for the 17 agent-platform paths and capture their batch-local before inventory.
- [ ] 3.2 Add evidence-backed Purpose sections to `agent-config`, `agent-core-budget-enforcement`, `agent-core-cli-extraction`, `agent-core-dead-code-cleanup`, `agent-core-memory-enhancement`, `agent-core-memory-lifecycle`, `agent-core-resilience-utility`, `agent-core-tool-resilience`, `agent-docker-local-dev`, `agent-docs-agent-config`, `agent-docs-harness`, `agent-docs-orchestration-enhanced`, `agent-docs-research`, `agent-docs-sync-code-intelligence`, `agent-docs-sync-project-scaffold`, `agent-durable-execution`, and `agent-yaml-config`.
- [ ] 3.3 Validate all 17 files independently, compare requirement/scenario inventories, and require the full-root invalid-id set to drop by only these 17 ids before marking the batch complete.

## 4. Repair Batch 2 — Documentation and Dependency Flows

- [ ] 4.1 Recheck dirty-state ownership for the 10 documentation/dependency paths and capture their batch-local before inventory.
- [ ] 4.2 Add evidence-backed Purpose sections to `blocking-dependency-tracking`, `dependency-visualization`, `docs-sync-memory`, `docs-sync-memory-wiring`, `docs-sync-observability`, `docs-sync-parallel-multi-repo`, `docs-sync-resilience`, `docs-sync-validation-dedup`, `integration-guide`, and `traceability`.
- [ ] 4.3 Validate all 10 files independently, compare requirement/scenario inventories, and require the full-root invalid-id set to drop by only these 10 ids before marking the batch complete.

## 5. Repair Batch 3 — Composition, Gateway, and SDK

- [ ] 5.1 Recheck dirty-state ownership for the 12 composition/gateway/SDK paths and capture their batch-local before inventory.
- [ ] 5.2 Add evidence-backed Purpose sections to `bifrost-gateway`, `configuration`, `consumer-composition-boundary`, `consumer-pattern`, `flavor-composition-sdk`, `mcp-integration`, `orchestration-command-api`, `resilient-gateway-sdk`, `resilient-tool-adoption`, `sdk-public-api`, and `typed-orchestration-state`.
- [ ] 5.3 Normalize only the two malformed scenario structures in `consumer-config-composition`, preserving parent requirements, text, order, conditions, and outcomes.
- [ ] 5.4 Validate all 12 files independently, compare requirement/scenario inventories with the approved normalization exception, and require the full-root invalid-id set to drop by only these 12 ids before marking the batch complete.

## 6. Repair Batch 4 — Harness, Memory, Evaluation, and Observability

- [ ] 6.1 Recheck dirty-state ownership for the 13 harness/memory/evaluation/observability paths and capture their batch-local before inventory.
- [ ] 6.2 Add evidence-backed Purpose sections to `evaluation`, `harness-integration`, `harness-media`, `harness-runtime-authoring`, `hooks`, `langfuse-otel-integration`, `memory-framework`, `memory-system`, `memory-vector-integration`, `mlflow-otel-integration`, `observability`, `otel-auto-instrumentation`, and `structured-eval-metrics`.
- [ ] 6.3 Validate all 13 files independently, compare requirement/scenario inventories, and require the full-root invalid-id set to drop by only these 13 ids before marking the batch complete.

## 7. Repair Batch 5 — Reporting and Operational Documentation

- [ ] 7.1 Recheck dirty-state ownership for the nine reporting/operational paths and capture their batch-local before inventory.
- [ ] 7.2 Add evidence-backed Purpose sections to `enhanced-report-sections`, `epic-data-collection`, `glossary`, `jira-daily-reports`, `report-generation`, `risk-analysis`, `runbook`, `spreadsheet-export-enhancement`, and `status-aggregation`.
- [ ] 7.3 Validate all nine files independently, compare requirement/scenario inventories, and require the full-root invalid-id set to drop by only these nine ids before marking the batch complete.

## 8. Repair Batch 6 — Workflow and Validation Contracts

- [ ] 8.1 Recheck dirty-state ownership for the five workflow/validation paths and capture their batch-local before inventory.
- [ ] 8.2 Add evidence-backed Purpose sections to `dynamic-workflow`, `pattern-decisions`, `validation-consistency`, and `workflow-dag`.
- [ ] 8.3 Add the missing `## Requirements` container to `ai-review-durable-scheduler` around its existing requirement blocks without changing normative content.
- [ ] 8.4 Validate all five files independently, compare requirement/scenario inventories, and require the full-root invalid-id set to drop by only these five ids before marking the batch complete.

## 9. Establish the Green Baseline

- [ ] 9.1 Run strict validation for each touched main spec, all main specs, all active changes, and the full root; require zero invalid main specs and no newly failing active change.
- [ ] 9.2 Compare final requirement/scenario inventories with the frozen baseline and investigate every difference other than the approved two-scenario structural normalization.
- [ ] 9.3 Verify every repaired spec remains at its original path and that no store metadata, `defaultStore`, workset, nested-spec move, or symlink target changed.
- [ ] 9.4 Review the final `tdt-meta` diff for placeholders, new normative behavior, credentials, application code, dependencies, generated assets, and unrelated OpenSpec artifacts.
- [ ] 9.5 Complete the evidence ledger and rollback record, validate this change strictly, and stop before archive, commit, or push.
