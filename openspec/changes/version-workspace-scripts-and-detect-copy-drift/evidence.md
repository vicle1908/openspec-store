# Verification Evidence: Version Workspace Scripts and Detect Copy Drift

## Date: 2026-10-04

Targets:
- `~/Developer/scripts/workstation-daily-update.sh` — the daily 08:00 launchd job,
  which gains the drift stage. `~/Developer` is not a Git repository.
- `openspec-store/scripts/` — the recorded mirrors, under version control.

---

## 1. Script provenance manifest (tasks 1.1–1.2)

- **Artifact**: `openspec-store/config/script-provenance-manifest.tsv`
- **Format**: `<executed path><TAB><recorded path or -><TAB><authority>`
- **Content**: 7 executed scripts declared, authority always `executed`.
- **Verification (1.2)** — every executed path resolves to a readable file:

  ```text
  OK   .../scripts/workstation-daily-update.sh
  OK   .../scripts/workspace-worktree-scan.sh
  OK   .../scripts/knowledge-refresh/refresh-knowledge-indexes.sh
  OK   .../scripts/knowledge-refresh/knowledge-status.sh
  OK   .../scripts/knowledge-refresh/sync-notion-knowledge.sh
  OK   .../scripts/knowledge-refresh/install-hooks.sh
  OK   .../scripts/knowledge-refresh/install-launchagent.sh
  checked=7 bad=0
  ```

- The manifest was initially written declaring recorded paths for the two
  unversioned scripts; that was corrected to `-` because those mirrors did not
  exist yet, so the declaration never named a nonexistent artifact. Task 2.4 then
  restored the paths once the mirrors existed.

---

## 2. Recorded mirrors for the unversioned scripts (tasks 2.1–2.4)

### 2.1 / 2.2 Byte identity

```text
workstation-daily-update.sh      exec=64a70f27f6ad rec=64a70f27f6ad IDENTICAL
workspace-worktree-scan.sh       exec=4402ea55ffd0 rec=4402ea55ffd0 IDENTICAL
```

Both recorded files are tracked by `git ls-files` (committed in `de38a342`).

### 2.3 The recorded copies are inert

- **Command**: `grep -l "openspec-store/scripts" ~/Library/LaunchAgents/*.plist`
- **Observed**: no match. Both jobs still reference their installed paths:

  ```text
  com.developer.workstation-daily-update → /Users/androidteam/Developer/scripts/workstation-daily-update.sh
  com.developer.index-refresh            → /Users/androidteam/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh
  ```

### 2.4 Every declared script states a recorded path that exists

```text
OK: workstation-daily-update.sh -> scripts/workstation-daily-update.sh
OK: workspace-worktree-scan.sh  -> scripts/workspace-worktree-scan.sh
OK: refresh-knowledge-indexes.sh, knowledge-status.sh, sync-notion-knowledge.sh,
    install-hooks.sh, install-launchagent.sh
total=7 unresolved=0
```

---

## 3. Reconcile the recorded knowledge-refresh pair (tasks 3.1–3.5)

### 3.1b Direction confirmed by evidence *before* reconciling

- All 12 repositories present only in the installed inventory:

  ```text
  verified=12 problems=0        # each is a real git repo AND carries a live
                                # .gitnexus or graphify-out index
  ```

- Repositories present only in the recorded copy (would be dropped):

  ```text
  (empty = none)
  ```

So reconciling cannot drop an indexed repository nor omit a gone one.

### 3.1 Inventory reconciled

```text
before: installed 32 entries | recorded 20 entries
after : installed 32 entries | recorded 32 entries
cmp: IDENTICAL
```

### 3.2 Approval digest regenerated

```text
recorded digest : c855c50d5b1117d7eb14fdcfe91279066b5fe6bcf58f0f3d0076da331cf5fde7
recorded inventory hash: c855c50d5b1117d7eb14fdcfe91279066b5fe6bcf58f0f3d0076da331cf5fde7
installed digest: c855c50d5b1117d7eb14fdcfe91279066b5fe6bcf58f0f3d0076da331cf5fde7
```

All three now agree; format remains `<sha256>  <filename>`.

### 3.3 Running job unaffected

```text
$ refresh-knowledge-indexes.sh --check
refresh: inventory approved (c855c50d5b11...)
```

The approval gate passes, so `com.developer.index-refresh` is not blocked. The
`rc=1` is the correct freshness result (25 of 32 indexes stale), not an approval
failure.

### 3.4 Remaining knowledge-refresh files — one drifted, reported not reconciled

- Five of six are byte-identical.
- **`sync-notion-knowledge.sh` differs**: the executed copy (mtime
  `2026-10-04 10:17`) is newer and adds `wiki/entities/shb.md` and
  `wiki/entities/omniroute.md`; both referenced files exist, so the edit is
  complete.
- This task authorises reporting differences, not reconciling them, so it is left
  drifted deliberately and is surfaced by the group-4 drift stage.

### 3.5 Requirement correction applied via the delta

The `MODIFIED` delta deliberately does **not** hand-edit the main spec: per the
store's workflow a `MODIFIED` requirement merges at *archive*. Verified the delta:

- contains no `20-repo` literal (0 occurrences);
- contains no unconditional `return code 0` assertion (0 occurrences);
- asserts agreement instead (`same repository entries`, `taken from the installed
  inventory`);
- retains all 3 original scenarios plus 2 freshness scenarios.

The main spec still holds the old text (1 occurrence), as expected pre-archive.

---

## 4. Drift detection (tasks 4.1–4.7)

### 4.1 Helper reports per-pair state

Live run during development, which correctly found two real drifts:

```text
      - workstation-daily-update.sh: DRIFTED (executed f7d499777b5d != recorded 64a70f27f6ad)
      - workspace-worktree-scan.sh: in sync
      - refresh-knowledge-indexes.sh: in sync
      - knowledge-status.sh: in sync
      - sync-notion-knowledge.sh: DRIFTED (executed 30e19f65dee6 != recorded 1d9f604116ce)
      - install-hooks.sh: in sync
      - install-launchagent.sh: in sync
    checked=7 drifted=2 missing_record=0
```

After the mirror of the edited script was refreshed, exactly the one genuine
pre-existing drift remained:

```text
checked=7 drifted=1 missing_record=0
```

### 4.2 Content only — a permission change is not drift

```text
digest before chmod 700 = 4402ea55ffd0...
digest after  chmod 700 = 4402ea55ffd0...   (content unchanged)
helper verdict for that file: in sync
mode restored to -rwxr-xr-x
```

### 4.3 A drifted script is named, with which copy differs

Appending a marker to the **recorded** copy of `install-hooks.sh`:

```text
      - install-hooks.sh: DRIFTED (executed 1df79eb5e385 != recorded 0669488f2148)
```

Marker reverted → verdict returned to `in sync`.

### 4.4 The check never writes to either copy

Across the deliberate-drift run, the executed copy's digest was unchanged:

```text
executed: SAME
```

(A stray file created by a mistyped test path was detected and removed; it was a
test artifact, not produced by the helper.)

### 4.5 Stage placement and renumbering

```text
[Stage 1/9] ... [Stage 9/9]
parity=399  drift=422  validation=457   → ORDER OK
```

Drift sits after parity and before validation.

### 4.6 Drift is a reported degradation, not fail-closed

```text
WARNING: executed scripts differ from their recorded mirrors (or lack a record).
Reported only — neither copy is modified. Reconcile deliberately after review.
...
DEGRADED: executed scripts drifted from their recorded mirrors (or lack a record).
```

The run still reached stage 9/9 and exited `0`; the parity fail-closed path did
not trigger.

### 4.7 Success when every pair agrees

The helper reports the per-pair state and a `checked=/drifted=/missing_record=`
summary and always returns `0` (report-only), so an agreeing set yields an
explicit no-drift report.

---

## 5. Verification and integration (tasks 5.1–5.7)

### 5.1 `--check` does not mutate either copy

```text
before: 05b28d9ce42f3062ea521a7b79b557970490e90ae9aa59c6b035863aa94b6cb5
check rc=0
after : 05b28d9ce42f3062ea521a7b79b557970490e90ae9aa59c6b035863aa94b6cb5
PASS: --check did not mutate recorded copies
```

### 5.2 Full run: nine stages, zero regressions

```text
rc=0
stages executed: 9
Totals: 438 passed, 0 failed (438 items)
```

### 5.3 Idempotence

```text
run1 drift: checked=7 drifted=1 missing_record=0
run2 drift: checked=7 drifted=1 missing_record=0
```

### 5.4 No LaunchAgent change required

```text
com.developer.workstation-daily-update → .../scripts/workstation-daily-update.sh   Hour 8  Minute 0
com.developer.index-refresh            → .../scripts/knowledge-refresh/refresh-knowledge-indexes.sh  Hour 2  Minute 30
```

Both program paths and schedules are unchanged.

### 5.7 No requirement still asserts a fixed 20-repository inventory

- Delta: `0` occurrences of `20-repo`.
- Main specs: `1` occurrence, in `organization-namespaces`, which is the
  requirement this change's `MODIFIED` delta replaces at archive. That is the
  expected pre-archive state, not an unaddressed leftover.

---

## 6. Durability (task 5.6)

All artifacts and recorded mirrors are committed: `de38a342`, `8f6a68bd`,
`95f51e9f`. Verified with `git ls-files`.

---

## Residual risks

- **`sync-notion-knowledge.sh` remains drifted** (executed newer, adds two
  existing wiki entity paths). Reported by the drift stage; reconciling it is
  deliberate follow-up work, deliberately not absorbed here.
- **A recorded mirror can go stale again.** That is the point of the drift
  stage: it now surfaces within a day rather than being discovered by accident.
  A prior one-off reconciliation (`4741f899`) did not hold.
- **25 of 32 knowledge-refresh indexes are stale** (`Total: 32 FRESH: 7
  STALE: 25`), so `refresh-knowledge-indexes.sh --check` exits `1`. That is a
  true freshness result. This change corrects the requirement that demanded
  exit `0`; refreshing the indexes is separate work.
- **Latent defect not fixed** (out of scope, recorded): in single-repository mode
  the script sets the Graphify state to `"STALE (<rev> != <rev>)"` but tests for
  the bare string `"STALE"`, so a repository with a stale Graphify index and a
  fresh GitNexus index is reported fresh and the check returns `0`. The
  full-inventory path is unaffected.
- **Symlinking the duplicated copies instead of duplicating them** is deferred;
  the manifest now records the relationship so a future change can alter it
  deliberately.
