# Spec Delta

## MODIFIED Requirements

### Requirement: Shared Agent Skills SHALL be discoverable across independent repositories

The workspace SHALL maintain shared Agent Skills in canonical skill roots under `~/Developer/.agents/skills/`, where each skill root contains `SKILL.md`. Container directories without a root `SKILL.md` MUST NOT be counted as skills. Standard-compatible agents running inside independent workspace Git repositories SHALL discover the selected shared skills through supported repository or user-level `.agents/skills` locations without requiring copied shared skill directories under product-specific configuration roots. Pi SHALL be treated as a covered standard-compatible agent.

When a workspace skill root is exposed for user-scope discovery, the entry at `~/.agents/skills/<skill-name>` SHALL be a link resolving to the canonical workspace skill root. User-scope entries MUST NOT hold content duplicated from a workspace skill root. A skill with no workspace counterpart MAY exist as a real directory in `~/.agents/skills` and SHALL be preserved.

#### Scenario: Codex discovers OpenSpec from an independent repository

- **GIVEN** Codex starts inside a workspace Git repository that has no repository-local OpenSpec skill mirror
- **WHEN** the user explicitly invokes `$openspec-explore`
- **THEN** Codex SHALL load the selected skill through standard `.agents/skills` discovery
- **AND** the invocation SHALL NOT require a copied OpenSpec directory under `~/.agents/skills`

#### Scenario: Standard user-level links bridge independent Git roots

- **GIVEN** `~/Developer/.agents/skills/` is above each independent repository's Git root
- **WHEN** selected workspace skill roots are synchronized for user-scope discovery
- **THEN** `~/.agents/skills/<skill-name>` SHALL resolve to the canonical workspace skill root
- **AND** stale, broken, missing, or conflicting links MUST be reported by verification

#### Scenario: A workspace skill exposed at user scope is a link, not a copy

- **GIVEN** a skill exists under `~/Developer/.agents/skills/<name>` and is selected for user-scope discovery
- **WHEN** the user-scope surface is synchronized
- **THEN** `~/.agents/skills/<name>` SHALL be a link to the workspace skill root
- **AND** a real directory holding identical content at that path MUST be reported as a deviation and corrected

#### Scenario: Skill inventory distinguishes containers from skills

- **GIVEN** the workspace collection contains directories with and without a root `SKILL.md`
- **WHEN** the collection is audited or synchronized
- **THEN** only directories containing a root `SKILL.md` SHALL be counted as skills
- **AND** container directories SHALL be reported separately

### Requirement: Product-native skill surfaces MUST preserve distinct capabilities without shared-content drift

Product-native directories MUST retain configuration or capabilities that are not provided by the shared Agent Skills surface. Claude-native OpenSpec skills and `/opsx:*` commands SHALL remain available through `.claude/`, while `.codex/` MUST retain Codex configuration, roles, hooks, automation, memories, system skills, and genuinely Codex-specific skills. Shared skill content MUST NOT be copied into `~/.agents/skills` when standard `.agents/skills` discovery has been verified. Product-specific configuration roots such as `~/.pi/agent/skills` MUST NOT hold copies of skills that are available through standard `.agents/skills` discovery.

#### Scenario: Claude loads its native OpenSpec workflow

- **GIVEN** Claude Code starts inside an independent workspace repository
- **WHEN** the user explicitly invokes an OpenSpec skill or `/opsx:*` command
- **THEN** Claude Code SHALL load the corresponding native skill or command through a supported `.claude` discovery path
- **AND** all twelve generated OpenSpec commands SHALL be present

#### Scenario: A product-specific skill root duplicates standard discovery

- **GIVEN** a product-specific root such as `~/.pi/agent/skills` contains entries that are also available through `~/.agents/skills`
- **WHEN** the skill surfaces are audited
- **THEN** the duplicate entries MUST be reported, including whether any entry is unique to the product-specific root
- **AND** removal SHALL proceed only when no entry would be lost

#### Scenario: Codex-specific governance remains intact

- **GIVEN** shared skills are removed from `~/.agents/skills`
- **WHEN** the Codex workspace configuration is audited
- **THEN** `config.toml`, custom roles, hooks, automation, memories, security constraints, and system or Codex-specific skills MUST remain intact
- **AND** repository ownership, read-only role, non-overlapping-writer, credential-protection, and Context7 policies MUST remain documented

#### Scenario: Existing global installations are preserved

- **GIVEN** `~/.agents/skills/` contains real directories installed through global `npx skills`
- **WHEN** workspace skill links are synchronized
- **THEN** the synchronizer MUST preserve those real directories and their lockfile provenance
- **AND** a workspace skill name collision with a real global installation MUST fail verification instead of overwriting content

## ADDED Requirements

### Requirement: Skill placement SHALL follow a global-versus-workspace ownership rule

Skills SHALL be placed according to ownership. Machine- or service-level guidance and vendor or library guidance SHALL be exposed at user scope so they apply in any project. Skills owned by a generator, CLI, or package SHALL remain in the canonical workspace skill root and MUST NOT be relocated to user scope, where the owning tool cannot maintain them.

#### Scenario: A generator-owned skill is considered for user scope

- **GIVEN** a skill is generated by a CLI or package such as the OpenSpec CLI or the GitNexus package
- **WHEN** placement is evaluated
- **THEN** the skill SHALL remain in `~/Developer/.agents/skills` under its generator's ownership
- **AND** user-scope exposure SHALL occur only through a link to that canonical root

#### Scenario: Machine-scoped guidance is placed at user scope

- **GIVEN** a skill documents a machine-local service or vendor library rather than a repository
- **WHEN** placement is evaluated
- **THEN** the skill SHALL be available at user scope so it applies in every project
