## Context

OpenSpec 1.6 strict validation records 66 invalid main specs out of 212: 64
missing `## Purpose`, one (`ai-review-durable-scheduler`) missing
`## Requirements`, and one (`consumer-config-composition`) with two requirements
that produce four scenario-shape findings. All active changes pass, so the debt
is isolated to legacy main-spec structure.

The files span many TDT domains and are normative documentation. A bulk rewrite
would be fast but unsafe: generic Purpose text could misstate ownership or
behavior, and scenario reformatting could accidentally remove or alter
requirements. The work therefore runs manually in a dedicated change after the
OpenSpec 1.7 runtime migration has captured its comparison baseline.

Only `tdt-meta/openspec/specs/*/spec.md` and this change's planning artifacts are
in scope. There is no application deployment, package installation, service
restart, external API call, or database change.

## Goals / Non-Goals

**Goals:**

- Make all 66 recorded legacy main specs pass strict validation.
- Preserve every existing normative requirement and scenario meaning.
- Author capability-specific Purpose text from evidence, never placeholders.
- Make each batch independently reviewable, reversible, and measurable.
- End with a machine-readable all-main-spec validation baseline.

**Non-Goals:**

- Changing product behavior or adding normative requirements.
- Reorganizing capability directories or the planning-root topology.
- Repairing active-change artifacts, generated agent workflows, or application
  documentation outside the affected main specs.
- Using a formatter or bulk replacement that rewrites unrelated content.
- Archiving, committing, or pushing without separate authorization.

## Decisions

### Decision 1: Freeze semantic inventories before editing

For every affected file, record its path, hash, requirement headers, scenario
headers, validation findings, and evidence source for Purpose text. After an edit,
the requirement-name inventory must be identical. Scenario inventories must also
be identical except for the two explicitly malformed
`consumer-config-composition` scenario structures, whose text and ordering must
be preserved while their headers are normalized.

**Alternative rejected:** trust a green validator alone. Structural validation
cannot prove that an existing requirement or scenario was not silently lost.

### Decision 2: Use six bounded capability batches

The 66 files are partitioned exactly once:

1. **Agent platform (17):** `agent-config`,
   `agent-core-budget-enforcement`, `agent-core-cli-extraction`,
   `agent-core-dead-code-cleanup`, `agent-core-memory-enhancement`,
   `agent-core-memory-lifecycle`, `agent-core-resilience-utility`,
   `agent-core-tool-resilience`, `agent-docker-local-dev`,
   `agent-docs-agent-config`, `agent-docs-harness`,
   `agent-docs-orchestration-enhanced`, `agent-docs-research`,
   `agent-docs-sync-code-intelligence`, `agent-docs-sync-project-scaffold`,
   `agent-durable-execution`, `agent-yaml-config`.
2. **Documentation and dependency flows (10):** `blocking-dependency-tracking`,
   `dependency-visualization`, `docs-sync-memory`, `docs-sync-memory-wiring`,
   `docs-sync-observability`, `docs-sync-parallel-multi-repo`,
   `docs-sync-resilience`, `docs-sync-validation-dedup`, `integration-guide`,
   `traceability`.
3. **Composition, gateway, and SDK (12):** `bifrost-gateway`, `configuration`,
   `consumer-composition-boundary`, `consumer-config-composition`,
   `consumer-pattern`, `flavor-composition-sdk`, `mcp-integration`,
   `orchestration-command-api`, `resilient-gateway-sdk`,
   `resilient-tool-adoption`, `sdk-public-api`, `typed-orchestration-state`.
4. **Harness, memory, evaluation, and observability (13):** `evaluation`,
   `harness-integration`, `harness-media`, `harness-runtime-authoring`, `hooks`,
   `langfuse-otel-integration`, `memory-framework`, `memory-system`,
   `memory-vector-integration`, `mlflow-otel-integration`, `observability`,
   `otel-auto-instrumentation`, `structured-eval-metrics`.
5. **Reporting and operational documentation (9):**
   `enhanced-report-sections`, `epic-data-collection`, `glossary`,
   `jira-daily-reports`, `report-generation`, `risk-analysis`, `runbook`,
   `spreadsheet-export-enhancement`, `status-aggregation`.
6. **Workflow and validation contracts (5):** `ai-review-durable-scheduler`,
   `dynamic-workflow`, `pattern-decisions`, `validation-consistency`,
   `workflow-dag`.

Each batch gets its own before/after inventory, per-file strict validation, and
full-root comparison before the next batch starts.

**Alternative rejected:** one 66-file pass. It produces an unreviewable diff and
makes regression isolation expensive.

### Decision 3: Author Purpose from current capability evidence

Purpose text is a concise description of what the existing requirements already
govern and why the capability exists. Evidence order is: the file's current
requirements, its archived OpenSpec history, then canonical repository docs.
Purpose text must not introduce SHALL/MUST behavior, implementation promises,
volatile repository lists, private endpoints, or placeholders.

**Alternative rejected:** generate a common template. Repeated generic text would
satisfy syntax while degrading the planning contract.

### Decision 4: Treat the two non-Purpose failures as surgical repairs

`ai-review-durable-scheduler` receives the missing Requirements container around
its existing requirement blocks without rewriting them.
`consumer-config-composition` keeps its current requirement/scenario text and
ordering; only malformed scenario structure is converted to valid level-4
scenario headers with WHEN/THEN bullets.

**Alternative rejected:** replace either file from another branch or archived
copy. That could import unrelated behavioral drift.

### Decision 5: Ratchet validation and preserve rollback boundaries

After each batch, the invalid-id set must be the previous set minus only the
batch's repaired ids; no new id or error class is accepted. A batch is not marked
complete until semantic inventories match and its files validate independently.
If a check fails, stop and revert only that batch's edits through a reviewed
inverse patch; never use destructive Git reset in the dirty worktree.

### Decision 6: Keep topology and runtime changes out

All files remain at their existing `openspec/specs/<capability>/spec.md` paths.
The change does not register stores, set `defaultStore`, create worksets, move
specs into nested folders, alter symlinks, or update the OpenSpec runtime.

## Risks / Trade-offs

- **Purpose text overstates behavior** → require a recorded evidence source and
  forbid new normative language.
- **Large documentation diff hides deletion** → compare requirement/scenario
  inventories and hashes per batch.
- **Concurrent spec edits overlap a batch** → refresh Git status before every
  batch and stop on any affected dirty path not owned by this change.
- **A green count masks a different failure set** → compare exact ids and error
  classes, not counts alone.
- **The runtime migration changes validator output** → begin implementation only
  after the exact OpenSpec version is recorded and keep the machine-readable
  before/after reports.

## Migration Plan

1. Confirm the OpenSpec runtime migration baseline and refresh the 66-id set.
2. Capture per-file semantic inventories, hashes, and Purpose evidence sources.
3. Apply and validate the six batches in order, stopping on overlap or drift.
4. Run per-file, all-spec, all-change, and full-root strict validation.
5. Review the final diff for requirement/scenario preservation and topology
   stability.
6. Stop before archive, commit, or push.

Rollback is batch-local: preserve the before inventory and patch, reverse only
the failing batch, and rerun its prior strict-validation baseline. No service
rollback is needed because the change modifies documentation only.

## Open Questions

None. Any file whose Purpose cannot be supported by existing requirements,
history, or canonical docs is removed from its batch and escalated rather than
filled speculatively.
