## Context

See `proposal.md` for the motivation and narrowed scope. The live source
inspection identified three important constraints:

- `agent-core.lifecycle_identity` already has a ratified assertion/result model
  and an existing `SubjectAssertionVerifier` seam. The concurrent
  `SubjectResolver` addition has the same `resolve()` signature, so keeping both
  would leave two canonical protocols.
- The current `ConfigFileResolver` accepts `TDT_ACTOR_ID` and constructs a
  valid high-assurance subject without a signed assertion. That conflicts with
  `authenticated-lifecycle-actors`, which requires a ratified host adapter and
  trust root and explicitly rejects caller/environment values as authority.
- The path helpers and bounded JSON loader are already present in dirty
  `agent-core` work and are partly adopted by both consumers. The harness path
  wrapper currently needs a macOS symlink regression check before it can be
  accepted as a security-preserving replacement.

## Goals / Non-Goals

**Goals:**

- Establish one canonical lifecycle resolver seam and migrate all in-scope
  callers directly to it.
- Make every production default fail closed until a ratified identity adapter
  and trust root are available.
- Reuse path containment and bounded JSON validation only where their contracts
  are equivalent to the consumer behavior.
- Preserve consumer-specific policy/error/evidence boundaries and verify the
  complete implementation across all three repositories.

**Non-Goals:**

- Compatibility aliases, broad exception-taxonomy changes, or a new identity
  broker.
- Common Graphify/GitNexus transport, evidence, freshness, or hash-comparison
  contracts.
- ArtifactStore redesign or ecosystem tooling/dependency standardization.

## Decisions

### 1. `SubjectResolver` is the canonical protocol

The new consumer-facing name is selected as the single public seam because the
consumer operations resolve an operation-bound subject and the current partial
consumer migration already uses that name. The existing
`SubjectAssertionVerifier` declaration will be removed, and
`agent_core.authority_execution` plus all direct callers will use
`SubjectResolver`. There will be no type alias or parallel protocol.

The alternative—keeping `SubjectAssertionVerifier` and deleting the new name—
would minimize core edits but would leave consumer-facing code tied to a
verification-internal name. Either choice is safe only if one symbol remains;
this plan chooses the name already used by the consumer migration.

`IdentityError`, `IdentityUnavailableError`, `require_subject()`, and
`unavailable_resolver()` are shared boundary helpers only. Docs-sync and
harness retain their own policy-specific errors and map the shared result into
those errors at their respective authorization boundaries.

### 2. Identity resolution is fail closed

`unavailable_resolver()` returns `UnavailableSubjectResolver`, never
`ConfigFileResolver`. `ConfigFileResolver` must not synthesize an
`AuthenticatedSubject` from `TDT_ACTOR_ID`, display text, process ownership, or
OS identity. Because the existing SDK contract names `ConfigFileResolver`, the
symbol may remain exported as an explicitly unavailable/non-authoritative
implementation until a separate spec-reviewed API decision removes it; its
presence must not imply that config text establishes authority.

The valid path remains a signed, operation-bound assertion checked against the
requested audience, nonce, ratified adapter, trust root, key, freshness,
revocation, assurance, and policy generation. No broker, trust root, or
authentication shortcut is invented in this refactor.

### 3. Migrate imports directly; do not preserve aliases

Docs-sync removes `LifecycleSubjectResolver`, `LifecycleIdentityError`, and
`LifecycleIdentityUnavailableError` aliases. Its state, CLI, and tests import
the core error/helper names directly. Harness removes the
`GateSubjectResolver` alias and `unavailable_gate_resolver()` wrapper; runner
annotations and calls use `SubjectResolver` and `unavailable_resolver()`.

`GateIdentityError`, `GateIdentityUnavailableError`, gate bindings, separation
of duties, and safe evidence remain harness-owned because their constructor and
policy contracts are not interchangeable with docs-sync's lifecycle ledger.

### 4. Share containment primitives, not policy

`is_within()`, `expand_resolve()`, `validate_contained()`, and
`validate_within_any()` are pure core helpers. They resolve paths before
containment comparison and preserve the caller's exception mapping.

Symlink rejection is scoped to components between the approved boundary and
the candidate path. Canonical operating-system ancestors such as macOS's
`/var -> /private/var` must not be rejected merely because the platform uses a
system symlink; symlink components introduced inside the approved boundary
remain rejected. Traversal, outside-root, non-existent-path, and symlink-inside
root tests are required.

Docs-sync keeps `WriteContainmentError` and its workspace-relative write policy.
Harness keeps ArtifactStore's CAS and symlink/TOCTOU validation unless a future
contract proves the shared helper equivalent. Core built-in tools may use
`is_within()` only while preserving their `ToolError` code and diagnostics.

### 5. Keep JSON loading bounded and adapter-neutral

`load_json_artifact()` and `validate_artifact_schema()` may be shared for local,
bounded JSON files. The utility owns file existence, size, JSON-object shape,
approved-root containment, and basic schema/repository checks.

It does not own Graphify or GitNexus semantics. The core `compare_hashes()`
addition is removed because it is not compatible with docs-sync's nested
`ast_hash`/`mtime` change-dictionary API. Docs-sync keeps its own comparison and
Markdown/directory parsing. Harness keeps source identity, freshness, result
bounds, evidence construction, and GitNexus envelope/transport validation.

### 6. Verification is a release gate

A task is complete only when the implementation and the affected repository's
full test, Ruff, and strict mypy checks pass. The final gate also runs strict
OpenSpec validation, store doctor, `git diff --check`, and a dirty-path
ownership audit. Known unrelated active changes are reported separately and do
not become part of this change.

## Risks / Trade-offs

| Risk | Mitigation |
| --- | --- |
| Removing duplicate protocol names breaks stale internal imports | Perform a bounded repository-wide search, update all callers/tests, and require full suites before completion. |
| Removing the environment shortcut exposes unconfigured workflows | Treat the resulting unavailable error as the intended fail-closed behavior; require a separately ratified adapter before enabling production identity. |
| Shared symlink checks reject valid macOS paths or weaken boundary checks | Test system symlink ancestors separately from symlinks inside the approved root, and retain ArtifactStore's existing security tests. |
| Generic JSON validation collapses consumer-specific errors | Map only at the adapter boundary and preserve typed unavailable/stale/out-of-bounds outcomes. |
| Concurrent workers or generated files are overwritten | Audit each dirty path against the ownership table and stage only change-owned files. |

## Migration Plan

1. Keep the current OpenSpec artifacts aligned with this design; no
   implementation code is changed by the planning update.
2. Complete the lifecycle canonicalization and fail-closed tasks in
   `agent-core`, then migrate consumer imports and remove aliases.
3. Finish path adoption and the macOS symlink regression without modifying
   ArtifactStore's durable semantics.
4. Remove the incompatible shared hash helper, finish the bounded JSON adapter
   checks, and run the three full verification profiles.
5. Archive this change only after every task is checked and the final OpenSpec
   validation gate is clean except for explicitly unrelated work.

Rollback is a source-level revert of only the change-owned implementation
commits. Do not reset or delete concurrent dirty work, generated indexes, or
unrelated OpenSpec changes.

## Open Questions

None. The canonical protocol, no-alias migration, fail-closed identity rule,
and excluded work are decisions for this change; deferring any of them would
make the task breakdown ambiguous.
