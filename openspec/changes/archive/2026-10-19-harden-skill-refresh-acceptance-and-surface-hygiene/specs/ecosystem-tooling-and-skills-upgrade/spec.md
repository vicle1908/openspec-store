# Spec Delta

## MODIFIED Requirements

### Requirement: Verified lockfile compatibility mirror publication and manual update acceptance

The maintenance pipeline (across both `workstation-daily-update.sh` and `shb-schedule:step_skills_refresh`) SHALL treat `~/Developer/skills-lock.json` as the sole writable Skills CLI project lockfile and SHALL invoke `sync-workspace-agent-skills.py --accept-refresh` after healthy `skills update -y` runs (or `--recover-from-snapshot` on failure) before running `--check` parity verification.

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

#### Scenario: DBOS step_skills_refresh runs --accept-refresh before --check when skills update succeeds
- **WHEN** `shb-schedule:step_skills_refresh` runs `skills update -y` and `_classify_skills_refresh_output` reports `failed == 0`
- **THEN** `step_skills_refresh` SHALL invoke `sync-workspace-agent-skills.py --accept-refresh` to rotate `.skill-snapshots/{current,previous}/` and publish `~/Developer/.agents/skills-lock.json` before invoking `sync-workspace-agent-skills.py --check`
- **AND** if `--accept-refresh` or `skills update -y` fails, `step_skills_refresh` SHALL set `failed >= 1` and invoke `sync-workspace-agent-skills.py --recover-from-snapshot` when `current/manifest.json` exists
