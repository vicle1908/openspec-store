## Context

The harness exposes request, token, cost, concurrency, output, revision, and retention settings. Today, model-authored `usage` inside the structured planning result can satisfy token and cost checks; missing token/cost values are treated as zero for comparison. Request and revision limits are cumulative, but token and cost are checked only against each stage result. Claude receives the full configured cost cap for every stage, while Codex exposes no adapter-enforced hard cost cap. `concurrency` and retention values are parsed but have no runtime consumer.

This change follows `harden-harness-provider-execution`. That change owns the combined stdout/stderr process bound and isolation profile; this change consumes that contract and owns usage provenance, cumulative budgets, and truthful configuration/reporting.

Only `ai-harness-skills` and the permanent `harness-workflow` contract are affected. State remains local SQLite and deployment remains an internal `uv tool` upgrade; no service or external dependency is added.

## Goals / Non-Goals

**Goals:**

- Make usage provenance authoritative and independent of model-authored planning content.
- Enforce requests, tokens, and cost cumulatively across a run whenever the provider exposes the required hard-control capability.
- Record usage for successful, invalid, failed, timed-out, and cancelled invocations when the provider reports it.
- Ensure automated support claims match the configured policies the adapter can enforce.
- Remove or reserve configuration fields that have no runtime behavior.
- Expose deterministic usage totals, remaining budget, provenance, and enforcement quality.

**Non-Goals:**

- Maintain provider pricing tables or estimate money from token counts.
- Add a global daemon, distributed semaphore, PostgreSQL, or multi-host execution.
- Automatically delete immutable revisions.
- Require paid live-provider calls in deterministic CI.
- Reimplement provider isolation or process output limits owned by the preceding change.

## Decisions

### 1. Separate invocation telemetry from model content

The provider boundary will return an invocation outcome containing session identity, process outcome, provider-native usage telemetry, and an optional validated stage result. Model-authored `usage` in the structured result is ignored for enforcement and either removed from the stage schema or retained only as explicitly advisory content.

Provider adapters extract usage from the native Claude response envelope and Codex event stream where available. Guided mode records usage as unknown because the harness does not own the host invocation.

Alternative considered: require the model to echo usage accurately. Rejected because the same untrusted output being constrained would control the constraint.

### 2. Persist attempts and authoritative usage transactionally

The ledger will record every started invocation and reconcile it exactly once with outcome, usage provenance, tokens, cost, and completion time. Run totals derive from reconciled provider attempts, including attempts whose structured result is rejected. Duplicate reconciliation and negative/non-finite values fail closed.

A request slot is reserved transactionally before process start so concurrent commands cannot exceed the request limit. Token and cost totals are updated from provider telemetry after the attempt, whether the planning artifact is accepted or rejected.

Alternative considered: sum mutable JSON metadata at report time. Rejected because it cannot safely reserve work or guarantee exactly-once accounting.

### 3. Pass remaining hard budget to capable providers

Before invocation, the workflow computes remaining run limits from authoritative ledger totals and the pinned run configuration. If a hard request, token, or cost limit is exhausted, it fails before spawning the provider.

Claude receives the remaining enforceable cost budget rather than the original run cap on every stage. When a provider exposes a native token/turn limit, it receives the remaining bounded value. Post-invocation reconciliation detects provider contract violations but is not described as prevention.

### 4. Make enforcement quality part of the execution decision

A configured hard policy has one of three states:

- `enforced`: the harness/provider can prevent crossing it;
- `observed`: authoritative telemetry exists but crossing can only be detected afterward;
- `unavailable`: authoritative telemetry or control is absent.

Automated execution requiring a hard cost or token policy proceeds only when that policy is `enforced`. An `observed` or `unavailable` hard policy downgrades the provider/profile and requires explicit experimental opt-in or a configuration that does not claim a hard guarantee.

Alternative considered: calculate Codex cost from token totals. Rejected because model pricing is external, mutable, and may not match the authenticated provider.

### 5. Remove inactive concurrency and retention claims from version 1 configuration

The exact stage machine is sequential and currently implements no in-stage fan-out. A local per-run lease prevents duplicate advancement but is not a global concurrency controller. Therefore configuration containing the unused `concurrency` setting is rejected before run creation with actionable migration guidance. The key remains reserved until a separately specified fan-out design exists.

No cleanup command or scheduler currently applies provider-event or completed-run retention. Configuration containing numeric provider-event or completed-run retention settings is rejected before run creation with actionable migration guidance. Documentation states that local metadata and immutable revisions remain until an explicit future export/prune operation. This change does not add silent deletion or preserve the dormant keys as non-enforcing metadata.

### 6. Preserve stable report structure with added policy detail

Status and verification reports add authoritative cumulative totals, remaining limits, provenance, and enforcement quality. Unknown values remain `null`; they are never normalized to zero. Existing run/stage outcome fields remain unchanged.

## Risks / Trade-offs

- **Codex may lose automated status under a hard cost cap** -> Report the exact missing control and permit explicit experimental use without claiming enforcement.
- **Provider event formats evolve** -> Probe and parse versioned known event shapes; unknown shapes produce unavailable telemetry, not zero.
- **Failed attempts now consume recorded budget** -> This reflects real consumption and prevents retries from bypassing a run cap.
- **Ledger schema migration is high risk** -> Use a versioned forward migration with backup guidance, integrity checks, and rollback that preserves the pre-migration database.
- **Removing dormant config keys is breaking** -> Fail with actionable migration text instead of silently ignoring them.
- **CRITICAL/HIGH blast radius** -> Preserve RED/GREEN commits and verify CLI, provider, workflow, ledger, recovery, and reporting paths together.

## Migration Plan

1. Add failing tests proving missing/model-authored usage cannot satisfy enforcement and that failed attempts count.
2. Add failing tests for cumulative request/token/cost totals, remaining Claude budget, exhausted preflight, and Codex hard-policy downgrade.
3. Add failing configuration tests for dormant concurrency/retention keys and unknown usage provenance.
4. Introduce versioned provider invocation outcomes and ledger usage records with an explicit database migration.
5. Reconcile usage on every provider exit path and calculate remaining run policy before invocation.
6. Update doctor, status, report, schema, and documentation contracts.
7. Reject dormant configuration fields with migration guidance and update examples.
8. Run frozen sync, lint, format, strict typing, complete tests/coverage, dependency audit, OpenSpec/schema/skill validation, and GitNexus scope checks.

Deployment is a manual internal package upgrade after the provider-hardening change. Before migrating a non-empty ledger, preserve a filesystem backup. Rollback restores the backup and earlier package; it does not attempt a lossy down-migration of authoritative usage records.

## Open Questions

- The implementation spike must confirm which installed Codex event supplies authoritative token usage. Absence of such an event yields `unavailable`, not an inferred value.
