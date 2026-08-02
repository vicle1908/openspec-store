## ADDED Requirements

### Requirement: OpenSpec generated surfaces remain version-current
Documentation consistency checks SHALL compare the repository-approved
OpenSpec version with generated skill metadata, native-skill policy, manifests,
and documented installation commands. The check MUST reject stale generator
versions, floating CI installations, incomplete version migrations, and an
inventory other than 132 skills across the exact eleven generator-managed tool
surfaces plus twelve canonical OpenSpec copies under `.agents/skills`.

#### Scenario: All OpenSpec version records agree
- **WHEN** documentation and generated-surface validation runs after a refresh
- **THEN** the approved pin, all 132 generator-managed `generatedBy` values, all twelve canonical-copy values, policy version, manifest entries, and CI install version identify the same reviewed OpenSpec release

#### Scenario: A generated skill is stale
- **WHEN** any managed OpenSpec skill records a generator version different from the approved pin
- **THEN** validation fails and reports the exact surface requiring regeneration

#### Scenario: CI follows an unpinned installer
- **WHEN** a verification workflow installs OpenSpec through `latest`, an unversioned bootstrap, or another value not derived from the approved pin
- **THEN** documentation consistency fails and identifies the workflow and expected version source

### Requirement: OpenSpec tool paths and invocations remain current
Documentation checks MUST validate the managed path and invocation invariants
for the exact configured OpenSpec tool inventory, including skills-only tools
and approved legacy-path removals. Generated-path validation and canonical
`.agents` parity SHALL be reported separately. Diagnostics SHALL distinguish
stale generated files from hand-authored content and MUST NOT repair either
automatically.

#### Scenario: Configured tool output is incomplete
- **WHEN** one of the eleven repository-approved tools or any of its selected workflow outputs is absent after generation
- **THEN** validation fails and identifies the missing tool and output even if the upstream updater completed or reported other tools successfully

#### Scenario: Canonical copy diverges from generated Codex skill
- **WHEN** a canonical `.agents/skills/openspec-*` copy differs from its approved generated Codex source
- **THEN** parity validation fails separately from tool-path validation and identifies both compared paths

#### Scenario: Codex advertises a slash command
- **WHEN** a managed Codex OpenSpec skill or document advertises `/opsx:*` instead of its installed skill invocation
- **THEN** validation fails and identifies the stale reference

#### Scenario: Legacy Kimi managed files remain
- **WHEN** OpenSpec-owned skills remain under `.kimi/` after the approved Kimi Code migration
- **THEN** validation fails while leaving hand-authored legacy files untouched

#### Scenario: Unsupported runtime-specific tool is referenced
- **WHEN** a generated workflow requires a host-specific interaction or task-list tool unavailable to other supported agents
- **THEN** validation fails and identifies the generated file and unsupported reference category
