# Proposal: provision-herdr-full-system-permissions

## Why

Herdr's host permissions and background environment were incompletely provisioned, and the initial verification overstated runtime activation and upgrade safety. This revision preserves the granted host capabilities while requiring actual signing-identity checks, fail-closed reporting, and honest operator gates.

The initial implementation granted the requested TCC services and installed the integrations. Review found that the live server still has launchd's default PATH, that the checker ignores stored signing requirements, and that absent binaries or unavailable verification can look successful. Historical execution records are not evidence that later file revisions passed the same checks.

## What Changes

- Verify the current Herdr, OMP, and shared host Python automation identities for Accessibility, Screen Recording, and Full Disk Access; retain the existing AX/Screen Recording policy for the other canonical agent CLIs. Resolve executable identities at runtime rather than pinning Cellar versions.
- Evaluate each granted TCC record's stored code-signing requirement against the actual executable. Missing executables, missing/malformed signing requirements, denied services, and Darwin database/read failures must not produce a clean result.
- Use consistent read-only verification behavior in the host scheduler and fallback Bash runner; propagate reporter failures and inventory drift into the aggregate result. Maintain byte-identical host/store script mirrors.
- Keep Homebrew as Herdr's package owner. Treat `homebrew.mxcl.herdr` as a host-local LaunchAgent: the installed formula has no service declaration. Distinguish the staged plist PATH from the running process environment.
- Retain the 16 installed integrations and official skill. Distinguish installation from activation, five lifecycle-reporting integrations from session-only hooks, and recorded session identity from demonstrated restore behavior.
- Correct the notifier documentation: three-second default polling, `blocked`/`done` transitions, third-party relay delivery by default, optional direct APNs, and transcript-preview privacy implications.
- Reconcile the proposal, design, deltas, tasks, and current evidence. Reopen runtime work that has not been applied rather than accepting a checked box as proof.

## Confirmed Scope Decisions

- The operator authorized completing the `homebrew.mxcl.herdr` LaunchAgent reload after inspecting that all panes were idle shells (`herdr agent list` empty); the reloaded `herdr server` (`PID 94235`) is verified with the expanded `EnvironmentVariables.PATH` and restored workspaces `w1` and `w2`.
- The operator selected **Use supported consent behavior**. Remove the unsupported permanent reminder-suppression guarantee. Historical private `replayd` plist edits are not proof of suppression; no further plist changes, periodic workaround, or suppression job is authorized by this remediation.
- Existing Python grants remain unchanged. They are shared host-automation privileges, not dependencies of `herdr-notifier.py`; the notifier only needs its configured files, Herdr socket/API access, and outbound delivery. Any future revocation requires separately scoped approval.

## Non-Goals

- No upstream Herdr source modifications, competing self-updater, package upgrade, or broad cleanup.
- No TCC database writes, SIP/Gatekeeper bypass, authorizationdb relaxation, permission grants/revocations, or GUI consent automation during remediation.
- No guarantee of root authority, access to every protected resource, or AppleEvents access to arbitrary receivers; the recorded functional probe targets System Events only.
- No forced agent restarts, claim that existing agents loaded newly installed hooks, or interruption of active panes.
- No APNs credentials, device tokens, transcript contents, or secrets in evidence; no push delivery or Notion publication as a verification side effect.

## Capabilities

### New Capabilities

None; reuse the four existing workstation capability paths.

### Modified Capabilities

- `workstation-remote-and-agent-permissions`: Role-scoped host permissions, actual signing-requirement validation, fail-closed provenance checks, explicit consent/reminder boundaries.
- `portable-workstation-toolchain`: Homebrew package authority, host-local supervision, effective runtime PATH acceptance and operator-approved activation, accurate integration lifecycle semantics.
- `workstation-toolchain-inventory`: Herdr ownership and shadow reporting with direct inspection and behavioral evidence rather than unrelated test-suite success.
- `agent-cli-inventory-coverage`: Consistent Homebrew-governed coverage classification and fallback/scheduler reporting.

## Impact

- `/Users/androidteam/Developer/platform/openspec-store`: Owns planning artifacts, canonical verification helpers/tests, manifests, runbook, and tracked script mirrors.
- `/Users/androidteam/Developer/shb/shb-schedule`: External implementation root for the host scheduler and its tests; acceptance requires bounded file and command evidence, not implied permission from central `allowedEditRoots`.
- `/Users/androidteam/Developer/scripts`: Unversioned host execution directory; modified fallback scripts must match their tracked store copies.
- `/Users/androidteam/Developer/wiki`: Separate repository for corrected Herdr operational documentation.
- `~/Library/LaunchAgents` and live Herdr panes: Reloaded under explicit operator instruction (`finish TODO, finish changes`) after confirming zero active pane agents; `PID 94235` is running with the configured `PATH` and restored workspaces `w1` and `w2`.
