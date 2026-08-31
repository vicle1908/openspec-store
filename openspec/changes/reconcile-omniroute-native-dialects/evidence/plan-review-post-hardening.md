# Plan Review — Post-Hardening Adjudication Record (value-blind)

Change: `reconcile-omniroute-native-dialects`
Round: post-hardening (round-3 binding consequence — closes task 2.2)
Dispatched 2026-08-31 (`deleg_009e0f2e`), completed 03:37; narrow in-scope
credentials re-review completed 03:35.

## Verdicts (4 reviewers + 1 narrow re-review)

1. **Consistency — PASS, 0 approval blockers.** Phase-scoped task 2.4,
   phase-split acceptance, drift-register v3, deferred semantics all
   coherent. Fresh strict validate green; route-contract baseline negative
   control retained (5 PASS / 12 FAIL, identical counts to the frozen
   baseline run — fail-to-pass gates intact); artifact pins 56/56.

2. **Apply-tooling — PASS, 0 approval blockers.** Source-level fail-closed
   verification of `apply-backups.py`, `manifest-check.py`,
   `capture-manifest.py`, `apply-overlays.py`; overlay-contract exact-set
   allowlist verified; behavioral fixtures (D1–D10, M1–M5) green.

3. **Credentials (broad) — FAIL, 4 blockers.** Adjudication: ALL four
   blockers concern files OUTSIDE this change's 11-file write set
   (`~/.codex/auth.json` mode 644; `~/.claude/backups/*` six mode-644
   files; backup-creation umask default). None are read, written, or
   modified by this change; the baseline manifest excludes them. The
   verdict is therefore superseded FOR THIS CHANGE'S GATE by the narrow
   in-scope re-review (item 4). Every finding is recorded verbatim —
   metadata only, no values — as user-owned external remediation items
   (`evidence/external-remediation-items.md`).

4. **Credentials (narrow in-scope re-review) — PASS, 0 approval blockers.**
   Scope: change artifacts only — templates env-ref-only,
   `apply-blockers.json` explicit release conditions,
   `incident-credential-exposure.md` containment rules. No live-home
   inspection.

5. **Protocol — PASS, 3 approval blockers adjudicated non-blocking:**
   - *"Task 2.2 open"* — gate echo: closed by this record.
   - *"Kimi/Cline deferred"* — policy by design (`apply-blockers.json`),
     not a review finding.
   - *"Self-pin not reproducible"* — resolved: the independent pin-semantics
     verifier reproduces the self-pin under a UNIQUE documented-consistent
     interpretation (zeroing reviewer, reviewed_at, every artifact sha256,
     head_commit, and input hash fields; empty-style; trailing newline
     kept) — matching the algorithm text recorded in `review-scope.yaml`.

## Pin resolution

- 57 artifact entries = 56 external (raw byte-for-byte disk match, 56/56)
  + 1 self (`review-scope.yaml` normalized policy hash by documented
  design — NOT a raw-file pin).
- Self-pin reproduction: exactly ONE interpretation matches (no
  ambiguity); documented-consistent = TRUE.

## Orchestrator disclosure (NOT a review input)

`T/hermes-orchestrate-partial-apply.py` and its verifier
`T/hermes-verify-orchestrator.py` are TEMPORARY OPERATOR HARNESS files in
the OS temp directory — not change artifacts, not pinned, not part of
review input. Fresh run 2026-08-31: **36/36 PASS** — fail-closed without
valid backups (rc=3), TOCTOU baseline-sha guard, per-target gates
(parse → secret-shape → route-contract → live probes), rollback
(modify: backup bytes+mode restore; create: unlink) on any gate
failure, fail-stop with explicit NOT-ATTEMPTED lines, route-map
validation fail-closed at startup (unknown check name or missing target
→ exit 6 before any write), real-home `--fail-inject` refused, no
evidence-dir pollution, probes gated to real-home execute with
`OMNIROUTE_API_KEY` required. If the orchestrator is ever admitted as
change evidence, that admission is a new planning edit requiring re-pin
and re-review.

## Post-review tooling repair (2026-08-31, after adjudication — disclosed)

During the live partial apply, the `goose.pm.messages` probe failed while
the goose response was protocol-correct (rc 0, final assistant text ==
sentinel, thinking preserved, `/v1/messages`). A replay through the
production runner proved a RUNNER-EXTRACTION-GAP: `exact_sentinel()` only
parsed the last non-empty line, and goose `--output-format json` emits
pretty-printed multi-line session JSON whose last line is `}` — a correct
response was rejected (false negative). The fail-stop discipline held:
goose-pm was rolled back (created file deleted), targets after it were
NOT-ATTEMPTED, codex stayed applied, and the backups plus the deferred
Kimi/Cline surfaces were untouched.

Repairs (all confined to evidence tooling; no template, protocol, or
provider changes):
1. `exact_sentinel()` attempts a whole-output JSON parse before the
   line-based paths (the line-based paths are preserved unchanged).
2. `contains_final_assistant_text()` tightened with final-block and
   final-message semantics: the sentinel is credited only when the LAST
   content block of the FINAL assistant/result message is a text block
   equal to the sentinel; sentinel strings in user prompts, thinking,
   tool blocks, metadata, or signatures are never credited, an earlier
   assistant echo followed by different final text is rejected, and a
   sentinel text followed by any trailing block (text, thinking,
   tool_use, tool_result) is rejected.
2b. (Attempt-2 postmortem) A dedicated JSONL contract was added for
   `kilo --format json` output (one JSON record per line): the sentinel
   is credited ONLY from the LAST formal text carrier
   (`record.type == "text"`, `record.part.type == "text"`,
   `record.part.text`), and only end-of-turn control records
   (`step_finish`) may trail it. Outputs with no formal carriers fall
   through to the generic contract unchanged. The recursive oracle was
   NOT loosened for this. Replay-proven via the production runner for
   both kilo rows; fixtures J1–J8.
2c. (Attempt-3 postmortem) A grok session-envelope contract was added for
   `grok --output-format json` output (a single JSON document whose
   top-level `text` string is the final assistant reply): the sentinel is
   credited only when the envelope's `text` field equals it exactly; the
   `thought` field (reasoning) and usage/session metadata are never
   credited. Fixtures G1–G4; both live grok rows were replay-proven
   through the production runner before the repair (direct rc=0, sentinel
   present in the top-level text, runner False) — the same extraction-gap
   class as goose and kilo.
3. `capture-manifest.py` `rollback_metadata()` fails closed when a
   `--deferred-target` path is not part of the captured file set
   (previously silently ignored, rc 0 — exposed by the D9 fixture).

Focused verification (ad-hoc, T/ harness, production-runner replay):
fixture matrix U1–U18 (JSON whole/line contracts) plus JSONL J1–J8 (kilo
carrier contract) plus G1–G4 (grok session envelope) — 30 unit fixtures —
plus the live goose probe through the production runner in a disposable
HOME and pre-resume safety assertions; the focused suite totals 45
checks, all green. Both kilo rows and both grok rows were additionally replay-proven through the production runner before the
JSONL repair. Full battery regression and strict validation are rerun
after every repair and before the apply resumes. Live attempts'
value-blind outcome records are preserved in
`evidence/partial-apply-attempts.json` (attempt records carry explicit
provenance; `recorded_at` marks the reconstruction time, and
`attempt_completed_at` is recorded as unknown where not captured at
completion — the orchestrator's temp results file is shared and later
overwritten by verifier sandbox-execute runs, so a post-hoc mtime is not
attempt evidence; the value-blind outcome snapshot taken immediately
after each attempt's execute is the durable basis of the book). These repairs post-date the 2.2
adjudication and the artifact pins; the apply gate re-opens only after
re-pin, independent pin verification, and a fresh full-battery run.

## Adjudication

**In-scope review gate: ACCEPTED after adjudication (2026-08-31).** Three of
four reviewers returned PASS with no approval blockers; the broad credentials
reviewer returned FAIL whose four blockers all concern files OUTSIDE this
change's write set, and is superseded FOR THIS CHANGE'S GATE ONLY by the
narrow in-scope re-review. This acceptance does NOT assert that every
credential-security concern on the machine is resolved — the out-of-scope
findings remain open as user-owned external remediation items
(`external-remediation-items.md`). Task 2.2 is ticked with this record as
the binding citation. Live apply remains gated on: real backups for the
7 safe modify targets (task 2.4 partial), the Kimi/Cline rotation gate
(user decision — deferred surfaces untouched including backups), and a
plan-only dry-run of the orchestrator before `--execute`.
