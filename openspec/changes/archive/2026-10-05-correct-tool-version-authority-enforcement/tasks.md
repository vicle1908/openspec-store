# Tasks

## 1. Provenance and authoritative-copy correctness

- [x] 1.1 Define the shared supported-updater and installation-source data model used by inventory and coverage classification; verify unknown tool/source combinations fail closed in an in-memory harness.
- [x] 1.2 Correct provenance precedence so Homebrew Cellar/Caskroom paths containing `node_modules` remain Homebrew-owned; verify formula, cask, npm-global, vendor, and unknown fixtures produce distinct source classifications.
- [x] 1.3 Ensure inventory duplication output always includes the active authoritative copy before appending other discovered copies; verify a Homebrew copy plus a toolbelt duplicate reports both copies and nonzero duplication.
- [x] 1.4 Make wrapper records inherit resolved target source, authority, target root, drift state, and update eligibility; remove the Qoder name-specific shell exception and verify a misaligned target gates both wrapper and target.
- [x] 1.5 Reconcile Prime-Agent and other ambiguous package-wrapper classifications from verified receipt, realpath, and runtime evidence; verify unknown or unhealthy provenance is reported with an evidence gap and no automated mutation.

## 2. Updater declarations and target alignment

- [x] 2.1 Populate the conservative updater registry only with commands verified for the tool and installation source; verify arbitrary nonempty and source-mismatched commands resolve to no supported update path.
- [x] 2.2 Replace the invalid Kilo declaration with its verified supported command and reconcile Kilo's inventory, coverage roster, and runbook status; verify no report contains the obsolete command.
- [x] 2.3 Validate every covered declaration against elected authority, active realpath, target scope, and registry entry; verify an npm declaration cannot authorize a Homebrew-owned target or a wrong-prefix write.
- [x] 2.4 Generate all npm remediation commands against the declared sanctioned npm prefix while reporting the active root separately; verify scoped and unscoped package fixtures never recommend an inferred system prefix.
- [x] 2.5 Normalize manager query identities before applying deny rosters, preserving scoped names while removing version suffixes; verify denied version-suffixed packages are excluded and unrelated packages remain eligible.
- [x] 2.6 Split Homebrew formula and cask deny rosters and apply them independently; verify one misaligned cask does not suppress unrelated formula upgrades and one formula finding does not suppress unrelated casks.

## 3. Pause policy and background-writer evidence

- [x] 3.1 Centralize pause truthiness parsing for `DISABLE_UPDATES` and `DISABLE_AUTOUPDATER`; verify string, numeric, and boolean true forms pause all mutation stages while read-only reports still run.
- [x] 3.2 Preserve audit-as-is behavior for pause configuration; verify reporters emit normalized setting names and booleans without changing configuration files or exposing values.
- [x] 3.3 Implement bounded value-blind inspection of accessible user and system LaunchAgents; verify labels, executable baselines, schedule metadata, and environment-key names are retained while values and secrets are omitted.
- [x] 3.4 Implement bounded user-crontab inspection with redacted arguments and explicit limitations for root-owned jobs, inaccessible domains, arbitrary script indirection, and external process engines; verify the report does not claim exhaustive conflict absence.
- [x] 3.5 Report candidate independent scheduled writers as authority findings only when observable evidence supports the association; verify unknown or indirect writers remain bounded unknowns and gate only according to explicit evidence policy.

## 4. Post-update outcome and currency reporting

- [x] 4.1 Separate updater execution status, local version mutation, and release-channel currency in the agent-stage result model; verify unchanged before/after versions are idempotent but not current without channel evidence.
- [x] 4.2 Add supported channel adapters or explicit unverified outcomes for each covered tool; verify only a successful channel comparison may emit `current`, while offline or unavailable comparison emits `unverified`.
- [x] 4.3 Treat zero-exit updater output containing recognized error or failure diagnostics as an update execution failure; verify it cannot produce a successful current result.
- [x] 4.4 Preserve independent reporting classes for authority drift, coverage findings, updater failures, measurement failures, pause skips, and currency unknown; verify a multi-defect stub run emits distinct summary fields.

## 5. Documentation, declarations, and mirror integration

- [x] 5.1 Reconcile the covered and uncovered rosters across both reporters, both runner declarations, and both runbooks from one measured current-state source; verify no CLI has contradictory status or updater command.
- [x] 5.2 Update `workstation-toolchain-inventory.md` with provenance precedence, conservative registry behavior, prefix remediation, pause semantics, bounded schedule scope, and currency terminology.
- [x] 5.3 Update `agent-cli-coverage-reconciliation.md` with the normalized manager-filter contract, Kilo status, wrapper inheritance, updater registry, and idempotence-versus-currency distinction.
- [x] 5.4 Keep the executed and store copies of `workstation-daily-update.sh` byte-identical and update the existing provenance manifest only if the implementation changes its governed scope; verify digest parity with `cmp` and SHA-256.
- [x] 5.5 Add focused regression fixtures for Cellar `node_modules`, authoritative-copy duplication, wrapper inheritance, scoped npm filtering, pause truthiness, invalid updater declarations, zero-exit error output, and unknown currency.

## 6. Corrective evidence and release gates

- [x] 6.1 Record the archived change's stale or unsupported claims in the new active evidence record with task identifiers, current paths, line references, statuses, and value-blind metadata; do not edit the archive.
- [x] 6.2 Verify standalone reporters and focused fixtures run without network access, updater verbs, package-manager mutations, configuration writes, or secret-bearing output.
- [x] 6.3 Verify check mode executes no update verbs and applies per-tool/per-manager gates without broad unrelated suppression; use stubs or dry-run seams rather than live package upgrades.
- [x] 6.4 Verify the archive directory remains byte-unchanged throughout implementation and evidence collection; record any mismatch as a blocking integrity finding.
- [x] 6.5 Run shell syntax/lint, Python lint, focused behavioral checks, mirror parity, strict OpenSpec validation, and archive-readiness verification; mark the corrective change ready only when all results and limitations are recorded truthfully.
