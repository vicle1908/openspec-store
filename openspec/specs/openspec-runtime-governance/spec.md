# openspec-runtime-governance Specification

## Purpose

Define how TDT selects, upgrades, generates, validates, activates, and rolls back the OpenSpec runtime and its agent workflow surfaces without corrupting shared planning state or allowing stale instructions to control cross-repository work.

## Requirements

### Requirement: Released version authority and immediate package availability

TDT SHALL select an exact official OpenSpec release as the normative runtime, SHALL verify its target commit through the upstream forge, and SHALL verify the executable path and reported version before generation. TDT SHALL NOT enforce a time-based minimum package age, so newly published versions and the current `latest` dist-tag remain immediately eligible. Registry-integrity or exact-version-resolution failures MUST still stop the migration. Context7 or upstream `main` material MAY inform research but SHALL NOT override the reviewed release source when their version or syntax differs.

#### Scenario: Exact release is immediately eligible
- **WHEN** `@fission-ai/openspec@1.7.0` is published and registry-resolvable
- **THEN** the migration SHALL exercise that exact package read-only before global installation
- **AND** the globally responding executable SHALL report `1.7.0` before any generated asset is accepted

#### Scenario: Time-based restriction is encountered
- **WHEN** a package command is blocked only because the published version is considered too new
- **THEN** the operator-approved minimum-age restriction SHALL be removed or disabled
- **AND** the exact reviewed package SHALL be retried without substituting an unreviewed version

#### Scenario: Registry integrity fails
- **WHEN** the exact package cannot be resolved or fails a registry-integrity check for a reason other than age
- **THEN** the migration MUST stop before installation or generation
- **AND** it MUST NOT fall back to a floating or unreviewed package

#### Scenario: Documentation sources disagree
- **WHEN** Context7 or OpenSpec `main` describes a key, command, or topology not present in the official 1.7.0 release source at its verified target commit
- **THEN** TDT SHALL use the released 1.7.0 contract and record the other material as non-normative

### Requirement: Dirty-state and ownership preflight

The migration SHALL inventory repository, ignored, and user-global OpenSpec surfaces before mutation, SHALL classify the owner of every affected path, and MUST stop when an overlapping dirty path or unresolved owner could be overwritten.

#### Scenario: Unrelated OpenSpec work is present
- **WHEN** `tdt-meta` contains pre-existing changes outside `upgrade-openspec-1-7-runtime`
- **THEN** the migration SHALL preserve and report them
- **AND** it SHALL proceed only if no planned generated or configuration path overlaps

#### Scenario: Path ownership is ambiguous
- **WHEN** a workflow file could be OpenSpec-generated, TDT-maintained, or user-authored and provenance cannot be established
- **THEN** the migration MUST NOT remove or regenerate that file
- **AND** it SHALL request ownership resolution

### Requirement: Stable workflow profile during regeneration

The migration SHALL preserve the explicit `core` profile, `delivery: both`, and the selected propose, explore, apply, update, sync, and archive workflows throughout the 1.7.0 regeneration unless a separate approved change alters the workflow product.

#### Scenario: Update would change selected workflows
- **WHEN** preflight or post-update configuration differs from the snapshotted core workflow set
- **THEN** the migration SHALL stop activation and restore or explicitly reconcile the profile
- **AND** it SHALL NOT accept added or pruned workflows as incidental upgrade churn

#### Scenario: Core profile remains stable
- **WHEN** the 1.7.0 update regenerates tool assets with the same profile and delivery
- **THEN** each supported detected tool SHALL receive exactly the workflow surfaces expected for its released adapter capabilities

### Requirement: Codex skills-only migration is ordered and authorized

The migration SHALL establish and verify project-local Codex skills for every selected workflow before removing any OpenSpec-managed global Codex prompt, SHALL use `$openspec-*` as the Codex invocation contract, and MUST obtain explicit authorization before deleting user-global files.

#### Scenario: Replacement skills are ready
- **WHEN** all six selected `.codex/skills/openspec-*` files report generation by 1.7.0 and pass content inspection
- **THEN** the migration MAY offer cleanup of the corresponding managed `~/.codex/prompts/opsx-*.md` files
- **AND** cleanup SHALL occur only after explicit user confirmation

#### Scenario: Replacement skill is missing or invalid
- **WHEN** any selected Codex skill is absent, stale, malformed, or advertises a non-Codex invocation
- **THEN** global prompt cleanup SHALL remain blocked
- **AND** Codex workflow activation SHALL fail closed

#### Scenario: Prompt provenance is unknown
- **WHEN** a global prompt does not match a known OpenSpec-managed workflow or cannot be proven managed
- **THEN** the migration MUST preserve it

### Requirement: Generated and TDT-managed surfaces converge before activation

OpenSpec-managed tool assets SHALL be regenerated by the verified 1.7.0 CLI, while TDT-maintained `.agents` assets SHALL remain under their declared owner. Agent-driven apply, sync, single archive, and bulk archive MUST remain blocked until every host-visible OpenSpec surface agrees on version-appropriate invocation and archive semantics.

#### Scenario: Official surfaces are current but the TDT mirror is stale
- **WHEN** `.codex` and other OpenSpec-managed assets are at 1.7.0 but `.agents/skills/openspec-*` still contains 1.6.0 or background archive delegation
- **THEN** CLI browsing and planning validation MAY continue
- **AND** agent-driven apply, sync, single archive, and bulk archive MUST remain blocked

#### Scenario: All host-visible surfaces converge
- **WHEN** the OpenSpec-managed surfaces and the separately owned TDT mirror pass the same version, invocation, and archive-contract checks
- **THEN** the migration MAY mark agent workflow activation ready

### Requirement: Single and bulk archive synchronization completes inline and verifies delta semantics

Agent-driven single and bulk archive SHALL run requested spec synchronization inline, SHALL wait for completion, and SHALL verify every included delta capability before moving the corresponding change or reporting specs as synced. Background delegation of that synchronization is prohibited.

#### Scenario: Added and modified deltas are synchronized
- **WHEN** a change contains ADDED or MODIFIED requirements and synchronization is requested
- **THEN** archive SHALL verify the added requirements and modified content are present in main specs
- **AND** it SHALL verify unrelated scenarios were not lost

#### Scenario: Removed and renamed deltas are synchronized
- **WHEN** a change contains REMOVED or RENAMED requirements and synchronization is requested
- **THEN** archive SHALL verify removed or old names are absent and renamed requirements exist under the new name

#### Scenario: Synchronization fails or differs
- **WHEN** sync fails, is cancelled, cannot load current instructions, or leaves any delta mismatch
- **THEN** archive MUST stop before moving the change
- **AND** it MUST NOT report the specs as successfully synced

#### Scenario: Bulk archive excludes an unimplemented conflict delta
- **WHEN** bulk conflict analysis excludes a delta because its implementation is not present
- **THEN** bulk archive SHALL omit that delta from sync and verification
- **AND** it SHALL report the delta as sync skipped with its recorded reason rather than as synced

#### Scenario: Bulk archive is cancelled
- **WHEN** the user cancels the consolidated bulk confirmation
- **THEN** bulk archive MUST stop without writing a main spec or moving any selected change

### Requirement: Operation guidance is current, scoped, and non-authoritative

The centralized OpenSpec configuration SHALL provide concise `operations.apply.guidance` and `operations.archive.guidance` that is fetched at operation time, SHALL keep guidance separate from artifact rules and project context, and MUST NOT weaken user choices, built-in workflow instructions, authentication boundaries, or TDT safety policy.

#### Scenario: Apply instructions are requested
- **WHEN** an agent requests current apply instructions for a change
- **THEN** the output SHALL include applicable repository-directory, active-change, dirty-state, GitNexus-symbol, uv, and verification guidance
- **AND** it SHALL omit secrets and inapplicable integration details

#### Scenario: Archive instructions are requested
- **WHEN** an agent requests current archive instructions
- **THEN** the output SHALL include task-completion, touched-spec comparison, strict-validation, inline-sync, and approval boundaries

#### Scenario: Guidance conflicts with authority
- **WHEN** operation guidance conflicts with user direction, CLI state, built-in workflow behavior, artifact rules, or load-bearing TDT policy
- **THEN** the conflicting guidance SHALL NOT be followed
- **AND** the conflict SHALL block mutation until reviewed

### Requirement: Validation uses a scoped non-regression ratchet

The migration SHALL record the complete pre-upgrade strict-validation baseline, SHALL require every active change and every touched main spec to pass the applicable 1.7.0 validation, and MUST NOT increase the number or classes of unrelated main-spec failures.

#### Scenario: Pre-existing main-spec debt remains unchanged
- **WHEN** the post-upgrade full validation still reports the same 66 unrelated invalid main specs and no new error class
- **THEN** the runtime migration MAY pass its scoped validation gate
- **AND** the debt SHALL remain assigned to a separate remediation change

#### Scenario: New regression appears
- **WHEN** an active change fails, a touched main spec fails, the invalid-main-spec count rises above 66, or a new error class appears
- **THEN** activation MUST stop and the regression SHALL be resolved or the runtime rolled back

### Requirement: Existing nearest-root topology remains authoritative

The 1.7.0 migration SHALL retain `tdt-meta/openspec/` as the centralized planning root discovered through the workspace-root symlink and parent-directory traversal. It MUST NOT configure a store, project store pointer, machine-global `defaultStore`, or workset as a source of truth in this change.

#### Scenario: Repository lacks a local OpenSpec symlink
- **WHEN** a command runs from a TDT repository without its own `openspec` entry
- **THEN** it SHALL resolve the workspace parent root with `source: nearest`
- **AND** documentation SHALL describe that parent traversal rather than claim a nonexistent per-repository symlink

#### Scenario: Default store is considered
- **WHEN** the nearest workspace root already resolves successfully
- **THEN** the migration SHALL leave `defaultStore` unset because it would not win inside TDT and could affect unrelated directories outside TDT

### Requirement: Privileged mutations require explicit authorization and protect secrets

Global package installation and deletion of user-global prompt files SHALL be treated as privileged external-state mutations requiring explicit authorization. The migration MUST NOT read, print, copy, or transmit credential values and SHALL NOT alter TDT authentication configuration.

#### Scenario: Global installation is ready
- **WHEN** preview evidence passes and the exact install command is known
- **THEN** the migration SHALL present the version, executable path, expected generated effects, and rollback before requesting authorization

#### Scenario: Credential-bearing content is encountered
- **WHEN** an environment, npm, OpenSpec, or prompt file could expose a credential value
- **THEN** the migration SHALL avoid emitting or copying that value
- **AND** only non-sensitive path, version, status, or redacted metadata MAY enter evidence

### Requirement: Rollback is exact, scoped, and verifiable

The migration SHALL maintain a rollback path that restores OpenSpec 1.6.0 and its managed surfaces without destructive Git operations or changes to unrelated work. Rollback SHALL be verified with the same root, profile, asset, and validation evidence used for forward activation.

#### Scenario: Runtime activation fails
- **WHEN** the 1.7.0 binary, generated assets, instructions, validation ratchet, or host convergence gate fails after mutation
- **THEN** the operator SHALL reinstall exactly 1.6.0, regenerate only OpenSpec-managed 1.6.0 assets, and restore verified managed prompts when required
- **AND** unrelated dirty paths and TDT-managed `.agents` files SHALL remain untouched

#### Scenario: Rollback completes
- **WHEN** the prior version, profile, root resolution, managed asset inventory, and validation baseline are restored
- **THEN** the migration SHALL report rollback verified and keep 1.7 activation disabled
