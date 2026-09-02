## Purpose

Extends `omniroute-closure-integrity` to close the gap where checked-but-void gate ticks evade the existing archive-while-open rule.

## ADDED Requirements

### Requirement: Archive validity requires verifiable gate evidence

Every checked owner gate in an archived change's ledger SHALL have verifiable evidence that satisfies the gate's declared release condition (owner decision, probe execution, or explicit reclassification) and closure text consistent with those states. An archive where any checked gate lacks verifiable satisfying evidence or has closure text inconsistent with the gate's actual state is void and MUST be recorded by a subsequent active change.

#### Scenario: Checked gate has no satisfying evidence
- **WHEN** an archived change's ledger records a gate as checked [x] but no verifiable evidence exists that satisfies the gate's declared release condition (evidence file missing, cites quarantined record, or fabricated)
- **THEN** the archive is void for that gate and MUST be recorded by a subsequent active change

#### Scenario: Checked gate has contradictory evidence
- **WHEN** an archived change's ledger records a gate as checked [x] but the evidence shows a different model, provider, or outcome than the ledger claims
- **THEN** the archive is void for that gate and MUST be recorded by a subsequent active change

#### Scenario: Closure text contradicts gate states
- **WHEN** an archived change's closure decision text contradicts the gate states recorded in the same ledger line (e.g., "archive" while recording "verification pending")
- **THEN** the archive is void and MUST be recorded by a subsequent active change

#### Scenario: Gate evidence satisfies release condition
- **WHEN** an archived change's ledger records a gate as checked [x] and verifiable evidence exists showing genuine satisfaction of the gate's declared release condition with consistent claims
- **THEN** the archive is valid for that gate
