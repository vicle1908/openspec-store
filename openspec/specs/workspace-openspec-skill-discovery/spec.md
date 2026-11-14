# workspace-openspec-skill-discovery Specification

## Purpose
Defines canonical shared Agent Skill ownership, cross-repository discovery, product-native skill surfaces, and evidence-backed synchronization across the multi-repository workspace.

## Requirements

### Requirement: Shared Agent Skills SHALL be discoverable across independent repositories

The workspace SHALL maintain shared Agent Skills in canonical skill roots under `~/Developer/.agents/skills/`, where each skill root contains `SKILL.md`. Container directories without a root `SKILL.md` MUST NOT be counted as skills. Standard-compatible agents running inside independent workspace Git repositories SHALL discover the selected shared skills through supported repository or user-level `.agents/skills` locations without requiring copied shared skill directories under product-specific configuration roots. Pi SHALL be treated as a covered standard-compatible agent.

When a workspace skill root is exposed for user-scope discovery, the entry at `~/.agents/skills/<skill-name>` SHALL be a link resolving to the canonical workspace skill root. For agents whose native user-scope loader reads a dedicated profile skill directory rather than `~/.agents/skills/` (including Claude Code at `~/.claude/skills/<skill-name>` and Hermes at `~/.hermes/skills/<skill-name>`), only manifest-selected workspace skill roots SHALL be exposed as user-scope links resolving to `~/Developer/.agents/skills/<skill-name>`, without enabling broad project trust or blanket `external_dirs` scanning. User-scope entries MUST NOT hold content duplicated from a workspace skill root. A skill with no workspace counterpart MAY exist as a real directory in `~/.agents/skills` and SHALL be preserved.

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

#### Scenario: Selected Hermes user-scope links expose workspace skills without blanket trust

- **GIVEN** `~/Developer` is not a Git root and `~/Developer/.hermes/skills/` is not loaded by Hermes when running in nested repositories or untrusted directories
- **WHEN** manifest-selected workspace skills (such as the six `ponytail*` skills) are synchronized for Hermes user-scope discovery
- **THEN** `~/.hermes/skills/<skill-name>` SHALL resolve as a link to `~/Developer/.agents/skills/<skill-name>` for only the manifest-selected skills
- **AND** synchronization SHALL NOT configure blanket `external_dirs` or broad project trust, and SHALL preserve existing non-colliding Hermes, Grok, and Goose skill entries

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

### Requirement: Skill provenance and discovery SHALL be independently verifiable

The workspace SHALL distinguish registry-tracked skills, generated OpenSpec artifacts, repository-specific skills, locally managed shared skills, and global installations. Consistency claims MUST be backed by structural inventory, comparison of `~/Developer/skills-lock.json` and its `~/Developer/.agents/skills-lock.json` replica, native agent loader or invocation probes, synchronization checks, focused OpenSpec validation, and Git-diff review.

#### Scenario: Lockfile coverage is reported accurately

- **GIVEN** project and global `npx skills` lockfiles cover only subsets of discovered skill roots
- **WHEN** skill provenance is audited
- **THEN** the audit SHALL report tracked and untracked roots separately
- **AND** discovery by `npx skills list` MUST NOT be presented as registry provenance

#### Scenario: Native agent probes reject filesystem-search fallbacks

- **GIVEN** a shared skill is selected for Claude, Codex, or Hermes discovery
- **WHEN** a fresh read-only session or native loader probe evaluates that skill
- **THEN** the verification SHALL inspect native catalog or loader output for native loading evidence
- **AND** a result obtained by searching the filesystem manually MUST NOT count as native discovery

#### Scenario: Unrelated dirty state is preserved

- **GIVEN** workspace repositories contain pre-existing or unrelated source, Graphify, GitNexus, or generated-file changes
- **WHEN** skill setup is reconciled
- **THEN** only skill-setup-owned files SHALL be changed, staged, or committed
- **AND** unrelated dirty state SHALL remain untouched and be reported separately

#### Scenario: Skills CLI agent list output is not accepted as native host discovery

- **GIVEN** `skills list` or `npx skills list` attributes a project skill to an agent based on workspace directory layout
- **WHEN** cross-agent discovery is verified
- **THEN** `skills list` output SHALL be treated as file-layout inventory only and MUST NOT be accepted as proof that the target host agent natively loads the skill
- **AND** verification SHALL require fresh native catalog or loader evidence from the host agent runtime

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

### Requirement: Shared Agent Skills SHALL be self-contained and modularly packaged

Shared Agent Skills in canonical skill roots under `~/Developer/.agents/skills/` SHALL be self-contained, encapsulating their own execution scripts, operational documentation, and templates rather than depending on ambient machine tools or undocumented external shell scripts. When a skill executes automated commands, it SHALL bundle executable CLI scripts under a `scripts/` directory with explicit argument handling and error boundaries. Complex or secondary reference documentation SHALL be separated into `references/` subfiles to optimize system prompt injection overhead.

#### Scenario: A skill bundles portable execution scripts and reference documentation
- **GIVEN** an agent skill wraps automated verification or execution workflows
- **WHEN** the skill root is inspected
- **THEN** it SHALL contain an executable CLI script under `scripts/`
- **AND** detailed failure taxonomies or manuals SHALL be isolated under `references/`

#### Scenario: A skill provides structured machine-readable CLI interfaces
- **GIVEN** a bundled execution script within a skill
- **WHEN** invoked with `--json`
- **THEN** it SHALL emit valid, machine-readable JSON summarizing operation success, execution details, and diagnostic violations
- **AND** it SHALL exit non-zero when violations are detected

### Requirement: Shared Agent Skills SHALL conform to progressive disclosure and frontmatter standards

Every shared skill `SKILL.md` SHALL start with standard YAML frontmatter defining `name`, `description`, and platform metadata. For internally authored shared skills, the `description` field MUST contain a self-contained, unambiguous trigger condition within the first 57 characters and SHALL NOT exceed 60 characters total, preventing prompt truncation in compact agent catalog listings, and the body of `SKILL.md` SHALL follow progressive disclosure with explicit invocation criteria, quick start commands, procedural workflows framed through native agent tools (`terminal`, `read_file`), negative counter-triggers ("When NOT to use"), and testable verification criteria. For upstream vendor-original skills installed and tracked via the official Skills CLI (`skills` / `npx skills`), `SKILL.md` files SHALL remain unmodified upstream copies whose YAML-decoded `description` scalar stays within the 1,024 UTF-8 byte `skill-index-hygiene` loader ceiling (800-byte advisory threshold), while workstation-specific installation-tier caveats are documented outside the vendor `SKILL.md` files.

#### Scenario: Frontmatter description defines a self-contained trigger within 57 characters
- **GIVEN** an internally authored shared agent skill's `SKILL.md`
- **WHEN** the frontmatter `description` is parsed
- **THEN** the active trigger phrase SHALL be fully self-contained within the first 57 characters
- **AND** the entire description string SHALL NOT exceed 60 characters

#### Scenario: Negative counter-triggers prevent inappropriate invocation
- **GIVEN** an internally authored shared agent skill's `When to Use` section
- **WHEN** evaluated by an autonomous agent
- **THEN** it SHALL explicitly define scenarios where the skill MUST NOT be used
- **AND** all command executions SHALL be framed through native agent tools

#### Scenario: Vendor-original upstream skill metadata is governed by the decoded 1,024-byte loader budget
- **GIVEN** an upstream vendor skill package (such as `DietrichGebert/ponytail` or `googleworkspace/cli`) is installed in `~/Developer/.agents/skills/` via the official Skills CLI
- **WHEN** its `SKILL.md` frontmatter `description` is decoded with a spec-compliant YAML parser supporting folded and literal block scalars
- **THEN** the vendor `SKILL.md` file SHALL remain unmodified upstream content rather than being rewritten to the 60-character internal authoring limit
- **AND** the decoded `description` UTF-8 byte length SHALL be verified against the 1,024-byte maximum (and 800-byte advisory threshold) without regex line truncation

### Requirement: Official Google Workspace agent skills SHALL be maintained via npx skills

The workspace SHALL maintain official Google Workspace Agent Skills (`gws-*`) sourced from upstream `googleworkspace/cli` via `npx skills` in canonical skill roots under `~/Developer/.agents/skills/`, with symlinks established under `~/Developer/.claude/skills/` for Claude Code and state tracked in `~/Developer/.agents/skills-lock.json`. Each skill root contains an official `SKILL.md` specifying command syntax, parameters, and output contracts for `/opt/homebrew/bin/gws`.

#### Scenario: Agent discovers official Google Workspace Calendar skill
- **GIVEN** an agent operates within an independent workspace repository
- **WHEN** the agent invokes or searches for Google Workspace calendar capabilities
- **THEN** the agent SHALL discover `gws-calendar` in `.agents/skills/`
- **AND** the skill entry SHALL reference `/opt/homebrew/bin/gws` subcommands with structured JSON output

#### Scenario: User-scope synchronization exposes official GWS skills
- **GIVEN** `gws-calendar` is registered in `codex-user-skill-manifest.txt`
- **WHEN** `sync-workspace-agent-skills.py` executes
- **THEN** `~/.agents/skills/gws-calendar` SHALL be created as a link to `~/Developer/.agents/skills/gws-calendar`
- **AND** no duplicate copy SHALL be created in product-specific configuration roots

### Requirement: Official Google Workspace skills SHALL support upstream updates via npx skills update

Official Google Workspace skills tracked in `~/Developer/.agents/skills-lock.json` SHALL support recurring automated synchronization against upstream releases using `npx skills update`.

#### Scenario: Updating skills brings latest upstream enhancements
- **WHEN** `npx skills update` runs in `~/Developer/`
- **THEN** the skill manager SHALL query upstream `googleworkspace/cli` for changes
- **AND** updated `SKILL.md` definitions SHALL be synchronized into `.agents/skills/` and `.claude/skills/` with refreshed lockfile hashes

### Requirement: Multi-hop OpenSpec symlink ownership is preserved across workspace and user skill roots

Workspace skill synchronization SHALL classify workspace and user skill symlinks as managed whenever either their parent-resolved immediate link target or their fully resolved canonical target lies within a declared managed target root, ensuring deselected or broken multi-hop OpenSpec links are pruned even under symlinked macOS `/tmp` or `/var` roots.

#### Scenario: Deselected multi-hop Claude or Codex OpenSpec link is pruned
- **GIVEN** `~/Developer/.claude/skills/<name>`, `~/.claude/skills/<name>`, or `~/.agents/skills/<name>` (including isolated runs under symlinked `/tmp` or `/var` roots) is a symlink pointing through an intermediate symlink (`platform/openspec-store/.claude/skills/<name>` or `~/Developer/.agents/skills/<name>`) whose canonical target lies in `platform/openspec-store/.agents/skills/`
- **WHEN** `<name>` is no longer in the desired OpenSpec skill set or its intermediate/canonical target is removed
- **THEN** workspace skill synchronization `--check` SHALL report `<name>` as a managed removal rather than ignoring it or leaving a broken unmanaged link
- **AND** normal synchronization SHALL unlink `<name>` cleanly without touching unmanaged user-authored links
