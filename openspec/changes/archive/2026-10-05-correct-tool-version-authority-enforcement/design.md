# Design

## Context

See `proposal.md` for motivation. The current implementation has two read-only Python reporters and two byte-identical shell runners. The reporters independently classify provenance and updater commands; the runner converts inventory JSON into manager-specific deny rosters before mutation stages. Existing specifications already require one version authority, active-path provenance, cross-stage gating, explicit coverage, value-blind evidence, and immutable archives. This change closes inconsistencies in those contracts rather than introducing a new update system.

## Goals / Non-Goals

**Goals:**

- Establish one conservative updater contract that can be consumed by both reporters and the shell declaration/gating layer.
- Preserve active installation provenance: Homebrew Cellar/Caskroom, npm global, vendor download, toolbelt, and unknown remain distinct.
- Make wrapper identity a projection of the resolved target instead of a second authority.
- Make all manager filters compare normalized package identities.
- Separate execution success, local version mutation, and upstream channel currency.
- Discover accessible scheduled writers without exposing configuration values or overstating scan coverage.
- Produce reproducible, value-blind corrective evidence and preserve exact mirror parity.

**Non-Goals:**

- No package-manager or updater execution during implementation verification beyond explicitly isolated stubs.
- No migration of tools between package managers.
- No privileged inspection of root LaunchDaemons or inaccessible launchd domains.
- No universal claim that a successful local updater proves the newest upstream release.
- No archive rewrite, archive move, or retroactive task ticking in the archived change.

## Decisions

### 1. Use a conservative supported-updater registry

Define a declarative registry keyed by tool identity and installation source. Each entry records the supported invocation, whether it mutates locally, any compatible delegating writer, accepted target scope, and the evidence source used to verify it. The registry is an allowlist, not a parser for arbitrary command strings.

Unknown, ambiguous, or source-mismatched declarations resolve to `updater_dispatch=none` and an explicit evidence gap. This is safer than attempting to infer safety from a nonempty verb. Kilo is represented by its documented `upgrade` command, not the invalid `update` command. OpenCode's native command remains a compatible dispatch entrypoint only when its installation detector identifies the underlying manager.

### 2. Keep provenance precedence explicit

Resolve source in this order:

1. Real executable and wrapper target.
2. Homebrew Cellar/Caskroom receipt boundaries.
3. Ecosystem package manifest boundaries, including scoped packages.
4. Vendor/toolbelt roots.
5. Unknown with evidence gaps.

A Homebrew Cellar path containing `libexec/node_modules` remains Homebrew-owned. The authoritative active copy is always included in duplicate-copy output before other discovered copies are appended. Wrapper records inherit the target's source, authority, target root, drift status, and updater eligibility.

### 3. Separate declaration, authority, and mutation gates

The inventory produces facts and findings. The coverage reporter validates declared handling against the same registry. The shell runner consumes normalized findings and produces package-manager-specific rosters:

- formula deny roster;
- cask deny roster;
- npm package deny roster;
- agent-stage deny roster;
- pause roster.

A finding for one cask MUST NOT suppress unrelated formula updates. An npm deny comparison strips only the query's version suffix while preserving scoped package names. Every roster entry carries the underlying tool identity, so wrappers do not require name-specific shell branches.

### 4. Treat currency as a separate state

Post-update reporting stores three independent facts:

- execution status: succeeded, failed, timed out, or skipped;
- local mutation: changed or unchanged;
- channel currency: current, behind, or unverified.

`before == after` proves only local idempotence. It can produce `unchanged/idempotent` but not `current` without an allowed channel comparison. Check mode and offline local checks use `unverified`. A channel adapter may report `current` only after a successful comparison against the selected release channel; unavailable or failed channel checks remain unverified rather than failing open.

### 5. Normalize pause state without changing configuration

Use one parser for `1`, numeric one, boolean true, and case-insensitive `true`. Evaluate both `DISABLE_UPDATES` and `DISABLE_AUTOUPDATER` where the policy contract calls for them. Record setting names and normalized booleans only. A global pause gates all mutation stages while read-only inventory and reconciliation still run.

### 6. Bound scheduled-writer discovery

Read accessible user LaunchAgents, accessible system LaunchAgents, and the user's crontab using structural parsing. Emit label/path, executable baseline, schedule keys, and environment-key names only. Never emit environment values or raw command strings containing sensitive arguments. Candidate writer classification is advisory evidence; hidden script indirection, root-owned jobs, inaccessible domains, container engines, and other external schedulers become explicit unknown boundaries rather than a clean conflict-free assertion.

### 7. Preserve mirror and archive ownership

The store script is canonical for review, and `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` remains its executed mirror. Changes MUST be synchronized and digest-checked through the existing provenance manifest contract. The archived prior change is read-only; corrective evidence lives only in this active change and, after implementation, its live evidence or runbook locations.

## Risks / Trade-offs

- A strict registry may classify a newly released tool as unsupported until evidence is added. This intentionally favors fail-closed mutation over speculative execution.
- Channel-currency verification may remain `unverified` when a vendor has no stable manifest or network access is unavailable. This is more truthful than calling unchanged versions current.
- Bounded schedule inspection cannot detect arbitrary script indirection or privileged jobs. The report will expose the boundary instead of implying exhaustive detection.
- Shared registry data reduces drift between reporters but requires careful mirror/import handling so shell declarations cannot silently diverge from Python classification.
- Correcting Kilo and Prime-Agent may change the covered count. Runbooks and evidence must be updated from the live measured roster rather than preserving historical counts.
