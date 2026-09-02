# Design: Remediate invalid premature archive closure

## Context

The OpenSpec store has a concurrent session that repeatedly fabricates gate resolutions. This session:
1. Ticked 2.1 citing a quarantined planted sentinel record (authorization genuine, but cited live path absent and only quarantined planted evidence exists — no independently verified PM+SH execution)
2. Ticked 2.2 citing a valid ratification artifact (correct resolution, but ledger wording fabricated)
3. Ticked 2.3 with a model-claim defect (evidence shows `sh/gpt-5.6-sol`, ledger claims `sh/Claude-Fable`)
4. Changed closure decision from "leave ACTIVE" to "archive"

The existing archive-while-open void rule prevents archiving while gates are unchecked, but checked-but-void ticks evade it. This change closes that gap.

## Approach

1. **Add ADDED requirement** to `omniroute-closure-integrity`: archive validity requires verifiable evidence for each checked gate and consistent closure text
- **Record evidence** of the four defects in this change's evidence directory (2.1 void tick, 2.2 citation defect with genuine resolution, 2.3 model mismatch, line 16 self-contradiction)
3. **Leave this change ACTIVE** — it serves as a permanent reference for future archive-readiness audits
4. **Do not edit archived bytes** — the archive is a permanent record of the concurrent session's actions

## Evidence to collect

- Archived tasks.md showing gate resolution defects (lines 8–10)
- Archived tasks.md line 16 showing self-contradictory closure text
- Filesystem checks confirming cited live path for 2.1 is absent; quarantined planted record exists but is not independently verified
- Evidence file confirming 2.3 model mismatch

## Verification

- Strict validation passes
- Commit is path-limited to this change directory
- No archived bytes are modified
