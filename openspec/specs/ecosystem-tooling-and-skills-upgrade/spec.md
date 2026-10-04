# ecosystem-tooling-and-skills-upgrade Specification

## Purpose
Defines formal requirements, baseline snapshots, verification sentinels, validation criteria, and daily scheduled automation for upgrading and maintaining developer runtimes, coding agent engines, utility CLIs, Homebrew casks, and cross-agent skills manifests.

## Requirements

### Requirement: Baseline state preservation and recovery snapshotting

The upgrade automation SHALL capture full inventory snapshots of all installed Homebrew casks, global npm packages, and store-wide OpenSpec validation results before executing any package modifications.

#### Scenario: Pre-upgrade snapshots are recorded
- **WHEN** the upgrade pipeline initializes
- **THEN** it SHALL write the active Homebrew bundle and global npm package list to local backup files
- **AND** it SHALL record the full strict validation baseline of `openspec-store`.

### Requirement: Desktop application and Homebrew cask modernization

The system SHALL upgrade identified outdated Homebrew casks without disruption to background services, and verify that container runtimes and network daemons remain operational post-upgrade.

#### Scenario: Homebrew casks are upgraded and verified
- **WHEN** outdated casks (`copilot-cli`, `droid`, `zed`, `gcloud-cli`, `postman-cli`, `google-drive`, `lark`, `teamviewer`) are upgraded via `brew upgrade --cask`
- **THEN** the system SHALL invoke targeted cask upgrade commands
- **AND** `copilot-cli` SHALL report version 1.0.91 or higher
- **AND** `droid` SHALL report version 0.233.0 or higher
- **AND** `zed` SHALL report version 1.22.0 or higher
- **AND** `gcloud-cli` SHALL report version 587.0.0 or higher
- **AND** `postman-cli` SHALL report version 1.69.0 or higher
- **AND** `docker ps` SHALL respond and existing services remain operational.

### Requirement: Upstream Git Agent Repository Fast-Forward Alignment
Tracked core agent repositories in `platform/` (`platform/prime-agent`) SHALL track their canonical remote `origin/main` branch without unmerged divergence, fast-forwarding upstream release and bugfix commits while maintaining working tree cleanliness.

#### Scenario: Prime agent repository tracks origin/main
- **WHEN** `git -C platform/prime-agent fetch origin` reports upstream commits on `origin/main`
- **THEN** the branch SHALL be fast-forwarded to `origin/main`
- **AND** `git status` SHALL report working tree clean and up to date with `origin/main`

### Requirement: Developer utility CLIs and research tools alignment

The system SHALL upgrade global npm utility CLIs, align GitNexus to version `1.6.12` across all global prefixes, and update Graphify to version `0.9.68` via uv tool.

#### Scenario: Utility CLIs and intelligence tools are aligned
- **WHEN** utility CLIs are upgraded
- **THEN** `@brightdata/cli`, `@kilocode/cli`, `@qoder-ai/qodercli`, `codexuse-cli`, and `happy` SHALL be updated in `~/.npm-global`
- **AND** `gitnexus` SHALL be updated to `1.6.12` in `~/.npm-global`
- **AND** `graphifyy` SHALL be upgraded to `0.9.68` via `uv tool upgrade`.

### Requirement: Cross-agent skills ecosystem manifest reconciliation

The system SHALL regenerate Graphify platform skills across Pi, OpenCode, and Copilot, update user skill manifests with all unmapped skills, and ensure `sync-workspace-agent-skills.py` exits cleanly with code 0.

#### Scenario: Skills manifests are reconciled and verified
- **WHEN** the skills reconciliation phase executes
- **THEN** `graphify install --platform <platform>` SHALL be executed for `pi`, `opencode`, and `copilot`
- **AND** all 24 missing skills SHALL be declared in `codex-user-skill-manifest.txt` and `claude-user-skill-manifest.txt`
- **AND** `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` SHALL exit with returncode 0.

#### Scenario: Undeclared user-scope links are declared rather than deleted
- **WHEN** user-scope fanout links exist whose names are absent from the codex manifest
- **THEN** each SHALL be declared in `config/codex-user-skill-manifest.txt` so the curation is explicit
- **AND** reconciliation SHALL NOT delete a resolvable fanout link merely because it is undeclared.

### Requirement: Coding agent CLIs upgrade and headless probe verification

The system SHALL upgrade Claude Code, OpenAI Codex, OpenCode, Droid, and Pi extensions, and SHALL verify each agent through live headless PONG execution probes.

#### Scenario: Coding agents are upgraded and probed
- **WHEN** coding agent packages are upgraded
- **THEN** `claude` SHALL be updated via `claude update` to `2.1.283`
- **AND** `@openai/codex` (`0.157.0`) and `opencode-ai` (`1.18.32`) SHALL be installed in `~/.npm-global`
- **AND** `pi` plugins (`pi-subagents`, `pi-mcp-adapter`, `pi-web-access`, `pi-lens`, `pi-intercom`) SHALL be updated in `~/.npm-global`
- **AND** each agent SHALL successfully execute a non-interactive probe command verifying model passthrough.

### Requirement: OpenSpec store validation gate and zero-regression enforcement

The system SHALL upgrade the OpenSpec CLI to version `1.13.2` and SHALL execute a full store validation across all 400 specs to verify zero new validation failures or schema regressions.

#### Scenario: OpenSpec validator is upgraded and store validated
- **WHEN** `@fission-ai/openspec` is upgraded to `1.13.2` in `~/.npm-global`
- **THEN** the system SHALL execute `openspec validate --all --strict --store openspec-store`
- **AND** the validation SHALL confirm zero regression delta compared to the pre-upgrade baseline.

### Requirement: Unified daily scheduled maintenance and check-and-update automation

The system SHALL deploy a unified daily maintenance script supporting `--check` and `--apply` modes, register a LaunchAgent scheduled daily at 08:00 AM, retire legacy failing update plists, and filter global npm package updates to prevent 404 errors on git-installed packages.

#### Scenario: Unified daily maintenance job is registered and verified
- **WHEN** daily maintenance automation is deployed
- **THEN** obsolete update LaunchAgents (`com.user.brew-npm-update` and `com.microservices.developer-workstation-tool-update`) SHALL be unloaded and disabled
- **AND** `~/Developer/scripts/workstation-daily-update.sh` SHALL execute across Homebrew, Bun, filtered npm, uv tools, coding agents, skills sync, and store validation
- **AND** `com.developer.workstation-daily-update.plist` SHALL be loaded into launchd and scheduled for daily execution at 08:00 AM.

### Requirement: Two-Tier Coding Agent Management and Homebrew-First Alignment
The workstation coding agent maintenance lifecycle SHALL adhere to a two-tier operational hierarchy:
1. **Tier 1 (Homebrew-First Preferred Channel)**: Coding agents distributed as Homebrew formulae or casks (`block-goose-cli`, `block-goose`, `grok-build`, `pi-coding-agent`) SHALL be managed and upgraded through Homebrew automation (`brew upgrade --formula` and `brew upgrade --cask`).
2. **Tier 2 (Official Native Command Channel)**: Coding agents distributed outside Homebrew (`prime-agent`, `claude`, `codex`, `opencode`, `kilo`, `auggie`, `qoder`) SHALL be declared in `AGENT_CLI_COVERED` and upgraded via their official CLI subcommands under timeout fences.

#### Scenario: Grok managed via official Homebrew cask
- **WHEN** `grok --version` or `which grok` is executed
- **THEN** the command resolves to `/opt/homebrew/bin/grok` provided by `grok-build` cask (v1.0.46+)
- **AND** `brew list --cask grok-build` confirms successful Homebrew cask tracking

#### Scenario: Daily maintenance executes both formula and cask upgrades
- **WHEN** `workstation-daily-update.sh` executes Stage 1 in apply mode
- **THEN** both `brew upgrade --formula` and `brew upgrade --cask` SHALL execute
- **AND** Homebrew-managed agent casks (`grok-build`, `block-goose`) receive automated upgrades

#### Scenario: Prime Agent native updater integration
- **WHEN** `workstation-daily-update.sh` executes Stage 5
- **THEN** `prime-agent` SHALL be included in the covered agent set
- **AND** in check mode it SHALL report its active version (`installed: prime-agent (0.9.8)`)
- **AND** in apply mode it SHALL invoke `prime-agent update` bounded by `AGENT_UPDATE_TIMEOUT`

### Requirement: Canonical skill store entries resolve to readable content

Every entry in the canonical store `~/Developer/.agents/skills/` SHALL resolve to a readable `SKILL.md` containing parseable frontmatter. A self-referential or dangling symlink SHALL be reported as a broken entry.

#### Scenario: Broken entries are reported
- **WHEN** canonical-root verification runs and an entry is a self-referential or dangling symlink
- **THEN** the entry SHALL be reported as broken
- **AND** verification SHALL exit non-zero.

#### Scenario: A repair restores real content
- **WHEN** a skill previously recorded as a broken entry is restored
- **THEN** `~/Developer/.agents/skills/<skill>/SKILL.md` SHALL exist as a regular readable file with parseable frontmatter
- **AND** the entry SHALL no longer be reported as broken.

#### Scenario: Unrecoverable skills are restored from an authoritative source
- **WHEN** a broken skill is recoverable from a declared upstream source
- **THEN** it SHALL be restored from that source
- **AND** when no upstream source exists, it SHALL be restored from an authoritative local backup copy rather than deleted.

#### Scenario: Entry points use the canonical filename casing
- **WHEN** a canonical entry resolves its `SKILL.md` on a case-insensitive filesystem
- **THEN** the on-disk filename SHALL use the canonical `SKILL.md` casing rather than a variant
- **AND** a store-wide scan SHALL report no entry whose on-disk casing differs from the canonical name.

#### Scenario: Non-official plugin directories do not shadow skill entry points
- **WHEN** a canonical entry contains a directory that would cause an agent to treat the entry as a plugin container
- **THEN** that directory SHALL be reported as a malformed entry, because it stops the catalog walk before `SKILL.md`
- **AND** a directory not part of the Agent Skills layout and absent from upstream sources SHALL be removed rather than retained.

#### Scenario: Undiscoverable entries fail verification
- **WHEN** verification runs against entries that resolve but are not discoverable
- **THEN** it SHALL name each affected entry and its defect
- **AND** verification SHALL exit non-zero so the scheduled maintenance step fails.

### Requirement: User-scope fanout links resolve to canonical content

Each entry in the user-scope fanout directory `~/.agents/skills/` SHALL resolve to the corresponding canonical skill or to an agent-owned skill root, so that agents whose discovery depends on user scope reach workspace skills regardless of working directory.

#### Scenario: Fanout entries resolve from any working directory
- **WHEN** an agent resolves a declared user-scope skill entry
- **THEN** that entry SHALL resolve to a readable `SKILL.md`
- **AND** resolution SHALL NOT depend on the process working directory.

#### Scenario: User-scope coverage survives leaving the workspace directory
- **WHEN** an agent enumerates skills from a working directory outside the workspace root
- **THEN** skills that are only reachable through project scope SHALL be absent, as the official project scope is working-directory-relative
- **AND** skills declared in user scope SHALL remain reachable.

#### Scenario: Unresolved fanout entries are detected
- **WHEN** a user-scope fanout entry does not resolve to readable content
- **THEN** verification SHALL report it as broken
- **AND** reconciliation SHALL NOT report success while it remains unresolved.

### Requirement: Scheduled maintenance fails closed on unresolved skill links

The scheduled skills maintenance step SHALL treat any unresolved canonical or fanout skill link as a failure condition and SHALL NOT report success while such links remain.

#### Scenario: Broken links fail the maintenance run
- **WHEN** the scheduled skills parity step runs and one or more skill links are unresolved
- **THEN** the step SHALL report failure
- **AND** the overall maintenance run SHALL NOT conclude with a success status.

#### Scenario: Reconciliation that does not resolve the failure still fails
- **WHEN** the scheduled step attempts reconciliation and unresolved links remain afterward
- **THEN** re-verification SHALL report failure
- **AND** the overall maintenance run SHALL NOT conclude with a success status.

#### Scenario: Clean state passes the maintenance run
- **WHEN** the scheduled skills parity step runs and no skill link is unresolved
- **THEN** the step SHALL report success.

### Requirement: Scheduled upstream skill content refresh

The daily maintenance job SHALL refresh upstream-sourced skill content in the canonical store as a scheduled stage, so that content currency does not depend on a human running the skills CLI by hand.

#### Scenario: Upstream content is refreshed on schedule
- **WHEN** the daily maintenance job runs and upstream-sourced skills have newer content available
- **THEN** it SHALL pull the updated content into the canonical store without interactive prompts
- **AND** the refreshed entries SHALL resolve to readable `SKILL.md` content

#### Scenario: Refresh runs after link parity and before store validation
- **WHEN** the daily maintenance job executes its stages
- **THEN** the content refresh SHALL run after the skills parity check
- **AND** it SHALL run before the OpenSpec store validation gate

#### Scenario: Local skills are not refreshed from upstream
- **WHEN** a skill in the canonical store has no declared upstream source
- **THEN** the refresh SHALL NOT modify or remove that skill

### Requirement: Skill content refresh outcomes are reported

The refresh stage SHALL report a per-run outcome distinguishing refresh-available, refreshed, already-current, path-ambiguous, and refresh-failed, and SHALL record the outcome in the maintenance log.

#### Scenario: Outcome summary is recorded
- **WHEN** the refresh stage completes
- **THEN** the maintenance log SHALL record how many entries were refreshed, already current, skipped as path-ambiguous, and failed

#### Scenario: Drift is visible without application
- **WHEN** the refresh stage detects that upstream content differs from the local canonical store
- **THEN** it SHALL report that entries were refreshed
- **AND** the report SHALL be distinguishable from a run where no entry changed

### Requirement: Drift is observable before content is replaced

The refresh stage SHALL determine whether upstream content differs from the canonical store before it replaces any skill content, and SHALL report drift availability independently of whether that content is then applied.

#### Scenario: Drift check does not mutate
- **WHEN** the refresh stage evaluates whether any upstream content has changed
- **THEN** it SHALL report drift availability before any skill content is replaced

#### Scenario: Unchanged content is reported as already current
- **WHEN** the refresh stage runs and no upstream content differs from the canonical store
- **THEN** it SHALL report that no entry changed
- **AND** the reported outcome SHALL be distinguishable from a run that replaced content

### Requirement: Path-ambiguous upstream skills are informational

When upstream publishes the same skill at multiple paths, the refresh SHALL classify the resulting skip as an informational condition and SHALL NOT treat it as stale, broken, or failing.

#### Scenario: Multi-path upstream entry is reported as informational
- **WHEN** upstream publishes one skill at more than one path and the refresh tool declines to choose between them
- **THEN** the refresh SHALL report the entry as path-ambiguous
- **AND** the run SHALL NOT classify that entry as stale, broken, or failed

#### Scenario: Path-ambiguous entry does not fail the maintenance run
- **WHEN** the only unrefreshed entry in a run is path-ambiguous
- **THEN** the maintenance run SHALL still be able to conclude successfully

### Requirement: Refresh failures degrade without masking

An unreachable upstream or failed content refresh SHALL be reported as a degradation and SHALL NOT be reported as a silent success.

#### Scenario: Unreachable upstream is reported
- **WHEN** upstream content cannot be reached during the scheduled refresh
- **THEN** the refresh SHALL report the failure for the affected entries
- **AND** the maintenance run SHALL NOT report the refresh stage as fully successful

#### Scenario: A failed refresh does not abort unrelated stages
- **WHEN** the refresh stage fails for one or more entries
- **THEN** the remaining maintenance stages SHALL still execute

#### Scenario: Transient network failure is distinguishable from drift
- **WHEN** the refresh fails because of a network condition rather than a content difference
- **THEN** the reported outcome SHALL identify a refresh failure rather than a refreshed or already-current result

### Requirement: Refresh is time-bounded

Each refresh invocation SHALL be time-bounded, and a refresh that exceeds its bound SHALL be reported as a refresh failure rather than being allowed to run indefinitely.

#### Scenario: A hung refresh is abandoned and reported
- **WHEN** a refresh invocation exceeds its configured time bound
- **THEN** it SHALL be terminated
- **AND** its outcome SHALL be reported as a refresh failure

#### Scenario: A hung refresh does not stall the maintenance run
- **WHEN** a refresh invocation is terminated for exceeding its bound
- **THEN** the remaining maintenance stages SHALL still execute

### Requirement: Coding agent CLI coverage reflects installed agents

The coding agent CLI stage SHALL update every agent CLI in the stage's declared covered set that is installed, and SHALL report both the covered set and any installed agent CLI outside it.

#### Scenario: All installed agent CLIs are updated
- **WHEN** the coding agent CLI stage runs and more than one agent CLI from the covered set is installed
- **THEN** each installed agent CLI in the covered set SHALL be updated by the stage

#### Scenario: The covered set is declared
- **WHEN** the coding agent CLI stage runs
- **THEN** it SHALL report which agent CLIs the covered set contains
- **AND** the covered set SHALL NOT be inferred only from what happens to be installed

#### Scenario: Uncovered agents are reported
- **WHEN** an installed agent CLI is not in the covered set
- **THEN** the stage SHALL report it as uncovered

#### Scenario: Absent agents are skipped without error
- **WHEN** an agent CLI in the covered set is not installed
- **THEN** the stage SHALL skip it without reporting a failure

### Requirement: A zero-exit updater that reports an error is a failure

An agent CLI update that exits with a success status while reporting an error SHALL be reported as a failure rather than as a successful update.

#### Scenario: Error output with a zero exit is reported as failure
- **WHEN** an agent CLI updater exits zero and its output reports an error
- **THEN** the stage SHALL report that agent as failed
- **AND** the run SHALL report a degraded agent-update outcome

#### Scenario: A healthy updater is not reported as failed
- **WHEN** an agent CLI updater exits zero and its output contains no error report
- **THEN** the stage SHALL report that agent as updated
- **AND** the run SHALL NOT report a degraded agent-update outcome

#### Scenario: The failure outcome survives to the run summary
- **WHEN** the stage reports any agent as failed
- **THEN** the recorded agent-failure outcome SHALL reach the run's final summary
- **AND** it SHALL NOT depend on re-matching the stage's own printed text

### Requirement: Check mode does not mutate

When the maintenance job runs in check mode, the agent CLI and skill-content stages SHALL report their findings without applying any update.

#### Scenario: Check mode leaves skill content unchanged
- **WHEN** the maintenance job runs in check mode
- **THEN** the skill-content stage SHALL NOT replace or remove any skill content
- **AND** the reported outcome SHALL indicate that no content was applied

#### Scenario: Check mode leaves agent CLIs unchanged
- **WHEN** the maintenance job runs in check mode
- **THEN** the agent CLI stage SHALL NOT invoke any agent updater
- **AND** it SHALL report the covered set and which covered agents are installed

#### Scenario: Apply mode still updates
- **WHEN** the maintenance job runs in apply mode
- **THEN** the agent CLI and skill-content stages SHALL perform their updates as specified

### Requirement: Refresh lockfile integrity is not asserted from an internal digest

The refresh stage SHALL NOT treat the lockfile lock digest as an authoritative drift signal, and SHALL determine whether content changed from the pulled content itself.

#### Scenario: Internal digest does not gate the refresh
- **WHEN** the refresh stage evaluates whether an entry needs refreshing
- **THEN** it SHALL NOT compare the lockfile lock digest against a locally computed content digest as its drift signal

#### Scenario: Content comparison uses the pulled content
- **WHEN** the refresh stage determines whether an entry changed
- **THEN** it SHALL base that determination on the content the refresh produced

### Requirement: Executed maintenance scripts are version controlled

Every script that a scheduled job executes from the workstation scripts directory SHALL have a copy recorded under version control in the OpenSpec store, so each script has revision history and a recovery path.

#### Scenario: A scheduled script has a recorded copy
- **WHEN** a LaunchAgent executes a script from `~/Developer/scripts/`
- **THEN** a copy of that script SHALL exist under version control in the store's `scripts/` tree
- **AND** the recorded copy SHALL be retrievable from the store's history

#### Scenario: A script executed with no recorded copy is reported
- **WHEN** a script is executed from the workstation scripts directory and no recorded copy exists in the store
- **THEN** the discrepancy SHALL be reported
- **AND** the script SHALL be named in the report

#### Scenario: History survives loss of the executed copy
- **WHEN** the executed copy of a version-controlled script is lost or corrupted
- **THEN** its content SHALL be recoverable from the recorded copy without relying on any other backup

### Requirement: Each script has one declared source of truth

For each script that exists both as an executed copy and a recorded copy, the relationship SHALL be declared explicitly, and the copies SHALL NOT be treated as independently editable.

#### Scenario: The source of truth is declared
- **WHEN** a script exists as both an executed copy and a recorded copy
- **THEN** which of the two is authoritative SHALL be stated, rather than left implicit
- **AND** the declared relationship SHALL be discoverable without inspecting file contents

#### Scenario: Copies are not left as unrelated duplicates
- **WHEN** a script is present as two separate files that are byte-identical
- **THEN** the duplication SHALL be resolved so the relationship is declared
- **AND** the two copies SHALL NOT remain independently editable with no recorded link

### Requirement: Installed-copy drift is detected and reported

The scheduled maintenance job SHALL compare the executed copy of a version-controlled script against its recorded copy and SHALL report any difference.

#### Scenario: Drift is reported
- **WHEN** the executed copy of a script differs in content from its recorded copy
- **THEN** the maintenance job SHALL report that script as drifted
- **AND** the report SHALL name the script and indicate which copy differs

#### Scenario: Drift is a reported degradation, not a silent success
- **WHEN** drift is detected during a maintenance run
- **THEN** the run SHALL report a degraded outcome
- **AND** the run SHALL NOT conclude reporting that the scripts are consistent

#### Scenario: Agreement is reported
- **WHEN** the executed and recorded copies of every checked script agree
- **THEN** the maintenance job SHALL report that no script drift was found

#### Scenario: Reconciliation follows the installed copy
- **WHEN** a recorded inventory disagrees with the installed inventory
- **THEN** every repository listed only in the installed inventory SHALL be confirmed to exist as a repository before it is recorded
- **AND** a repository that exists only in the recorded inventory SHALL be reported rather than dropped

#### Scenario: Drift detection does not rewrite either copy
- **WHEN** drift is detected
- **THEN** the maintenance job SHALL NOT modify the executed copy or the recorded copy
- **AND** reconciling the difference SHALL require a deliberate change

### Requirement: Inventory approval digest accompanies its inventory

When a recorded inventory of repositories differs from the inventory its approval digest was computed over, the digest SHALL be regenerated in the same change, so the recorded pair remains internally consistent.

#### Scenario: A reconciled inventory carries a matching digest
- **WHEN** a recorded repository inventory is brought in line with the executed inventory
- **THEN** the recorded approval digest SHALL be recomputed over the reconciled inventory
- **AND** the recorded digest SHALL match the recorded inventory

#### Scenario: A mismatched pair is reported
- **WHEN** a recorded inventory's content does not hash to the digest recorded beside it
- **THEN** the pair SHALL be reported as inconsistent
- **AND** the affected inventory SHALL be named in the report
