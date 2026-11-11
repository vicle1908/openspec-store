# Spec Delta

## ADDED Requirements

### Requirement: Emptied OpenSpec command directories are pruned while non-OpenSpec and tool-skill directories stay intact
`platform/openspec-store` SHALL remove emptied OpenSpec command directories left after skills-only reconciliation while preserving active non-OpenSpec tool runtimes and tracked tool symlink trees.

#### Scenario: Emptied command directories are pruned cleanly
- **WHEN** `platform/openspec-store` is reconciled to OpenSpec `1.17.0+` skills-only delivery
- **THEN** emptied command directories (`.claude/commands/opsx`, `.agents/workflows`, `.factory/commands`, `.junie/commands`, `.kilocode/workflows`, `.kiro/prompts`, `.pi/prompts`, `.qoder/commands/opsx`) SHALL be absent
- **AND** directories containing active non-OpenSpec tool assets or tracked symlinks (`.opencode/`, `.agent/skills`, `.goose/skills`, `.zencoder/skills`) SHALL remain intact and unmodified

## MODIFIED Requirements

### Requirement: TDT skills use one reviewed OpenSpec release contract

All OpenSpec workflow `SKILL.md` files across active `platform/openspec-store` adapter trees (`.agents/skills`, `.claude/skills`, `.factory/skills`, `.junie/skills`, `.kilocode/skills`, `.kiro/skills`, `.pi/skills`, `.qoder/skills`) SHALL derive from the same installed official OpenSpec CLI release (`1.17.0` or newer) and SHALL record matching `metadata.generatedBy` provenance.

#### Scenario: Complete skill set is refreshed
- **WHEN** the OpenSpec agent surface in `platform/openspec-store` is prepared for activation
- **THEN** all 12 canonical OpenSpec skills across all 8 active adapter trees (96 `SKILL.md` files) SHALL match the installed `1.17.0+` workflow contracts and report identical `metadata.generatedBy`
- **AND** no host-visible OpenSpec skill SHALL remain at `1.12.0` or advertise deprecated `/opsx:*` command-shim invocations

#### Scenario: Mixed version is found
- **WHEN** any OpenSpec `SKILL.md` in `platform/openspec-store` reports a stale `metadata.generatedBy` version or retains an incompatible workflow section
- **THEN** parity verification SHALL fail and agent-driven apply, sync, single archive, and bulk archive MUST remain gated until reconciled

### Requirement: Legacy command wrappers retire after replacement proof

All 96 generated `/opsx:*` and `opsx-*` command, workflow, and prompt wrappers in `platform/openspec-store` and their 24 managed symlinks under `~/Developer/.claude/commands/opsx/` and `~/.claude/commands/opsx/` SHALL be retired once all 12 corresponding `1.17.0+` `openspec-*` skills are generated, valid, and discoverable via `.agents/skills` and `.claude/skills`.

#### Scenario: Replacements pass
- **WHEN** all 12 `openspec-*` skills report `metadata.generatedBy` `1.17.0` (or newer) and pass `sync-workspace-agent-skills.py` verification
- **THEN** `openspec update` under `"delivery": "skills"` SHALL remove all 96 unmodified generated command, workflow, and prompt files in `platform/openspec-store`
- **AND** `sync-workspace-agent-skills.py` SHALL prune the 24 managed command symlinks in `~/Developer/.claude/commands/opsx/` and `~/.claude/commands/opsx/` (`claude_commands=0`)

#### Scenario: Replacement is missing
- **WHEN** any of the 12 canonical `openspec-*` replacement skills is absent or invalid in `.agents/skills` or `.claude/skills`
- **THEN** command wrapper retirement MUST stop and `sync-workspace-agent-skills.py --check` SHALL exit non-zero

### Requirement: Cross-surface activation is deterministic

Activation SHALL require generator-version parity across `platform/openspec-store/.agents/skills/openspec-*` and `platform/openspec-store/.claude/skills/openspec-*`, zero orphaned manual split files inside generated skill directories, and a clean `sync-workspace-agent-skills.py --check` exit (`0`).

#### Scenario: Parity and indexes pass
- **WHEN** all 12 OpenSpec skills pass `1.17.0+` generator parity, orphaned `openspec-onboard/references/onboarding-walkthrough.md` files are removed, legacy `/opsx:*` wrappers are retired, and `sync-workspace-agent-skills.py --check` exits `0`
- **THEN** the runtime migration SHALL mark skills-only agent-driven apply, sync, single archive, and bulk archive active across Codex, Claude Code, OMP, Hermes, Pi, and OpenCode

#### Scenario: Separately owned index remains stale
- **WHEN** workflow content is regenerated in `platform/openspec-store` but workspace/user symlinks or `.skill-snapshots/current/` report drift
- **THEN** `sync-workspace-agent-skills.py --check` SHALL exit non-zero
- **AND** activation MUST wait until `sync-workspace-agent-skills.py` reconciles links and snapshot checks pass
