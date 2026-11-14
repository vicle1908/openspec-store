# workspace-openspec-skill-discovery Delta Specification

## ADDED Requirements

### Requirement: Multi-hop OpenSpec symlink ownership is preserved across workspace and user skill roots

Workspace skill synchronization SHALL classify workspace and user skill symlinks as managed whenever either their parent-resolved immediate link target or their fully resolved canonical target lies within a declared managed target root, ensuring deselected or broken multi-hop OpenSpec links are pruned even under symlinked macOS `/tmp` or `/var` roots.

#### Scenario: Deselected multi-hop Claude or Codex OpenSpec link is pruned
- **GIVEN** `~/Developer/.claude/skills/<name>`, `~/.claude/skills/<name>`, or `~/.agents/skills/<name>` (including isolated runs under symlinked `/tmp` or `/var` roots) is a symlink pointing through an intermediate symlink (`platform/openspec-store/.claude/skills/<name>` or `~/Developer/.agents/skills/<name>`) whose canonical target lies in `platform/openspec-store/.agents/skills/`
- **WHEN** `<name>` is no longer in the desired OpenSpec skill set or its intermediate/canonical target is removed
- **THEN** workspace skill synchronization `--check` SHALL report `<name>` as a managed removal rather than ignoring it or leaving a broken unmanaged link
- **AND** normal synchronization SHALL unlink `<name>` cleanly without touching unmanaged user-authored links

## MODIFIED Requirements

### Requirement: Product-native skill surfaces MUST preserve distinct capabilities without shared-content drift

Product-native directories MUST retain host-specific configuration without copying shared skills into `~/.agents/skills` or `~/.pi/agent/skills`. Claude-native OpenSpec skills SHALL load via `.claude/skills/openspec-*` resolving through OpenSpec `2.0.0+` shared `.agents/skills/openspec-*` canonical directories (`claude_commands=0`), while `.codex/` MUST retain Codex configuration, roles, hooks, memories, and system skills.

#### Scenario: Claude loads its native OpenSpec workflow

- **GIVEN** Claude Code starts inside an independent workspace repository after OpenSpec `2.0.0+` shared-skill migration
- **WHEN** the user explicitly invokes `/openspec-explore` (or another canonical `/openspec-<skill>` workflow)
- **THEN** Claude Code SHALL load the corresponding native skill through `.claude/skills/openspec-*` resolving to the canonical `platform/openspec-store/.agents/skills/openspec-*` `SKILL.md`
- **AND** all 12 generated OpenSpec skills SHALL be present with zero managed `/opsx:*` command shims (`claude_commands=0`)

#### Scenario: Managed command symlinks are pruned while non-managed files remain untouched

- **GIVEN** `platform/openspec-store/.claude/commands/opsx/` is absent under OpenSpec `2.0.0+` skills-only installation (`claude_commands=0`)
- **WHEN** workspace skill synchronization reconciles `~/Developer/.claude/commands/opsx/` and `~/.claude/commands/opsx/`
- **THEN** symlinks targeting `platform/openspec-store/.claude/commands/opsx/` SHALL be removed, emptied `commands/opsx/` directories SHALL be removed rather than recreated, and subsequent `--check` runs SHALL report zero `missing-destination` conflicts when `commands/opsx/` is absent
- **AND** any non-symlink or user-authored file outside `managed_target_roots` SHALL remain untouched

#### Scenario: A product-specific skill root duplicates standard discovery

- **GIVEN** a product-specific root such as `~/.pi/agent/skills` contains entries that are also available through `~/.agents/skills`
- **WHEN** the skill surfaces are audited
- **THEN** the duplicate entries MUST be reported, including whether any entry is unique to the product-specific root
- **AND** removal SHALL proceed only when no entry would be lost

#### Scenario: Codex-specific governance remains intact

- **GIVEN** shared skills are exposed as symlinks under `~/.agents/skills`
- **WHEN** the Codex workspace configuration is audited
- **THEN** `config.toml`, custom roles, hooks, automation, memories, security constraints, and system or Codex-specific skills MUST remain intact
- **AND** repository ownership, read-only role, non-overlapping-writer, credential-protection, and Context7 policies MUST remain documented

#### Scenario: Existing global installations are preserved

- **GIVEN** `~/.agents/skills/` contains real directories installed through global `npx skills`
- **WHEN** workspace skill links are synchronized
- **THEN** the synchronizer MUST preserve those real directories and their lockfile provenance
- **AND** a workspace skill name collision with a real global installation MUST fail verification instead of overwriting content
