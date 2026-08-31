# Archive Invalidity Report: reconcile-omniroute-native-dialects

Date: 2026-08-31 · Read-only analysis — the archived directory is never edited by this change.

## Summary

The archived change `2026-08-31-reconcile-omniroute-native-dialects` was closed and archived on 2026-08-31 while verifiable closure defects remained. This report enumerates each defect with read-only citations.

## Defect 1: Unreleased credential-rotation gate — codex and Cline applied anyway

**Citation:**

- `evidence/apply-blockers.json` lines 15–30: codex Code live-apply `blocked-pending-credential-rotation` with release condition "User confirms the affected keys have been rotated upstream, or explicitly approves proceeding without rotation."
- `evidence/apply-blockers.json` lines 32–47: Cline live-apply same blocker.
- `evidence/post-apply-manifest.json` `apply_log` includes `~/.codex` and `~/.cline/data/settings/providers.json` — both sensitive targets were applied.
- `tasks.md` task 5.1 ticked; task 5.7 ticked despite the blocker file saying task 5.7 "stays unchecked."
- `tasks.md` task 6.6: "Archive only if every required applied route is green" — the codex routes were applied but their rotation gate was never released.

**Defect:** the archive violated its own safety lock by applying and archiving over an unreleased security gate.

## Defect 2: SH route model-ID contamination in final-evidence-manifest

**Citation:**

- `evidence/final-evidence-manifest.json` line 12: `"canonical_sh": "POST http://localhost:20128/v1/responses sh/Claude-Fable"` — the SH route model ID is wrong; the change's contract requires `sh/codex`.
- `evidence/final-evidence-manifest.json` lines 28, 31, 33, 35: live sentinel rows cite `sh/Claude-Fable` as the SH model.
- `tasks.md` task 1.1: the approved route models are `pm/Claude-Fable` and `sh/codex`.
- `proposal.md` "Corrected routing contract" table: `sh/codex` for the Responses route.

**Defect:** the archived manifest's SH route model ID is contaminated; the correct SH route model is `sh/codex`.

## Defect 3: Post-apply manifest omits the codex apply

**Citation:**

- `evidence/post-apply-manifest.json` `applied_at`: `2026-08-31T11:09:42` — captured before the codex apply.
- `evidence/partial-apply-attempts.json` attempt 3: codex `ROLLED-BACK post-write probe failure` with `sha_restored: 8626abe9...` at `recorded_at: 2026-08-31T07:44:38+07:00`.
- The codex live config applied at 2026-08-31 ~11:29:04 (20 minutes after the manifest was written) — confirmed by the codex apply existing on disk but the post-apply manifest's `apply_log` and `mutated_files` omitting it.
- `tasks.md` task 4.4 ticked for codex.

**Defect:** the post-apply manifest was captured before the codex apply and never re-captured; the codex apply is unrecorded in the closure manifest.

## Defect 4: omp mode tightening without named approval

**Citation:**

- `evidence/pre-apply-manifest.json`: `~/.omp/agent/models.yml` baseline mode `0o644`.
- Live disk mode at 2026-08-31: `0o600`.
- `tasks.md` task 2.4: "any future `0644→0600` change requires a separate named approval recorded in the post-apply manifest's `allowed_mode_tightenings`."
- `evidence/post-apply-manifest.json`: no `allowed_mode_tightenings` field exists; the omp mode change is not ratified.

**Defect:** the omp file mode was tightened from 0644 to 0600 without the named approval the change's own policy required.

## Defect 5: Unmapped `new_files` label `~/.Claude-Fable`

**Citation:**

- `evidence/final-evidence-manifest.json` `new_files`: includes `"~/.Claude-Fable": "0600"` — a label that maps to no verified apply target in the change's write set.
- The two verified created files are `~/.codex` and `~/.config/goose/custom_providers/custom_omniroute_anthropic.json`.
- `evidence/post-apply-manifest.json` `new_files`: empty list.

**Defect:** the final-evidence-manifest claims a `new_files` entry for a path that was never a verified apply target; its referent is unknown and requires owner reconciliation.

## Credential scan

No credential values appear in this report. All citations are to file paths, line numbers, hashes, and mode strings.
