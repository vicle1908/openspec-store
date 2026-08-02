## Context

The TJ-1683 epic ("Allow biometric verification in trade submission") has 207 tasks across iOS, Android, and Backend platforms. Current sprint shows:
- 21% completion (2 tasks done)
- 9 tasks in progress
- 152 tasks (73%) unassigned
- 24 tasks in Draft status (not ready)
- Requirements blockers on TJ-1916 and TJ-1613

The sprint goal is to complete development coding and move all in-progress work to SIT testing.

## Goals / Non-Goals

**Goals:**
- Assign all unassigned tasks to team members based on skills/platform
- Finalize Draft tasks to ready-for-development status
- Accelerate parallel development across iOS/Android/Backend
- Track sprint progress with daily burndown metrics
- Move all development tasks to SIT by sprint end

**Non-Goals:**
- Modifying the biometric verification feature requirements (those are already defined)
- Completing SIT testing (only development coding)
- Changing code architecture or refactoring

## Decisions

### 1. Bulk Task Assignment Strategy
Use Jira bulk edit via `kbs` CLI or PatchedJira to assign tasks based on:
- iOS tasks → iOS team (To Vu Duong)
- Android tasks → Android team (sangtran)
- Backend tasks → Backend team (Kelvin/PL_Duong)
- Cross-platform → assigned based on component label

**Alternative Considered:** Manual assignment via Jira UI
- **Decision:** Automated via CLI - faster, less error-prone, auditable

### 2. Draft Task Finalization
Priority order based on dependencies:
1. High-priority Draft tasks that block critical path
2. Platform-specific Draft tasks (iOS/Android/Backend)
3. Low-priority Draft tasks

**Alternative Considered:** Process all Drafts in parallel
- **Decision:** Prioritized sequence - ensures critical path is unblocked first

### 3. Progress Tracking
Daily report via `epic-report insights` + Google Sheets integration
- Morning: Generate current epic status
- Evening: Update sprint burndown sheet

**Alternative Considered:** Manual Jira board review
- **Decision:** Automated - ensures consistency and reduces manual effort

### 4. Parallel Workstreams
Enable concurrent work by platform:
- iOS workstream: 26 stories + subtasks
- Android workstream: 26 stories + subtasks  
- Backend workstream: Core API + subtasks

**Alternative Considered:** Single-threaded assignment
- **Decision:** Parallel - required to meet SIT target in sprint timeframe

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Requirements blocker (TJ-1613) | Delays dependent tasks | Escalate to PO immediately |
| Bulk assignment conflicts | Multiple assignees on same task | Use component/platform labels |
| Sprint capacity exceeded | Task overflow | Weekly reprioritization |
| Test environment unavailable | SIT delayed | Coordinate with DevOps early |

## Open Questions

1. **Sprint end date?** Need exact date for burndown calculation
2. **Team capacity?** How many tasks can each developer complete?
3. **Draft task prioritization?** Confirm priority order with PM
4. **TJ-1613 dependencies?** What tasks are blocked by this requirement?

## Repository Changes

- `jira-epic-report/`: Add TJ-1683 sprint accelerator scripts
- `tdt-core/`: Potentially extend `kbs` CLI for bulk operations
- No code changes to iOS/Android repos (feature implementation is separate)
