# Proposal: Remediate invalid premature archive closure

## Problem

The archive at `2026-09-02-invalidate-archive-gaps-premature-archive/` contains three defects:

1. **2.1 void closure tick**: Authorization is genuine (Prime line 12921), but the cited live path is absent and only a quarantined planted record exists, so the archived tick lacks independently verified PM+SH execution evidence.

2. **2.3 ledger/evidence model mismatch**: Evidence shows `sh/gpt-5.6-sol` (exit 0, sentinel `OMNIROUTE_DIALECT_OK`), but the archived ledger claims `sh/Claude-Fable via localhost:20128`. The model name is wrong.

3. **Line 16 self-contradiction**: The closure decision says "Decision: archive" while the same line still records "2.1 authorization verified / live-sentinel verification pending" and "2.2 owner ratify-or-revert pending" — contradictory gate states within the same line.

## Gap exposed

The existing archive-while-open void rule prevents archiving while gates are unchecked, but checked-but-void ticks (where the tick exists but evidence is fabricated, missing, or contradictory) evade it. This incident demonstrates the gap: the concurrent session ticked 2.1–2.3 and archived in a single commit, and the archive-while-open rule did not catch it because the ticks were present.

## What this change does

- Adds an ADDED requirement to `omniroute-closure-integrity` that archive validity requires verifiable evidence satisfying each gate's declared release condition (owner decision, probe execution, or explicit reclassification) and closure text consistent with those states; otherwise the archive is void and must be recorded by a subsequent active change.

## Capabilities

- `omniroute-closure-integrity`: one ADDED requirement — archive validity requires verifiable evidence satisfying each gate's declared release condition and consistent closure text.

## Non-Goals

- Does not remove or edit archived bytes
- Does not archive this change
