# Plan Review — Round 1 Record (value-blind reconstruction)

Change: `reconcile-omniroute-native-dialects`
Round 1 ran 2026-08-29/30, before the evidence-repair pass. The original
reviewer outputs were not retained as files; this record reconstructs the
round from the retained repair diffs, ledger annotations, and the review-scope
identity chain. It is value-blind: no credential values, no raw outputs.

## Reviewer verdicts (round 1)

| Reviewer | Lens | Verdict | State |
|---|---|---|---|
| Codex | Quality & tests / oracle | FAIL | actionable findings (repaired) |
| Antigravity (agy) | Architecture / spec coverage | FAIL | actionable findings (repaired) |
| Claude Code | Security | UNKNOWN | model rejection — no verdict |
| Kimi | Product scope | NOT_REVIEWED | bounded timeout |

UNKNOWN and NOT_REVIEWED are blockers, not implicit approvals; they carry into
round 2 as required fresh-review edges.

## Findings and repairs

- **R1-F1 (Codex — acceptance oracle incomplete).** The change defined no
  executable fail-to-pass / pass-to-pass oracle. Repair: `review-scope.yaml`
  `acceptance` section added — fail_to_pass `static-route-contract`
  (candidate green) and `candidate-cli-probes`; pass_to_pass
  `openspec-strict`, `planning-artifact-parse`, `cli-identity-inventory`,
  `overlay-contract`, `default-probe-contract`, `manifest-preservation`.
  Status: repaired; re-validated in round 2 (with the pre-apply/post-apply
  phase split and the added `apply-backups` / `sentinel-fixtures` entries).
- **R1-F2 (Codex/AGY — probe rows asserted unproven mechanisms).** The cline
  rows used an unproven provider argv and lacked the FBC-5 native-failure
  binding; the codex SH row asserted a selectable-profile mechanism with no
  isolated proof. Repair: cline argv rebound to the proven
  `openai-omniroute-chat` provider with `fbc-5-native-provider-lockout`
  recorded; the 3-arm Codex profile-mechanism probe was added
  (negative-control env key, exact post-strip sentinel equality) and PASSed
  on the active binary (0.149.0 originally; repeated on cask 0.151.0 after
  the upgrade — `codex-profile-mechanism-result.json`).
  Status: repaired.
- **R1-F3 (AGY — spec coverage gaps).** Delta specs did not require
  client-specific native-route acceptance (raw HTTP 200 was being treated as
  CLI success), had no installed-CLI classification requirement, and no
  per-file rollback requirement. Repair: `omniroute-agent-cli-routing` spec
  ADDED requirements: "Native route acceptance SHALL be client-specific",
  "Installed CLI support SHALL be classified before mutation", "Per-file
  rollback SHALL cover dialect regressions". Status: repaired.

## Carried-forward requirements for round 2

1. Fresh verdicts required on all approval-critical edges; round-1 results are
   not reusable (stale-verdict rule: artifact hashes changed during repair).
2. Claude (security lens) and Kimi (product scope) must return real verdicts
   or remain explicit blockers.
3. Round 2 reviews the current artifact set including: the phase-split
   acceptance oracle, `apply-mechanism.md`, `apply-blockers.json`,
   `apply-backups.json`, `sh-chat-reliability-observations.md` (corrected),
   and the drift-provenance archived-ownership corrections.
