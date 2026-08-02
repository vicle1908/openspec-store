## Why

The TJ-1683 epic ("Allow biometric verification in trade submission") has 207 tasks with only 21% completion. Current sprint shows critical bottlenecks: 73% tasks unassigned, 24 in Draft status, and development velocity is too slow to meet sprint SIT target. Without intervention, the epic will not reach SIT by sprint end.

## What Changes

1. **Sprint Task Triage** — Assign all 152 unassigned tasks to team members
2. **Draft-to-Ready Pipeline** — Finalize 24 Draft tasks into ready-for-development status
3. **Requirements Unblock** — Resolve blockers on TJ-1916 and TJ-1613
4. **Parallel Workstreams** — Enable concurrent development across iOS/Android/Backend
5. **Daily Standup Automation** — Track progress with automated reporting
6. **Sprint Burndown** — Monitor completion rate against SIT target

## Capabilities

### New Capabilities

- `jira-epic-sprint-accelerator`: Automation tooling to accelerate epic completion via bulk task assignment, status transitions, and sprint metrics tracking
- `jira-task-ownership-tracker`: Track task ownership distribution and identify workload imbalances

### Modified Capabilities

- `jira-daily-reports`: Extend with epic-specific burndown metrics for TJ-1683
- `jira-sprint-spreadsheet-ssot`: Add TJ-1683 epic sheet with real-time progress

## Impact

- **Jira Project TJ**: 207 tasks affected across 3 platforms (iOS, Android, Backend)
- **Team Capacity**: 5 developers + potential capacity reallocation
- **Dependencies**: Requires access to TJ project with bulk edit permissions
- **Tools**: Uses `jira-epic-report` CLI and `kbs` for tracking
