# workspace-topology-and-hygiene Delta Specification

## MODIFIED Requirements

### Requirement: Workspace domain taxonomy isolation
The workspace root at `~/Developer/` SHALL maintain dedicated domain subtrees (`legacy/`, `apps/`, `study/`, `ai-tooling/`, `migration-archives/`) alongside organization subtrees (`platform/`, `tdt/`, `shb/`, `vds/`, `ascend/`, `ghtk/`, `fpt/`, `infra/`), and SHALL NOT store unclassified standalone projects or static assets flat at the workspace root.

#### Scenario: Categorizing unclustered projects into domain subtrees
- **WHEN** standalone projects or migrated assets are introduced to the workspace
- **THEN** they SHALL be placed in their designated domain directory (`legacy/` for inactive checkouts, `apps/` for standalone client tools, `study/` for reference code, `ai-tooling/` for agent tools, or `migration-archives/` for migration receipts)
- **AND** they SHALL NOT reside unclassified at the top-level `~/Developer/` directory
