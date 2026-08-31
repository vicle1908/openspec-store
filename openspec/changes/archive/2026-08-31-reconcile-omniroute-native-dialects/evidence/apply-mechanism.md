# Apply Mechanism and Safety Contract — 2026-08-30

Value-blind. No credential values, raw bodies, or secret-shaped literals appear here.

This document defines the concrete execution mechanism for tasks 2.4/2.6 and
section 4, so the apply phase has one authoritative operational reference.

## 1. Backups (task 2.4)

- Producer: `evidence/apply-backups.py` → `evidence/apply-backups.json`.
- Scope: exactly the 9 existing files this change modifies (kilo.jsonc,
  opencode.json, factory settings.json, grok config.toml, kimi-code config.toml,
  omp models.yml, pi models.json, prime models.json, cline providers.json).
  Externally owned or deferred surfaces (Claude helper/profiles/launcher,
  `.zshrc`, goose SH chat provider, Codex base config.toml) receive no backup
  here — they are not written by this change.
- Location: the manifest rollback templates under
  `~/.hermes/backups/reconcile-omniroute-native-dialects/` (outside Git; dir
  mode 0700, backups mode 0600). The script refuses any path escaping that root.
- Atomicity: temp file in the backup dir + `fsync` + `os.replace` + `chmod 600`.
- Created-file targets (`~/.codex/omniroute.config.toml`, goose
  `custom_omniroute_anthropic.json`) get no backup; their frozen baseline
  absence is the rollback record (rollback = delete the created file).
- Fail-closed preflight: a full read-only integrity pass (all 9 modify targets
  vs frozen baseline sha+mode, 2 create targets absent, untouched files vs
  baseline, drift-registered non-targets vs the drift register, no foreign
  files in the backup root, destinations inside the 0700 root) runs BEFORE any
  byte is copied; `--preflight-only` proves the gate without copying.
- Partial target set (rotation-gated): `--target <path>` (repeatable) selects
  the files to back up. The default safe batch is the 7 rotation-unaffected
  modify targets (kilo, opencode, factory, grok, omp, pi, prime); `--include-sensitive`
  adds Kimi Code and Cline and is used only after the exposed credentials are
  rotated. The preflight verifies the FULL untouched-state integrity
  regardless of the copy selection.
- Deferred-target manifest semantics: until rotation, the post-apply manifest
  declares `deferred_targets` = the Kimi Code and Cline live paths.
  `capture-manifest.py --deferred-target` marks their rollback records
  `backup_status: deferred-pending-credential-rotation` (no backup hash), and
  `manifest-check.py` accepts that state ONLY when the deferred path is a
  baseline-existing file that is absent from `changed_paths` whose live bytes
  still equal the frozen baseline. An undeclared missing backup still fails,
  and a deferred path whose bytes drifted fails as an unowned change.
- Preserved-file semantics: every baseline-existing file that this change does
  NOT write (not in `changed_paths`, not deferred) is preserved —
  `capture-manifest.py` (with `--changed-path` for each written file) records
  `backup_status: not-required-preserved` with no backup claim, and
  `manifest-check.py` requires its live bytes and mode to equal the frozen
  baseline. A preserved file that drifted fails as an unowned change; a
  preserved file falsely claiming a backup fails.
- Registered-surface semantics: externally owned surfaces (the archived
  Claude owner's helper/profile/launcher changes, the codex base
  `config.toml`, the deferred `.zshrc`, and the glob-captured
  `omniroute-pm.json` profile) are recorded in
  `evidence/baseline-drift-register.json` (v3) with their current state.
  `manifest-check.py --drift-register evidence/baseline-drift-register.json`
  accepts a registered path ONLY when the candidate records exactly the
  registered sha+mode; any further drift fails until the register is
  re-captured value-blind (e.g. after credential rotation). Registered paths
  carry no backup/rollback contract for this change — their mutation and
  rollback belong to their owning change.
- Phase-aware sensitive batch (post-rotation, no dead end): when the rotation
  is confirmed and the drift register is re-captured value-blind for the two
  sensitive paths, `apply-backups.py --authorized-drift <path>` anchors those
  paths to the REGISTERED current state instead of the frozen baseline, and
  `--applied-manifest evidence/post-apply-manifest.json` anchors the 7
  already-applied targets to the post-apply manifest — the sensitive batch can
  therefore run without touching (or being blocked by) the frozen baseline
  comparisons for surfaces already applied.

## 2. One writer and atomic replacement (per live file)

- Single writer: the root apply session. No parallel agent writes any target.
- Every live replacement is: build merged content in memory → write temp file
  in the same directory → `fsync` → `os.replace` → explicit `chmod` → parse
  validation with the CLI's native parser → bounded sentinel probe → on any
  gate failure, restore that file's mode-600 backup atomically (or delete the
  created file) and record the CLI as blocked/unchanged.
- Merge semantics: overlays are additive. Missing fields inherit the frozen
  baseline; protected fields (defaults, roles, unrelated providers) are never
  deleted or replaced. For files carrying literal credentials (Kimi Code),
  the merge is a text-splice of the named provider/model blocks only —
  untouched regions keep their exact baseline bytes; the file is never
  reparse-reserialized wholesale.
- Modes: no active mode tightening. New files are created `0600` (helper
  `0700`). Any future `0644→0600` tightening requires a separate named
  approval recorded in the post-apply manifest's `allowed_mode_tightenings`.

## 3. Known baseline-manifest defect (worked around, not edited)

The retained `pre-apply-manifest.json` (immutable rollback anchor; policy in
`drift-provenance.md` §Baseline policy) has a defective
`expected_new_file_modes` map: it lists `/Users/androidteam/.Claude-Fable`
(a path that is not in the 31-entry `files` map and matches no real target —
presumed producer defect) and omits `~/.codex/omniroute.config.toml`.

Handling:

- The baseline is preserved unchanged (rollback data derives from the intact
  `files` map; the defect is inert there).
- `manifest-check.py` validates `expected_new_file_modes` from the CANDIDATE
  manifest only, so the post-apply capture MUST declare both created files
  explicitly:
  `--expected-new-file-mode /Users/androidteam/.codex/omniroute.config.toml=0o600`
  `--expected-new-file-mode /Users/androidteam/.config/goose/custom_providers/custom_omniroute_anthropic.json=0o600`
- The candidate must NOT copy the baseline's defective map. This requirement
  is part of the post-apply gate contract.

## 4. Default-preservation assertions (task 2.6)

Executed per apply (one file at a time) and again post-apply:

1. `capture-manifest.py` → candidate manifest (schema 2, value-blind).
2. `manifest-check.py --baseline pre-apply-manifest.json --candidate
   post-apply-manifest.json` must PASS: defaults equal, no provider/model
   removals, no unapproved mode changes, no unowned byte changes, protected
   selector fragments equal, launcher identifiers preserved, rollback records
   anchored to baseline bytes.
3. `route-contract-check.py --phase candidate` must PASS all 17 checks
   (baseline negative control retained: rc=1, 5 PASS / 12 FAIL).
4. No-override default probes for all 13 candidates
   (`default-probe-matrix.json`) record actual default identities separately
   from explicit-route results (gate 5.4).
5. On any mismatch: restore that file's backup, re-capture, re-compare.

## 4a. Two-phase acceptance (partial apply, rotation-gated)

While Kimi Code and Cline are deferred, the FULL route-contract 17/17 is not
the immediate post-apply gate — the two deferred CLIs' checks cannot pass
before their apply. Acceptance is phase-split:

- Partial gate (immediately after the 9-surface apply):
  `route-contract-check.py --phase candidate` restricted via repeatable
  `--check` to the applied surfaces' named checks — pi, prime, opencode,
  kilo, droid, codex, grok, goose, omp — plus the global invariants that hold
  in the partial state: shell-byo, modes, grok-credentials,
  codex-credentials, omp-credentials, active-dlg (15 checks). The manifest
  comparator simultaneously proves Kimi/Cline byte-equality to baseline plus
  their deferred records. The kimi and cline checks are excluded until the
  sensitive batch applies.
- Full gate (17/17) runs only after rotation is confirmed and the sensitive
  batch (Kimi + Cline overlays, with `--authorized-drift` register refresh)
  is applied and green.

Live probe/default-probe completion (tasks 5.1–5.4) is likewise recorded per
applied surface only; deferred surfaces record unchanged-status evidence. The
change stays ACTIVE with blockers until the sensitive batch closes (task 6.6
archive rule).

## 5. Stale-selector policy (preserved, not deleted)

Preserved legacy registrations are NOT removed by this change (defaults and
unrelated providers are protected): goose `custom_omniroute_sh` /
`custom_omniroute` legacy `sh/Claude-Fable` rows, kilo `agent.debug.model`
legacy selector, opencode legacy `omniroute` provider, `.zshrc`
`COPILOT_MODEL` default. Retirement of stale selectors is a separately named
task requiring its own approval. The route checker enforces only that no
ACTIVE alias selects a retired or cross-dialect route.

## 6. Blockers

See `apply-blockers.json` (partial-apply policy): Kimi Code and Cline live
apply — including their live backups — are blocked-pending-credential-rotation
(transcript exposure incidents 1 and 2, `incident-credential-exposure.md`);
the other 9 surfaces apply independently once the review gate passes. The
sh/* chat-surface upstream flakiness observation affects only the legacy
`sh/Claude-Fable` row and does not reclassify this change's retained
`sh/gpt-5.6-sol` fallback evidence.

## 6a. Pi stale-model retirement (route-checker-driven)

Pi's legacy `omniroute` provider is the reconciled Responses surface itself
(the probe selector binds `sh/gpt-5.6-sol` through it), and it still carries a
stale `sh/Claude-Fable` model row. `route-contract-check.py`'s pi SH gate
requires the qualifying provider to contain `sh/gpt-5.6-sol` WITHOUT
`sh/Claude-Fable`, so the apply upserts the `sh/gpt-5.6-sol` model entry by id
and removes that one stale row from the omniroute provider. All unrelated
models (ollamacloud/*) and all other providers are preserved verbatim. This is
the reconciliation's own retirement semantics on the reconciled provider, not
a deferred-legacy row (the deferred list — goose legacy rows, kilo
`agent.debug.model`, opencode legacy `omniroute` provider — applies to
preserved providers where the checker tolerates stale rows).

## 7. Checker provenance note

`route-contract-check.py` received cosmetic docstring/comment edits on
2026-08-30 (archived-change wording) with zero check-logic delta; the baseline
negative control was re-anchored after the edit (rc=1, 5 PASS / 12 FAIL,
unchanged) and the retained result file records the re-anchor.
