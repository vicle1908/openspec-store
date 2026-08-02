## Why

The designated macOS developer workstation had npm lifecycle scripts blocked by
an ineffective user allowlist and a conflicting project-level `allowScripts`
field, causing routine Pi extension updates to require repeated intervention.
The workstation also lacked one explicit, observable contract for serial daily
updates across Homebrew, Bun, npm, Pi, Pi extensions, and Oh My Posh.

## What Changes

- Establish a user-scoped workstation preflight that resolves the actual
  executables, configuration precedence, update ownership, and installed
  versions before mutation.
- Make the user's explicit blanket npm lifecycle-script trust decision
  observable through `dangerously-allow-all-scripts=true`, while documenting
  its security impact and a reversible return to reviewed allowlists.
- Define one serialized update sequence for Homebrew, Bun, eligible top-level
  global npm packages, Pi core, Pi extensions, and Oh My Posh, including
  repeatable already-current behavior, explicit heavy-package deferral, and
  stage-specific failure reporting.
- Schedule the sequence once daily at 09:00 in the workstation's local time
  through one user-scoped macOS LaunchAgent, prevent overlapping runs, and
  report each run without exposing credentials, package-registry tokens, or
  unrelated user-home data.
- Replace the initial Codex heartbeat executor with the LaunchAgent only after
  disabling the heartbeat, so exactly one scheduler can mutate the workstation.
  Codex may inspect retained reports but is not required for execution.
- Install an integrity-checked copy of the repository-owned runner under the
  current user's Application Support directory before bootstrap, so launchd
  never needs access to the Google Drive/FileProvider source checkout.
- Treat vulnerability-audit results separately from update-command success;
  unresolved findings remain visible and are not silently force-fixed across
  compatibility boundaries.
- Prevent a package with a pathologically large actual tree from consuming two
  consecutive daily timeout windows: the npm stage uses explicit top-level
  package requests, reports reviewed heavy-package exclusions, and leaves
  those exclusions to a separate operator-invoked maintenance window.
- Add acceptance and rollback requirements for configuration verification,
  extension-script execution, scheduler state, failure recovery, and removal of
  blanket lifecycle-script permission.
- This is not a production-service, API, database, event, container, deployment,
  or repository dependency-upgrade change. It does not make the monorepo or its
  deployment artifacts release-ready.

## Capabilities

### New Capabilities

- `developer-workstation-package-maintenance`: Defines safe preflight,
  explicitly authorized npm script policy, serialized multi-tool updates,
  daily scheduling, redacted reporting, vulnerability visibility, retry
  behavior, and rollback for the designated macOS developer workstation.

### Modified Capabilities

None. Existing `dependency-checking`, `security-vulnerability-checking`, and
`upgrade-proposal-generation` requirements govern repository or CI dependency
analysis and remain unchanged.

## Impact

- **Ownership boundary:** Developer-tooling maintainers own the workstation
  automation; no microservice or shared platform module consumes it.
- **Affected state:** The current user's npm configuration, installed Homebrew,
  Bun, npm, Pi, Pi-extension, and Oh My Posh packages; one plist under
  `~/Library/LaunchAgents`; one installed runner bundle under
  `~/Library/Application Support`; and removal or pausing of the superseded
  Codex heartbeat executor.
- **Repository surfaces:** One locked maintenance runner, a versioned
  LaunchAgent template and installation/inspection support, fixture-only tests,
  root Make targets, and an indexed operator runbook.
- **Contracts and data:** No REST, Protobuf, Kafka, Temporal, PostgreSQL, or
  cross-service contract changes. No production data ownership changes.
- **Compatibility:** Updates may expose upstream peer-dependency,
  deprecation, native-build, filesystem-scale, or vulnerability issues. A
  command exiting zero does not waive those findings. `omniroute` is excluded
  from the daily npm request by default after its 817-directory dependency tree
  exceeded the two-hour npm stage ceiling; its maintenance remains explicit.
- **Rollout:** Verify the blanket npm policy, run the complete sequence once,
  separately exercise Pi extension updates, verify versions and audit summary,
  disable the Codex heartbeat executor, install and verify the user-local
  runner bundle, install and bootstrap exactly one user LaunchAgent, and inspect
  its active 09:00 calendar configuration.
- **Rollback:** Boot out and remove only the matching LaunchAgent, verify the
  scheduler is inactive, remove `dangerously-allow-all-scripts`, restore
  reviewed `allowScripts` entries where required, and use each package
  manager's supported version rollback rather than deleting unrelated user
  data.
