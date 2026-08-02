# release-audit-playbook Specification

## Purpose
TBD - created by archiving change ecc-harness-alignment. Update Purpose after archive.
## Requirements
### Requirement: The playbook SHALL be runnable end-to-end by a single agent

The system SHALL execute the 4-phase audit (Discovery, Static-Diff, Usage-Evidence, Output/Verify) without human intervention between phases.

#### Scenario: One-agent execution

- **WHEN** an audit is invoked via `/opsx:apply ecc-harness-alignment` on a new ECC release
- **THEN** the agent SHALL complete all four phases and produce updated `audit/` artifacts

### Requirement: The playbook SHALL be diffable between releases

The system SHALL support a release-over-release diff showing which entries changed classification.

#### Scenario: Release diff

- **WHEN** an audit completes for ECC release `vN+1` after release `vN`
- **THEN** the system SHALL produce a diff between `audit/<surface>-disposition.md` from both releases, highlighting: new entries, removed entries, reclassified entries

### Requirement: The playbook SHALL produce a `next-actions.md` artifact

The system SHALL generate `audit/next-actions.md` listing what changes the next ECC release will require.

#### Scenario: Next-actions content

- **WHEN** the audit completes
- **THEN** `audit/next-actions.md` SHALL include: any `disabled-default` hooks that became `keep-default` due to evidence, any `redundant-to-tdt-skill` TDT skills that need an OpenSpec change to formalize the precedence, any new v2.0 features recommended for adoption

### Requirement: The playbook SHALL be versioned with TDT-meta

The system SHALL store the playbook at `tdt-meta/docs/ecc-harness/playbook.md`.

#### Scenario: Playbook location

- **WHEN** the agent looks for the playbook
- **THEN** the path SHALL resolve to `tdt-meta/docs/ecc-harness/playbook.md` and the file SHALL exist with a `Last updated` header

### Requirement: The playbook SHALL link to the source OpenSpec change

The system SHALL include a pointer from `tdt-meta/docs/ecc-harness/playbook.md` back to `tdt-meta/openspec/changes/ecc-harness-alignment/` so future audits reference the same methodology.

#### Scenario: Back-reference

- **WHEN** a future agent reads the playbook
- **THEN** the playbook SHALL link to the OpenSpec change that produced it, so methodology updates stay traceable

### Requirement: The playbook SHALL be re-runnable within 30 minutes on a routine release

The system SHALL complete a routine (non-ECC-major-version-bump) audit in under 30 minutes of agent time.

#### Scenario: Time budget

- **WHEN** the audit runs against a release that added < 10 new entries per surface
- **THEN** the agent SHALL complete all four phases within 30 minutes, with most time spent in Phase 2 (usage evidence)

### Requirement: The playbook SHALL handle ECC major-version bumps explicitly

The system SHALL require a separate OpenSpec change when ECC ships a major-version bump (e.g., 2.x → 3.x), instead of attempting an in-place audit.

#### Scenario: Major-version fork

- **WHEN** `~/.claude/plugins/cache/everything-claude-code/ecc/<version>` shows a major version bump
- **THEN** the playbook SHALL refuse to run in-place and SHALL instruct the agent to create a new OpenSpec change (e.g., `ecc-harness-alignment-v3`) referencing this playbook

### Requirement: The playbook SHALL be cross-linked from `tdt-meta/AGENTS.md`

The system SHALL add a reference in `tdt-meta/AGENTS.md` "Skills" section pointing to `tdt-meta/docs/ecc-harness/playbook.md`.

#### Scenario: AGENTS.md cross-link

- **WHEN** a reader of `tdt-meta/AGENTS.md` reaches the Skills section
- **THEN** the section SHALL include a pointer to the ECC alignment playbook so future contributors know how to re-audit on the next release

