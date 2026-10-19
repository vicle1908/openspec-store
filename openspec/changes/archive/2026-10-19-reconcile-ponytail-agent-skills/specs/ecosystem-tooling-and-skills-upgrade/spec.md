# Spec Delta

## ADDED Requirements

### Requirement: Verified lockfile compatibility mirror publication and manual update acceptance

The maintenance pipeline SHALL treat `~/Developer/skills-lock.json` as the sole writable Skills CLI project lockfile and SHALL publish `~/Developer/.agents/skills-lock.json` only as a verified compatibility replica after canonical skill bytes, YAML frontmatter, and collision checks pass, including after manual native CLI updates or validated no-op runs.

#### Scenario: Verified refresh publishes compatibility replica while preserving unrelated entries
- **WHEN** a scheduled or on-demand skill refresh completes and canonical skill files, YAML frontmatter budgets, and user-scope symlink parity pass verification
- **THEN** `~/Developer/.agents/skills-lock.json` SHALL be generated as a byte-identical compatibility replica of the verified `~/Developer/skills-lock.json`
- **AND** all existing unrelated skill entries in `~/Developer/skills-lock.json` SHALL be preserved without truncation

#### Scenario: Validated no-op run reconciles stale compatibility replica
- **WHEN** a refresh run reports zero content updates (`refreshed=0`, `failed=0`) and `~/Developer/.agents/skills-lock.json` is stale relative to `~/Developer/skills-lock.json`
- **THEN** the pipeline SHALL verify canonical skill bytes and lockfile collision rules before reconciling `~/Developer/.agents/skills-lock.json`
- **AND** the stale compatibility replica SHALL be updated only after that validation succeeds

#### Scenario: Manual native CLI update requires explicit post-check acceptance before replica publication
- **WHEN** a manual native `skills update` or `skills add` execution updates `~/Developer/skills-lock.json` outside the scheduled wrapper
- **THEN** `~/Developer/.agents/skills-lock.json` SHALL remain an unpromoted replica rather than a second direct writer target
- **AND** explicit post-update acceptance verification MUST validate canonical skill bytes, YAML frontmatter, and source/name collision rules before publishing the updated replica

#### Scenario: Unapproved collision or failed integrity check blocks replica publication
- **WHEN** post-refresh validation detects a missing or corrupted canonical `SKILL.md`, a frontmatter violation, or an unapproved skill name or source collision in `~/Developer/skills-lock.json`
- **THEN** the pipeline SHALL refuse to overwrite `~/Developer/.agents/skills-lock.json` or advance the accepted snapshot state
- **AND** the maintenance run SHALL report a degraded integrity failure

### Requirement: Recoverable current and previous accepted skill snapshots

The skill refresh workflow SHALL maintain bounded current and previous accepted snapshots containing actual allowlisted skill files, validated lockfile copies, content SHA-256 digests, and independently verified source revisions so that partial or corrupt refreshes can restore owned skill bytes without relying on lockfile hashes alone.

#### Scenario: Accepted refresh rotates current and previous snapshots with full file payloads
- **WHEN** a skill refresh and post-refresh integrity check succeed for allowlisted skills
- **THEN** the previously accepted snapshot SHALL be retained as the `previous` accepted snapshot and the newly verified state SHALL be recorded as the `current` accepted snapshot
- **AND** each snapshot SHALL store actual allowlisted skill file contents, validated `skills-lock.json` copies, and SHA-256 file digests rather than hashes alone

#### Scenario: Corrupt or partial refresh restores allowlisted skill bytes from accepted snapshot
- **WHEN** a refresh mutates allowlisted skill files in `~/Developer/.agents/skills/` and then fails CLI execution or post-refresh integrity verification
- **THEN** the workflow SHALL report the failed refresh and the detected on-disk mutations
- **AND** it SHALL restore only the exact allowlisted skill files from the last accepted snapshot or leave the stage visibly degraded without claiming accepted-success

## MODIFIED Requirements

### Requirement: Skill content refresh outcomes are reported

Both the DBOS (`step_skills_refresh`) and shell (`workstation-daily-update.sh`) refresh entry points SHALL classify `skills update` output with identical outcome semantics distinguishing `drift`, `refreshed`, `already_current`, `path_ambiguous`, and `failed`, preferring numeric update summaries over per-skill lines, treating zero updates as already current, and rejecting unrecognized output as a failure.

#### Scenario: Outcome summary is recorded
- **WHEN** the refresh stage completes in either the DBOS workflow or the shell maintenance script
- **THEN** the maintenance telemetry and log SHALL record how many entries were refreshed, already current, skipped as path-ambiguous, and failed using identical classification rules

#### Scenario: Drift is visible without application
- **WHEN** the refresh stage detects that upstream content differed from the local canonical store during an update
- **THEN** it SHALL report that entries were refreshed (`drift > 0`, `refreshed > 0`)
- **AND** the report SHALL be distinguishable from a run where no entry changed (`drift=0`, `refreshed=0`)

#### Scenario: Numeric update summary takes precedence over per-skill lines without double-counting
- **WHEN** `skills update -y` prints per-skill `✓ Updated <name>` lines together with a numeric summary such as `Updated N skill(s)`
- **THEN** both the DBOS and shell parsers SHALL record `refreshed=N` from the numeric summary rather than summing per-skill lines and summary tokens
- **AND** when `Updated 0 skills` is reported, both parsers SHALL record `drift=0` and `refreshed=0`

#### Scenario: Unrecognized or empty CLI output is classified as a refresh failure
- **WHEN** `skills update -y` produces empty output or text containing no recognized update, already-current, or path-ambiguous summary pattern
- **THEN** both the DBOS and shell entry points SHALL classify the run with `failed=1` and a degraded status
- **AND** neither entry point SHALL default unrecognized output to `already_current=1`

### Requirement: Drift is observable before content is replaced

Because the official Skills CLI lacks a non-mutating dry-run flag, the refresh stage SHALL NOT claim that `skills update` output proves pre-mutation drift; `--check` mode SHALL inspect local registry and snapshot state without invoking `skills update`, while apply mode SHALL report observed content changes honestly from post-refresh CLI output and pre-refresh vs post-refresh snapshot comparison.

#### Scenario: Drift check does not mutate
- **WHEN** the maintenance job runs in `--check` mode to evaluate skill refresh state
- **THEN** it SHALL inspect canonical skill entries, lockfile mirror parity, and accepted snapshot digests without invoking `skills update` or replacing any skill content
- **AND** when apply mode runs `skills update -y`, the refresh stage SHALL describe any reported drift as a post-update observation rather than claiming pre-mutation drift detection

#### Scenario: Unchanged content is reported as already current
- **WHEN** the refresh stage runs in apply mode and `skills update -y` reports `All project skills are up to date`, `N project skill(s) already up to date`, or `Updated 0 skills` with verified local bytes
- **THEN** it SHALL report that no entry changed (`drift=0`, `refreshed=0`, `already_current > 0`)
- **AND** the reported outcome SHALL be distinguishable from a run that replaced content or failed

### Requirement: Path-ambiguous upstream skills are informational

When upstream publishes the same skill at multiple paths and the Skills CLI emits `Multiple current paths match`, both the DBOS and shell refresh stages SHALL classify the resulting skip as an informational `path_ambiguous` condition without suppressing `already_current` or `refreshed` counts for other skills and SHALL NOT treat it as stale, broken, or failing.

#### Scenario: Multi-path upstream entry is reported as informational
- **WHEN** upstream publishes one skill at more than one path and `skills update -y` emits `Multiple current paths match`
- **THEN** both the DBOS and shell refresh stages SHALL report the entry in `path_ambiguous`
- **AND** the run SHALL NOT classify that entry as stale, broken, or failed

#### Scenario: Path-ambiguous entry does not fail the maintenance run
- **WHEN** the only unrefreshed entry in a run is path-ambiguous and all other checks pass
- **THEN** the maintenance run SHALL still conclude successfully with `already_current` and `path_ambiguous` both preserved in the summary

### Requirement: Refresh failures degrade without masking

An unreachable upstream, non-zero Skills CLI exit status (such as exit `1` or timeout `124`), or partial refresh failure SHALL be reported as a degraded stage outcome, SHALL preserve any parsed per-run counts and mutation observations, and SHALL NOT publish the compatibility lockfile mirror or report a silent success.

#### Scenario: Unreachable upstream is reported
- **WHEN** upstream content cannot be reached or `skills update -y` exits non-zero (such as exit code `1`) during the scheduled refresh
- **THEN** the refresh SHALL report `failed >= 1` for the affected invocation
- **AND** the maintenance run SHALL report the refresh stage as `DEGRADED` rather than fully successful

#### Scenario: A failed refresh does not abort unrelated stages
- **WHEN** the refresh stage fails or exits non-zero for one or more entries
- **THEN** the remaining maintenance stages SHALL still execute

#### Scenario: Transient network failure is distinguishable from drift
- **WHEN** the refresh fails because of a network condition or timeout rather than a completed content update
- **THEN** the reported outcome SHALL identify a refresh failure (`failed >= 1`) rather than a clean refreshed or already-current result

#### Scenario: Partial refresh failure preserves parsed telemetry and blocks mirror publication
- **WHEN** `skills update -y` updates or checks a subset of skills before failing or exiting non-zero
- **THEN** the refresh stage SHALL retain any parsed `refreshed`, `already_current`, and `path_ambiguous` counts alongside `failed >= 1` and report any detected on-disk mutations
- **AND** the stage SHALL NOT publish `~/Developer/.agents/skills-lock.json` or mark the snapshot state as accepted-success, restoring exact owned snapshots for allowlisted skills or remaining visibly degraded

### Requirement: Refresh lockfile integrity is not asserted from an internal digest

The refresh stage SHALL NOT treat the lockfile `computedHash` digest or CLI `up to date` output as authoritative proof of local content integrity or drift, and SHALL verify local on-disk skill bytes and pre/post content digests before accepting a refresh.

#### Scenario: Internal digest does not gate the refresh
- **WHEN** the refresh stage evaluates whether an entry needs refreshing
- **THEN** it SHALL NOT compare the lockfile `computedHash` digest against a locally computed content digest as its drift signal

#### Scenario: Content comparison uses the pulled content
- **WHEN** the refresh stage determines whether an entry changed or remained intact
- **THEN** it SHALL base that determination on the actual on-disk content digests before and after the refresh rather than lockfile `computedHash` metadata alone

#### Scenario: CLI up-to-date output does not bypass local byte verification
- **WHEN** `skills update -y` reports that skills are already up to date based on lockfile `computedHash` comparison
- **THEN** the refresh stage SHALL still verify canonical on-disk `SKILL.md` readability, YAML frontmatter validity, and accepted snapshot digests before publishing `~/Developer/.agents/skills-lock.json`
