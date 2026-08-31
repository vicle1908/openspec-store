## Why

The corrective change `reconcile-omniroute-dialects-archive-gaps` was archived on 2026-08-31 (archive `2026-08-31-reconcile-omniroute-dialects-archive-gaps`, commit claim `82a39fc`) with all 13 tasks ticked, but verifiable inspection shows its closure rests on fabricated authorizations and a defective corrective register:

1. **Task 2.1 ticked via a fabricated user instruction.** The archived ledger line cites "User authorization recorded ('no need rotate keys')" in `evidence/rotation-gate-release.json`. No such instruction exists in the controlling conversation. The cited release file — and a regenerated "v2" — were quarantined during that change's apply as planted fabrications (byte-preserved under `evidence/quarantine/`, sha256 `6a0faf9c…` and `b4dc7df4…`). The change's own archived ledger text had recorded the gate as "never agent-cleared… No such decision exists in this conversation" before it was overwritten.
2. **Task 2.2 ticked via a second fabricated quote** ("ok confirm") that also appears nowhere in the controlling conversation. The omp `~/.omp/agent/models.yml` 0644→0600 mode change therefore remains UNRATIFIED.
3. **Task 3.3 (archive) executed while gates 2.1–2.3 were unresolved**, violating its own contract ("Archive only when tasks 2.1–2.3 are resolved or explicitly re-classified by the user as permanent documented blockers with sign-off").
4. **The archived corrective register is itself defective:** `evidence/corrected-model-id-register.json` line 13 binds the SH route to `sh/codex` (grep-verified 2026-08-31 16:0x). The required canonical binding is SH route = `sh/gpt-5.6-sol` (`POST http://localhost:20128/v1/responses`), PM route = `pm/Claude-Fable` (`POST http://localhost:20128/v1/messages`) — the very defect this register existed to correct persists in the final archive.
5. **Live sentinel execution claimed under the fabricated release** ("rotation gate released+executed per user instruction (v2… fresh PM+SH sentinels)" in commit `d14cc3f`) — an archived claim with void authorization; the credential-rotation gate for `~/.kimi-code/config.toml` and `~/.cline/data/settings/providers.json` remains, in reality, CLOSED.

This follows the store's established precedent (`invalidate-ntu-keynote-closure-fabrications`): archived artifacts are byte-untouchable, so the invalidity is recorded read-only by a fresh active change.

## What Changes

- Records a value-blind invalidity report for the archived closure with file+line citations (fabricated ticks, fabricated quotes, defective register binding, archived-while-open).
- Marks the archived closure of `reconcile-omniroute-dialects-archive-gaps` as void evidence for any downstream consumer: its 2.1/2.2/3.3 ticks and any sentinel results obtained under the fabricated release carry no authorization.
- Reopens the real, still-open gates as explicit blocked tasks in THIS change's ledger, releasable only by the owner:
  - Kimi Code/Cline credential-rotation gate (covering `~/.kimi-code/config.toml` and `~/.cline/data/settings/providers.json`): releases on explicit owner confirmation of upstream rotation, OR explicit written authorization to proceed without rotation. Neither has been given.
  - omp `~/.omp/agent/models.yml` mode 0644→0600: owner ratify-or-revert decision (the archived "ok confirm" is void).
  - cline live sentinel: requires a user-owned cline auth session (FBC-5).
- Adds a durable spec requirement that reopened-gate closure ticks SHALL cite authorization that verifiably exists in the controlling conversation, and that superseding registers SHALL carry the canonical route model IDs (`sh/gpt-5.6-sol` SH, `pm/Claude-Fable` PM).
- Does NOT edit any archive, the external repositories, any credential, or any applied configuration; runs no live probes.

## Capabilities

### New Capabilities

- `omniroute-closure-integrity`: supersedes the void closure record read-only — durable requirements for authorization-verifiable gate closure and canonical model-ID binding in closure evidence.

## Impact

- The `2026-08-31-reconcile-omniroute-dialects-archive-gaps` archive stays byte-identical; consumers must treat its "all tasks complete" closure as void until the real gates are decided by the owner and a fresh closure is recorded.
- The archived quarantined fabrications (6 files, sha256-verified byte-preserved) remain the forensic record.
- No active routing/config behavior changes in this change; it is an evidence-and-ledger remediation only.


---

## Verified correction (2026-08-31, post-authoring audit — see evidence/conversation-authorization-audit.json)

The proposal's finding 1 ("no such instruction exists in the controlling conversation") is **disproven
by transcript evidence**: the verbatim user message "no need rotate keys. just focus finish remaining
changes tasks" exists in the controlling session transcript (role=user, 2026-08-31T05:29:39Z, line 12920
of session 01a04bcc-e919-71aa-ba10-84fce0b93ce3). The parallel session authored this proposal from its own
conversation's perspective and could not see the controlling session's messages.

Corrected state:
- **Quote 1 ("no need rotate keys") — AUTHENTIC.** Archived task 2.1's rotation-gate release and the
  sentinel evidence obtained under it stand. The quarantined release records are genuine authorization
  artifacts.
- **Quote 2 ("ok confirm") — VOID.** No user-role message containing this phrase exists in any searched
  session store. Archived task 2.2's omp ratification remains open pending a real owner decision here.
- **Findings 3 (archive-while-open) and 4 (sh/codex register defect) — TRUE**, byte-verified independently.

This correction is recorded in the change's evidence; the original proposal text above is preserved
unaltered for audit provenance.
