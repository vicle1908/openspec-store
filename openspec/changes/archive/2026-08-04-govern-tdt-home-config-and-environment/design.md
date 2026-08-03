# Design: TDT_HOME Provider Foundation

## Context

The existing `tdt-core` provider already exposes a dynamic root resolver, dotenv loading, state helpers, and scheduler configuration. The security worktree adds a descriptor-relative filesystem kernel, strict control-plane schemas, packaged participant-registry validation, typed path helpers, environment profiles, and a base CLI. The provider is not yet green: the current branch still has a failing environment-profile test and static-check findings, and downstream repositories have not adopted the provider.

The proposal defines the boundary for this change. The delta specification defines observable provider behavior. This document records the implementation choices and the evidence gates that make those behaviors trustworthy.

## Goals / Non-Goals

**Goals:**

- Provide one call-time root and path contract for provider-owned runtime data.
- Preserve development compatibility while making production precedence explicit and process-selected.
- Keep secret values out of general config and diagnostics.
- Make provider-owned filesystem mutations fail closed when object identity, containment, or platform capabilities cannot be verified.
- Provide an installed-wheel doctor and mandatory packaged contract data.
- Produce a verifiable provider artifact before any consumer adoption.

**Non-Goals:**

- Consumer path migration, consumer deployment facts, or repository-owned manifests.
- Cross-repository source audit enforcement.
- A migration-plan compiler, live migration executor, journal recovery engine, or operator cutover.
- Nexus publication, launchd/Compose rollout, or live `~/.tdt` repair.

Those non-goals become successor changes named in `proposal.md`. They must not be smuggled back into this provider change through guessed maps or placeholder manifests.

## Decisions

### Decision 1: One dynamic provider boundary

All public provider paths call `tdt_root()` at operation time. No module-level constant captures `TDT_HOME`. Components are validated before a path is returned. Explicit paths remain injectable for tests, but default behavior always re-evaluates the provider root.

The provider exposes bounded helpers for config, credentials, schedules, logs, state, and runtime files. The API returns paths for read-only callers and delegates provider-owned creation/replacement to the security kernel.

**Alternative rejected:** retaining separate `Path.home() / ".tdt"` logic in consumers. That preserves the current drift and makes alternate-root tests unreliable.

### Decision 2: Process-selected environment profiles

`TDT_ENV_PROFILE` is read only from the inherited process environment before either dotenv file is opened. The default profile is `development` for compatibility. Development may load the repository-local `.env` with override semantics; `production` never loads that file. Unknown non-empty profiles fail closed.

Initialization is protected by a process-local re-entrant lock. A successful load publishes one terminal state. A failed load publishes no partial initialized state. Test isolation acquires the same lock and restores only keys it changed; it is not a production concurrency primitive.

**Alternative rejected:** inferring production from the current directory or allowing a dotenv file to select the profile. Either permits a lower-trust file to change deployment semantics.

### Decision 3: Typed non-secret configuration

The provider loads supported YAML/TOML sources into typed, redacted structures. Secret-shaped keys accept only the full-scalar `${VAR_NAME}` grammar. Values are resolved after environment loading. Duplicate logical settings are normalized deterministically; equal values are compatibility evidence, while conflicts fail closed.

General config remains free of credential values. Application-specific schemas stay with their owning repositories. Scheduler consumption uses the governed provider parser only after the provider contract is available.

**Alternative rejected:** silently choosing one literal DSN or password when sources conflict. That hides ownership and makes a future migration non-deterministic.

### Decision 4: Descriptor-relative security kernel

Provider-owned mutation anchors an existing root or an approved bootstrap parent once, retains the relevant directory descriptors, validates each relative component, and checks object identity after open/create. Descendant traversal uses no-follow semantics. Protected regular files require the declared type, owner/access policy, and single-link policy.

Temporary writes are created privately, written completely, synchronized, renamed relative to retained descriptors, and reopened for final identity/digest checks. Parent-directory synchronization is part of the successful replacement boundary. If a required primitive is unavailable, mutation fails closed; read-only path construction may remain available.

The exact `dir_fd`, no-follow, close-on-exec, synchronization, and platform-capability choices are design/test constraints. They are deliberately not repeated as normative spec statements.

**Alternatives rejected:**

- `Path.resolve()` plus pathname-based copy/replace operations in the mutation boundary, because a validated pathname can be redirected before use.
- Recursive `mkdir` or implicit ancestor discovery, because bootstrap policy must identify the approved anchor.
- A ctypes syscall shim or undocumented numeric constants, because portability and capability detection must remain explicit.

### Decision 5: Redacting doctor as a provider boundary

`tdt config doctor` runs against an explicit or effective root and reports stable relative paths, logical keys, source names, object classes, modes, ownership/access findings, and link status. It never prints secret values, raw DSNs, full environment values, or arbitrary journal contents. Runtime doctor imports only installed provider resources and does not require the workspace.

External principals are represented by typed attestations in successor work; the provider must not claim access for a principal it cannot map or directly prove.

### Decision 6: Mandatory packaged provider contracts

The provider packages its registry/schema/rule resources through the package-resource API. Loading validates resource identity, version, uniqueness, and required fields. Missing or malformed package data is an operational failure, not an empty default. Synthetic resources may be used by provider tests, while real consumer manifests remain outside this change.

### Decision 7: Release verification is local and reproducible

The provider release gate builds a wheel and a complete locked local wheelhouse, then installs into a clean environment with no checkout and no `PYTHONPATH`. It checks distribution/runtime version equality, base CLI availability without scheduler extras, package-resource presence, redacted doctor behavior, and provider-only contract tests. Nexus availability is recorded as a separate conditional fact and is not required for local provider readiness.

## Transaction Boundaries

The implementation must make these boundaries explicit in tests and diagnostics:

1. **Environment initialization:** lock acquisition, source selection, complete load, and terminal publication.
2. **Root bootstrap:** approved anchor verification, one-component-at-a-time creation, descriptor re-open, and parent synchronization.
3. **Protected replacement:** private staging creation, complete write, file synchronization, descriptor-relative rename, parent synchronization, and post-open verification.
4. **Configuration load:** source discovery, parse, reference resolution, duplicate/conflict validation, redacted result publication.
5. **Doctor snapshot:** stable root identity, bounded traversal, finding collection, and redacted serialization.
6. **Package contract load:** resource discovery, schema/identity validation, and readiness publication.

No live migration transaction is implemented here. Journaled plan/apply/recovery boundaries belong to `build-tdt-home-synthetic-migration-engine`.

## Implementation Evidence Classification

- The `tdt-core-home-security-kernel` branch is the only implementation candidate for this change. Its committed kernel, schema, registry, path, environment, and CLI work are evidence to be mapped task-by-task after the provider gates pass.
- The `tdt-core-home-control-plane` worktree is a superseded prototype. Its guessed path map, caller/PID quiescence, and pathname-oriented recovery must not be promoted into this design.
- Existing code is never sufficient by itself to check a task complete. A task requires the matching test or verification evidence and a clean scope review.

## Risks / Trade-offs

- **Security kernel is platform-sensitive** → run a positive capability matrix on the supported macOS/Python build and fail mutation closed when the baseline is unavailable.
- **Development compatibility can mask production mistakes** → require an inherited process profile and test that production excludes repository-local dotenv files.
- **Strict secret rejection may expose legacy configuration drift** → report logical keys and sources only, then handle consumer migration in separate changes.
- **Package-resource omissions can pass editable tests** → require clean wheelhouse installation with no checkout or `PYTHONPATH`.
- **The provider touches high-fanout call paths** → rerun GitNexus impact/detect checks against the implementation candidate before committing provider work.

## Migration Plan

1. Finish provider RED/GREEN tests and the security-kernel implementation in the owned `tdt-core` worktree.
2. Run full provider tests, Ruff, format, strict mypy, redaction/security scans, and installed-wheel smokes.
3. Verify the provider artifact and package resources in a clean local wheelhouse.
4. Mark only evidenced provider tasks complete and run OpenSpec verification.
5. Create successor changes for source conformance, synthetic migration, consumer adoption, rollout, and live cutover.
6. Do not alter the real `~/.tdt` tree in this change.

Rollback restores the pre-change provider artifact and metadata. Since consumers and live operator data are outside this change, rollback does not remove or rewrite consumer state.

## Open Questions

None for the provider boundary. Questions about consumer principals, deployment writers, migration plans, release authority, and live cutover are intentionally deferred to the successor changes and must be answered by their owning repositories/operators.
