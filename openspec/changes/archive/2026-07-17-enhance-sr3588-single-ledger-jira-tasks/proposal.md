# Proposal: Enhance Jira Planned Tasks for SR-3588 (Single Ledger Phase 1)

## Why

The Jira Epic SR-3588 "USSO Single Ledger" currently has 13 high-level child tasks but lacks critical cross-cutting requirements identified in the URS document "P3 system enhancements - Single ledger project v1.0 20042026.pdf". Without proper task breakdown, Phase 1 implementation will hit blockers and miss key functionality. This change enhances the Jira planning to ensure complete, actionable task coverage.

## What Changes

- Create missing Jira sub-tasks under Epic SR-3588 for Phase 1 completeness
- Add platform-specific (Android/iOS) subtasks for each feature area
- Define API contracts and dependencies between tasks
- Establish acceptance criteria for each task
- Remove redundant probe task SR-3753

## Capabilities

### New Capabilities

- `cis-flag-api-contract`: Define the API contract for the CIS flag that controls dual UX switching (Legacy vs Merged)
- `m2-platform-access-control`: Implement platform-level access control to restrict M2 platform accounts
- `options-activation-flow`: Implement the user flow for activating/deactivating options trading
- `platform-subtask-breakdown`: Platform-specific (Android/iOS) task breakdown for each feature area
- `realized-pl-merged-view`: Merge realized P/L data across stocks and options positions
- `error-handling-graceful-degradation`: Implement error handling for partial data failures

### Modified Capabilities

- `jira-workflow-validator`: May need enhancement to enforce Epic SR-3588 subtask completeness

## Impact

### Affected Systems

- **Jira (SR project)**: New sub-tasks under Epic SR-3588
- **poems-mobile3-android**: Android implementation subtasks
- **poems-mobile3-ios**: iOS implementation subtasks
- **Backend services**: CIS flag API, M2 platform access control

### Dependencies

- URS document: `/Users/lekhanhvinh/Developer/tdt/docs/urs/usso/P3 system enhancements - Single ledger project v1.0 20042026.pdf`
- Jira Epic: `https://psplit.atlassian.net/browse/SR-3588`
- Figma designs: Referenced in Epic description

### New Dependencies

- None anticipated for task creation phase

## Non-Goals

- This change does NOT implement the actual Single Ledger features
- This change does NOT modify the URS document
- This change does NOT create implementation code for any feature

## Jira Gap Analysis Summary

| Missing Area | Priority | Blocker For |
|-------------|----------|-------------|
| CIS Flag API Contract | Critical | All UI tasks |
| M2 Platform Access Control | High | Phase 1 rollout |
| Options Activation Flow | High | Options functionality |
| Android Subtasks | High | Android implementation |
| iOS Subtasks | High | iOS implementation |
| Realized P/L Merged View | Medium | Positions view |
| Error Handling | Medium | Production stability |

## Current Jira Task Status

- **Epic**: SR-3588 (To Do, High priority, Assignee: PL_Duong(Kelvin))
- **Child Tasks**: 13 tasks, all in "To Do" status with 0 subtasks each
- **Gaps**: No CIS flag, no platform-specific breakdown, no cross-cutting concerns
