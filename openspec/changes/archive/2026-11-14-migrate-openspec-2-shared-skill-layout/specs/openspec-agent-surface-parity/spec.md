# openspec-agent-surface-parity Delta Specification

## MODIFIED Requirements

### Requirement: TDT skills use one reviewed OpenSpec release contract

All 12 canonical OpenSpec workflow `SKILL.md` files in `platform/openspec-store` SHALL live once under `.agents/skills/openspec-*` with matching `metadata.generatedBy` provenance from the installed official OpenSpec CLI release (`2.0.0` or newer), tracked in `.agents/skills/.openspec-target` and linked via relative symlinks for `own-files` tools.

#### Scenario: Complete skill set is refreshed
- **WHEN** the OpenSpec agent surface in `platform/openspec-store` is prepared for activation under OpenSpec `2.0.0+`
- **THEN** all 12 canonical OpenSpec skills under `platform/openspec-store/.agents/skills/openspec-*` SHALL match the installed `2.0.0+` workflow contracts and report identical `metadata.generatedBy`
- **AND** `.agents/skills/.openspec-target` SHALL record the configured tool set retaining `claude own-files` (`claude own-files`, `codex`, `factory`, `junie`, `kilocode`, `kiro own-files`, `pi`, `qoder`) with zero deprecated `/opsx:*` command-shim invocations

#### Scenario: Mixed version is found
- **WHEN** any OpenSpec `SKILL.md` in `platform/openspec-store` reports a stale `metadata.generatedBy` version or retains a divergent physical copy in a per-tool folder
- **THEN** parity verification SHALL fail and agent-driven apply, sync, single archive, and bulk archive MUST remain gated until reconciled

#### Scenario: Linked and direct tools share the single canonical copy
- **WHEN** `.claude/skills/openspec-*` and `.kiro/skills/openspec-*` are inspected in `platform/openspec-store`
- **THEN** each of the 24 entries SHALL be a relative directory symlink (`../../.agents/skills/openspec-<skill>`) resolving to the corresponding canonical `.agents/skills/openspec-<skill>` directory
- **AND** every other `.<dir>/skills` directory in `platform/openspec-store` (outside `.agents/skills` and declared `own-files` link directories) SHALL hold zero `openspec-*` physical copies or duplicate links

### Requirement: Legacy command wrappers retire after replacement proof

All generated `/opsx:*` and `opsx-*` command, workflow, and prompt wrappers in `platform/openspec-store` and their 24 managed symlinks under `~/Developer/.claude/commands/opsx/` and `~/.claude/commands/opsx/` SHALL remain retired once all 12 `2.0.0+` `openspec-*` skills are valid and discoverable.

#### Scenario: Replacements pass
- **WHEN** all 12 `openspec-*` skills report `metadata.generatedBy` `2.0.0` (or newer) in `.agents/skills/openspec-*` and pass workspace skill synchronization verification
- **THEN** `openspec update` SHALL leave zero generated command, workflow, or prompt files in `platform/openspec-store`
- **AND** workspace skill synchronization SHALL keep `~/Developer/.claude/commands/opsx/` and `~/.claude/commands/opsx/` pruned (`claude_commands=0`)

#### Scenario: Replacement is missing
- **WHEN** any of the 12 canonical `openspec-*` replacement skills is absent or invalid in `.agents/skills` or `.claude/skills`
- **THEN** activation MUST stop and workspace skill synchronization `--check` SHALL exit non-zero

### Requirement: Cross-surface activation is deterministic

Activation SHALL require generator-version parity across `platform/openspec-store/.agents/skills/openspec-*`, valid `.openspec-target` and `own-files` relative symlinks, zero orphaned manual split files inside generated skill directories, and a clean workspace skill synchronization `--check` exit (`0`).

#### Scenario: Parity and indexes pass
- **WHEN** all 12 OpenSpec skills pass `2.0.0+` generator parity in `.agents/skills/openspec-*`, `.claude/skills/openspec-*` and `.kiro/skills/openspec-*` resolve via relative symlinks, legacy `/opsx:*` wrappers remain retired, and workspace skill synchronization `--check` exits `0`
- **THEN** the runtime migration SHALL mark shared-layout skills-only agent-driven apply, sync, single archive, and bulk archive active across Codex, Claude Code, OMP, Hermes, Pi, and OpenCode

#### Scenario: Separately owned index remains stale
- **WHEN** workflow content is regenerated in `platform/openspec-store` but workspace/user symlinks or `.skill-snapshots/current/` report drift
- **THEN** workspace skill synchronization `--check` SHALL exit non-zero
- **AND** activation MUST wait until workspace skill synchronization reconciles links and snapshot checks pass

### Requirement: Emptied OpenSpec command directories are pruned while non-OpenSpec and tool-skill directories stay intact

`platform/openspec-store` SHALL remove emptied OpenSpec command directories and retired per-host OpenSpec physical skill copies while preserving active non-OpenSpec tool runtimes and tracked non-OpenSpec skill symlink trees.

#### Scenario: Emptied command directories are pruned cleanly
- **WHEN** `platform/openspec-store` is reconciled to OpenSpec `2.0.0+` shared skill layout
- **THEN** emptied command directories (`.claude/commands/opsx`, `.agents/workflows`, `.factory/commands`, `.junie/commands`, `.kilocode/workflows`, `.kiro/prompts`, `.pi/prompts`, `.qoder/commands/opsx`) SHALL be absent
- **AND** directories containing active non-OpenSpec tool assets or tracked symlinks (`.opencode/`, `.agent/skills`, `.goose/skills`, `.zencoder/skills`) SHALL remain intact and unmodified

#### Scenario: Retired per-host OpenSpec copies are removed without disturbing Bright Data links
- **WHEN** OpenSpec `2.0.0+` removes the 60 redundant physical `openspec-*/SKILL.md` copies from `.factory/skills`, `.junie/skills`, `.kilocode/skills`, `.pi/skills`, and `.qoder/skills`
- **THEN** all non-linked `.<dir>/skills` directories in `platform/openspec-store` (including `.factory/skills`, `.junie/skills`, `.kilocode/skills`, `.pi/skills`, `.qoder/skills`, `.agent/skills`, `.goose/skills`, and `.zencoder/skills`) SHALL contain zero `openspec-*` entries
- **AND** existing non-OpenSpec skill symlinks (`brightdata-cli`, `data-feeds`, `search`) inside those directories SHALL remain intact and unbroken
