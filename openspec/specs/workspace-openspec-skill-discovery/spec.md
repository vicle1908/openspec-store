# workspace-openspec-skill-discovery Specification

## Purpose
Defines canonical shared Agent Skill ownership, cross-repository discovery, product-native skill surfaces, and evidence-backed synchronization across the multi-repository workspace.
## Requirements
### Requirement: Shared Agent Skills SHALL be discoverable across independent repositories

The workspace SHALL maintain shared Agent Skills in canonical skill roots under `~/Developer/.agents/skills/`, where each skill root contains `SKILL.md`. Container directories without a root `SKILL.md` MUST NOT be counted as skills. Standard-compatible agents running inside independent workspace Git repositories SHALL discover the selected shared skills through supported repository or user-level `.agents/skills` locations without requiring copied shared skill directories under product-specific configuration roots.

#### Scenario: Codex discovers OpenSpec from an independent repository

- **GIVEN** Codex starts inside a workspace Git repository that has no repository-local OpenSpec skill mirror
- **WHEN** the user explicitly invokes `$openspec-explore`
- **THEN** Codex SHALL load the selected skill through standard `.agents/skills` discovery
- **AND** the invocation SHALL NOT require a copied OpenSpec directory under `.codex/skills`

#### Scenario: Standard user-level links bridge independent Git roots

- **GIVEN** `~/Developer/.agents/skills/` is above each independent repository's Git root
- **WHEN** selected workspace skill roots are synchronized for user-scope discovery
- **THEN** `~/.agents/skills/<skill-name>` SHALL resolve to the canonical workspace skill root
- **AND** stale, broken, missing, or conflicting links MUST be reported by verification

#### Scenario: Skill inventory distinguishes containers from skills

- **GIVEN** the workspace collection contains directories with and without a root `SKILL.md`
- **WHEN** the collection is audited or synchronized
- **THEN** only directories containing a root `SKILL.md` SHALL be counted as skills
- **AND** container directories SHALL be reported separately

### Requirement: Product-native skill surfaces MUST preserve distinct capabilities without shared-content drift

Product-native directories MUST retain configuration or capabilities that are not provided by the shared Agent Skills surface. Claude-native OpenSpec skills and `/opsx:*` commands SHALL remain available through `.claude/`, while `.codex/` MUST retain Codex configuration, roles, hooks, automation, memories, system skills, and genuinely Codex-specific skills. Shared skill content MUST NOT be copied into `.codex/skills` when standard `.agents/skills` discovery has been verified.

#### Scenario: Claude loads its native OpenSpec workflow

- **GIVEN** Claude Code starts inside an independent workspace repository
- **WHEN** the user explicitly invokes an OpenSpec skill or `/opsx:*` command
- **THEN** Claude Code SHALL load the corresponding native skill or command through a supported `.claude` discovery path
- **AND** all twelve generated OpenSpec commands SHALL be present

#### Scenario: Codex-specific governance remains intact

- **GIVEN** shared skills are removed from `.codex/skills`
- **WHEN** the Codex workspace configuration is audited
- **THEN** `config.toml`, custom roles, hooks, automation, memories, security constraints, and system or Codex-specific skills MUST remain intact
- **AND** repository ownership, read-only role, non-overlapping-writer, credential-protection, and Context7 policies MUST remain documented

#### Scenario: Existing global installations are preserved

- **GIVEN** `~/.agents/skills/` contains real directories installed through global `npx skills`
- **WHEN** workspace skill links are synchronized
- **THEN** the synchronizer MUST preserve those real directories and their lockfile provenance
- **AND** a workspace skill name collision with a real global installation MUST fail verification instead of overwriting content

### Requirement: Skill provenance and discovery SHALL be independently verifiable

The workspace SHALL distinguish registry-tracked skills, generated OpenSpec artifacts, repository-specific skills, locally managed shared skills, and global installations. Consistency claims MUST be backed by structural inventory, lockfile comparison, native agent invocation probes, synchronization checks, focused OpenSpec validation, and Git-diff review.

#### Scenario: Lockfile coverage is reported accurately

- **GIVEN** project and global `npx skills` lockfiles cover only subsets of discovered skill roots
- **WHEN** skill provenance is audited
- **THEN** the audit SHALL report tracked and untracked roots separately
- **AND** discovery by `npx skills list` MUST NOT be presented as registry provenance

#### Scenario: Native agent probes reject filesystem-search fallbacks

- **GIVEN** a shared skill is selected for Claude or Codex discovery
- **WHEN** a fresh read-only session explicitly invokes that skill
- **THEN** the verification SHALL inspect output or logs for native loading evidence
- **AND** a result obtained by searching the filesystem manually MUST NOT count as native discovery

#### Scenario: Unrelated dirty state is preserved

- **GIVEN** workspace repositories contain pre-existing or unrelated source, Graphify, GitNexus, or generated-file changes
- **WHEN** skill setup is reconciled
- **THEN** only skill-setup-owned files SHALL be changed, staged, or committed
- **AND** unrelated dirty state SHALL remain untouched and be reported separately

