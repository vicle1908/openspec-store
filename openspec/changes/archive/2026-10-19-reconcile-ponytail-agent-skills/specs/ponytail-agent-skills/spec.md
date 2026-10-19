# Spec Delta

## ADDED Requirements

### Requirement: Skills-tier operator guidance outside vendor files

The workspace SHALL provide operator documentation outside vendor skill directories defining Ponytail's skills-only installation tier, including host-appropriate standalone skill invocation (`/ponytail*` in hosts exposing slash skill commands and `$ponytail*` in Codex without the `$ponytail:<skill>` plugin namespace), absence of automatic hook activation or `band` statusline output, exclusion of `/plugin update ponytail`, and preservation of Claude Code's installation authority.

#### Scenario: Operator guidance clarifies standalone skill invocation and omitted plugin features
- **WHEN** an operator or agent consults workspace documentation for `DietrichGebert/ponytail` usage
- **THEN** the non-vendor guidance SHALL document that `ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, and `ponytail-help` are invoked as standalone skills using `/ponytail*` in hosts that expose slash skill commands and `$ponytail*` in Codex (without the `$ponytail:<skill>` plugin namespace), without claiming every host exposes identical slash commands
- **AND** it SHALL state that automatic hook-driven activation, `ponytail-map.js` regex scanning, `band` statusline output, and Pi/OMP extensions are intentionally absent in the skills-only tier

#### Scenario: Update guidance forbids plugin marketplace commands and preserves vendor files
- **WHEN** operator documentation describes how to refresh Ponytail skills or inspect `ponytail-help` capabilities
- **THEN** it SHALL direct updates through the official Skills CLI (`skills update` / `npx skills update`) rather than `/plugin update ponytail` without altering Claude Code's installation authority
- **AND** canonical `~/Developer/.agents/skills/ponytail*/SKILL.md` files SHALL remain unedited upstream copies

### Requirement: Independent local byte integrity and recoverable Ponytail snapshots

The workspace MUST verify installed `~/Developer/.agents/skills/ponytail*/` bytes independently of Skills CLI `up to date` output or lockfile `computedHash` values and SHALL maintain recoverable current and previous accepted snapshots containing actual allowlisted skill files, validated lockfile copies, content digests, and independently verified source revisions.

#### Scenario: Local byte tampering is detected despite CLI up-to-date status
- **WHEN** `skills update` reports that `DietrichGebert/ponytail` is already up to date because upstream `computedHash` matches `~/Developer/skills-lock.json`, but a local `~/Developer/.agents/skills/ponytail*/SKILL.md` file differs from the accepted snapshot digest
- **THEN** local integrity verification SHALL report a content mismatch and refuse to mark the refresh as accepted-success
- **AND** restoration SHALL recover the exact allowlisted skill files from the accepted snapshot payload rather than treating a recorded hash alone as a rollback mechanism

#### Scenario: Provenance records exact commit SHA only when independently verified
- **WHEN** an accepted Ponytail snapshot record is written after a verified installation or refresh
- **THEN** the provenance record SHALL store the full 40-character upstream Git commit SHA only when independently verified from the fetched source revision
- **AND** when the CLI refresh path does not expose a verifiable commit SHA, the provenance record SHALL record `"unknown"` rather than fabricating a commit hash

### Requirement: Immutable archive preservation and corrective verification evidence

The workspace MUST preserve archived change `2026-10-19-adopt-ponytail-agent-skills` at commit `c09d952a` without modification and SHALL record corrective verification evidence using full YAML-decoded frontmatter descriptions, native Hermes loader discovery, independent local byte checks, and isolated refresh failure lifecycle probes.

#### Scenario: YAML frontmatter budget is measured from decoded scalar content
- **WHEN** corrective verification measures `DietrichGebert/ponytail` `SKILL.md` `description` lengths against the 1,024 UTF-8 byte `skill-index-hygiene` ceiling
- **THEN** the check SHALL parse the YAML frontmatter so multi-line folded scalars (`>-`) include their final lines rather than truncating via line-based regex
- **AND** upstream vendor descriptions within the 1,024 UTF-8 byte budget SHALL be accepted without applying the 60-character internal skill authoring limit

#### Scenario: Archived change remains untouched while active evidence records lifecycle proofs
- **WHEN** corrective evidence is recorded for Ponytail adoption and refresh behavior
- **THEN** all files under `openspec/changes/archive/2026-10-19-adopt-ponytail-agent-skills/` from commit `c09d952a` SHALL remain byte-for-byte unchanged
- **AND** the corrective evidence SHALL include native Hermes skill catalog verification, local byte integrity verification, and isolated probes covering healthy refresh, unreachable upstream, partial failure, and mirror reconciliation

## MODIFIED Requirements

### Requirement: Canonical Ponytail skill installation and lockfile tracking

The workspace SHALL maintain the six official `DietrichGebert/ponytail` skills (`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`) under `~/Developer/.agents/skills/`, treat `~/Developer/skills-lock.json` as the sole writable project lockfile authority, and publish `~/Developer/.agents/skills-lock.json` only as a verified compatibility mirror that preserves unrelated entries.

#### Scenario: Official skills are installed and recorded in workspace lockfiles
- **WHEN** `/opt/homebrew/bin/skills add DietrichGebert/ponytail --skill '*' --agent universal claude-code hermes-agent -y` is executed in `~/Developer/` and verified acceptance completes
- **THEN** `~/Developer/.agents/skills/` SHALL contain direct child directories `ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, and `ponytail-help`, each with an uppercase `SKILL.md`
- **AND** `~/Developer/skills-lock.json` SHALL record each skill as the CLI's sole writable project registry with `"source": "DietrichGebert/ponytail"`, `"sourceType": "github"`, and `"skillPath": "skills/<name>/SKILL.md"`
- **AND** `~/Developer/.agents/skills-lock.json` SHALL be generated as a read-only compatibility mirror only after canonical skill bytes and lockfile entries pass verification

#### Scenario: Exact skillPath disambiguates OpenClaw duplicate paths during updates
- **WHEN** `skills update -y` clones `DietrichGebert/ponytail` with `fullDepth: true` and discovers both `skills/<name>/SKILL.md` and `.openclaw/skills/<name>/SKILL.md`
- **THEN** the recorded `"skillPath": "skills/<name>/SKILL.md"` SHALL disambiguate each skill via `exactPathDisambiguates`
- **AND** `skills update -y` SHALL emit zero `Multiple current paths match` warnings for `DietrichGebert/ponytail`

#### Scenario: Mirror publication preserves unrelated entries and fails closed on collisions
- **WHEN** `~/Developer/.agents/skills-lock.json` is reconciled from `~/Developer/skills-lock.json` after a verified refresh or validated no-op check
- **THEN** all existing unrelated skill entries in `~/Developer/skills-lock.json` SHALL be preserved in the generated mirror
- **AND** if an unapproved skill name or source collision or canonical byte integrity failure is detected, mirror publication SHALL fail closed and leave the last accepted mirror and snapshot state intact

#### Scenario: Manual native CLI update requires explicit acceptance check before replica update
- **WHEN** an operator runs a manual native `skills update` or `npx skills update` command in `~/Developer/` that mutates `~/Developer/skills-lock.json`
- **THEN** `~/Developer/.agents/skills-lock.json` SHALL NOT be treated as a second independent writer target
- **AND** an explicit post-update acceptance check MUST verify canonical `~/Developer/.agents/skills/ponytail*/` bytes and decoded YAML frontmatter before publishing the updated compatibility replica and rotating the accepted snapshot

### Requirement: Multi-agent manifest declaration and user-scope symlink fanout

All six `ponytail*` skill slugs SHALL be declared in user-skill manifests under `platform/openspec-store/config/` so `sync-workspace-agent-skills.py` reconciles selected user-scope symlinks into `~/.agents/skills/`, `~/.claude/skills/`, and `~/.hermes/skills/` targeting `~/Developer/.agents/skills/<name>` without enabling blanket `external_dirs` or workspace project-root trust.

#### Scenario: Workspace skill synchronizer links Ponytail skills cleanly
- **WHEN** `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` is executed after manifest declaration and reconciliation
- **THEN** the command SHALL exit with status code `0` and report `malformed_entries=0`, `conflicts=0`, and `broken=0`
- **AND** `~/.agents/skills/<name>`, `~/.claude/skills/<name>`, and `~/.hermes/skills/<name>` for all six `ponytail*` skills SHALL resolve as symlinks to `/Users/androidteam/Developer/.agents/skills/<name>`

#### Scenario: Workspace project agent mirrors and Codex isolation are preserved
- **WHEN** `DietrichGebert/ponytail` skills are installed and synchronized in `~/Developer/`
- **THEN** `~/Developer/.claude/skills/ponytail*` and `~/Developer/.hermes/skills/ponytail*` SHALL resolve as relative symlinks (`../../.agents/skills/<name>`)
- **AND** `~/Developer/.codex/skills/` SHALL remain restricted to `.system/` and `migrate-to-codex` without duplicate shared skill copies

#### Scenario: Hermes native loader discovers selected user-scope Ponytail skills
- **WHEN** Hermes enumerates its native skill catalog without adding `~/Developer/.agents/skills` to `external_dirs` or trusting `~/Developer` as a Git project root
- **THEN** all six `ponytail*` skills SHALL be discoverable through Hermes's user-scope loader via `~/.hermes/skills/<name>`
- **AND** verification SHALL require native Hermes loader catalog evidence rather than treating `skills list` inventory output as host discovery proof

#### Scenario: Existing Grok and Goose skill links are preserved without broad rollout
- **WHEN** user-scope skill synchronization runs for the selected manifests
- **THEN** existing `~/.grok/skills/ponytail*` and `~/.config/goose/skills/ponytail*` symlinks SHALL remain intact
- **AND** synchronization SHALL NOT perform an unapproved rollout to additional workstation agent directories

### Requirement: Unmodified upstream content for idempotent npx skills updates

The canonical `~/Developer/.agents/skills/ponytail*/SKILL.md` files MUST remain unmodified upstream copies so on-demand `npx skills update` (or `skills update -y`) and scheduled daily maintenance (`shb-schedule` `step_skills_refresh` and `workstation-daily-update.sh` Stage 11) refresh them cleanly without local merge conflicts or frontmatter validation failures.

#### Scenario: On-demand and scheduled skill updates succeed idempotently
- **WHEN** `skills update -y` or `/opt/homebrew/bin/skills update ponytail ponytail-review ponytail-audit ponytail-debt ponytail-gain ponytail-help -y` executes in `~/Developer/` with reachable upstream
- **THEN** the CLI SHALL check `https://github.com/DietrichGebert/ponytail.git` against `~/Developer/skills-lock.json` and exit with status code `0`
- **AND** every refreshed `SKILL.md` YAML-decoded frontmatter description SHALL remain within the 1,024 UTF-8 byte `skill-index-hygiene` ceiling before `~/Developer/.agents/skills-lock.json` and accepted snapshots are updated

#### Scenario: Upstream unreachable during refresh degrades gracefully
- **WHEN** `https://github.com/DietrichGebert/ponytail.git` is unreachable or `skills update` exits non-zero (such as exit code `1`) during a scheduled refresh
- **THEN** existing `~/Developer/.agents/skills/ponytail*/SKILL.md` files, user-scope symlinks, and the last accepted `~/Developer/.agents/skills-lock.json` mirror SHALL remain intact or be restored from the accepted snapshot if partial mutation occurred
- **AND** the refresh stage SHALL classify the non-zero CLI exit or unreachable upstream as a degraded failure outcome without aborting subsequent maintenance stages
