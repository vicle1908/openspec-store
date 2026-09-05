# Symlink Correction — prior dryrun-2026-09 findings

The 2026-09-05 dry-run classified six paths under ~/orca/workspaces/agent-core/ as orphaned checkouts with large file counts (~139MB claimed). That observation data followed symlinks: the paths are 0-byte symlinks to canonical repos, not copies.

## readlink proof
~/orca/workspaces/agent-core/code-daily-scan -> /Users/androidteam/Developer/code-daily-scan
~/orca/workspaces/agent-core/jira-daily-reports -> /Users/androidteam/Developer/jira-daily-reports
~/orca/workspaces/agent-core/jira-epic-report -> /Users/androidteam/Developer/jira-epic-report
~/orca/workspaces/agent-core/tdt-core -> /Users/androidteam/Developer/tdt-core
~/orca/workspaces/agent-core/tdt-observability -> /Users/androidteam/Developer/tdt-observability
~/orca/workspaces/agent-core/tdt-scheduler -> /Users/androidteam/Developer/tdt-scheduler

## Orca DB registration (these are live workspace registrations, PROTECTED)
1403c564-10bb-418f-aebb-979d81bddd7a::/Users/androidteam/Developer/tdt-scheduler
da9f4ea8-e5f4-4bd1-a50f-d585510d8adc::/Users/androidteam/Developer/tdt-core
7d052c95-a830-4ef2-9141-384f68421a39::/Users/androidteam/Developer/code-daily-scan
da9f4ea8-e5f4-4bd1-a50f-d585510d8adc::/Users/androidteam/Developer/tdt-core/repair-tdt-core-quality-baseline
1403c564-10bb-418f-aebb-979d81bddd7a::/Users/androidteam/Developer/tdt-scheduler/local-compose-tdt-scheduler-docs
1403c564-10bb-418f-aebb-979d81bddd7a::/Users/androidteam/Developer/tdt-scheduler/tdt-scheduler-fresh-db-control
186dd10b-b5ce-4b13-b29d-6b25f6bb0a17::/Users/androidteam/Developer/tdt-observability/tdt-observability-backends
186dd10b-b5ce-4b13-b29d-6b25f6bb0a17::/Users/androidteam/Developer/tdt-observability/tdt-observability-coordinator
186dd10b-b5ce-4b13-b29d-6b25f6bb0a17::/Users/androidteam/Developer/tdt-observability/tdt-observability-foundation
1403c564-10bb-418f-aebb-979d81bddd7a::/Users/androidteam/Developer/tdt-scheduler/tdt-scheduler-compose-repair
186dd10b-b5ce-4b13-b29d-6b25f6bb0a17::/Users/androidteam/Developer/tdt-observability/obs-compose-health-project
186dd10b-b5ce-4b13-b29d-6b25f6bb0a17::/Users/androidteam/Developer/tdt-observability/observability-coordinator-readiness
1403c564-10bb-418f-aebb-979d81bddd7a::/Users/androidteam/Developer/tdt-scheduler/scheduler-integration-clean
186dd10b-b5ce-4b13-b29d-6b25f6bb0a17::/Users/androidteam/Developer/tdt-observability/observability-gap-review
186dd10b-b5ce-4b13-b29d-6b25f6bb0a17::/Users/androidteam/Developer/tdt-observability/tdt-observability-integrated
186dd10b-b5ce-4b13-b29d-6b25f6bb0a17::/Users/androidteam/Developer/tdt-observability
186dd10b-b5ce-4b13-b29d-6b25f6bb0a17::/Users/androidteam/Developer/tdt-observability/langfuse-composite-correction

## Corrected classification
The six symlinks are PROTECTED aliases (Orca-managed registrations of canonical checkouts). The real orca-space content was only the review-hermes-cron worktree (139MB, 97M generated graphify-out).
