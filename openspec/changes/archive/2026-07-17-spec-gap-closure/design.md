## Context

The microservices platform has 10 archived openspec changes with 69 spec files, 50 main specs in `openspec/specs/`, and ~400 Go source files across 9 modules. A comprehensive audit on 2026-07-17 revealed that while the codebase is substantial (~65-70% complete), the specs do not accurately reflect implementation status. Many SHALL/MUST requirements are either fully implemented, partially implemented, or deferred, but the specs don't indicate this.

The audit was performed by 5 parallel agents examining:
1. Order Service MVP (9 specs) — ~85% implemented
2. Phase 2 Platform Services (21 specs) — ~65-70% implemented
3. DDD Cleanup + Workflow Extraction (13 specs) — ~50-75% implemented
4. Remaining Changes (6 changes, 20+ specs) — 30-100% implemented
5. Deployment Infrastructure — ~80% implemented

## Goals / Non-Goals

**Goals:**
- Update all 50 main specs with accurate IMPLEMENTED/PARTIAL/DEFERRED status annotations
- Create delta specs for 3 new capabilities (test-coverage, architecture-tests, operational-readiness)
- Create delta specs for 5 modified capabilities (kafka-harness, temporal-versioning, hexagonal-enforcement, order-temporal-workflow, order-rest-api)
- Generate prioritized tasks for the highest-impact gaps
- Establish a baseline for ongoing spec-code alignment

**Non-Goals:**
- No code changes in this change (spec-only)
- No new service implementations
- No dependency version updates
- No API contract changes
- No infrastructure provisioning changes
- Not addressing every minor gap — focus on critical and high-severity items only

## Decisions

### Decision 1: Spec-Only Change (No Code)

**Choice**: This change modifies only spec files, not code.

**Rationale**: The audit revealed gaps across 50 specs and 10 changes. Attempting to fix code and specs simultaneously would be unfocused and risk introducing bugs. Separating spec alignment from code implementation allows:
- Clear audit trail of what was specified vs what exists
- Independent verification of spec accuracy
- Focused code changes in subsequent changes

**Alternatives considered**:
- Combined spec+code change: Rejected because it conflates two concerns and makes rollback harder
- Skip specs, just fix code: Rejected because specs are the source of truth for requirements

### Decision 2: Delta Specs for Modified Capabilities

**Choice**: Use MODIFIED Requirements in delta specs rather than rewriting main specs.

**Rationale**: The openspec sync-specs workflow handles merging delta specs into main specs at archive time. This preserves the change history and allows reviewing what changed before it's applied.

**Alternatives considered**:
- Direct main spec edits: Rejected because it bypasses the openspec workflow and loses change history
- New specs for each modification: Rejected because it fragments the spec surface

### Decision 3: Three New Capabilities

**Choice**: Create test-coverage-gap-closure, architecture-test-expansion, and operational-readiness as new capabilities.

**Rationale**: These represent the three largest gap categories identified by the audit:
1. Test coverage (30-40% vs 90/90/80 targets)
2. Architecture test enforcement (1 of 12+ categories)
3. Operational readiness (broker UI, rollback, runbooks, agent configs)

**Alternatives considered**:
- Single "gaps" capability: Rejected because it's too coarse for task assignment
- Per-service capabilities: Rejected because gaps are cross-cutting concerns

### Decision 4: Prioritized Task Generation

**Choice**: Generate tasks ordered by dependency and impact, not alphabetically.

**Rationale**: The audit identified clear priority tiers:
- **Critical**: Test coverage for customer/notification/payment/inventory/shipping services
- **High**: Architecture test expansion, K8s network policy egress rules
- **Medium**: Broker UI, rollback rehearsal, agent config wiring
- **Low**: ArgoCD notifications, image updater, fuzz testing expansion

**Alternatives considered**:
- Flat task list: Rejected because it doesn't communicate priority
- Per-change task lists: Rejected because gaps span multiple archived changes

## Risks / Trade-offs

### Risk: Spec Drift Recurs
**→ Mitigation**: Add a `make spec-audit` target that runs periodically and compares spec status annotations against code evidence. This change establishes the baseline; future changes maintain it.

### Risk: Delta Spec Merge Conflicts
**→ Mitigation**: Delta specs use MODIFIED Requirements with full requirement blocks. The sync-specs workflow handles intelligent merging. If conflicts arise, the agent-driven sync can resolve them.

### Risk: Status Annotations Become Stale
**→ Mitigation**: Status annotations are tied to specific code evidence (file paths, test counts). The verification/traceability.yaml files in each service provide a machine-readable mapping.

### Risk: New Capabilities Add Spec Surface Without Implementation
**→ Mitigation**: The 3 new capabilities have clear, measurable acceptance criteria (test counts, test categories, operational items). They can be verified objectively.

### Trade-off: Completeness vs Actionability
The audit found many minor gaps. This change focuses on the top 20% of gaps that provide 80% of the value. Minor gaps (e.g., individual test file additions) are deferred to per-service changes.

## Migration Plan

1. Create delta specs for new and modified capabilities
2. Generate tasks ordered by priority
3. Sync specs to main specs (via openspec-sync-specs at archive time)
4. Subsequent changes implement the tasks
5. Each task includes verification criteria matching the spec scenarios

## Open Questions

1. Should the `make spec-audit` tool be a Python script or Go tool? (Depends on team preference)
2. What's the target date for closing critical gaps? (Depends on team capacity)
3. Should operational-readiness include Helm chart migration from Kustomize? (Scope question)
