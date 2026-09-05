# Prepared Retirement Record: `wiki-cron-validator`

## 1. Status and Invariants

- **Execution State**: **PREPARED ONLY — NOT EXECUTED**
- **Safety Gate**: Preserved in place per OpenSpec constraints and workspace safety policies. No deletion or pruning was performed during `reconcile-wiki-worktree-ownership`.
- **Target Worktree**: `/Users/androidteam/Developer/wiki-cron-validator`
- **Canonical Repository**: `/Users/androidteam/Developer/wiki`

---

## 2. Reclaimability Justification Summary

- **Git Status**: Clean, detached HEAD at `3b610d5d27d366b34b74a189bde861edbc41cfe5`.
- **Tree Equivalence**: 100% byte-for-byte identical to `/Users/androidteam/Developer/wiki` at `3b610d5`.
- **Active References**: 0 active references in Orca orchestration DB, 0 active processes (`lsof`), 0 launchctl jobs, 0 active OpenSpec tasks.

---

## 3. Approved Retirement Procedure (For Future Execution Upon Approval)

When explicit operator/user approval is granted to retire `wiki-cron-validator`, execute the following sequence:

### Step 1: Pre-execution Safety Check
```bash
# Verify working tree remains 100% clean and detached at 3b610d5
git -C /Users/androidteam/Developer/wiki-cron-validator status
git -C /Users/androidteam/Developer/wiki-cron-validator rev-parse HEAD
# Confirm no process has acquired an open descriptor
lsof +D /Users/androidteam/Developer/wiki-cron-validator
```

### Step 2: Native Git Worktree Removal
```bash
# Remove the linked worktree via canonical git worktree command
git -C /Users/androidteam/Developer/wiki worktree remove /Users/androidteam/Developer/wiki-cron-validator
```
*Note: Do NOT use raw `rm -rf`.*

### Step 3: Ecosystem Scanner Sync
In `/Users/androidteam/Developer/scripts/workspace-worktree-scan.sh`:
- Remove `"wiki-cron-validator"` from `REPOSITORIES=(...)`.

### Step 4: Post-retirement Verification
```bash
git -C /Users/androidteam/Developer/wiki worktree list
bash /Users/androidteam/Developer/scripts/workspace-worktree-scan.sh
```
Expected output:
- `git worktree list` shows only `/Users/androidteam/Developer/wiki 3b610d5 [main]`.
- Scanner shows `wiki worktrees=1 extra=0` and `linked_paths=0`.

---

## 4. Current Action

- No changes made to `/Users/androidteam/Developer/wiki-cron-validator`.
- Worktree preserved.
