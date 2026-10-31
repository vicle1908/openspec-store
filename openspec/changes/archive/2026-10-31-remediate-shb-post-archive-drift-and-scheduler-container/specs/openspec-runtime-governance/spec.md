# Delta Specification: openspec-runtime-governance

## ADDED Requirements

### Requirement: Archive immutability verification and forward-remediated range auditing

`scripts/validate-archive-readiness.py --range` SHALL fail closed if a commit in the audited range modifies files inside an already-archived directory under `openspec/changes/archive/` unless recorded in a sanctioned forward-remediation ledger, and SHALL resolve historical missing-evidence violations via active corrective evidence rather than mutating old archives.

#### Scenario: Historical missing evidence and post-archive edit accounted via forward remediation
- **WHEN** `python3 scripts/validate-archive-readiness.py --range HEAD~35..HEAD --store /Users/androidteam/Developer/platform/openspec-store --strict` is executed after forward-remediating `2026-10-20-reconcile-dev-tooling-and-hermes-runtime` (`804a8968`) and `2026-10-20-upgrade-omniroute-to-v3-8-52` (`a3eb1fda`)
- **THEN** the validator SHALL verify the corrective evidence ledger without requiring further edits to pre-existing `openspec/changes/archive/` directories
- **AND** any new unapproved post-archive modification in future commits SHALL fail with exit code `4`
