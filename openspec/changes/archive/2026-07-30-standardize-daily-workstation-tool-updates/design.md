## Context

The designated macOS arm64 workstation resolves Homebrew from
`/opt/homebrew`, Bun from the current user's Bun installation, Pi from the
current user's npm prefix, and Oh My Posh from the current user's Bun bin
directory. At diagnosis time, npm 11.17.0 blocked dependency lifecycle scripts
that were not covered by an allowlist. The user's `.npmrc` attempted to allow
only repeated `fsevents` entries, while `/Users/androidteam/package.json`
declared its own `allowScripts` field and therefore took precedence over that
user allowlist.

The initial Homebrew npm 11.17.0 build recognized
`dangerously-allow-all-scripts` but did not expose `npm install-scripts` as an
executable command. The attempted `npm install-scripts approve ls` invocation
was consequently parsed as an install request whose unmatched package argument
was `ls`, producing `ENOMATCH`. The completed global update subsequently moved
the active user-prefix npm to 12.0.1. The LaunchAgent PATH therefore prefers
the user's npm-global and Bun bin directories before Homebrew so scheduled and
interactive maintenance resolve the same user-owned tools. Durable behavior
still relies on feature/configuration preflight rather than a permanent npm
version assumption.
Current npm CLI source and documentation identify the blanket switch as a
bypass of reviewed allowlists; this is a deliberately broad trust decision,
not a harmless prompt preference.

The one-time rollout completed the requested update chain successfully, ran Pi
extension updating separately because plain `pi update` skips extensions,
verified the effective npm setting, and created an initial daily Codex
heartbeat at 09:00 local time. Subsequent scheduler research against the
current host's `launchd.plist(5)` and `launchctl(1)` interfaces identified a
user LaunchAgent as the durable macOS-native executor. The heartbeat is
therefore historical implementation evidence and must be disabled before the
LaunchAgent is enabled. The Pi extension dependency tree still reports nine
known vulnerabilities (five moderate and four high), so update success and
security acceptance must remain separate states.

The first live LaunchAgent kickstart proved that macOS denies background
launchd jobs access to the Google Drive/FileProvider source checkout:
`getcwd` and execution both failed with `Operation not permitted`. Granting
broader privacy access or moving the repository would expand workstation
scope. The approved correction is to install a verified copy of the
repository-owned runner into the user's Application Support directory and
execute only that copy.

The first natural 09:00 LaunchAgent run exposed a separate npm scalability
failure. Its unscoped `npm update -g` spent the full 7,200-second ceiling
reifying the global tree, then the generic retry began the same operation
again. Process sampling showed four libuv workers dominated first by `unlink`
and then by `lstat`. The installed `omniroute` 3.8.48 package has 74 regular
dependencies, 8 optional dependencies, and 817 immediate directories under
its nested `node_modules`; npm was resolving 3.8.49 with incompatible React and
marked peer ranges. This is deterministic filesystem-scale work, not an
approval prompt or transient registry failure.

The durable implementation is repository-owned:
`scripts/workstation-tool-update.sh` provides the lock, policy preflight,
stage-aware execution, bounded retry, resume, redaction, versions, and audit
report; the root Makefile provides the supported entry points; and
`docs/runbooks/developer-workstation-package-maintenance.md` owns operations
and rollback guidance.

This capability is owned by developer tooling and changes host/user state only.
There is no service transaction, event delivery, ordering, or versioned
application contract. There are no container images and therefore no
`linux/arm64` image-selection decision.

## Goals / Non-Goals

**Goals:**

- Define the observable preflight, trust decision, command order, schedule,
  reporting, retry, and rollback behavior for daily workstation maintenance.
- Keep reruns idempotent when every tool is already current.
- Make partial failure, blocked lifecycle scripts, audit findings, and scheduler
  state visible without exposing credentials or unrelated user data.
- Preserve user control over the high-risk blanket npm lifecycle-script policy.
- Ensure Pi extensions participate even though `pi update` omits them.
- Use the current macOS user-session scheduler without requiring Codex to be
  running, while retaining reports that Codex or an operator can inspect.

**Non-Goals:**

- Upgrade Go modules, repository lockfiles, Docker images, deployment
  manifests, service APIs, databases, Kafka events, or Temporal workflows.
- Assert that package-manager success removes vulnerabilities, resolves peer
  incompatibilities, or makes the monorepo deployable.
- Automatically apply breaking or forceful vulnerability remediations.
- Pin transient "latest" workstation versions inside the durable capability
  contract.
- Delete caches, user data, credentials, package-manager state, or application
  preferences during normal update or rollback.

## Decisions

### 1. Keep workstation maintenance separate from repository dependency checking

Create the new `developer-workstation-package-maintenance` capability. Existing
`dependency-checking`, `security-vulnerability-checking`, and
`upgrade-proposal-generation` specs address repository/CI inputs and remain
unchanged. This prevents host package-manager mutation from being mistaken for
a repository dependency proposal or release gate.

Alternative considered: extend `dependency-checking`. Rejected because its
inputs are Go modules and Docker images and its scheduled execution is CI,
whereas this change mutates one user's macOS toolchain.

### 2. Represent blanket npm script execution as an explicit trust boundary

The selected policy is the current user's explicit request:
`dangerously-allow-all-scripts=true` at user scope. The obsolete
`allow-scripts=fsevents,...` entry is removed. Verification reads only the
relevant redacted npm keys and exercises a dependency update; it never prints
registry credentials or the complete npm configuration.

The root `package.json#allowScripts` entry is not deleted merely to suppress a
warning because it is separate user-owned state and can serve again if blanket
permission is rolled back. The blanket setting bypasses both current and future
package review, so every report must preserve that warning.

Alternative considered: approve only the six packages from the original
warning. Rejected because the user explicitly requested all scripts to run
without recurring approval. It remains the recommended rollback destination.

### 3. Serialize one canonical update order

The canonical order is:

1. `brew update`
2. `brew upgrade`
3. `bun update`
4. `bun upgrade`
5. targeted global npm update with explicit eligible top-level package names
6. `pi update`
7. `pi update --extensions`
8. `omp update`

All commands run from `/Users/androidteam`. The runner itself prepends the
current user's npm-global and Bun bin directories so manual and LaunchAgent
invocations resolve the same owned tools even when an interactive shell places
another Node distribution earlier in its inherited `PATH`.
Before stage 5, the runner reads only top-level installed package manifests,
builds an explicit npm package-name array, removes the reviewed heavy-package
set, and runs `npm update -g -- <eligible-package>...`. `omniroute` is the
default reviewed exclusion because it exceeded the daily budget. The report
lists both eligible and deferred names. An empty eligible set is a successful
no-op and never falls back to an unscoped global update. Heavy packages use a
separate operator-invoked maintenance window with retained timing evidence.
That window sets `WORKSTATION_TOOL_UPDATE_NPM_TARGET_PACKAGES` to an explicit
validated package-name list, so the same locked runner targets only those npm
packages and records `explicit-override` selection in its report.
The Pi extension stage is explicit because Pi 0.82.1 reports that plain
`pi update` skips extensions. A single-run lock is required before unattended
operation so the daily invocation cannot overlap a manual or earlier scheduled
run. Already-current output is successful and requires no mutation.

Alternative considered: parallel package-manager updates. Rejected because
Homebrew, Bun, npm, and their dependent tools can change executables or native
artifacts used by later stages.

Alternative considered: keep unscoped `npm update -g` with a longer timeout or
automatic retry. Rejected because the natural run proved that it can consume
successive multi-hour windows repeating deterministic global-tree traversal.

### 4. Stop the shell chain on failure, then diagnose and resume explicitly

Within an attempt, each stage starts only after the prior stage exits zero.
When a stage fails, the automation records the failed stage, performs only
safe in-scope diagnosis, and resumes from the failed or next safe stage after
the cause is corrected. It must not reinterpret a warning as failure, silently
skip a failed stage, or report later stages as passed when they did not run.

Retry is stage-aware and idempotent: completed package-manager updates may be
rechecked, while ordinary transient stage failures receive a bounded retry.
The global npm stage is the exception: exit `124` receives no automatic retry,
because repeating the same unmodified global-tree operation is not remediation.
An operator may explicitly resume from that stage after changing the reviewed
target or correcting the cause. Repeated external failures remain visible and
do not trigger destructive cache clears, forced upgrades, privilege escalation,
or unrelated configuration changes.

### 5. Use one user LaunchAgent as the macOS-native executor

The durable schedule is one user LaunchAgent with label
`com.microservices.developer-workstation-tool-update`, installed at
`~/Library/LaunchAgents/com.microservices.developer-workstation-tool-update.plist`.
It uses `StartCalendarInterval` with hour 9 and minute 0,
`RunAtLoad=false`, and `KeepAlive=false`. Its `ProgramArguments`,
`WorkingDirectory`, environment, and stdout/stderr paths are explicit so the
job does not depend on an interactive shell profile.

The source runner, LaunchAgent controller, and plist template are installed as
a user-owned bundle under
`~/Library/Application Support/com.microservices.developer-workstation-tool-update/`.
The bundle contains a manifest of SHA-256 hashes, and installation or
inspection fails closed when the installed files do not match that manifest.
The LaunchAgent invokes the installed locked runner and uses the current
user's home directory as `WorkingDirectory`; it never executes from or changes
directory into the Google Drive/FileProvider checkout. Machine-readable
reports remain under
`~/.local/state/microservices-workstation-tool-update/runs/`.

The service lifecycle uses current `launchctl` interfaces against the logged-in
user's GUI domain: `bootstrap` to register the plist, `bootout` to remove it,
`kickstart` for an explicit test invocation, and `print` for inspection.
Legacy `load`, `unload`, and `list` interfaces are not part of the supported
workflow.

`StartCalendarInterval` is selected instead of `StartInterval`: when the Mac is
asleep at 09:00, launchd starts the job after the next wake and coalesces
multiple missed calendar occurrences into one invocation. The LaunchAgent
runs only in the user's login context and does not wake a powered-off machine
or run as a system daemon before login.

Each run reports start/end time, every stage's outcome, effective tool
versions, whether npm blanket script trust remains active, Pi extension
coverage, vulnerability counts by severity, overlap status, and any
remediation. Reports omit tokens, registry URLs containing credentials,
environment dumps, package payloads, and unrelated home-directory paths.
Codex may inspect these retained reports, but no Codex task or application
availability is required for execution.

The initial Codex heartbeat executor must be paused or deleted and verified
inactive before the LaunchAgent is bootstrapped. Preflight treats an active
heartbeat, matching cron entry, or second LaunchAgent as a conflicting
scheduler and stops mutation until exactly one owner remains.

Alternatives considered:

- A LaunchDaemon is rejected because it runs in a privileged system context,
  while Homebrew, Bun, npm, Pi, Oh My Posh, their configuration, and their
  reports are owned by the current user.
- `cron` is rejected because it skips invocations while the computer sleeps and
  is not the preferred macOS service lifecycle.
- Shortcuts personal automation is rejected because it provides weaker
  repository-controlled command, logging, inspection, and rollback semantics.
- `SMAppService` is rejected because it manages helper executables bundled
  inside a macOS application; this workflow is a repository-owned command-line
  maintenance service.
- Keeping the Codex heartbeat as executor is rejected because package
  maintenance should not depend on the Codex application, task, or AI
  diagnosis being available.

### 6. Keep update and vulnerability states independent

`npm update -g` and Pi extension updating can exit zero while `npm audit`
continues to report findings. The automation reports both states. It may apply
only non-breaking, reviewed remediation in scope; it must not automatically use
forceful audit fixes or substitute major versions solely to make the count
zero.

### 7. Roll back without destructive cleanup

Rollback first boots out the matching LaunchAgent, waits for an active run to
finish, removes only its user plist, and verifies that the label is absent from
the GUI domain. It then removes `dangerously-allow-all-scripts` from user npm
configuration and verifies the effective value is false. Reviewed
package/version-specific `allowScripts` entries can then be restored.
Tool-version rollback uses each owner's supported mechanism and must not delete
caches, lockfiles, credentials, or unrelated user data. Rollback does not
reactivate the superseded Codex heartbeat unless a separately reviewed
recovery decision explicitly selects it as the sole scheduler.

## Risks / Trade-offs

- **[Any dependency can execute code during install]** → Keep the dangerous
  setting explicit in every status report, run updates as the unprivileged
  user, avoid untrusted registries, and retain a documented allowlist rollback.
- **[A daily upstream release can break compatibility]** → Serialize stages,
  report exact versions and warnings, stop on non-zero status, and avoid
  automatic force/major remediation.
- **[A scheduler and a manual run can overlap]** → Require a per-user
  single-run lock and report a skipped-overlap outcome instead of starting a
  second mutation.
- **[A successful update can hide audit debt]** → Collect and report audit
  counts separately; unresolved moderate/high findings remain explicit.
- **[User PATH differences can select another executable]** → Resolve and
  report command paths during preflight and stop if required tools are missing
  or unexpectedly change ownership.
- **[Automation output can leak credentials]** → Use narrow configuration
  reads and summarized audit/status output; never emit full npm, shell, or
  environment configuration.
- **[Long native builds may appear hung]** → Preserve streaming progress and
  distinguish an active build from a prompt or terminated process.
- **[A global npm package has a pathological actual tree]** → Send explicit
  top-level update requests, defer reviewed heavy packages from the daily set,
  report the deferral, and maintain them in a separate timed operator window.
- **[A user is logged out at the calendar time]** → Document the user-session
  boundary, inspect the service after login, and retain manual `kickstart`
  recovery without promoting the job to a root LaunchDaemon.
- **[The Mac sleeps through 09:00]** → Use `StartCalendarInterval`, accept one
  coalesced run after wake, and rely on the single-run lock to prevent overlap.
- **[A plist has unsafe ownership or permissions]** → Refuse bootstrap until
  the per-user file is owned by the user and is not group/world writable.
- **[launchd has a minimal environment]** → Use absolute program paths, an
  explicit working directory and bounded environment, and test through
  `kickstart` rather than an interactive shell.
- **[FileProvider denies background access to the source checkout]** → Install
  a hash-verified runner bundle in user Application Support, execute from the
  user's home directory, and never grant launchd broader cloud-storage access.
- **[The installed bundle becomes stale or is modified]** → Record source
  hashes during installation, verify installed hashes during preflight, and
  require an explicit reinstall from the repository before execution.

## Migration Plan

1. Resolve command paths, versions, npm prefix/root, relevant npm policy keys,
   home `package.json#allowScripts`, scheduler inventory, and active-run state.
2. Remove the ineffective user `allow-scripts` entry and set
   `dangerously-allow-all-scripts=true` at user scope.
3. Verify the effective policy using narrow `npm config get` calls and a
   dependency operation that produces no blocked-script warning.
4. Run the canonical update order once from the user's home directory, using
   explicit eligible global npm package names and retaining eligible/deferred
   package lists, stage outcomes, and warnings.
5. Verify Pi extensions separately, record final tool versions, and record npm
   audit severity counts without claiming the findings are fixed.
6. Treat the completed heartbeat rollout as historical evidence, pause or
   delete that executor, and verify it cannot schedule another update.
7. Install the runner, lifecycle controller, and plist template into user
   Application Support with a hash manifest; verify ownership, permissions, and
   installed-file integrity without requiring launchd to access the checkout.
8. Render and install exactly one user LaunchAgent with a 09:00
   `StartCalendarInterval`, the installed runner path, the user home working
   directory, an explicit environment, and retained log paths.
9. Bootstrap the plist into the current user's GUI domain, inspect it with
   `launchctl print`, and exercise the runner once with `launchctl kickstart`.
10. Verify overlap, redaction, report retention, asleep/wake behavior, and
   non-destructive `bootout` rollback.
11. Observe at least one naturally scheduled or wake-coalesced run before
    declaring unattended behavior accepted.

Rollback reverses steps 9, 8, and 2 in that order, preserves the inert installed
bundle for audit/reinstallation, then verifies that no update is running, no
matching scheduler remains active, and npm no longer permits all lifecycle
scripts.

## Open Questions

- The first naturally triggered LaunchAgent run is retained as failure evidence
  for unscoped global npm reification; a passing natural run with the revised
  targeted policy remains required for unattended acceptance.
- The nine current npm audit findings require a separate compatibility and
  remediation decision; they are not resolved by this change.
