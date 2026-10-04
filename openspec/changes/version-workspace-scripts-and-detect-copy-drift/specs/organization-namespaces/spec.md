# Spec Delta

## MODIFIED Requirements

### Requirement: Tooling and script path resolution invariants

Automated workspace maintenance scripts, LaunchAgents, and knowledge synchronization pipelines SHALL resolve repository paths dynamically or reference canonical two-tier organization paths (`~/Developer/<organization>/<repository>`), and SHALL NOT depend on deprecated flat workspace paths.

#### Scenario: Discovering OpenSpec specifications for knowledge cataloging
- **WHEN** `sync-notion-knowledge.sh` or automated catalog generators scan for governed capability specifications
- **THEN** the script SHALL resolve `openspec-store` at its canonical location `~/Developer/platform/openspec-store`
- **AND** all active capability specifications under `openspec/specs/**/spec.md` SHALL be discovered and cataloged without returning an empty set

#### Scenario: Handling missing or moved repository targets
- **WHEN** a script encounters an inventory path that does not exist at the historical flat root
- **THEN** the script SHALL fail closed with an explicit descriptive error indicating the missing canonical path
- **AND** it SHALL NOT emit a false-positive success or silent zero-count output

#### Scenario: Validating approved knowledge refresh inventory digest
- **WHEN** `refresh-knowledge-indexes.sh` verifies inventory integrity against the approval digest
- **THEN** `knowledge-refresh-inventory.tsv` and `knowledge-refresh-approval.sha256` SHALL contain the same repository entries with valid SHA-256 approval digests across both `~/Developer/scripts/knowledge-refresh/` and `platform/openspec-store/scripts/knowledge-refresh/`
- **AND** each copy's inventory SHALL match the digest recorded beside it
- **AND** the set of repositories SHALL be taken from the installed inventory rather than from a count fixed in this requirement

#### Scenario: Freshness check reports a non-fresh workspace without false success
- **WHEN** `refresh-knowledge-indexes.sh` runs its freshness check and one or more indexed repositories are stale or missing
- **THEN** the script SHALL report the per-repository freshness state and a total
- **AND** it SHALL exit non-zero rather than reporting success

#### Scenario: Freshness check reports an all-fresh workspace
- **WHEN** `refresh-knowledge-indexes.sh` runs its freshness check and every indexed repository is fresh
- **THEN** the script SHALL report the per-repository freshness state and a total
- **AND** it SHALL exit zero

#### Scenario: Single-repository mode classifies staleness the same way
- **WHEN** `refresh-knowledge-indexes.sh` checks one repository and that repository's Graphify index is stale while its GitNexus index is fresh
- **THEN** it SHALL report the repository as stale
- **AND** it SHALL exit non-zero
- **AND** the reported state SHALL show which revisions differ without that displayed text preventing the stale classification
