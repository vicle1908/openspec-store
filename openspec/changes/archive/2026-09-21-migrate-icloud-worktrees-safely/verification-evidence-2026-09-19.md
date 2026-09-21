# Evidence and provenance

**Generated:** 2026-09-19 (eighth-pass verification session)
**Change:** `migrate-icloud-worktrees-safely`
**Scope:** read-only, metadata-only, value-blind. No iCloud mutation. No Git probe against unresolved pointers.

---

## 1. What changed in this session

Two independent evidence surfaces were produced or re-verified outside the OpenSpec store, and one
earlier evidence span was reconciled to a live filesystem path.

| # | Evidence surface | Location | Status |
|---|---|---|---|
| E1 | Declared-scope pointer enumeration (46 worktrees) | this file, §2 | **new** |
| E2 | Authorized hydrated-only reconciliation manifest re-verification | `~/Developer/vds-content-migration/` | **re-verified** |
| E3 | Restored pilot destination + quarantine permission audit | `~/Developer/recovery-pilot/` | **reconciled to live path** |

No OpenSpec task is marked complete by this document. It records evidence and states exactly which
gate each surface can and cannot advance.

---

## 2. E1 — Declared-scope pointer enumeration (metadata-only)

Method: `os.lstat` / plain-text read of each `.git` file. **No Git command was executed.**
`.git` bodies, `.git` directories, and unresolvable admin directories were never entered.

### 2.1 Source root

`/Users/androidteam/Library/Mobile Documents/com~apple~CloudDocs/project/vds/WHO-project`

- `worktrees/` contains exactly **46** entries, matching the declared worktree count.
- All 46 worktree directories report mode `0o40700`.
- Pointer kind distribution across the 46 declared worktrees:

| Pointer kind | Count | Note |
|---|---|---|
| Absolute `.../vds-scripts/.git/worktrees/<name>` or `.../vds-skills/.git/worktrees/<name>` | 41 | targets a linked-worktree admin dir |
| `/Users/vds-ai/.git-stores/...` | 1 | `vds-scripts-phase232-evolution-graduation` |
| `.git` absent (exact metadata error, `errno 2`) | 4 | see §2.3 |

Plus 26 further `.git` **files** under `worktrees/*/.venv/.../temporalio/bridge/sdk-core/` whose
contents are the relative pointer `gitdir: ../../../.git/modules/sdk-core`. These are vendored
Python-package submódulo pointers, not project worktrees; they are recorded for completeness and
excluded from the worktree classification.

### 2.2 Top-level repository pointers

| Repository | Pointer target | Target present locally |
|---|---|---|
| `vds-scripts/.git` | `/Users/vds-ai/.git-stores/vds-scripts` | **no** |
| `vds-skills/.git` | `/Users/vds-ai/.git-stores/vds-skills` | **no** |

Both pointer files are regular files (mode `0o100600`, `st_flags=0x8040`, not dataless), not
symlinks. `/Users/vds-ai` and its `.git-stores` tree do not exist on this workstation.

Because the admin directories that the 41 relative-style pointers resolve into do not exist
locally, every declared worktree remains **unresolved**. A pointer string is not backing-store
proof, and this enumeration does not claim otherwise.

### 2.3 Exact metadata errors

Four declared worktrees have no `.git` entry at all. The exact metadata result is
`OSError errno 2` ("No such file or directory") on `lstat`:

1. `vds-scripts-phase146-offline-passthrough`
2. `vds-scripts-phase152-targeted-workflow-followup`
3. `vds-scripts-phase153-confluence-sdk-hardening`
4. `vds-skills-circular-dependency-skill-20260321`

Per the metadata-inventory requirement, these are classified **unresolved** with the exact error
recorded. No in-place Git repair was attempted.

### 2.4 Structural sweep (broader, metadata-only)

A whole-source metadata walk produced, for non-excluded paths:

- total entries inspected: **400,012** (`os.walk` truncated at that count)
- `SF_DATALESS` entries: **296,687** (140,424 under `worktrees/`)
- metadata errors: **0**
- `.git`-related entries: 19 (all regular files)

This is a structural observation only. It does **not** establish readability: a non-dataless
`lstat` result is not proof that a file body is readable, and a dataless flag is not proof that the
whole tree is unreadable.

### 2.5 What E1 advances and what it does not

- **Advances:** nothing. Tasks 3.1 and 3.2 remain unchecked.
- **Reinforces:** the pre-existing `pointer-evidence/pointer_identity_evidence.json` conclusion that
  both `/Users/vds-ai/.git-stores` targets are absent (`gitdir_target_exists: false`), and extends it
  from 2 pointers to the full 46-worktree declared scope.
- **Does not close:** readability, secret, replacement, or deletion gates.

---

## 3. E2 — Hydrated-only reconciliation manifest, re-verified

### 3.1 Location and scale

| Item | Path | Measured |
|---|---|---|
| Destination root | `~/Developer/vds-content-migration/WHO-project` | 3.1 GB |
| Manifest | `~/Developer/vds-content-migration/migration-manifest.json` | 16,114 entries, 4.0 MB |
| Quarantine | `~/Developer/vds-content-migration/sensitive-quarantine` | 6 files |
| Out-of-contract note | `~/Developer/vds-content-migration/OUT-OF-CONTRACT-RECONCILIATION.txt` | 905 B |

Manifest version key: `version` present; `entries` keyed by source-relative path with
`mode`, `mtime_ns`, `sha256`, `size`.

### 3.2 Independent hash verification

Every manifest entry was independently re-read at the destination and re-hashed:

| Check | Result |
|---|---|
| Manifest entries | 16,114 |
| Destination files present | 16,114 / 16,114 |
| `size` match | 16,114 / 16,114 |
| `sha256` match | 16,114 / 16,114 |
| Missing at destination | 0 |
| Size or digest mismatch | 0 |
| Manifest entries absent at source | 0 |

This is a genuine **digest** verification, not a byte-count-only check.

### 3.3 Coverage against the declared scope (the important limit)

| Measure | Value |
|---|---|
| Destination files delivered and verified | 16,114 |
| Non-excluded source entries | 155,645 |
| Source entries not represented in the manifest | 135,539 |
| Source **hydrated** (non-`SF_DATALESS`) regular files | 20,563 (3,357 MB) |
| Source **dataless** regular files | 120,571 (3,158 MB logical) |
| Hydrated files **not** delivered | 4,449 (68.1 MB) |

Per-worktree coverage:

| Measure | Count |
|---|---|
| Declared worktrees | 46 |
| Worktrees with ≥1 delivered file | 26 |
| Worktrees with **zero** delivered files | 20 |

The 20 zero-delivery worktrees appear at the destination only as directory skeletons — the few
entries present under them are macOS `*.nosync` symlinks (`.venv -> .venv.nosync`,
`__pycache__ -> __pycache__.nosync`, `.pytest_cache -> .pytest_cache.nosync`) and one stale absolute
symlink into `PAR-project`. Representative counts: `vds-skills-phase131-dev` 39 dirs / **0** files;
`vds-scripts-phase232-evolution-graduation` 559 dirs / 2 files.

Of the 4,449 undelivered hydrated files, the dominant group is generated tooling output —
1,978 under `graphify-out/cache/`. The remainder cluster in worktree subdirectories
(~72–73 files each for most delivered worktrees).

### 3.4 Gate status after E2

`reconciliation-evidence.md` already states this run was **outside the explicit seven-file
non-sensitive allowlist and outside the restricted-copy contract**, and that it must not be
generalized. Re-verification confirms both the scale claim (16,114 entries) and its verification
scope, and adds the coverage limit above.

- **Advances:** nothing by itself.
- **Reinforces:** a substantial *partial* hydrated delivery exists and its delivered entries are
  hash-intact.
- **Does not close:** task 3.1 (no independent backing-store identity), 3.2 (no candidate
  replacement clone), any 4.x task, or 5.1. The destination is **not** a complete replacement for
  the declared source scope.

Whether this hydrated-only delivery may be reclassified as satisfying "reconstruct locally" under
task 3.2 is an **owner decision**, not an inference this evidence makes. The honest reading is that
it is a partial local reconstruction of readable content with no Git history and no coverage of 20
declared worktrees.

---

## 4. E3 — Pilot destination reconciled to a live path

`design.md` and task 2.4 previously noted that the historical pilot destination
`~/Developer/WHO-project-worktrees/` was "currently absent from disk in `~/Developer`", leaving the
retained-pilot-content audit without a live filesystem path.

That destination now exists at `~/Developer/recovery-pilot/`:

| Directory | Mode | Files | Contents |
|---|---|---|---|
| `recovery-pilot/WHO-project-worktrees/` | `0o40755` | **7** | `vds-scripts-phase128/{pyproject.toml,README.md,AGENTS.md}`, `phase150-eval-timeout-resilience/{pyproject.toml,README.md,AGENTS.md,CLAUDE.md}` |
| `recovery-pilot/quarantine-pilot/` | `0o40700` | **4** | same tree, files `0o100600`; `.venv`-style symlinks present |
| `recovery-pilot/restricted-nonsecret/` | `0o40755` | **0** | empty |

### 4.1 Findings

1. **The 7-file pilot total is confirmed on a live path.** This matches the recorded pilot manifest
   total (18 allowlisted candidates, 7 copied and destination-verified, 11 not copied, 0 read
   failures). `vds-scripts-phase128/AGENTS.md` is present as recorded. No generalization beyond 7
   files is made.

2. **`restricted-nonsecret/` is now empty**, whereas task 2.4's evidence recorded the four flagged
   files as quarantined **from** `restricted-nonsecret/`. The pilot destination still contains all 7.

3. **The 4 quarantined files were copied, not moved.** All four `quarantine-pilot/` files are
   byte-identical (SHA-256) to their counterparts still present in `WHO-project-worktrees/`:
   `vds-scripts-phase128/AGENTS.md`, `vds-scripts-phase128/README.md`,
   `phase150-eval-timeout-resilience/AGENTS.md`, `phase150-eval-timeout-resilience/CLAUDE.md`.
   The sensitive-name matches in this pilot were therefore benign content over-matching the
   category filter — consistent with the design's expectation that filename/content matching is
   conservative.

4. **`WHO-project-worktrees/` remains a retained pilot destination, not an empty general recovery
   destination.** Because sensitive content was flagged in this pilot, the secret gate stays
   **blocked** and the general recovery destination remains unavailable for further batches, per
   the bounded-copy and quarantine requirements.

### 4.2 Permission snapshot

The pilot and quarantine destinations are two distinct dispositions and are recorded as two
separate point-in-time snapshots; neither overwrites the other:

| Snapshot | Directories | Files |
|---|---|---|
| `WHO-project-worktrees/` (general pilot destination) | `0o755` | `0o644` |
| `quarantine-pilot/` (restricted) | `0o700` | `0o600` |

The quarantine destination is permission-restricted as required.

---

## 5. AgentMemory note

A separate audit of the migrated content found an AgentMemory-shaped defect worth recording for the
owner, independent of the migration gates: the hydrated destination includes
`vds-skills/.../graphify-out/cache/` and similar generated artifact trees delivered as ordinary
files. Reconstructing a *working* development tree from this destination would require
regenerating those caches rather than trusting them. This is operational guidance only and does not
close or advance any gate.

---

## 6. Summary gate table

| Gate | State after this session | Reason |
|---|---|---|
| Metadata inventory | **closed** | E1 enumerates all 46 declared worktrees with pointer kind, flags, and exact errors |
| Capacity | passed (projection only) | free space exceeds logical projection; not readability |
| Readability | **blocked / unverified** | 4,449 hydrated files undelivered; 20 worktrees have zero delivery; capacity ≠ readability |
| Secret | **blocked** | sensitive-name matches exist; quarantine excluded; general destination remains unavailable |
| Replacement | **unresolved** | `/Users/vds-ai/.git-stores/*` absent; no verified clone; E2 is partial and outside contract |
| Deletion authorization | **absent** | no exact-path authorization record exists for any iCloud path |
| Deletion execution | **prohibited** | no deletion capability; guard is fail-closed |

Tasks 3.1, 3.2, 4.1, 4.3, and the gate in 5.1 accordingly remain **unchecked**.
