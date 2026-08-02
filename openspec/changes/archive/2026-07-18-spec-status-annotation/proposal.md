# Proposal: Spec Status Annotation

## Problem
The OpenSpec audit found that 50 of 56 specs lack IMPLEMENTED/PARTIAL/DEFERRED status annotations. Without status annotations, it is impossible to determine at a glance which specs have been implemented in code, which are partially implemented, and which are deferred for future work. This creates confusion for developers, makes audit trails incomplete, and prevents automated tooling from tracking implementation progress.

## Solution
Add `> **Status**: IMPLEMENTED/PARTIAL/DEFERRED` annotations to every requirement in all 50 specs that currently lack them. Each annotation will include brief evidence supporting the status determination.

## Scope
- All 50 specs identified in the audit that lack status annotations
- Status annotations added to each requirement section within each spec
- No changes to spec content beyond adding status annotations

## Status Definitions
- **IMPLEMENTED**: Code exists and matches spec requirement
- **PARTIAL**: Some code exists but doesn't fully meet spec
- **DEFERRED**: No code exists yet, planned for future

## Benefits
1. **Visibility**: At-a-glance view of implementation status across all specs
2. **Audit Trail**: Clear documentation of what has been implemented vs planned
3. **Tooling**: Enables automated tracking of implementation progress
4. **Developer Onboarding**: New developers can quickly understand what exists

## Risks
- **Maintenance**: Status annotations may become stale if code changes without spec updates
- **Subjectivity**: Status determination requires judgment calls about "partial" vs "implemented"

## Mitigations
- Include brief evidence in each annotation to justify the status
- Recommend periodic re-audit to keep annotations current
