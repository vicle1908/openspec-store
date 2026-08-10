## Why

The live `agent-core`, `agent-docs-sync`, and `agent-harness` checkouts contain
partially applied consolidation work, but the existing proposal still describes
the superseded eight-area plan. In particular, the new lifecycle seam currently
duplicates `SubjectAssertionVerifier`, and the default config resolver can turn
caller-controlled environment text into authenticated authority, which conflicts
with the existing fail-closed lifecycle contract.

This change now records the smaller, contract-driven refactor that can be safely
completed against the current code and existing OpenSpec requirements.

## What Changes

- Make `SubjectResolver` the one canonical lifecycle resolver protocol in
  `agent-core`; remove the duplicate `SubjectAssertionVerifier` protocol and
  update its current core caller without retaining an alias.
- Make the lifecycle default fail closed. `unavailable_resolver()` must use the
  unavailable provider, and `ConfigFileResolver` must never convert
  `TDT_ACTOR_ID`, caller text, or another unsigned config value into an
  authenticated subject.
- Remove consumer compatibility aliases. `agent-docs-sync` and
  `agent-harness` will import the canonical core symbols directly while keeping
  their distinct policy, audit, gate, and error-mapping behavior.
- Adopt the shared path-containment primitives in consumer code where their
  semantics match, preserving consumer-specific exception translation and the
  harness ArtifactStore CAS, symlink, and TOCTOU boundaries.
- Keep the shared tool utility narrow: bounded JSON loading and schema checks
  only. Preserve docs-sync Markdown/legacy manifest behavior and harness
  Graphify/GitNexus evidence, freshness, source-identity, and transport
  validation in their owning repositories.
- Add the regression and full-suite verification needed to finish the partial
  implementation, including macOS system-symlink path handling and strict
  OpenSpec validation.

## Capabilities

### New Capabilities

None. This is a contract-preserving implementation consolidation and a
fail-closed correction against existing lifecycle requirements.

### Modified Capabilities

None. Existing requirements in `authenticated-lifecycle-actors`,
`sdk-public-api`, and `stage-toolset-composition` remain authoritative; this
change does not introduce a delta spec.

## Non-Goals

- Unifying the Graphify or GitNexus adapters, transports, evidence models,
  Markdown parsers, or docs-sync's nested `compare_hashes()` contract.
- Moving consumer exceptions into a broad `AgentCoreError` taxonomy without a
  concrete cross-consumer caller and acceptance contract.
- Changing dependency versions, Ruff/mypy/coverage/uv policy, shared fixtures,
  or documentation counts; those belong to the separate
  `ecosystem-standardization` change.
- Replacing or weakening the harness ArtifactStore's durable CAS, idempotent
  retry, symlink, or TOCTOU protections.
- Preserving old lifecycle import names through aliases or compatibility
  wrappers. The requested migration is a complete internal update.

## Impact

### Affected Repositories

- **agent-core**: owns the canonical resolver seam, fail-closed default, path
  primitives, and bounded JSON utility.
- **agent-docs-sync**: migrates lifecycle imports and adopts shared path/JSON
  helpers while retaining its write-policy and report parsing boundaries.
- **agent-harness**: migrates lifecycle imports and path resolution while
  retaining gate policy, typed evidence, provider validation, and ArtifactStore
  boundaries.

### Ownership Boundaries

`agent-core` owns reusable primitives and their tests. Each consumer owns its
policy overlays, domain exceptions, evidence models, and call-site migration.
The concurrent dirty files and generated outputs in each repository must be
classified before implementation changes are staged; unrelated work remains
untouched.

### Security and API Impact

The environment-based identity shortcut is removed from the authority path, so
an unconfigured or unratified provider fails closed. Existing stable symbols
required by the current SDK contract may remain as explicitly fail-closed
implementations, but no legacy consumer aliases are retained.

The change keeps `skip_specs: true` because it adds no new capability or delta
requirement; implementation must continue to satisfy the existing lifecycle,
SDK, and read-only code-intelligence specifications.
