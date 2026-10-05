# Verification Evidence: Govern Tool Version Authority and Drift

**Date:** 2026-10-04
**Change:** `govern-tool-version-authority-and-drift`
**Scope of this record:** complete implementation and verification evidence for all 32 tasks
under `govern-tool-version-authority-and-drift`.

All values are read back from disk or command output.

---

## 1. The Defect (peer-reported, independently reproduced)

`~/Developer/scripts/workstation-daily-update.sh` captured the reporter exit status in stages 8
and 9 but never read it:

```console
line 440  local snap_out snap_rc=0
line 441  snap_out="$(run_with_timeout 60 python3 .../measure-snapshot-growth.py 2>&1)" || snap_rc=$?
line 453  local inv_out inv_rc=0
line 454  inv_out="$(... inventory-workstation-toolchain.py 2>&1)" || inv_rc=$?
```

Neither `snap_rc` nor `inv_rc` was consulted. Stage 10 (`rec_rc`) did check its code, so the
pattern was inconsistent even within the same file.

**Consequence:** a crashing reporter (nonzero exit, no `Status:` line — e.g. a Python traceback)
produced no finding and was indistinguishable from a healthy run.

**Reproduced before the fix:**

```console
snap_rc=3 SNAPSHOT_STORE_EXCEEDED=0
=> crash produced NO finding (indistinguishable from healthy)
```

Two `shellcheck` SC2034 warnings flagged exactly these unused variables, against the repository's
baseline of zero findings.

---

## 2. The Fix

Applied to both the store mirror and the executed copy:

- Stage 8: on nonzero `snap_rc`, set `SNAPSHOT_MEASURE_FAILED=1`; otherwise keep the existing
  `Status: EXCEEDED` grep.
- Stage 9: on nonzero `inv_rc`, set `INVENTORY_MEASURE_FAILED=1`; otherwise keep the existing
  `SPLIT_DETECTED` grep.
- Stage 10: split the previous use of `AGENT_UNDECLARED_COUNT` as a failure indicator into
  `AGENT_COVERAGE_MEASURE_FAILED=1` on nonzero `rec_rc`, leaving `AGENT_UNDECLARED_COUNT` to mean
  what its name says.
- Summary: three new `DEGRADED` lines consuming the new flags, each stating that the state is
  *unknown, not clear*.
- Comment numbering: three colliding `# 8.` comments resolved to `1..12` with no collisions
  (the stale refresh comment removed, the validation gate renumbered to `# 12.`).

---

## 3. Why Separate Flags (not reusing the content flag)

`SNAPSHOT_STORE_EXCEEDED` means **"measured and over ceiling"**. A crash means **"could not
measure"**. These are different facts, and collapsing them would let the summary claim a ceiling
breach that no measurement supports — a reporting falsehood, which is worse than the original
silence. The flags are therefore kept separate, mirroring how the run already distinguishes
`REFRESH_FAILED` from `SCRIPT_DRIFT`.

Severity is **DEGRADED**, not fail-closed: the script's only fail-closed path is the
state-affecting skill-link stage. The three reporters are read-only, so a crash degrades
observability, not correctness. Failing closed would make page measurement stricter than an
unresolved skill link.

---

## 4. Verification After the Fix

```console
$ shellcheck scripts/workstation-daily-update.sh
0 findings                      # baseline restored (was 3 SC2034 lines)

$ bash -n scripts/workstation-daily-update.sh
syntax OK
$ bash -n ~/Developer/scripts/workstation-daily-update.sh
syntax OK

$ diff ~/Developer/scripts/workstation-daily-update.sh scripts/workstation-daily-update.sh
IN SYNC
```

**Crash now visible** (measured through the real branch logic):

```console
snap_rc=126 SNAPSHOT_STORE_EXCEEDED=0 SNAPSHOT_MEASURE_FAILED=1
=> previously: EXCEEDED=0 (silent); now: MEASURE_FAILED=1 (visible)
```

**Comment numbering:**

```console
# 1. Homebrew ... # 7. Script provenance drift ... # 8. Snapshot Store Growth Bounds
# 9. Toolchain Inventory ... # 10. Agent CLI Coverage ... # 11. Skill Content Refresh
# 12. OpenSpec Store Validation Gate          # no collisions
```

---

## 5. Full Pipeline Run (`--check`, non-mutating)

```console
exit=0
>>> [Stage 7/12]  Script Provenance Drift Check
    checked=7 drifted=0 missing_record=0
>>> [Stage 8/12]  Snapshot Store Growth Bounds
    Status: EXCEEDED (Ceiling: 1G, Total: 9.76 GiB)
>>> [Stage 9/12]  Toolchain Inventory & Prefix Reconciliation
    Status:                      RECONCILED
>>> [Stage 10/12] Agent CLI Coverage Reconciliation
    Undeclared Count:       0
>>> [Stage 12/12] OpenSpec Store Strict Validation
    Totals: 439 passed, 0 failed (439 items)

DEGRADED: one or more Git snapshot stores exceed declared size ceilings.
2026-10-04 17:15:02 +07 — Complete [MODE=check]
```

Exactly one `DEGRADED` line, and it is a **genuine finding**: the snapshot store really is
9.76 GiB against its declared 1 GiB ceiling. That is the stage working as designed, not a defect.
No `MEASURE_FAILED` line appeared, confirming the reporters ran successfully.

---

## 6. Independent Confirmation

A second session independently reproduced the defect, verified the fix, and confirmed the run
shows `drifted=0` for the executed-vs-mirror comparison. It also confirmed the comment numbering
is now collision-free.

---

## 7. Provenance Scope (verified, no manifest change required)

The three reporting scripts are invoked as `python3 "${STORE_DIR}/scripts/<name>.py"`, so the
store copy **is** the executed copy. The provenance guarantee tracks only the duplication case —
a script with an executed copy outside the store and a recorded mirror inside it. Store-owned
scripts are exempt by construction and need no manifest row, which is why
`sync-workspace-agent-skills.py` has never had one either.

**The rule to keep:** if any of these scripts ever gains an executed copy under
`~/Developer/scripts/` (a copy step, sync, or shim), it becomes a drift candidate and requires a
manifest row at that point.

---

## 8. Implementation and Verification of Change Tasks (Groups 1–5)

All 32 tasks across Groups 1–5 have been implemented and validated against live code, standalone
reporters, isolated edge-case harnesses, and the daily maintenance pipeline.

### 8.1 Group 1: Version Authority Measurement & Provenance
- **Active Provenance & Wrapper Tracing (Task 1.1)**: `inventory-workstation-toolchain.py` traces wrapper
  chains (e.g. `qoder` -> `~/.qoder/entry/qoder` -> `qodercli`). Active install roots are derived dynamically
  via `derive_install_root_and_source()` from package manifests and path components, eliminating hardcoded
  path branches.
- **Updater Dispatch Analysis (Task 1.2)**: `opencode` is dynamically classified as delegating to Homebrew
  (`updater_dispatch='delegating'`), producing 0 drift. `claude` is classified as native standalone.
  Homebrew cask preferred source for `claude` was corrected from GUI `claude` (`Claude.app`) to CLI `claude-code`.
- **Installation-Aware Authority & Target Misalignment (Task 1.3)**: Correctly flags prefix target
  misalignments when tools resolve to `/opt/homebrew` while declared prefix is `~/.npm-global` (`codex`,
  `gitnexus`, `qodercli`), while verifying clean status when tools resolve within `~/.npm-global`.
- **Unknown Authority Gating (Task 1.4)**: `cce` is classified as `authority='unknown'`, `drift_status='unknown'`.
  Unknown tools are included in `has_drift`, triggering `Status: DRIFT_DETECTED` and suppressing automated mutation.
- **Documentation (Task 1.5)**: Documented in `docs/runbooks/workstation-toolchain-inventory.md`.

### 8.2 Group 2: Drift Reporting & Robust Measurement
- **Conflict & Drift Findings (Tasks 2.1–2.4)**: Clear separation between target misalignments, independent
  writer conflicts, and compatible delegations.
- **Robust Measurement Failure Contract (Task 2.5)**: `workstation-daily-update.sh` Stage 10 was hardened
  and tested in isolation across 8 distinct failure modes:
  1. `empty_success` (exit 0, empty): `AGENT_COVERAGE_MEASURE_FAILED=1` (rejects missing output).
  2. `clean_valid_success` (exit 0, valid header + count 0): `undeclared=0, measure_failed=0`.
  3. `valid_domain_report` (exit 1, valid header + count 5): `undeclared=5, measure_failed=0`.
  4. `malformed_domain_report` (exit 1, count='bananas'): `AGENT_COVERAGE_MEASURE_FAILED=1`.
  5. `contradictory_domain_zero` (exit 1, count=0): `AGENT_COVERAGE_MEASURE_FAILED=1`.
  6. `traceback_with_count_marker` (exit 1 with Python Traceback): `AGENT_COVERAGE_MEASURE_FAILED=1`.
  7. `partial_count_only_report` (missing header): `AGENT_COVERAGE_MEASURE_FAILED=1`.
  8. `timeout` (exit 124): `AGENT_COVERAGE_MEASURE_FAILED=1`.
- **Documentation (Task 2.6)**: Documented in `docs/runbooks/agent-cli-coverage-reconciliation.md`.

### 8.3 Group 3 & 3a: Declared Update Verbs, Backstop & Policy Gating
- **Declaration Compatibility Validation (Tasks 3.1–3.2)**: `evaluate_update_path()` in
  `reconcile-agent-cli-coverage.py` rejects incompatible manager verbs (e.g. `brew upgrade codex` for
  npm-managed installations).
- **Runner Pre-Flight Safety & Stage 5 Currency (Tasks 3.3–3.5, 3a.2–3a.3)**:
  - Pre-flight authority safety check added prior to Stage 1 parses `authority_reconciliation` and derives
    package-manager specific deny rosters (`DENY_ROSTER_BREW`, `DENY_ROSTER_NPM`, `DENY_ROSTER`).
  - Package-manager specific gating in Stage 1 suppresses broad Homebrew formula/cask upgrades when Homebrew
    assets are misaligned/conflicted, and Stage 3 dynamically filters denied npm packages while allowing
    independent packages to update.
  - `agent_cli_coverage()` in `workstation-daily-update.sh` pre-checks target prefix alignment (skipping
    misaligned tools like `codex`) and user policy pause (`DISABLE_UPDATES=1`).
  - Live apply mode execution (`MODE=apply`) verified:
    - `claude update` executed, confirmed idempotent: `already up to date (2.1.289) [active: ... -> ...] (currency verified)`.
    - `codex update` executed, confirmed idempotent: `already up to date (0.160.0) [active: ... -> ...] (currency verified)`.
    - `opencode upgrade` executed, confirmed idempotent: `already up to date (1.18.34) [active: ... -> ...] (currency verified)`.
    - `auggie update` executed, confirmed idempotent: `already up to date (0.36.0) [active: ... -> ...] (currency verified)`.
    - `qoder update` executed, confirmed idempotent: `already up to date (1.1.65) [active: ... -> ...] (currency verified)`.
    - `kilo update` failed and was caught by error regex: `Kilo (kilo): FAILED (rc=0 but reported an error)`, setting `AGENT_FAILED=1`.
    - Active executable currency verified against active `$PATH` and installation root (`[active: <path> -> <real>] (currency verified)`).
  - In an isolated authority-gated harness with active deny roster (`codex`, `qodercli`, `cce`), misaligned tools
    were verified cleanly skipped: `SKIPPED (authority gate: tool in deny roster due to drift, target misalignment, or conflict)`.
- **Background Settings Non-Destructive Audit (Task 3a.1)**: Audits `.claude.json`, `.claude/settings.json`
  (including nested `env` block: `DISABLE_AUTOUPDATER`, `DISABLE_UPDATES`, `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE`,
  `autoUpdatesChannel`), and `.grok/config.toml` without mutating files.
- **Lacking Update Path Reporting (Task 3a.4)**: Accurately flags `cce` as lacking an automated update path.
- **Documentation (Task 3a.5)**: Documented in runbooks.
### 8.4 Group 4: Documented-Channel Recording & Orthogonal Findings
- **Documented Channels (Tasks 4.1–4.2)**: Verified channels recorded for multi-channel tools (`codex`,
  `claude`, `opencode`, `hermes-agent`, `bru`, `newman`, `pi`).
- **Orthogonal Findings (Tasks 4.3–4.4)**: Unsanctioned wrapper paths (e.g. `~/.qoder/entry/qoder`) reported
  as orthogonal findings without confusing ownership authority. Documented in runbooks.

### 8.5 Group 5: Pipeline Integration & Strict Validation
- **Stage 1 Non-Mutating Check Gate (Task 5.4)**: `workstation-daily-update.sh` exports `HOMEBREW_NO_AUTO_UPDATE=1`
  and `HOMEBREW_NO_INSTALL_CLEANUP=1` during `--check`, preventing background git updates and API data downloads.
- **Parity (Task 5.2)**: Verified byte-identical parity via `cmp -s` between `~/Developer/scripts/workstation-daily-update.sh`
  and `platform/openspec-store/scripts/workstation-daily-update.sh` (SHA-256 identical).
- **Manifest Scope (Task 5.3)**: Verified store-owned scripts need no manifest entries.
- **Distinct Summary Degradation (Task 5.5)**: `AUTHORITY_DRIFT_DETECTED`, `PREFIX_SPLIT_DETECTED`,
  `AGENT_UNDECLARED_COUNT`, `INVENTORY_MEASURE_FAILED`, and `AGENT_COVERAGE_MEASURE_FAILED` print distinct reports.
- **Strict Validation (Task 5.7)**: Passed strict validation:
  `openspec validate govern-tool-version-authority-and-drift --strict --json --store openspec-store` (valid: true, issues: []).
