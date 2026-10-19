# workspace-openspec-skill-discovery Specification

## MODIFIED Requirements

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
