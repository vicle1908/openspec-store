# gitnexus-stable-contract Specification

## Purpose

Defines an exact, attributable, bounded, read-only GitNexus contract so impact and code-intelligence evidence can be safely consumed across the agent ecosystem.

## Requirements

### Requirement: Verified provider binding

Every GitNexus result SHALL identify the canonical installed CLI version, upstream source-tag revision, executable digest, TDT adapter/schema identifier and digest, target repository identity, indexed source revision, freshness status, query class, and bounded result status. The approved provider SHALL report GitNexus `1.6.9`, whose source tag resolves to `4227194ad7bdfbedc29a7fe20e09c6737ce0e744`. `latest`, release candidates, project-runner fallback, and schemas obtained from an unpinned branch SHALL NOT satisfy the binding. MCP exposure is optional.

#### Scenario: Binding is verified

- **WHEN** a consumer requests a supported read-only operation
- **THEN** the binding check SHALL verify CLI version/source, observed executable digest, adapter/schema ID/digest, explicit canonical repository root, and indexed revision equality with the intended source before execution
- **AND** the result SHALL carry those identities for downstream evidence

#### Scenario: Reviewed repository map changes

- **WHEN** a repository is added to or removed from the reviewed binding
- **THEN** the adapter SHALL validate its bounded ID-to-canonical-root map from digest-pinned configuration
- **AND** implementation code SHALL NOT require a duplicate hard-coded repository list

#### Scenario: tdt-meta policy and tooling changes

- **WHEN** an authorized change edits policy or tooling in `tdt-meta`
- **THEN** `tdt-meta` SHALL remain absent from the GitNexus repository binding and GitNexus impact/change-scope gates
- **AND** the edit SHALL instead require an apply-ready OpenSpec change, exact repository-local static caller review, focused regression tests, applicable schema/policy checks, and scoped diff review
- **AND** no `tdt-meta` index, bootstrap, or guessed provider alias SHALL authorize or block the edit

#### Scenario: Binding is ambiguous or stale

- **WHEN** provider, schema, repository, index revision, freshness, or immutable version/source attribution cannot be verified
- **THEN** the operation SHALL fail closed as unavailable or needs input
- **AND** it SHALL not return an empty successful result

### Requirement: Bounded read-only capability matrix

The stable contract SHALL expose only documented bounded query, exact-symbol
resolution, context, impact, detect-changes, status, and source-identity reads.
Repository identity SHALL be explicit even when the provider currently reports
multiple indexed repositories. Setup, refresh, analyze, rename, delete, clean, group
management/synchronization, shell, and code-execution operations SHALL remain
unavailable. Any bounded cross-repository read SHALL require a separately
approved contract and SHALL NOT be inferred from group membership. Provider
stdout and stderr SHALL remain digest-only; successful envelopes SHALL contain
only operation-specific allowlisted evidence. Host-provided MCP exposure SHALL
remain optional. An adapter-managed local stdio MCP subprocess MAY be used only
for structured `detect_changes` when it is launched from the same verified
executable and independently enforces the approved transport, repository,
method, byte, count, and timeout bounds.

#### Scenario: Authorized read

- **WHEN** a request names a supported repository, operation, symbol identity, bounds, and timeout
- **THEN** the adapter SHALL enforce timeout, result-count, byte/token, depth, and truncation bounds independently of provider annotations and the provider SHALL return validated results within those bounds
- **AND** the result SHALL preserve repository and source identity

#### Scenario: Mutation or unbounded request

- **WHEN** a caller requests mutation, setup, refresh, group management, shell, or an unbounded query
- **THEN** the contract SHALL reject it before provider execution

#### Scenario: Authorized stale-index recovery

- **WHEN** an index is stale and the user has contemporaneously authorized recovery for an exact repository set
- **THEN** an operator MAY run the already installed pinned CLI with `analyze --index-only --default-branch main` for only those repositories
- **AND** the operation SHALL reject package fallback, `--force`, embeddings, PDG, skills/context injection, setup, clean, group operations, or any repository outside the approved set
- **AND** read-only consumption SHALL remain unavailable until post-refresh status proves indexed revision equality

#### Scenario: Exact symbol resolves without ranked search

- **WHEN** a caller supplies a bounded symbol name and repository-relative file path for one current bound repository
- **THEN** the adapter SHALL use the pinned provider's native name-and-file disambiguation and return the exact provider UID only when epistemic status, returned name, returned file path, optional kind, repository identity, and source/index equality all match
- **AND** the exact result SHALL be usable as the UID input to a separately bounded context or impact request
- **AND** saturated ranked query output SHALL NOT be accepted or required as exact-symbol evidence

#### Scenario: Exact symbol is absent or ambiguous

- **WHEN** native name-and-file disambiguation is absent, ambiguous, mismatched, malformed, stale, truncated, or returns more than one possible identity
- **THEN** exact resolution SHALL return a typed incomplete result without a UID
- **AND** the adapter SHALL NOT guess a UID, refresh the index, or fall back to ranked search evidence

#### Scenario: Impact query resolves one symbol

- **WHEN** a caller requests impact evidence
- **THEN** the request/result identity SHALL include explicit repository ID, symbol UID or verified disambiguation, direction, depth, test-inclusion policy, confidence threshold, bounds, timeout, and truncation status
- **AND** an ambiguous symbol response SHALL remain incomplete until a UID obtained from a prior verified result is selected

#### Scenario: Change scope is current and bounded

- **WHEN** a caller requests detect-changes for one bound repository using `unstaged`, `staged`, `all`, or `compare`
- **THEN** the request/result identity SHALL include repository, source/index equality, scope, optional compare base, result limit, timeout, byte bounds, output digests, and truncation status
- **AND** limit-saturated, malformed, ambiguous, cross-repository, or incomplete results SHALL remain unavailable rather than being accepted as complete scope evidence

#### Scenario: Structured change scope bypasses provider display truncation

- **WHEN** the pinned CLI renderer reports a changed-symbol count larger than the rendered symbol list
- **THEN** the adapter MAY launch the same digest-verified GitNexus `1.6.9` executable as a bounded local stdio MCP subprocess and invoke exactly `tools/call` for `detect_changes`
- **AND** it SHALL verify MCP protocol/server identity, exact repository registration, requested scope/base, result count equality, result limit, output bytes, timeout, and digest-only output before accepting evidence
- **AND** general MCP tool routing, `tools/call` for any other tool, mutation/group/setup tools, guessed repository aliases, and host MCP dependencies SHALL remain unavailable

#### Scenario: Reviewed repository is absent from the MCP registry

- **WHEN** the bounded stdio transport does not expose the reviewed repository ID exactly
- **THEN** structured change scope SHALL return typed unavailable for that repository
- **AND** the adapter SHALL NOT substitute a display name, path-derived alias, group member, or other registry entry

#### Scenario: Current provider does not represent the target language

- **WHEN** the verified current provider returns exact not-found for a named file and symbol because that language is unsupported
- **THEN** an apply-ready change MAY use exact static callers, conservative risk, language syntax validation, and focused red/green fixtures for a worktree-only edit
- **AND** stale, ambiguous, unbound, or truncated indexed evidence SHALL NOT use this fallback
- **AND** the fallback SHALL NOT satisfy a pre-commit change-scope gate

#### Scenario: Current index does not contain the exact worktree symbol

- **WHEN** the verified current provider returns exact current-index not-found for a named symbol and repository-relative file while the target language is represented
- **THEN** an apply-ready owning change MAY use a worktree-static fallback only after proving source/index equality at committed `HEAD`, exact symbol presence or absence in the committed file, exact symbol presence and location in the current worktree, and complete single-repository change-scope evidence
- **AND** the fallback SHALL record every exact current-worktree caller, classify shared or effect-bearing entry points as at least MEDIUM risk, obtain confirmation for HIGH or CRITICAL risk, run focused red/green regressions plus the language syntax/type/format gates, and review the scoped post-edit diff
- **AND** ambiguous, stale, truncated, unbound, mismatched, or provider-unavailable results SHALL NOT use this fallback
- **AND** worktree-static evidence SHALL NOT become a guessed provider UID or satisfy a pre-commit change-scope gate

### Requirement: Consumer conformance

Consumers SHALL use the verified stable binding and SHALL surface unavailable, malformed, out-of-bounds, or stale results without synthesizing current evidence.

#### Scenario: Harness adapter consumes a result

- **WHEN** `agent-harness` receives a verified GitNexus result
- **THEN** it SHALL validate operation and every query-defining field, repository, revision equality, provider/transport/schema identity, bounds, truncation, and freshness before creating evidence

#### Scenario: Provider transport is unavailable

- **WHEN** no verified transport satisfies the binding
- **THEN** consumers SHALL return a typed unavailable/needs-input outcome
- **AND** readiness or code-change gates SHALL remain incomplete

### Requirement: Authorized scheduled workspace index recovery

A workspace-local scheduler SHALL perform bounded GitNexus index-only recovery only for an explicit reviewed repository inventory and SHALL NOT expose mutation through the consumer MCP adapter.

#### Scenario: Scheduled recovery is approved

- **WHEN** an operator explicitly approves installation of the workspace scheduler for a reviewed inventory
- **THEN** the scheduler MAY run the already installed pinned GitNexus `1.6.9` CLI with `analyze --index-only --default-branch <inventory-branch>` only for the exact inventory entries
- **AND** each run SHALL record the normalized inventory digest, canonical repository root, target HEAD, provider identity, and result status
- **AND** the scheduler SHALL reject `--force`, embeddings, PDG, setup, clean, group operations, package fallback, and repositories outside the inventory

#### Scenario: Inventory changes after approval

- **WHEN** the inventory is added to, removed from, or changed after scheduler approval
- **THEN** the scheduler SHALL fail closed until the changed inventory is explicitly reviewed and approved
- **AND** it SHALL not infer authorization from dynamic repository discovery or group membership

#### Scenario: Consumer adapter requests mutation

- **WHEN** a consumer requests refresh, analyze, or another mutation through the stable GitNexus adapter
- **THEN** the adapter SHALL continue to reject the request before provider execution
- **AND** the workspace scheduler's separate operator path SHALL not be exposed as an MCP mutation tool
