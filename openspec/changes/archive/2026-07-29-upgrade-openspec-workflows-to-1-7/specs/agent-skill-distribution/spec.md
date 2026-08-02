## ADDED Requirements

### Requirement: OpenSpec surfaces are generated from one approved version
The repository SHALL declare one exact approved OpenSpec CLI version and MUST
use that value for generated OpenSpec skills and commands, native-skill policy,
manifests, documentation checks, and CI validation. The repository SHALL also
declare the exact generator-managed tool set: Antigravity, Claude, Codex,
Cursor, Factory, Kilo Code, Kimi Code, Kiro, Oh My Pi, OpenCode, and Pi. A
refresh MUST verify the installed CLI version, exact tool set, complete
repository-approved workflow profile, and configured delivery mode before
changing a managed surface.

#### Scenario: Approved version refresh succeeds
- **WHEN** the installed CLI matches the approved version and the exact tools, profile, workflows, and delivery settings are active
- **THEN** the supported refresh regenerates all eleven tool surfaces and records that exact version and complete inventory in policy, generated metadata, and manifests

#### Scenario: Generator inputs do not match policy
- **WHEN** the installed CLI, configured tools, selected workflows, or delivery mode differs from the repository-approved inputs
- **THEN** the refresh fails before changing any managed surface and reports the mismatched input and required remediation

#### Scenario: Generator only partially refreshes configured tools
- **WHEN** the upstream update returns after one or more configured tools, workflows, skills, commands, prompts, or workflows failed to regenerate
- **THEN** post-generation verification rejects the refresh regardless of the updater's process result or success output and identifies every missing or incomplete managed surface

#### Scenario: A newer upstream release exists
- **WHEN** npm reports an OpenSpec release newer than the repository-approved version
- **THEN** verification reports the available release without changing the approved pin or regenerating files until a reviewed upgrade change authorizes it

### Requirement: OpenSpec delivery follows each tool's native contract
Generated OpenSpec content MUST use the file locations and invocation syntax
registered by each supported tool. Codex SHALL receive skills without generated
custom prompts, and Kimi Code SHALL use its current managed directory. The
upstream generator SHALL own the eleven declared tool surfaces and their 132
skills; repository synchronization SHALL separately own the twelve canonical
OpenSpec copies under `.agents/skills`. A path migration MUST remove or move
only files owned by OpenSpec while preserving hand-authored files in legacy or
destination directories.

#### Scenario: Codex surface is generated
- **WHEN** the approved OpenSpec refresh configures Codex
- **THEN** `.codex/skills/openspec-*/SKILL.md` uses `$openspec-*` skill invocations and no OpenSpec-owned Codex custom prompt is present

#### Scenario: Kimi surface is migrated
- **WHEN** the refresh encounters OpenSpec-owned skills under the legacy `.kimi/` directory
- **THEN** the upstream update automatically migrates the managed skills to `.kimi-code/`, removes only obsolete OpenSpec-owned files, and preserves unrelated files in both locations
- **THEN** a divergent managed destination copy is retained and reported for review instead of being overwritten silently

#### Scenario: Tool-specific command syntax is checked
- **WHEN** generated commands, prompts, workflows, and skill cross-references are validated
- **THEN** every supported tool uses the invocation form derived from its registered adapter or skills-only contract and no generated file advertises an unavailable command

#### Scenario: Canonical shared copies are synchronized
- **WHEN** all eleven generator-managed tool surfaces pass post-generation validation
- **THEN** the twelve generated Codex skills are copied through repository support into `.agents/skills` and exact parity is verified before the canonical manifest is accepted

### Requirement: OpenSpec regeneration is rollback-safe
The supported refresh MUST capture the exact pre-update state of every
OpenSpec-owned surface and its version policy before regeneration. Acceptance
MUST be atomic across the approved pin, generated files, canonical shared
copies, and manifests; rollback SHALL restore that coherent set without
changing unrelated agent integrations, credentials, caches, or user state.

#### Scenario: Generated validation fails
- **WHEN** regeneration completes but a surface, invocation, parity, manifest, or documentation check fails
- **THEN** the update is not accepted even when the upstream updater continued after an individual tool failure, and the retained snapshot identifies every OpenSpec-owned path required for a coherent rollback

#### Scenario: Rollback is applied
- **WHEN** a maintainer approves rollback of the OpenSpec refresh
- **THEN** only the captured OpenSpec-owned files and version metadata are restored and the prior focused validation is rerun

#### Scenario: Workstation package maintenance is active
- **WHEN** the global workstation package updater is running or the OpenSpec executable/version is unstable
- **THEN** regeneration fails before snapshot or file mutation and instructs the maintainer to wait for the package-maintenance run and verify its final report
