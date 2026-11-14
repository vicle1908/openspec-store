# openspec-runtime-governance Delta Specification

## MODIFIED Requirements

### Requirement: Released version authority and immediate package availability

TDT SHALL select an official `@fission-ai/openspec` release (`2.0.0` or newer `@latest`) at `~/.npm-global/bin/openspec` without enforcing a minimum package age, stopping on registry-integrity failure and preferring verified release source over unpinned docs.

#### Scenario: Exact release is immediately eligible
- **WHEN** `@fission-ai/openspec@2.0.0` (or a newer `@latest` release) is published and registry-resolvable
- **THEN** the migration SHALL exercise `openspec update --dry-run --json` read-only before mutating repository assets
- **AND** the globally responding executable at `~/.npm-global/bin/openspec` SHALL report the target release version before any generated asset is accepted

#### Scenario: Time-based restriction is encountered
- **WHEN** a package command is blocked only because the published version is considered too new
- **THEN** the operator-approved minimum-age restriction SHALL be removed or disabled
- **AND** the exact reviewed package SHALL be retried without substituting an unreviewed version

#### Scenario: Registry integrity fails
- **WHEN** the exact package cannot be resolved or fails a registry-integrity check for a reason other than age
- **THEN** the migration MUST stop before installation or generation
- **AND** it MUST NOT fall back to a floating or unreviewed package

#### Scenario: Documentation sources disagree
- **WHEN** Context7 or OpenSpec `main` describes a key, command, or topology not present in the official installed release source at its verified target commit
- **THEN** TDT SHALL use the released contract matching `openspec --version` and record the other material as non-normative

### Requirement: Stable workflow profile during regeneration

The workstation OpenSpec configuration (`~/.config/openspec/config.json`) SHALL maintain `"profile": "custom"`, `"defaultStore": "openspec-store"`, and all 12 canonical workflows (`propose`, `explore`, `new`, `continue`, `apply`, `ff`, `sync`, `archive`, `bulk-archive`, `verify`, `onboard`, `update`) without the retired `"delivery"` key during `2.0.0+` regeneration.

#### Scenario: Update would change selected workflows
- **WHEN** preflight or post-update configuration differs from the 12-workflow custom profile or `defaultStore: "openspec-store"`
- **THEN** the migration SHALL stop activation and restore or explicitly reconcile the profile
- **AND** it SHALL NOT accept added or pruned workflows as incidental upgrade churn

#### Scenario: Core profile remains stable
- **WHEN** `openspec update /Users/androidteam/Developer/platform/openspec-store` regenerates tool assets under `"profile": "custom"` in OpenSpec `2.0.0+`
- **THEN** `.agents/skills/openspec-*` SHALL hold the single canonical set of all 12 workflow `SKILL.md` files stamped with `metadata.generatedBy` matching `openspec --version` alongside `.agents/skills/.openspec-target`
- **AND** `own-files` tools (`claude`, `kiro`) SHALL receive relative symlinks (`../../.agents/skills/openspec-*`) while redundant physical copies and unmodified generated command shims are removed

#### Scenario: Retired delivery setting is omitted
- **WHEN** `~/.config/openspec/config.json` is reconciled for OpenSpec `2.0.0+`
- **THEN** the retired `"delivery"` key SHALL be absent from `~/.config/openspec/config.json`
- **AND** synchronization checks MUST NOT fail when `"delivery"` is omitted

### Requirement: Generated and TDT-managed surfaces converge before activation

OpenSpec-managed skills in `platform/openspec-store` SHALL converge on the `2.0.0+` shared `.agents/skills/` canonical layout with `.openspec-target` and `own-files` relative symlinks, and workspace/user symlinks SHALL be reconciled before activation. Agent-driven apply, sync, single archive, and bulk archive MUST remain blocked if host-visible skills drift.

#### Scenario: Official surfaces are current but the TDT mirror is stale
- **WHEN** `platform/openspec-store` skill trees are updated to `2.0.0+` shared layout but `~/Developer/.agents/skills/openspec-*`, `~/Developer/.claude/skills/openspec-*`, `~/.agents/skills/openspec-*`, or `~/.claude/skills/openspec-*` still contain broken links, stale copies, or unpruned command links
- **THEN** workspace skill synchronization `--check` SHALL exit non-zero
- **AND** migration completion SHALL remain blocked until synchronization passes cleanly

#### Scenario: All host-visible surfaces converge
- **WHEN** all 12 OpenSpec skills in `platform/openspec-store/.agents/skills/openspec-*`, `.openspec-target` (retaining `claude own-files`), `own-files` symlinks (`.claude/skills/openspec-*`, `.kiro/skills/openspec-*`), and reconciled workspace/user symlink roots report matching `metadata.generatedBy` (`2.0.0+`) and `openspec update --dry-run --json` reports empty `changes`, `notes`, and `failures`
- **THEN** workspace skill synchronization `--check` SHALL exit `0` and mark agent workflow activation ready

### Requirement: Rollback is exact, scoped, and verifiable

The migration SHALL maintain a non-destructive rollback path that restores the pre-migration `~/.config/openspec/config.json` file, reverts `platform/openspec-store` generated skill, target-list, and symlink paths to their pre-migration Git revision if activation gates fail, and re-runs workspace skill synchronization without touching unrelated work.

#### Scenario: Runtime activation fails
- **WHEN** `openspec update`, workspace skill synchronization `--check`, unit tests, or strict OpenSpec validation fails during migration
- **THEN** the operator SHALL restore `~/.config/openspec/config.json`, checkout only the OpenSpec-managed paths in `platform/openspec-store`, and re-run workspace skill synchronization
- **AND** unrelated active changes and external workspace repositories SHALL remain untouched

#### Scenario: Rollback completes
- **WHEN** the prior global config, store skill/symlink paths, workspace symlinks, and strict validation baseline are restored
- **THEN** workspace skill synchronization `--check` and `openspec validate --all --store openspec-store` SHALL pass with zero failures and strict main-spec warnings SHALL NOT exceed the recorded pre-migration baseline (`160`)

### Requirement: Single-owner OpenSpec CLI executable resolution

The `openspec` CLI on `iosteam-mac-mini` SHALL resolve from a single authoritative installation (`~/.npm-global/bin/openspec`, `@fission-ai/openspec` `2.0.0` or newer) without a duplicate shadowed Homebrew `openspec` formula binary on `PATH`.

#### Scenario: Only one openspec binary exists on PATH
- **WHEN** `which -a openspec` and `openspec --version` are executed on `iosteam-mac-mini`
- **THEN** `which -a openspec` SHALL return only `/Users/androidteam/.npm-global/bin/openspec` reporting version `2.0.0` or newer

### Requirement: Automated OpenSpec CLI-to-skill generator convergence

Workspace skill synchronization SHALL verify OpenSpec `2.0.0+` shared-layout parity (`metadata.generatedBy` matching `openspec --version`, `.agents/skills/.openspec-target` retaining `claude own-files`, `own-files` relative symlinks, zero `openspec-*` entries in non-linked `.*/skills` folders, and empty `changes`/`notes`/`failures` from `openspec update --dry-run --json`) with isolated `HOME`/`XDG_CONFIG_HOME` overrides and exclusive lock serialization.

#### Scenario: Check mode reports OpenSpec skill generator drift without mutating files
- **WHEN** workspace skill synchronization runs in `--check` mode while `openspec --version` differs from `metadata.generatedBy` in `platform/openspec-store/.agents/skills/openspec-*`
- **THEN** the check SHALL report OpenSpec skill generator drift with both version strings and exit non-zero
- **AND** it SHALL NOT modify files in `platform/openspec-store` or workspace skill directories

#### Scenario: Reconcile mode updates OpenSpec skill trees under exclusive file lock
- **WHEN** workspace skill synchronization runs without `--check` while `DISABLE_UPDATES` is unset and OpenSpec generator version or shared-layout topology drifts
- **THEN** synchronization SHALL acquire an exclusive lock on `/tmp/openspec-skill-sync.lock`, execute `openspec update /Users/androidteam/Developer/platform/openspec-store`, and reconcile workspace/user symlinks
- **AND** a subsequent `--check` run SHALL confirm `metadata.generatedBy` equals `openspec --version`, shared-layout topology is intact, and exit `0`

#### Scenario: Update pause policy suppresses OpenSpec skill regeneration
- **WHEN** `DISABLE_UPDATES` is active during `workstation-daily-update.sh` or workspace skill synchronization
- **THEN** `openspec update` SHALL NOT be executed and `platform/openspec-store` skill trees SHALL remain unmodified

#### Scenario: Unmodified custom command file blocks silent deletion during reconciliation
- **WHEN** `openspec update` encounters a hand-edited command or skill file in a tool folder that does not match a released OpenSpec fingerprint
- **THEN** `openspec update --dry-run --json` SHALL report that condition in `notes` (such as `legacy-artifacts` or `edited-skills`) while keeping user-owned content on disk
- **AND** workspace skill synchronization (in both `--check` and post-`update` reconcile modes) SHALL surface the note and fail closed rather than ignoring or deleting user-owned content

#### Scenario: Check mode rejects broken own-files symlinks or dry-run drift
- **WHEN** workspace skill synchronization runs in `--check` mode and `.agents/skills/.openspec-target` is missing or lacks `claude own-files`, an `own-files` entry under `.claude/skills/openspec-*` or `.kiro/skills/openspec-*` is not a valid symlink to `../../.agents/skills/openspec-*`, any non-linked `.<dir>/skills` folder contains an `openspec-*` entry, or `openspec update --dry-run --json` reports non-empty `changes`, `notes`, or `failures`
- **THEN** the check SHALL report the specific OpenSpec 2.0 topology violation and exit non-zero without mutating disk state

#### Scenario: Isolated config and home overrides do not touch live global config
- **WHEN** workspace skill synchronization is invoked with `--home-dir` or `--openspec-config`
- **THEN** child `openspec` commands SHALL run with isolated `HOME` and `XDG_CONFIG_HOME` environment variables pointing to the overridden location rather than reading or modifying `/Users/androidteam/.config/openspec/config.json`
