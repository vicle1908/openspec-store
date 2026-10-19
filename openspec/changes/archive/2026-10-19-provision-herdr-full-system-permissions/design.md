# Design: provision-herdr-full-system-permissions

## Context

See `proposal.md` for motivation and the operator's remediation decisions. The installed Herdr 0.9.5 server is a host-local launchd service. Review observed PID 2084 running with `PATH=/usr/bin:/bin:/usr/sbin:/sbin` despite the expanded PATH in the plist on disk. `herdr server reload-config` reloads Herdr configuration, not the launchd job definition or an existing process's environment.

The existing system TCC database contains the requested grants. Path strings and `auth_value = 2` alone do not establish that the current executable satisfies the record's `csreq`. The initial audit also conflated installed integration files with active hooks and private plist contents with guaranteed reminder suppression.

## Goals / Non-Goals

**Goals:**
- Reuse the current canonical CLI verification entry points and result structure while checking executable existence, role-specific grants, and actual stored signing requirements.
- Make required verification failures observable and non-successful in both maintenance runners.
- Keep package ownership, host supervision, integration installation, activation, and permission scope separate.
- Preserve current host grants and active sessions while recording incomplete operator-gated work honestly.

**Non-Goals:**
- No daemon or agent restart, permission mutation, consent bypass, private reminder maintenance, new recurring job, or external notification/publication during remediation.
- No assumption that Full Disk Access implies root/SIP bypass or blanket Automation permission.

## Decisions

### 1. Verify identities, not just TCC row presence

Reuse the existing read-only system TCC audit boundary. For every required identity, resolve the active executable, require an existing executable target and the expected TCC client type, then require every policy service to have an allowed record whose stored signing requirement accepts that executable.

Evaluate the full code requirement with macOS Security APIs or equivalent native code-signing verification. Do not compare raw `csreq` bytes to a hash, parse only one ad-hoc CDHash layout, or treat missing/malformed `csreq` as allowed. Certificate-based designated requirements must remain supported. Native Core Foundation/Security objects must be released on success and failure.

The scheduler and fallback must share the same policy and verification semantics. Prefer a small standard-library Python helper under the existing central scripts root, with a read-only JSON CLI, over duplicated embedded signing implementations. The scheduler's public `verify_tcc_provenance` entry point remains a consumer; a missing helper or malformed result must be an error, never a success fallback.

### 2. Declare permission roles explicitly

| Role | Required services |
|---|---|
| Canonical agent CLIs (`omp`, `node`, `opencode`, `goose`, `claude`, `kimi`, `herdr`) | Accessibility and Screen Recording |
| Herdr supervisor and OMP host automation | Additionally Full Disk Access |
| Existing shared host Python automation executable and applicable `org.python.python` identity | Accessibility, Screen Recording, Full Disk Access |

Track active realpaths rather than the historical Cellar versions. Python privileges are retained as existing shared host automation authority, not requirements of the notifier. Resolve the matching framework application's identity where applicable; do not manufacture a bundle record on a non-framework Python installation.

`CLEAN` requires a nonempty, completely verified required target set. An unresolved required tool or denied/missing/identity-mismatched record is drift. Missing/unreadable/corrupt TCC data or failed native verification infrastructure is an error. Non-Darwin is the only normal not-applicable skip. Keep failed identities/reasons in value-blind output.

Both runners propagate failed required checks to non-success. The scheduler also propagates reporter failures, inventory drift, target misalignment, unknown authority, and malformed reporter data rather than merely looking for the substring `conflict`.

### 3. Separate staged host configuration from applied runtime state

Herdr's package is Homebrew-managed; its installed formula has no `service do` block. The `homebrew.mxcl.herdr` filename does not make the host-local LaunchAgent reproducible or restartable through `brew services`.

A correct plist and `plutil -lint` establish only disk staging. Effective PATH acceptance requires a freshly loaded launchd job and inspection of the actual server process's PATH, plus normal server availability. A config reload cannot satisfy this gate. Server upgrades can also leave a compatible old server running; record the running version/identity separately from the selected client binary.

**Operator decision:** Initially deferred to preserve active panes, then explicitly authorized (`finish TODO, finish changes`) after verifying `herdr agent list` was empty. Reloaded `~/Library/LaunchAgents/homebrew.mxcl.herdr.plist` in `gui/502` (`PID 94235`) and verified `PATH => /Users/androidteam/.local/bin:/Users/androidteam/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin` via `launchctl print gui/502/homebrew.mxcl.herdr`, `herdr status`, and `herdr workspace list` (`w1` and `w2` restored).

### 4. Separate integration installation from activation

Reuse official `herdr integration install` and skill synchronization. Pi and OMP extension roots remain distinct; absent optional agent directories remain absent.

Of the 16 installed integrations, Pi, OMP, Kimi, OpenCode, and Kilo report lifecycle state in addition to session identity. Other installed integrations retain screen-based state detection. Existing agent processes may need new startup/session events or agent-specific restarts before loading hooks. `integration status: current` proves installed files, not live session reporting or tested restore. No forced agent restart is authorized here.

Correct operational examples to the installed `herdr pane ...` and `herdr agent ...` command surface. The notifier defaults to `POLL_SECONDS=3`, `blocked,done`, and relay delivery; with default previews its notification body can contain transcript snippets. Direct APNs is optional, not the default deployment contract.

### 5. Use supported consent behavior, not a private-plist guarantee

**Operator-approved scope revision:** Remove the original permanent-suppression acceptance condition. Existing `ScreenCaptureApprovals.plist` strings are historical private state and are left unchanged; reading them back proves neither runtime interpretation nor future suppression. No timestamp rewrite, `replayd` signal, or periodic workaround is part of remediation.

Apple's managed `forceBypassScreenCaptureAlert` restriction is a separate management mechanism and cannot be treated as an available manual-install remedy on this workstation. Ordinary macOS permission/reminder UI remains controlling. Any future managed policy or private-workaround proposal requires separate scope and approval.

### 6. Respect execution and evidence boundaries

The central store owns artifacts and tracked helper/mirror files; `shb-schedule` and `wiki` have separate repository identities. `~/Developer/scripts` is an unversioned host directory, not an independent Git repository. Preserve concurrent edits and synchronize the executed fallback and tracked mirror byte-for-byte.

For each external slice, record exact changed paths, repository HEAD where applicable, bounded verification command, timestamp, exit status, current file hashes and mirror read-back. Exclude `.git` writes, secrets, private transcripts, broad scans, deletion, permission changes, publication and package updates. The current fix request covers the previously identified implementation roots; it does not authorize the separately declined runtime restart.

Historical evidence remains dated historical evidence. Append a remediation section that identifies superseded conclusions, records current source identities and fresh results, and explicitly reports blocked tasks. Never overwrite old hashes to imply they described newer bytes, or mark a blocked runtime task complete because tests pass.

## Risks / Trade-offs

- **Broader Python authority:** Retaining the existing grants preserves requested capabilities but authorizes other scripts running under those identities. Document the role; do not attribute it to notifier necessity or silently revoke it.
- **Verification unavailable:** Required native/database checks now fail closed, which may degrade maintenance until an operator resolves the cause. This is intentional; never hide the failure with an `ERROR`-to-success fallback.
- **Shared helper deployment:** Both runners require the deployed helper. Missing or invalid helper output is an explicit failure; exact paths and smoke results belong in evidence.
- **Active work loss:** Applying live PATH requires a LaunchAgent reload. Always check `herdr agent list` first and require operator authorization before reloading `homebrew.mxcl.herdr`.
- **Concurrent source edits:** Pin evidence to current file hashes and run verification after implementation slices settle. Report unrelated inventory findings separately instead of deleting or repairing unrelated tools.

## Migration Plan

1. Reopen invalidated tasks and revise deltas to the approved consent and runtime-gate decisions.
2. Implement native identity checks, explicit role policy and fail-closed aggregation; correct docs and preserve host/store mirror parity.
3. Run isolated regression tests and a read-only native signature/TCC smoke. Inspect current permissions without prompting or granting access.
4. Append bounded external execution evidence and current hashes. Run strict OpenSpec validation; report planning validity independently from incomplete live runtime activation.
5. Reload `~/Library/LaunchAgents/homebrew.mxcl.herdr.plist` in `gui/502` under operator authorization and verify the replacement server's `PATH` and workspace restoration.

## Sources

- [Herdr v0.9.5 configuration reload and startup-only settings](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.5/docs/next/website/src/content/docs/configuration.mdx)
- [Herdr v0.9.5 integrations and activation requirements](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.5/docs/next/website/src/content/docs/integrations.mdx)
- [Herdr v0.9.5 package-manager upgrade/server lifecycle](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.5/docs/next/website/src/content/docs/install.mdx)
- [Apple privacy-control identities and code requirements](https://support.apple.com/guide/deployment/privacy-preferences-policy-control-payload-settings-dep38df53c2a/web)
- [Apple managed restrictions, including forceBypassScreenCaptureAlert](https://github.com/apple/device-management/blob/b6202ca2fbd31286a52eb160b67a4db7b4fe1f1f/mdm/profiles/com.apple.applicationaccess.yaml)
