## MODIFIED Requirements

### Requirement: Cross-agent skills ecosystem manifest reconciliation

The system SHALL regenerate Graphify platform skills across Pi, OpenCode, and Copilot, update user skill manifests with all unmapped skills, and ensure `sync-workspace-agent-skills.py` exits cleanly with code 0.

#### Scenario: Skills manifests are reconciled and verified

- **WHEN** the skills reconciliation phase executes
- **THEN** `graphify install --platform <platform>` SHALL be executed for `pi`, `opencode`, and `copilot`
- **AND** all 24 missing skills SHALL be declared in `codex-user-skill-manifest.txt` and `claude-user-skill-manifest.txt`
- **AND** `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` SHALL exit with returncode 0

#### Scenario: Undeclared user-scope links are declared rather than deleted

- **WHEN** user-scope fanout links exist whose names are absent from the codex manifest
- **THEN** each SHALL be declared in `config/codex-user-skill-manifest.txt` so the curation is explicit
- **AND** reconciliation SHALL NOT delete a resolvable fanout link merely because it is undeclared

## ADDED Requirements

### Requirement: Canonical skill store entries resolve to readable content

Every entry in the canonical store `~/Developer/.agents/skills/` SHALL resolve to a readable `SKILL.md` containing parseable frontmatter. A self-referential or dangling symlink SHALL be reported as a broken entry.

#### Scenario: Broken entries are reported

- **WHEN** canonical-root verification runs and an entry is a self-referential or dangling symlink
- **THEN** the entry SHALL be reported as broken
- **AND** verification SHALL exit non-zero

#### Scenario: A repair restores real content

- **WHEN** a skill previously recorded as a broken entry is restored
- **THEN** `~/Developer/.agents/skills/<skill>/SKILL.md` SHALL exist as a regular readable file with parseable frontmatter
- **AND** the entry SHALL no longer be reported as broken

#### Scenario: Unrecoverable skills are restored from an authoritative source

- **WHEN** a broken skill is recoverable from a declared upstream source
- **THEN** it SHALL be restored from that source
- **AND** when no upstream source exists, it SHALL be restored from an authoritative local backup copy rather than deleted

#### Scenario: Entry points use the canonical filename casing

- **WHEN** a canonical entry resolves its `SKILL.md` on a case-insensitive filesystem
- **THEN** the on-disk filename SHALL use the canonical `SKILL.md` casing rather than a variant
- **AND** a store-wide scan SHALL report no entry whose on-disk casing differs from the canonical name

#### Scenario: Non-official plugin directories do not shadow skill entry points

- **WHEN** a canonical entry contains a directory that would cause an agent to treat the entry as a plugin container
- **THEN** that directory SHALL be reported as a malformed entry, because it stops the catalog walk before `SKILL.md`
- **AND** a directory not part of the Agent Skills layout and absent from upstream sources SHALL be removed rather than retained

#### Scenario: Undiscoverable entries fail verification

- **WHEN** verification runs against entries that resolve but are not discoverable
- **THEN** it SHALL name each affected entry and its defect
- **AND** verification SHALL exit non-zero so the scheduled maintenance step fails

### Requirement: User-scope fanout links resolve to canonical content

Each entry in the user-scope fanout directory `~/.agents/skills/` SHALL resolve to the corresponding canonical skill or to an agent-owned skill root, so that agents whose discovery depends on user scope reach workspace skills regardless of working directory.

#### Scenario: Fanout entries resolve from any working directory

- **WHEN** an agent resolves a declared user-scope skill entry
- **THEN** that entry SHALL resolve to a readable `SKILL.md`
- **AND** resolution SHALL NOT depend on the process working directory

#### Scenario: User-scope coverage survives leaving the workspace directory

- **WHEN** an agent enumerates skills from a working directory outside the workspace root
- **THEN** skills that are only reachable through project scope SHALL be absent, as the official project scope is working-directory-relative
- **AND** skills declared in user scope SHALL remain reachable

#### Scenario: Unresolved fanout entries are detected

- **WHEN** a user-scope fanout entry does not resolve to readable content
- **THEN** verification SHALL report it as broken
- **AND** reconciliation SHALL NOT report success while it remains unresolved

### Requirement: Scheduled maintenance fails closed on unresolved skill links

The scheduled skills maintenance step SHALL treat any unresolved canonical or fanout skill link as a failure condition and SHALL NOT report success while such links remain.

#### Scenario: Broken links fail the maintenance run

- **WHEN** the scheduled skills parity step runs and one or more skill links are unresolved
- **THEN** the step SHALL report failure
- **AND** the overall maintenance run SHALL NOT conclude with a success status

#### Scenario: Reconciliation that does not resolve the failure still fails

- **WHEN** the scheduled step attempts reconciliation and unresolved links remain afterward
- **THEN** re-verification SHALL report failure
- **AND** the overall maintenance run SHALL NOT conclude with a success status

#### Scenario: Clean state passes the maintenance run

- **WHEN** the scheduled skills parity step runs and no skill link is unresolved
- **THEN** the step SHALL report success
