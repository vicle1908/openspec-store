# Spec Delta

## MODIFIED Requirements

### Requirement: Product-native skill surfaces MUST preserve distinct capabilities without shared-content drift

Product-native directories MUST retain host-specific configuration without copying shared skills into `~/.agents/skills` or `~/.pi/agent/skills`. Claude-native OpenSpec skills SHALL load via `.claude/skills/openspec-*` under skills-only delivery (`claude_commands=0`), while `.codex/` MUST retain Codex configuration, roles, hooks, memories, and system skills.

#### Scenario: Claude loads its native OpenSpec workflow

- **GIVEN** Claude Code starts inside an independent workspace repository after OpenSpec `1.17.0+` skills-only migration
- **WHEN** the user explicitly invokes `/openspec-explore` (or another canonical `/openspec-<skill>` workflow)
- **THEN** Claude Code SHALL load the corresponding native skill through `.claude/skills/openspec-*`
- **AND** all 12 generated OpenSpec skills SHALL be present with zero managed `/opsx:*` command shims (`claude_commands=0`)

#### Scenario: Managed command symlinks are pruned while non-managed files remain untouched

- **GIVEN** `platform/openspec-store/.claude/commands/opsx/` contains zero generated `.md` files under `"delivery": "skills"` (`claude_commands=0`)
- **WHEN** `sync-workspace-agent-skills.py` reconciles `~/Developer/.claude/commands/opsx/` and `~/.claude/commands/opsx/`
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
