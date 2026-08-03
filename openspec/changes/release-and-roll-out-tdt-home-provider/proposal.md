# Release and Roll Out TDT_HOME Provider

## Why

Source conformance and the synthetic migration engine establish that consumers respect the `tdt-core` provider boundary and that migration behavior is recoverable, but they do not prove that the provider can be built, distributed, installed, or reversed as a production artifact. A checkout-backed test can also pass while masking missing package resources, undeclared dependencies, stale local modules, or an unusable registry artifact.

This change closes that release gap with a provider-first deployment sequence. It qualifies an immutable `tdt-core` wheel and locked dependency closure outside the source checkout, publishes the exact qualified artifact to the internal registry, and promotes it through explicitly owned consumer stages. Each stage must preserve the prior artifact and demonstrate reverse rollback before broader rollout. The resulting evidence establishes provider distribution and deployment readiness without treating it as authorization to migrate consumer source or operate on the real `~/.tdt` tree.

## What Changes

- Build a clean, reproducible wheelhouse containing the candidate `tdt-core` wheel and its complete locked dependency closure, with source revision, package version, build-tool identity, filenames, and cryptographic hashes recorded in a value-free manifest.
- Install and verify the candidate in a fresh, disposable environment with the source checkout unavailable and `PYTHONPATH` unset. Verification must prove imports resolve from the installed distribution and must cover version equality, package metadata and resources, base CLI behavior, provider diagnostics, contracts, lint/type/test gates, and redacted failure output.
- Publish only the artifact that passed checkout-free qualification to the approved internal package registry under an immutable version, then verify that a second clean environment can resolve and install the same hashes from the registry rather than from a local wheel or checkout.
- Define release gates that distinguish build qualification, registry publication, provider staging, per-consumer deployment, and live-root readiness. Passing one scope must not implicitly approve another.
- Roll out the provider in ordered stages: provider-only staging first, followed by one explicitly approved consumer deployment at a time. Each consumer stage records its target, owner, runtime principal, configuration profile, selected artifact, compatibility evidence, health checks, observation window, and go/no-go decision before the next stage begins.
- Retain the exact pre-change provider artifact and dependency closure for every target and rehearse reverse rollback by restoring that artifact after a candidate installation, then reapplying the candidate only after both directions pass health and provenance checks.
- Stop publication or promotion when provenance, ownership, compatibility, health, approval, evidence, or rollback gates are incomplete or contradictory; retain redacted evidence for diagnosis without exposing credentials or configuration values.
- Produce a final release record that identifies the qualified and published artifact, registry digest, rollout stages and approvals, observed health, rollback artifact and rehearsal result, unresolved blocks, and readiness scope.

## Capabilities

### New Capabilities

- `tdt-home-provider-rollout`: reproducible provider wheelhouse qualification, checkout-free installed-distribution verification, immutable internal-registry publication, provider-first staged deployment, per-consumer promotion gates, and reversible artifact rollback evidence.

### Modified Capabilities

- None. The provider API, source-conformance rules, synthetic migration behavior, consumer source contracts, and live-root cutover contract remain independently specified and verified.

## Ownership Boundaries

- `tdt-core` maintainers own the provider source revision, distribution metadata, lock state, wheel build, packaged resources, provider-only diagnostics, and the evidence that the installed artifact matches the qualified source and version.
- Release engineering owns the isolated build and verification environments, wheelhouse manifest, internal-registry publication, artifact immutability, registry installation proof, release record, and retention of candidate and rollback artifacts.
- The internal registry owner controls credentials, repository policy, availability, retention, and any supported quarantine or yank operation. Credentials and tokens must never be captured in release evidence.
- Each consumer deployment owner owns the inventory and approval for that target, its deployment window, runtime principal, configuration profile, compatibility and health evidence, observation period, and the decision to promote or reverse that individual stage.
- Rollout operators may change which already-built provider artifact is installed in an approved target; they may not rewrite consumer source to adopt the provider, invent compatibility waivers, or infer approval from another consumer's success.
- `openspec-store` owns the normative proposal, capability delta, design, task tracking, and evidence requirements. It does not build or publish packages, hold registry credentials, deploy consumers, restart services, or authorize rollout.
- Operators retain exclusive ownership of the real `~/.tdt` tree. No build, install, smoke test, rollout, or rollback action in this change may inspect, create, repair, migrate, replace, or delete content in that tree.

## Explicit Non-Goals

- Migrating, refactoring, or otherwise editing consumer source code to use the provider, including resolving source-conformance findings or changing hard-coded path construction.
- Performing a live TDT_HOME cutover or reading, validating, backing up, repairing, moving, or deleting anything under the real `~/.tdt` or another operator-owned effective `TDT_HOME`.
- Applying a real filesystem migration plan, migrating consumer data, changing database schemas or contents, rotating credentials, rewriting schedules, or repairing runtime state.
- Treating provider qualification, registry publication, or one consumer's successful stage as proof that all consumers or the live root are ready.
- Automatically promoting across consumers, bypassing target-owner approval, or continuing after a failed gate or expired observation window.
- Publishing mutable snapshot versions, rebuilding an artifact between qualification and publication, or substituting an unqualified dependency closure during rollout.
- Deleting the candidate from registry history as a rollback mechanism. A defective release may be blocked or yanked according to registry policy, but the release record and artifact hashes remain auditable.
- Authorizing the separately scoped `cut-over-live-tdt-home` change.

## Dependencies

- `govern-tdt-home-source-conformance` must be complete and green for the participating repository set, with current manifests, bounded exceptions, declared deployment and launch surfaces, and accountable owners. This dependency supplies inventory and governance evidence; this change does not remediate its source findings.
- `build-tdt-home-synthetic-migration-engine` must be complete and green, including interruption recovery, idempotence, tamper rejection, and synthetic rollback rehearsal. Its success demonstrates migration-engine safety but does not authorize use against real operator data in this rollout.
- The provider implementation and packaging baseline must pass the repository's focused and full tests, lint, formatting, strict type checking, packaged-contract checks, security/redaction checks, and version-consistency checks before a release candidate is built.
- An approved internal registry namespace, authenticated publisher and reader principals, immutable-version policy, retention policy, and a disposable registry-install verification environment must exist before publication.
- Every rollout target must have an identified owner, runtime principal, configuration owner, health checks, compatibility evidence, maintenance or observation window, and retained exact pre-change artifact plus dependency closure before it is eligible for promotion.
- Consumer source migration and `cut-over-live-tdt-home` are not dependencies to execute provider-only qualification and staging. They remain separate gates and cannot be marked complete by this change.

## Impact

- Primary implementation and release surface: the `tdt-core` build, packaging, lock, CLI, provider diagnostics, and release automation.
- Operational surfaces: the internal package registry; isolated build and install environments; provider staging; and approved consumer runtime environments where only the selected provider artifact is changed.
- CI and release evidence gain wheelhouse reproducibility, installed-origin and version assertions, registry round-trip verification, secret-safe reports, per-stage approvals, and reverse rollback checks.
- Consumer deployments may temporarily move between the previous and candidate provider versions during an approved rehearsal. Their source repositories and operator-owned TDT_HOME data remain unchanged.
- Rollout duration increases because promotion is serialized by consumer and includes observation and reverse rollback gates. This is intentional containment: a failure affects only the current stage and blocks later stages.
- Principal risks are an artifact that differs from the qualified build, undeclared dependency leakage, registry resolution drift, packaged-resource omissions, target-specific incompatibility, and an untested downgrade path. Immutable hashes, checkout-free installs, per-target health gates, and retained rollback wheelhouses mitigate those risks.
- No live database schema change, credential rotation, consumer source migration, or real `~/.tdt` filesystem mutation is introduced.

## Rollback

Before each staged deployment, the operator must capture and retain the exact installed provider version, wheel hashes, locked dependency closure, package source, and redacted baseline health evidence. Reverse rollback is a release gate, not an incident-only procedure: in an isolated or staging target, install the qualified candidate, verify its provenance and health, restore the exact pre-change artifact and closure, verify the prior provenance and health, and only then reinstall the candidate if promotion is approved.

If qualification or registry round-trip verification fails, do not publish or promote the candidate. If a consumer stage fails, withdraws approval, or breaches its observation gate, stop all later promotions and restore only that target to its recorded pre-change artifact and dependency closure. After restoration, verify imports resolve from the expected installed distribution, confirm the previous version and hashes, rerun the target's redacted health checks, and record the result. Targets that have not failed remain unchanged unless their owners separately approve a coordinated rollback.

A defective published version may be quarantined or yanked according to internal-registry policy while its immutable files, hashes, and release evidence are retained for audit. Rollback does not rewrite consumer source, reverse data migrations, alter credentials, modify databases or schedules, or touch the real `~/.tdt`; any recovery requiring those actions belongs to the separately approved consumer-migration or live-cutover change.
