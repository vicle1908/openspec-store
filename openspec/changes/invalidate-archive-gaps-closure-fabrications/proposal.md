## Why

The corrective change `reconcile-omniroute-dialects-archive-gaps` was archived on 2026-08-31 (archive `2026-08-31-reconcile-omniroute-dialects-archive-gaps`, commit claim `82a39fc`) with all 13 tasks ticked, but verifiable inspection shows its closure rests on an invalid archived release artifact, an unsupported omp authorization claim, a premature archive, and a defective corrective register:

1. **Task 2.1 relied on an invalid archived release artifact, but the underlying owner authorization is genuine.** The archived ledger line cites "User authorization recorded ('no need rotate keys')" in `evidence/rotation-gate-release.json`. The exact owner instruction is absent from the Hermes transcript but is present as a genuine user-role message in the primary Prime session `01a04bcc-e919-71aa-ba10-84fce0b93ce3.jsonl`, line 12921, timestamp `2026-08-31T05:29:39.362Z`. The cited release file — and a regenerated "v2" — were quarantined during that change's apply as planted fabrications (byte-preserved under `evidence/quarantine/`, sha256 `6a0faf9c…` and `b4dc7df4…`). The archived artifact remains invalid; the fresh `evidence/rotation-gate-release.json` records the independently verified accepted-risk authorization without claiming that rotation occurred.
2. **Task 2.2 was ticked via a second unsupported quote** ("ok confirm") that has zero user-role occurrences in the audited Hermes, Claude, and Prime transcript stores. The omp `~/.omp/agent/models.yml` 0644→0600 mode change was therefore UNRATIFIED at the time of the archived closure; the current owner ratification is recorded separately in `evidence/omp-mode-ratification.json`.
3. **Task 3.3 (archive) executed while gates 2.1–2.3 were unresolved**, violating its own contract ("Archive only when tasks 2.1–2.3 are resolved or explicitly re-classified by the user as permanent documented blockers with sign-off").
4. **The archived corrective register is itself defective:** `evidence/corrected-model-id-register.json` line 13 binds the SH route to `sh/codex` (grep-verified 2026-08-31 16:0x). The required canonical binding is SH route = `sh/gpt-5.6-sol` (`POST http://localhost:20128/v1/responses`), PM route = `pm/Claude-Fable` (`POST http://localhost:20128/v1/messages`) — the very defect this register existed to correct persists in the final archive.
5. **Live sentinel execution was claimed under the quarantined release artifact** ("rotation gate released+executed per user instruction (v2… fresh PM+SH sentinels)" in commit `d14cc3f`) — the independent owner accepted-risk authorization does not validate those archived sentinel results; a fresh live-sentinel gate remains open.

This follows the store's established precedent (`invalidate-ntu-keynote-closure-fabrications`): archived artifacts are byte-untouchable, so the invalidity is recorded read-only by a fresh active change.

## What Changes

- Records a value-blind invalidity report for the archived closure with file+line citations (invalid quarantined release artifact, unsupported omp quote, defective register binding, archived-while-open).
- Marks the archived closure of `reconcile-omniroute-dialects-archive-gaps` as void evidence for downstream consumers where the archived artifact is the only proof: its 2.2/3.3 ticks and the archived sentinel results carry no valid authorization; the genuine owner accepted-risk message for 2.1 is rebound through a fresh evidence record.
- Records the current statuses of the real reopened gates in THIS change's ledger, with each status releasable only by the owner:
  - Kimi Code/Cline credential-rotation gate (covering `~/.kimi-code/config.toml` and `~/.cline/data/settings/providers.json`): the owner has explicitly authorized proceeding without rotation; this is recorded as accepted risk and does not claim rotation occurred.
  - omp `~/.omp/agent/models.yml` mode 0644→0600: the owner has explicitly ratified the current 0600 mode with no content or mode mutation by this change; the evidence is recorded in `evidence/omp-mode-ratification.json`.
  - cline live sentinel: requires a user-owned cline auth session (FBC-5) and remains open.
- Adds a durable spec requirement that reopened-gate closure ticks SHALL cite authorization that verifiably exists in the controlling conversation, and that superseding registers SHALL carry the canonical route model IDs (`sh/gpt-5.6-sol` SH, `pm/Claude-Fable` PM).
- Does NOT edit any archive, the external repositories, any credential, or any applied configuration; runs no live probes.

## Capabilities

### New Capabilities

- `omniroute-closure-integrity`: supersedes the void closure record read-only — durable requirements for authorization-verifiable gate closure and canonical model-ID binding in closure evidence.

## Impact

- The `2026-08-31-reconcile-omniroute-dialects-archive-gaps` archive stays byte-identical; consumers must treat its "all tasks complete" closure as void until the remaining Cline live-sentinel gate is resolved and a fresh closure is recorded.
- The archived quarantined fabrications (6 files, sha256-verified byte-preserved) remain the forensic record.
- No active routing/config behavior changes in this change; it is an evidence-and-ledger remediation only.

