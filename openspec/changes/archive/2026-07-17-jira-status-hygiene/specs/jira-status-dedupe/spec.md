# jira-status-dedupe Specification

## Purpose

Define the instance-wide deduplication operation: the algorithmic process that collapses duplicate status records down to canonical targets across both team-managed and company-managed projects.

## ADDED Requirements

### Requirement: Canonical target selection rule

The canonical target for any `duplicate_cluster_id` SHALL be the record with `max(used_by_projects), min(jira_id)` — highest `used_by_projects` wins, ties broken by lowest Jira ID.

This rule SHALL be deterministic and reproducible. No human decision is required for standard cases. The selection is pre-computed and stored in `status_catalog.is_canonical_target` during `render-sheet`; the dedupe command SHALL honor that pre-computed flag.

#### Scenario: Deterministic target selection
- **WHEN** a cluster has records A (used_by=7), B (used_by=7), C (used_by=3)
- **THEN** A and B are tied at `max(used_by_projects)=7`
- **AND** A wins if `min(jira_id)` is lower than B's
- **AND** exactly one record is marked `is_canonical_target=true`

### Requirement: Cluster scope and project fan-out

A duplicate cluster contains multiple `Status` records sharing the same `(name_lc, category)` pair. Because team-managed status records are project-private, the same `name_lc` + `category` may appear as N distinct `jira_id` values across N projects. The dedupe operation SHALL treat each `(jira_id, project)` pair as the unit of work, not each `jira_id` in isolation.

Concretely: for each loser `jira_id` in a cluster, the operation SHALL

1. Call `find_issues_in_status_grouped_by_project(loser_id)` to discover which projects currently hold issues in that loser.
2. For each `(project, loser_id)` pair discovered, call `bulk_transition(project_key=project, from_id=loser_id, to_id=canonical_id)`.
3. After all project-scoped transitions succeed, call `delete_status(project_key="", status_id=loser_id)` once per loser.

#### Scenario: Same name in 102 projects, 102 distinct Jira IDs
- **WHEN** the "To Do" cluster has 102 records (one per project), each `jira_id` is project-private
- **AND** the canonical target is `id=10000` (highest `used_by_projects`)
- **THEN** for each of the other 101 loser IDs, the command SHALL find which projects hold issues in that loser
- **AND** transition those projects' issues to `id=10000`
- **AND** delete each loser ID via `DELETE /rest/api/3/statuses/{loser_id}` after its transitions complete
- **AND** the catalog drops from 750 records to ~228 (47 cluster survivors + ~181 singletons)

#### Scenario: Single loser spanning many projects
- **WHEN** the "Done" cluster has 100 records and `id=10014` (canonical) is referenced by 5 projects while `id=12833` is referenced by 7 other projects
- **THEN** the command SHALL transition issues in those 7 projects from `id=12833` to `id=10014`
- **AND** the 7 projects SHALL retain their reference to `id=10014` (or gain one if they didn't have it before)

### Requirement: Per-project sign-off gate

Before transitioning any project, the dedupe command SHALL verify that the project's row in `project_manifest` has both `instance_admin_signoff_at` and `project_admin_signoff_at` set to non-empty datetimes. If either sign-off is missing, the command SHALL skip that project and log `"skip <project_key> (no dual signoff)"`.

This is a per-project gate, not a per-cluster gate. A cluster whose affected projects are all signed off can proceed even if other clusters have unsigned projects.

#### Scenario: Mixed sign-off across a cluster
- **WHEN** a cluster's 7 affected projects are: PDS (signed off), PWM (signed off), RMD (instance_admin only), and 4 others (signed off)
- **THEN** the command SHALL transition PDS, PWM, and the 4 signed-off projects
- **AND** it SHALL skip RMD and emit `"skip RMD (no dual signoff)"`

### Requirement: Global gate before destructive action

Before any Jira write API is called, the dedupe command SHALL verify that at least one row in `project_manifest` has `instance_admin_signoff` non-empty. This is a coarse instance-wide sanity check that the operator has been through the sign-off flow at least once.

#### Scenario: No sign-off at all
- **WHEN** `dedupe --global-confirm` is called and `project_manifest` has no instance_admin sign-offs
- **THEN** it SHALL refuse with: `"No instance_admin signoff on file in project_manifest. Run: jira-skill status signoff --project <KEY> --role instance_admin"`
- **AND** exit with code 1

### Requirement: Dedupe idempotency

The dedupe operation SHALL be idempotent. Running it twice on the same catalog SHALL produce the same result as running it once.

#### Scenario: Re-running dedupe on already-deduped catalog
- **WHEN** `jira-skill status dedupe --global-confirm` is run on a catalog where `cluster_size` is already 1 for all clusters
- **THEN** it SHALL detect this from the Sheet and exit with: `"Catalog already deduped — all clusters have size <= 1."`
- **AND** it SHALL NOT call any Jira API

### Requirement: Global dedupe --dry-run output

`jira-skill status dedupe --dry-run` SHALL output a tabular summary showing for each cluster: `cluster_id`, `name`, `cluster_size`, `canonical_jira_id`, and a comma-separated list of `loser_jira_id`s. The `--dry-run` mode SHALL NOT call any Jira write API; it MAY read the catalog from the Sheet only.

#### Scenario: Dry-run preview
- **WHEN** `jira-skill status dedupe --dry-run` is called
- **THEN** it SHALL print one row per cluster with size > 1
- **AND** it SHALL NOT call any Jira write API

### Requirement: Dedupe log writes

For each cluster processed, the command SHALL append one row to `dedupe_log` containing: `dedupe_id`, `duplicate_cluster_id`, `canonical_name`, `canonical_category`, `records_merged` (count of losers), `target_jira_id`, `total_issues_transitioned` (sum across all per-project transitions), `operator`.

#### Scenario: One dedupe_log row per cluster
- **WHEN** a cluster with 4 losers collapses into the canonical target after transitioning 87 issues across 6 projects
- **THEN** exactly one row SHALL be appended to `dedupe_log` with `records_merged=4`, `total_issues_transitioned=87`, `target_jira_id=<canonical>`

### Requirement: Singleton mis-label fixes (deferred)

The singleton `bucket=mislabeled` workflow is specified under `jira-status-classify-singletons`. This dedupe spec SHALL NOT directly fix category metadata on singleton records; that is the singleton-classification capability's responsibility.

#### Scenario: Singleton mis-label records are routed to jira-status-classify-singletons
- **WHEN** the dedupe pipeline encounters a cluster with `bucket=mislabeled`
- **THEN** the dedupe command SHALL skip category-metadata fixes and SHALL emit a routing log entry pointing to `jira-status-classify-singletons`
- **AND** the cluster SHALL remain in the dedupe registry under `status=misdirected-pending-classification` until the singleton-classification capability resolves it

### Requirement: Error and partial-success handling

If `bulk_transition` raises `PartialTransitionError`, the dedupe command SHALL log a warning containing the failed issue keys and continue with the next `(project, loser)` pair. Other exceptions SHALL be logged at error level and the (project, loser) pair SHALL be skipped.

The command SHALL NOT abort on a partial failure of one (project, loser) pair; it SHALL continue processing the remaining pairs and the remaining clusters.

#### Scenario: PartialTransitionError on one (project, loser) pair does not abort the run
- **WHEN** `bulk_transition` raises `PartialTransitionError` for one (project, loser) pair while 3 other pairs remain
- **THEN** the dedupe command SHALL log a warning naming the failed issue keys and SHALL continue processing the remaining 3 pairs
- **AND** the final exit code SHALL reflect the partial failure (non-zero) without aborting mid-run

#### Scenario: Unexpected exception skips one (project, loser) pair and continues
- **WHEN** an unexpected exception (non-PartialTransitionError) is raised for one (project, loser) pair
- **THEN** the dedupe command SHALL log the exception at error level and SHALL skip that pair
- **AND** processing SHALL continue with the remaining pairs and remaining clusters
