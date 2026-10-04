# Verification Evidence: Govern Tool Version Authority and Drift

**Date:** 2026-10-04
**Change:** `govern-tool-version-authority-and-drift`
**Scope of this record:** the measurement-failure defect fix (task 2.5), which was already
implemented when this change was created and is recorded here because it is part of this
change's scope.

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

## 8. Status of the Remaining Tasks

Task 2.5 is complete. The remaining tasks (version-authority measurement, drift detection,
update-verb/backstop wiring, documented-channel recording, and pipeline integration) are **not
yet implemented** — the existing scripts implement read-only *coverage reconciliation* only, and
do not yet compute version authority, drift, or the self-update backstop. This record therefore
claims only what was verified.
