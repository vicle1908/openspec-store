# Govern TDT_HOME Source Conformance

## Why

The archived `govern-tdt-home-config-and-environment` change established `tdt-core` as the provider boundary for resolving `TDT_HOME`, but it did not establish how consumer repositories prove that they respect that boundary. Participating repositories currently lack a uniform, machine-readable declaration of their provider usage, deployment ownership, and temporary exceptions. Without that evidence, hard-coded `~/.tdt` construction can bypass the provider contract, ownership gaps can block safe rollout, and legacy allowances can become undocumented permanent behavior.

This change adds a read-only governance layer that identifies those conditions before per-consumer adoption or live migration begins. It makes conformance deterministic and reviewable without changing consumer source behavior, dependency metadata, deployed processes, or the operator-owned filesystem.

## What Changes

- Require every participating consumer repository to maintain a versioned `.tdt/governance-manifest.json` at its repository root.
- Define and validate the manifest contract for repository identity, provider-boundary status, deployment and launch-surface owners, approved source sites, repository-owned exceptions, and conformance evidence.
- Add a deterministic AST-based source audit that inspects source without importing or executing consumer code and rejects hard-coded construction of `~/.tdt` outside approved provider or exception sites.
- Recognize semantically equivalent construction patterns, including direct literals and common path-building or home-expansion forms, rather than relying on a text-only search.
- Require exceptions to be stored and reviewed in the affected repository, scoped to a specific source site, and accompanied by rationale and accountable ownership; undeclared, malformed, stale, or unmatched exceptions fail conformance.
- Track an accountable deployment owner for each declared deployment or launch surface so subsequent adoption and rollout work has an explicit assignee.
- Produce stable, redacted audit results suitable for local review and CI aggregation across the participating repository set.
- Keep audit and manifest processing read-only with respect to consumer application source, dependency files, deployed systems, and `TDT_HOME` contents.

## Capabilities

### New Capabilities

- None. This change extends the existing `tdt-env-loader-tdt-home` capability.

### Modified Capabilities

- `tdt-env-loader-tdt-home`: make cross-repository source conformance enforceable through consumer governance manifests, AST-based detection of hard-coded `~/.tdt` construction, explicit deployment ownership, and repository-owned exceptions.

## Ownership Boundaries

- `tdt-core` continues to own the canonical `TDT_HOME` provider boundary established by the predecessor change. This change does not redefine provider resolution, configuration, environment loading, or secure filesystem behavior.
- The conformance tooling owns the manifest schema, deterministic validation rules, AST audit semantics, approved provider-site policy, and redacted result format. It reads checked-out repositories but does not import their code or rewrite their files.
- Each consumer repository owns its `.tdt/governance-manifest.json`, the accuracy of its repository and deployment inventory, its declared source sites, its exception records, and its repository-local conformance evidence.
- The named deployment owner owns the accuracy of the declared launch/deployment surface and is accountable for a later provider-gated adoption and rollout change. Recording an owner does not authorize a deployment mutation.
- Exception approval remains with the affected repository. A central or cross-repository audit may validate an exception, but it may not invent, silently broaden, or persist a waiver on the repository's behalf.
- `openspec-store` owns the normative planning and capability-delta artifacts for this change; it does not own consumer application code, dependency metadata, deployment configuration, or operator runtime data.
- The operator owns the live `~/.tdt` tree. This change may identify source references to that tree but must not inspect, create, repair, move, or delete live filesystem contents.

## Explicit Non-Goals

- Migrating consumer source code from hard-coded paths to `tdt-core` provider APIs.
- Adding, removing, pinning, or upgrading consumer dependencies, including changing a consumer's `tdt-core` dependency floor.
- Changing the provider implementation, package version, configuration semantics, environment precedence, or filesystem security kernel established by `govern-tdt-home-config-and-environment`.
- Automatically rewriting source, generating migration commits, or converting audit findings into code changes.
- Treating an exception as proof that a consumer has adopted the provider; exceptions document bounded debt and do not satisfy provider-adoption gates.
- Mutating, validating, repairing, or migrating the live `~/.tdt` filesystem, including its permissions, links, credentials, logs, schedules, databases, configuration, or state.
- Restarting services, editing deployment definitions, changing launch mechanisms, publishing provider artifacts, or rolling out provider releases.
- Implementing migration-plan apply/recovery, interruption handling, reverse rollback rehearsal, or operator cutover.
- Inferring deployment ownership from live infrastructure or credentials when the repository has not declared an accountable owner.

## Deferred Successor Changes

The following work is intentionally deferred and SHALL remain separately owned:

1. `build-tdt-home-synthetic-migration-engine` — typed migration plans, attestations, journaled apply/recovery, and synthetic interruption testing.
2. One provider-gated adoption change per consumer repository — resolution of audit findings through source migration, dependency changes, deployment metadata updates, compatibility handling, and consumer-specific tests.
3. `release-and-roll-out-tdt-home-provider` — provider publication, provider-first deployment, rollout verification, and reverse rollback rehearsal after consumer gates are satisfied.
4. `cut-over-live-tdt-home` — separately approved operator work for the real `~/.tdt` tree after synthetic and deployment evidence is complete.

Audit findings, manifest ownership records, and bounded exceptions produced by this change are inputs to those successors; they do not authorize or perform successor work.

## Impact

- Participating consumer repositories gain one governed file at `.tdt/governance-manifest.json` plus repository-local validation evidence where required.
- Cross-repository verification gains deterministic schema validation and AST source auditing for hard-coded `~/.tdt` construction.
- Existing hard-coded sites without an approved location or valid repository-owned exception become explicit conformance failures. This may reveal adoption blockers but does not remediate them in this change.
- Deployment and launch surfaces without an accountable owner become manifest validation failures, preventing ownerless consumers from being treated as rollout-ready.
- CI may add read-only conformance checks, but consumer runtime behavior, package resolution, deployed processes, and operator data remain unchanged.
- Verification must cover valid and invalid manifests, representative accepted and rejected AST patterns, exception matching and stale-exception rejection, deterministic/redacted output, repository-set aggregation, and strict OpenSpec validation.

## Rollback

Rollback consists of reverting the conformance tooling, CI gate, and repository manifest commits introduced by this change, or temporarily disabling their enforcement while preserving findings for follow-up. Because the audit is read-only and this change does not migrate source, alter dependencies, deploy artifacts, restart services, or mutate `~/.tdt`, rollback requires no consumer data restoration or operator filesystem recovery. Any source, dependency, deployment, provider-release, or live-filesystem rollback belongs to the separately approved successor change that performed that mutation.
