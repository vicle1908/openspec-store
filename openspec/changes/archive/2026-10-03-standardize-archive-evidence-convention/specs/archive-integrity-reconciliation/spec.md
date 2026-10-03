# Spec Delta

## ADDED Requirements

### Requirement: Immutability violations are recorded and reverted

The reconciliation SHALL treat any file present in an archived change directory that was not part of the archived content as a violation. It SHALL record the violation with the archive path, the offending path, and the commit or reference that introduced it, and SHALL revert the archived directory to its pre-edit content. Reversion SHALL restore the archive without introducing any further change to archived bytes beyond removing the offending addition.

#### Scenario: An added file is found in an archived change

- **WHEN** reconciliation finds a file inside an archived change directory that is not part of the archived content
- **THEN** it records the archive path, the offending path, and the introducing reference
- **AND** it removes the added file so the archived directory matches its pre-edit content
- **AND** it preserves the recovered content in a new active change

#### Scenario: An archived file was edited in place

- **WHEN** reconciliation finds that a file belonging to the archived change has different content than the archived revision
- **THEN** it records the discrepancy with the path and the reference
- **AND** it restores the archived content from the recorded revision
- **AND** the corrective change remains incomplete until the archive matches its archived revision

#### Scenario: The violating commit is not recoverable

- **WHEN** the reference that introduced the violation cannot be identified
- **THEN** the reconciliation records the violation as unresolved with the observable evidence
- **AND** it SHALL NOT guess at the original content or delete an ambiguous file
