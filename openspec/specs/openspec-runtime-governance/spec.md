# openspec-runtime-governance Specification

## Purpose

Define how TDT selects, upgrades, generates, validates, activates, and rolls back the OpenSpec runtime and its agent workflow surfaces without corrupting shared planning state or allowing stale instructions to control cross-repository work.

## Requirements

### Requirement: Released version authority and immediate package availability

TDT SHALL select an official `@fission-ai/openspec` release (`1.17.0` or newer `@latest`) at `~/.npm-global/bin/openspec` without enforcing a minimum package age, stopping on registry-integrity failure and preferring verified release source over unpinned docs.

#### Scenario: Exact release is immediately eligible
- **WHEN** `@fission-ai/openspec@1.17.0` (or a newer `@latest` release) is published and registry-resolvable
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

### Requirement: Dirty-state and ownership preflight

The migration SHALL inventory repository, ignored, and user-global OpenSpec surfaces before mutation, SHALL classify the owner of every affected path, and MUST stop when an overlapping dirty path or unresolved owner could be overwritten.

#### Scenario: Unrelated OpenSpec work is present
- **WHEN** `~/Developer` contains pre-existing changes outside `upgrade-openspec-1-7-runtime`
- **THEN** the migration SHALL preserve and report them
- **AND** it SHALL proceed only if no planned generated or configuration path overlaps

#### Scenario: Path ownership is ambiguous
- **WHEN** a workflow file could be OpenSpec-generated, TDT-maintained, or user-authored and provenance cannot be established
- **THEN** the migration MUST NOT remove or regenerate that file
- **AND** it SHALL request ownership resolution

### Requirement: Stable workflow profile during regeneration

The workstation OpenSpec configuration (`~/.config/openspec/config.json`) SHALL maintain `"profile": "custom"`, `"delivery": "skills"`, `"defaultStore": "openspec-store"`, and all 12 canonical workflows (`propose`, `explore`, `new`, `continue`, `apply`, `ff`, `sync`, `archive`, `bulk-archive`, `verify`, `onboard`, `update`) throughout `1.17.0+` regeneration unless a separate approved change alters the workflow set.

#### Scenario: Update would change selected workflows
- **WHEN** preflight or post-update configuration differs from the 12-workflow custom profile or `defaultStore: "openspec-store"`
- **THEN** the migration SHALL stop activation and restore or explicitly reconcile the profile
- **AND** it SHALL NOT accept added or pruned workflows as incidental upgrade churn

#### Scenario: Core profile remains stable
- **WHEN** `openspec update /Users/androidteam/Developer/platform/openspec-store` regenerates tool assets under `"profile": "custom"` and `"delivery": "skills"`
- **THEN** each active configured tool adapter SHALL receive all 12 workflow `SKILL.md` files stamped with `metadata.generatedBy` matching `openspec --version`
- **AND** `reconcileCommandFiles()` SHALL remove unmodified generated `/opsx:*` and `opsx-*` command, workflow, and prompt shims while preserving any user-modified files
### Requirement: Codex skills-only migration is ordered and authorized

The migration SHALL establish and verify project-local Codex skills for every selected workflow before removing any OpenSpec-managed global Codex prompt, SHALL use `$openspec-*` as the Codex invocation contract, and MUST obtain explicit authorization before deleting user-global files.

#### Scenario: Replacement skills are ready
- **WHEN** all six selected `~/.agents/skills/openspec-*` files report generation by 1.7.0 and pass content inspection
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

OpenSpec-managed skill trees in `platform/openspec-store` SHALL be regenerated by the verified `1.17.0+` CLI, and workspace/user symlinks SHALL be reconciled via `scripts/sync-workspace-agent-skills.py`. Agent-driven apply, sync, single archive, and bulk archive MUST remain blocked if host-visible OpenSpec skills disagree on `metadata.generatedBy`, skill-native invocation syntax, or inline archive semantics.

#### Scenario: Official surfaces are current but the TDT mirror is stale
- **WHEN** `platform/openspec-store` skill trees are updated to `1.17.0+` but `~/Developer/.agents/skills/openspec-*` or `~/.claude/skills/openspec-*` still contain broken links, stale copies, or unpruned managed `/opsx:*` command links
- **THEN** `sync-workspace-agent-skills.py --check` SHALL exit non-zero
- **AND** migration completion SHALL remain blocked until synchronization passes cleanly

#### Scenario: All host-visible surfaces converge
- **WHEN** all 12 OpenSpec skills across `platform/openspec-store` and reconciled workspace/user symlink roots report matching `metadata.generatedBy` (`1.17.0+`), skill-native invocations, and zero managed `/opsx:*` command shims
- **THEN** `sync-workspace-agent-skills.py --check` SHALL exit `0` and mark agent workflow activation ready
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

The migration SHALL require `openspec validate --all --store openspec-store` and `openspec validate --changes --strict --store openspec-store` to exit `0` with zero failures, and MUST NOT increase strict warning-failing main specs above the recorded pre-migration baseline (`160` specs).

#### Scenario: Pre-existing main-spec debt remains unchanged
- **WHEN** `openspec validate --all --store openspec-store`, `openspec validate --changes --strict --store openspec-store`, and `openspec validate --all --strict --store openspec-store` run after regenerating skills and syncing delta specs
- **THEN** standard validation (`462` items) and strict change validation SHALL exit `0` with zero failures, and strict main-spec warning failures SHALL NOT exceed `160`
- **AND** `openspec store doctor` and `openspec doctor --store openspec-store --json` SHALL report healthy status

#### Scenario: New regression appears
- **WHEN** an active change fails, a touched main spec fails, or any previously passing main spec fails strict validation
- **THEN** activation MUST stop and the regression SHALL be resolved or rolled back before archival
### Requirement: Existing nearest-root topology remains authoritative

The workstation SHALL use the registered standalone OpenSpec store `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`) and machine-global `defaultStore: "openspec-store"` as the authoritative central planning root across multi-repository workflows, without relying on a workspace-root `~/Developer/openspec` compatibility symlink.

#### Scenario: Repository lacks a local OpenSpec symlink
- **WHEN** a command runs from a TDT or workspace repository without its own local `openspec/` root
- **THEN** it SHALL resolve `/Users/androidteam/Developer/platform/openspec-store` with `source: "store"` and `store_id: "openspec-store"`
- **AND** `openspec doctor --store openspec-store --json` SHALL report `"healthy": true`

#### Scenario: Default store is considered
- **WHEN** `openspec config list --json` is inspected on the workstation
- **THEN** `defaultStore` SHALL equal `"openspec-store"`

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

The migration SHALL maintain a non-destructive rollback path that restores the pre-migration `~/.config/openspec/config.json` delivery setting, reverts `platform/openspec-store` generated skill/command paths to their pre-migration Git revision if activation gates fail, and re-runs `sync-workspace-agent-skills.py` without touching unrelated dirty repositories or active changes.

#### Scenario: Runtime activation fails
- **WHEN** `openspec update`, `sync-workspace-agent-skills.py --check`, unit tests, or strict OpenSpec validation fails during migration
- **THEN** the operator SHALL restore `~/.config/openspec/config.json`, checkout only the OpenSpec-managed paths in `platform/openspec-store`, and re-run `sync-workspace-agent-skills.py`
- **AND** unrelated active changes and external workspace repositories SHALL remain untouched

#### Scenario: Rollback completes
- **WHEN** the prior delivery config, store skill/command trees, workspace symlinks, and strict validation baseline are restored
- **THEN** `sync-workspace-agent-skills.py --check` and `openspec validate --all --store openspec-store` SHALL pass with zero failures and strict main-spec warnings SHALL NOT exceed the recorded pre-migration baseline (`160`)

### Requirement: Single-owner OpenSpec CLI executable resolution

The `openspec` CLI on `iosteam-mac-mini` SHALL resolve from a single authoritative installation (`~/.npm-global/bin/openspec`, `@fission-ai/openspec` `1.17.0` or newer) without a duplicate shadowed Homebrew `openspec` formula binary on `PATH`.

#### Scenario: Only one openspec binary exists on PATH
- **WHEN** `which -a openspec` and `openspec --version` are executed on `iosteam-mac-mini`
- **THEN** `which -a openspec` SHALL return only `/Users/androidteam/.npm-global/bin/openspec` reporting version `1.17.0` or newer

### Requirement: Automated OpenSpec CLI-to-skill generator convergence
`sync-workspace-agent-skills.py` SHALL compare active `openspec --version` against `metadata.generatedBy` in `platform/openspec-store` OpenSpec skills, report drift without mutating files in `--check` mode, and serialize `openspec update` plus symlink reconciliation under `/tmp/openspec-skill-sync.lock` when updates are enabled.

#### Scenario: Check mode reports OpenSpec skill generator drift without mutating files
- **WHEN** `sync-workspace-agent-skills.py --check` (or `workstation-daily-update.sh --check`) runs while `openspec --version` differs from `metadata.generatedBy` in `platform/openspec-store` OpenSpec skills
- **THEN** the check SHALL report OpenSpec skill generator drift with both version strings and exit non-zero
- **AND** it SHALL NOT modify files in `platform/openspec-store` or workspace skill directories

#### Scenario: Reconcile mode updates OpenSpec skill trees under exclusive file lock
- **WHEN** `sync-workspace-agent-skills.py` runs without `--check` (invoked directly, by `workstation-daily-update.sh` in apply mode, or by `shb-schedule` `step_skills_refresh` after `--check` fails) while `DISABLE_UPDATES` is unset and `openspec --version` differs from `metadata.generatedBy`
- **THEN** `sync-workspace-agent-skills.py` SHALL acquire an exclusive `fcntl.flock` on `/tmp/openspec-skill-sync.lock`, execute `openspec update /Users/androidteam/Developer/platform/openspec-store`, and reconcile workspace/user symlinks
- **AND** a subsequent `sync-workspace-agent-skills.py --check` SHALL confirm `metadata.generatedBy` equals `openspec --version` and exit `0`

#### Scenario: Update pause policy suppresses OpenSpec skill regeneration
- **WHEN** `DISABLE_UPDATES` is active during `workstation-daily-update.sh` or `sync-workspace-agent-skills.py`
- **THEN** `openspec update` SHALL NOT be executed and `platform/openspec-store` skill trees SHALL remain unmodified

#### Scenario: Unmodified custom command file blocks silent deletion during reconciliation
- **WHEN** `openspec update` runs under `"delivery": "skills"` and `reconcileCommandFiles()` encounters a hand-edited command file that does not match a released OpenSpec fingerprint
- **THEN** the CLI SHALL keep that file on disk and report it in `kept` or `unchecked`
- **AND** the migration or maintenance runner SHALL surface the kept path rather than deleting user-owned content
### Requirement: Archive immutability verification and forward-remediated range auditing

`scripts/validate-archive-readiness.py --range` SHALL fail closed if a commit in the audited range modifies files inside an already-archived directory under `openspec/changes/archive/` unless recorded in a sanctioned forward-remediation ledger, and SHALL resolve historical missing-evidence violations via active corrective evidence rather than mutating old archives.

#### Scenario: Historical missing evidence and post-archive edit accounted via forward remediation
- **WHEN** `python3 scripts/validate-archive-readiness.py --range HEAD~35..HEAD --store /Users/androidteam/Developer/platform/openspec-store --strict` is executed after forward-remediating `2026-10-20-reconcile-dev-tooling-and-hermes-runtime` (`804a8968`) and `2026-10-20-upgrade-omniroute-to-v3-8-52` (`a3eb1fda`)
- **THEN** the validator SHALL verify the corrective evidence ledger without requiring further edits to pre-existing `openspec/changes/archive/` directories
- **AND** any new unapproved post-archive modification in future commits SHALL fail with exit code `4`
