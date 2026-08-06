## Purpose

Defines safe, observable, and reversible daily maintenance of the designated
macOS developer workstation's package-manager tools without expanding
repository or deployment readiness claims.

## ADDED Requirements

### Requirement: Live workstation maintenance preflight

Before changing developer-tool state, the maintenance workflow SHALL resolve
the current macOS architecture and local time zone; executable path and version
for Homebrew, Bun, npm, Pi, and Oh My Posh; npm user prefix and root; effective
`allow-scripts`, `dangerously-allow-all-scripts`, `strict-allow-scripts`, and
`ignore-scripts` values; root `package.json#allowScripts` presence; matching
user LaunchAgents, cron entries, and Codex automations; and active-run state.
It MUST stop before mutation when a required executable is missing, resolves
outside the expected current-user or Homebrew ownership boundary, another
maintenance run is active, or more than one scheduler can invoke the workflow.

#### Scenario: Supported workstation passes preflight

- **WHEN** every required executable resolves to an expected current-user or
  Homebrew path and no maintenance run is active
- **THEN** the workflow reports the redacted paths and versions and permits the
  update sequence to begin

#### Scenario: Required tool is missing or unexpectedly owned

- **WHEN** a required executable is absent or resolves outside the expected
  current-user or Homebrew ownership boundary
- **THEN** the workflow performs no package update or scheduler mutation and
  reports the blocking tool without printing environment or credential data

#### Scenario: Preflight is repeated

- **WHEN** preflight runs again without a relevant host, tool, policy, schedule,
  or active-run change
- **THEN** it reports the same effective state without installing packages,
  rewriting configuration, or creating a duplicate schedule

### Requirement: Explicit blanket npm lifecycle-script policy

The workstation SHALL enable the user's explicitly authorized blanket
lifecycle-script policy through the user-scoped effective setting
`dangerously-allow-all-scripts=true` and SHALL remove the obsolete user
`allow-scripts=fsevents,...` entry. Every maintenance report MUST state that the
blanket policy permits lifecycle scripts from current and future dependencies
without package review. Verification MUST read only the relevant policy keys
and MUST NOT expose registry credentials or full npm configuration.

#### Scenario: Blanket policy is effective

- **WHEN** npm policy configuration is applied and a dependency operation
  encounters packages with lifecycle scripts
- **THEN** the operation does not emit an unreviewed-script approval prompt,
  the effective dangerous setting is true, and the report includes the trust
  warning

#### Scenario: Project allowlist exists

- **WHEN** a project-level `package.json#allowScripts` field is present while
  the blanket user policy is active
- **THEN** the workflow reports the policy precedence without deleting the
  project allowlist or treating it as a failure

#### Scenario: Blanket policy is not effective

- **WHEN** the effective dangerous setting is false or a dependency lifecycle
  script is blocked
- **THEN** the update stops at that stage, reports the policy mismatch, and does
  not claim Pi extension maintenance succeeded

### Requirement: Serialized complete update sequence

Each maintenance run SHALL execute, in order and from the current user's home
directory, `brew update`, `brew upgrade`, `bun update`, `bun upgrade`, one
targeted global npm stage, `pi update`, `pi update --extensions`, and
`omp update`. The npm stage SHALL discover installed top-level global package
names from their package manifests, exclude reviewed heavy packages from the
daily request, and invoke `npm update -g -- <eligible-package>...` with explicit
package names. The default heavy-package exclusion SHALL include `omniroute`
and SHALL be reported without claiming that package was updated. Each next
stage MUST start only after the preceding stage exits zero. An already-current
stage SHALL count as success, and a single-run exclusion MUST prevent
overlapping scheduled or manual maintenance runs.

#### Scenario: Complete update succeeds

- **WHEN** every command in the canonical order exits zero
- **THEN** the run reports all eight stages as passed and records the final tool
  versions without claiming that unrelated repository or deployment validation
  passed

#### Scenario: Tools are already current

- **WHEN** one or more update stages report no available change and exit zero
- **THEN** those stages pass without reinstalling, duplicating configuration,
  or changing the command order

#### Scenario: Heavy global package is deferred

- **WHEN** an installed top-level global package is in the reviewed daily
  exclusion set
- **THEN** the npm stage omits it from the explicit update request, reports the
  package as deferred, and requires a separate operator-invoked maintenance
  window without treating it as silently updated

#### Scenario: Operator maintains a deferred global package

- **WHEN** an operator supplies a validated explicit heavy-package target in a
  reviewed maintenance window
- **THEN** the same locked workflow sends only the explicit package name to npm
  and reports the selection as an override without silently including other
  deferred packages

#### Scenario: No eligible global npm package exists

- **WHEN** every installed top-level global npm package is reviewed as heavy or
  no eligible package is installed
- **THEN** the npm stage reports an already-current no-op without invoking an
  unscoped `npm update -g`

#### Scenario: Pi core skips extensions

- **WHEN** `pi update` reports that extensions are skipped
- **THEN** the workflow still runs `pi update --extensions` as its own required
  stage and reports core and extension outcomes separately

#### Scenario: Another run is active

- **WHEN** a scheduled or manual maintenance run attempts to start while the
  single-run exclusion is held
- **THEN** the later run performs no package mutation and reports a
  skipped-overlap outcome

### Requirement: Stage-aware failure and retry behavior

When a stage exits non-zero, the workflow SHALL identify the failed stage,
preserve the outcomes of completed stages, mark all not-started stages as not
run, and perform only safe in-scope diagnosis. It MUST NOT silently skip the
failure, clear broad caches, force a breaking upgrade, escalate privileges, or
mutate unrelated configuration. After a cause is safely resolved, retry SHALL
resume at the failed stage or recheck a prerequisite and SHALL keep the same
canonical order. The workflow MUST NOT automatically retry the targeted global
npm stage after a timeout; that stage requires an explicit resume after
reviewing the retained evidence.

#### Scenario: Update stage fails

- **WHEN** any canonical update command exits non-zero
- **THEN** no later stage starts in that attempt and the report distinguishes
  passed, failed, and not-run stages

#### Scenario: Corrected stage succeeds on retry

- **WHEN** safe in-scope remediation corrects the failed stage
- **THEN** the workflow rechecks required prerequisites, resumes in canonical
  order, and reports both the original failure and final outcome

#### Scenario: Repeated external failure remains unresolved

- **WHEN** a registry, network, upstream build, or compatibility failure
  persists after bounded retry
- **THEN** the run remains failed, the scheduler stays observable, and no
  destructive cleanup or false success is performed

#### Scenario: Global npm stage reaches its timeout

- **WHEN** the targeted global npm stage reaches its configured time ceiling
- **THEN** the attempt exits with timeout evidence, receives no automatic
  second attempt, and later stages remain not run until an operator explicitly
  resumes after remediation

### Requirement: Daily local scheduling and observability

The workstation SHALL have exactly one active user LaunchAgent named
`com.microservices.developer-workstation-tool-update`, installed under the
current user's `~/Library/LaunchAgents`, with `StartCalendarInterval` configured
for 09:00 in the workstation's local time. Before bootstrap, the workflow SHALL
install the repository-owned runner, lifecycle controller, and plist template
under
`~/Library/Application Support/com.microservices.developer-workstation-tool-update/`
with a manifest of their SHA-256 hashes. The LaunchAgent SHALL invoke the
hash-verified installed runner, use the current user's home directory as its
working directory, and use explicit program arguments, bounded environment,
and output paths. Its explicit `PATH` SHALL prefer the current user's
npm-global and Bun bin directories before Homebrew so scheduled commands
resolve the same user-owned npm, Pi, Bun, and Oh My Posh tools as interactive
maintenance. It MUST NOT execute from or set its working directory to a
cloud-synced or FileProvider checkout. It SHALL set neither `RunAtLoad` nor
`KeepAlive` true and SHALL retain machine-readable reports under
`~/.local/state/go-microservices-workstation-tool-update/runs/`. Each run
SHALL report start and end times, per-stage status, final tool versions, npm
blanket-policy status, eligible and deferred global npm package names, Pi
extension coverage, vulnerability counts by severity, overlap status, and any
remediation. Reports MUST redact credentials,
authenticated registry URLs, environment dumps, package payloads, and
unrelated user-home paths. The superseded Codex heartbeat MUST be inactive
before the LaunchAgent is bootstrapped.

#### Scenario: Daily schedule is active

- **WHEN** schedule state is inspected after configuration
- **THEN** `launchctl print` shows exactly one user LaunchAgent with the 09:00
  calendar trigger, its workflow includes all eight canonical stages, and no
  matching Codex heartbeat or cron executor is active

#### Scenario: Installed runner bundle is valid

- **WHEN** the LaunchAgent is installed or preflight inspects it
- **THEN** every installed executable/template hash matches the user-owned
  manifest, the plist points to the installed runner, and its working directory
  is the current user's home directory

#### Scenario: Installed runner bundle is modified

- **WHEN** any installed executable or template differs from its recorded hash
- **THEN** preflight stops before package mutation and requires an explicit
  reinstall from the repository source

#### Scenario: Source checkout is FileProvider protected

- **WHEN** the repository is located in a cloud-synced FileProvider path
- **THEN** launchd executes only the installed Application Support copy and
  does not request or require access to the source checkout

#### Scenario: Scheduled run completes

- **WHEN** the scheduler triggers the workflow
- **THEN** one non-overlapping run executes and publishes a redacted per-stage
  report under the user-scoped maintenance state directory

#### Scenario: Mac is asleep at 09:00

- **WHEN** the calendar trigger elapses while the Mac is asleep
- **THEN** launchd starts one coalesced maintenance run after wake and does not
  replay every missed daily occurrence

#### Scenario: User is not logged in

- **WHEN** the 09:00 calendar time occurs without the owning user's login
  domain active
- **THEN** the workflow does not elevate to a LaunchDaemon, and the operator
  inspects or manually kickstarts the user service after login

#### Scenario: Operator tests the service

- **WHEN** the operator invokes `launchctl kickstart` for the service in the
  current user's GUI domain
- **THEN** the same locked runner, redaction, stage ordering, and report
  retention apply as for a calendar-triggered run

#### Scenario: Duplicate schedule is discovered

- **WHEN** preflight finds a second LaunchAgent, matching cron entry, or active
  Codex heartbeat that can invoke the maintenance workflow
- **THEN** package mutation stops until one owner is selected and duplicate
  scheduling is removed or paused without deleting unrelated automations

#### Scenario: Reporting encounters sensitive configuration

- **WHEN** diagnosis needs npm or shell configuration that can contain
  credentials
- **THEN** the workflow reads only required keys or emits a redacted summary and
  never records raw secrets or complete configuration

### Requirement: Update success is independent from vulnerability status

The workflow SHALL collect available npm audit severity counts for the Pi
extension dependency tree after updating and SHALL report them independently
from command success. It MUST NOT interpret a zero-exit update as proof that
vulnerabilities are absent and MUST NOT automatically apply forceful or
breaking audit remediation solely to reduce the count.

#### Scenario: Update passes with unresolved findings

- **WHEN** all canonical update stages exit zero and npm audit still reports
  vulnerabilities
- **THEN** the run is reported as update-successful with an explicit unresolved
  vulnerability summary

#### Scenario: No audit findings remain

- **WHEN** the post-update audit reports zero findings
- **THEN** the report records zero by severity without broadening that result to
  Go modules, container images, or production dependencies

#### Scenario: Remediation requires a compatibility decision

- **WHEN** removing a finding requires a major substitution, force flag, or
  incompatible peer-dependency change
- **THEN** the workflow leaves the finding visible and requires a separate
  reviewed change before applying the remediation

### Requirement: Non-destructive rollback

Rollback SHALL pause or delete the matching daily schedule, wait for any active
maintenance run to finish, boot out the matching user LaunchAgent, remove only
its plist, verify its label is absent from the user GUI domain, remove the
user-scoped
`dangerously-allow-all-scripts` setting, verify that blanket lifecycle-script
permission is no longer effective, and document how reviewed package/version
allowlist entries can be restored. Normal rollback MUST NOT delete package
caches, credentials, user data, repository lockfiles, or unrelated
automations.

#### Scenario: LaunchAgent rollback succeeds

- **WHEN** the operator rolls back daily scheduling
- **THEN** the matching service is booted out, only its plist is removed, no
  matching executor remains active, and the superseded Codex heartbeat is not
  silently reactivated

#### Scenario: Blanket policy rollback succeeds

- **WHEN** the user requests a return to reviewed lifecycle scripts
- **THEN** the schedule is inactive before policy mutation, the dangerous npm
  setting becomes false or absent, and future unreviewed lifecycle scripts are
  no longer silently permitted

#### Scenario: Active run delays rollback

- **WHEN** rollback is requested while a maintenance run holds the single-run
  exclusion
- **THEN** no second mutation starts, the scheduler is prevented from launching
  another run, and policy rollback waits for the active run to terminate safely

#### Scenario: Tool-version rollback is required

- **WHEN** an upstream update causes a confirmed regression
- **THEN** the affected tool uses its owner-supported version rollback while
  unrelated tools, caches, credentials, and user data remain intact
