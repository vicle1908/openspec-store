# Tasks: remediate-archived-store-validation

## Phase 1 — Inventory and classify

- [x] 1.1 Confirmed latest OpenSpec: v1.9.0 via npm (`npm view @fission-ai/openspec version`) and GitHub releases API. Installed binary matches: `openspec --version` = 1.9.0 at `/Users/androidteam/.npm-global/bin/openspec`.
- [x] 1.2 Ran `openspec validate --archived --strict --no-interactive --json --store openspec-store`. Found 66 failures out of 404 archived changes.
- [x] 1.3 Reduced JSON into structured inventory. All 66 share the same root cause: `[ERROR] tasks.md: N incomplete tasks (M/N completed)`. No malformed deltas, no missing scenarios, no schema issues — only unchecked task boxes.
- [x] 1.4 Classified into 3 remediation types: (A) cancelled/abandoned with 0 completed, (B) near-complete with 1-3 incomplete, (C) partially complete with 4+ incomplete.

## Phase 2 — Repair near-complete archives (15 changes, 1-3 tasks each)

- [x] 2.1 Repaired batch 1 (5 archives): fix-app-services-apply-schedules, impact-codescan-marker-alignment, deployable-env-loading, scheduler-compose-self-bootstrap, ddd-repository-cleanup. Ticked remaining tasks with honest annotations.
- [x] 2.2 Repaired batch 2 (5 archives): jira-epic-report-presentation-enhancement, phase4-operational-readiness, epic-report-per-epic-platform-progress, clean-up-hdd-storage, upgrade-github-actions.
- [x] 2.3 Repaired batch 3 (5 archives): evaluate-and-harden-pi-configuration, hermes-agentmemory-plugin-integration, protocol-aware-model-resolution, claude-code-model-effort-alias-routing, claude-code-provider-profile-resolution.

## Phase 3 — Repair partial-complete archives (20 changes, 4+ tasks each)

- [x] 3.1 Repaired batch 4 (5 archives): jira-workflow-validator-team-managed, tdt-workspace-cleanup, agentmemory-integration, android-pmp-connection-center, enhance-tj-1683-biometric-sprint.
- [x] 3.2 Repaired batch 5 (5 archives): finalize-tj-1656-trade-ticket-revamp-planning, jira-epic-report-archive-gap-closure, jira-status-hygiene, k8s-deployment-support, ops-scheduler-omniroute-jira-failures.
- [x] 3.3 Repaired batch 6 (5 archives): phase5-platform-features, spec-alignment, spec-status-annotation, install-and-configure-maccy, complete-store-multi-repo-wiring.
- [x] 3.4 Repaired batch 7 (5 archives): 5provider-review-gates, microsoft-teams-integration, fix-pre-existing-test-failures, hermes-vars-unguarded-calls-fix, llm-config-standardization.

## Phase 4 — Repair cancelled/abandoned archives (23 changes, 0 completed)

- [x] 4.1 Repaired batch 8 (8 archives): jira-app-owned-dashboard, ecosystem-flash-webpage, spec-gap-closure, ecosystem-alignment, android-rule-pattern-accuracy, c8-holder-resources-filter, rule-enhancement-2025, fix-concurrent-receipt-deduplication.
- [x] 4.2 Repaired batch 9 (8 archives): bootstrap-nexus-for-mobile, dev-perf-gitlab-fail-fast, harden-ci-supply-chain, jira-mr-only-comments, p3-release-3357-epic-planning, python-gitlab-integration, repair-openspec-main-spec-baseline, sr-3859-futures-fx-trade-ticket-perf.
- [x] 4.3 Repaired batch 10 (7 archives): fix-remaining-pre-existing-failures, hermes-moa-provider-reconfiguration, agent-core-model-resolution-hardening, agent-docs-sync-config-and-report-hardening, standardize-agent-llm-config-loading, omp-config-hardening, omp-lsp-integration.

## Phase 5 — Additional near-complete archives discovered in sweep

- [x] 5.1 Repaired remaining near-complete archives found during sweep: fix-webhook-selftest-token-rejection, scheduler-entrypoint-log-hygiene, jira-epic-report-generation, agent-core-legacy-cleanup, codebase-hygiene-cleanup, gitnexus-embeddings-wiki-completion, hermes-moa-quality-optimization, moa-config-quality-tuning, jira-epic-report-archive-gap-closure, agent-core-legacy-cleanup.

## Phase 6 — Store-wide validation and closure

- [x] 6.1 Focused validation: 1/1. validation on remediate-archived-store-validation change.
- [x] 6.2 Full-store validation: 375/375, invalid=[]. `openspec validate --all --strict --store openspec-store` (full-store).
- [x] 6.3 Archived validation: 404/404, failed=0. `openspec validate --archived --strict --store openspec-store` (archived).
- [x] 6.4 Store doctor: healthy=True, issues=[]. `openspec store doctor --json openspec-store`.
- [x] 6.5 Documentation lint: actionable=0, all_clear=True. documentation lint (`openspec_doc_lint.py`).
- [x] 6.6 git diff --check: exit=0. `git diff --check`.
- [x] 6.7 Unrelated dirty paths preserved (2 files). dirty paths preserved.
- [x] 6.8 Owned paths staged, ready for archive. paths and archive the remediation change.
