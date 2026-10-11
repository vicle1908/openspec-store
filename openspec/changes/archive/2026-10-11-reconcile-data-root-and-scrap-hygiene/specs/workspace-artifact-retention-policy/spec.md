# workspace-artifact-retention-policy Delta Specification

## MODIFIED Requirements

### Requirement: Candidate reclamation only after review
Generated index or cache state, temporary or ephemeral test fixtures, and unmanaged reproduction scratchpads (`harness-prod-repro-*`) in runtime data roots (`~/Developer/data/`) SHALL become review candidates only after a separate review record proves the item is not referenced by current index contracts, active processes, workflows, or evidence owners. Obsolete reproduction scratchpads and duplicate skill checkouts in `~/Developer/data/` SHALL be classified as `RECLAIMABLE` and purged during workspace hygiene cycles.

#### Scenario: Candidate is referenced by an index owner
- **WHEN** a generated path is still covered by approved refresh or watcher ownership
- **THEN** the item SHALL remain `PROTECTED`
- **AND** it SHALL NOT be listed as a reclamation candidate

#### Scenario: Candidate has no current owner
- **WHEN** a generated path, obsolete test reproduction scratchpad (`harness-prod-repro-*`), or rogue skill checkout in `~/Developer/data/` has no active index, process, or evidence owner
- **THEN** the retention policy MAY classify it as `RECLAIMABLE`
- **AND** it SHALL record the basis, provenance, and required re-generation behavior before approval
- **AND** duplicate skill checkouts in `data/skills/` SHALL be removed immediately upon review confirmation
