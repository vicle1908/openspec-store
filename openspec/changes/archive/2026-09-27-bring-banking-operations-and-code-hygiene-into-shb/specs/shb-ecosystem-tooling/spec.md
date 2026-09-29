# shb-ecosystem-tooling Specification Delta

## Purpose
Specifies additions to the `shb-tools` repository for end-of-day transaction reconciliation, automated banking code hygiene, PCI-DSS compliance scanning, and multi-repository documentation and schema synchronization.

## ADDED Requirements

### Requirement: End-of-Day Transaction Reconciliation Worker
The `shb-tools` package SHALL provide an End-of-Day (EOD) transaction reconciliation engine executable via `shb-recon` to match internal banking ledgers against clearing settlement statements (such as NAPAS247 or interbank settlement feeds).

#### Scenario: Settlement reconciliation run
- **WHEN** an operator runs `shb-recon run --date YYYY-MM-DD`
- **THEN** the reconciliation engine loads internal transaction records and partner settlement files, executes matching logic, and categorizes records as `MATCHED`, `DISCREPANCY`, or `ORPHAN`

#### Scenario: Reconciliation discrepancy reporting
- **WHEN** amount or fee mismatches exist between internal records and clearing files
- **THEN** `shb-recon diff --date YYYY-MM-DD` outputs a structured discrepancy report detailing transaction IDs, expected versus actual amounts, and recommended compensating adjustments

### Requirement: Automated Banking Compliance and Hygiene Scanner
The `shb-tools` package SHALL provide an automated compliance scanner executable via `shb-compliance-scan` that audits all 12 repositories under `~/Developer/shb/` for security credential leaks, unmasked payment card numbers, syntax deprecations, and type check health.

#### Scenario: Secret and credential leakage detection
- **WHEN** `shb-compliance-scan --target-dir ~/Developer/shb` is executed
- **THEN** the scanner inspects tracked files across all 12 repositories and flags any unencrypted `.env` secrets, private keys, or API tokens outside quarantined paths

#### Scenario: Payment card and PAN masking audit
- **WHEN** the scanner evaluates source code and test files
- **THEN** it flags any unmasked 16-digit Primary Account Numbers (PANs) or raw cardholder verification values in non-fixture source files per PCI-DSS standards

#### Scenario: Strict syntax and typing hygiene verification
- **WHEN** the scanner runs language hygiene checks
- **THEN** it verifies zero deprecated Python typing constructs (`typing.List`, `typing.Optional`) and asserts passing status for `uv run ruff check` and `uv run mypy` across all repos

### Requirement: Multi-Repository Documentation and Schema Synchronization
The `shb-tools` package SHALL provide an automated documentation and contract synchronization CLI named `shb-docs-sync` to maintain parity between centralized OpenSpec specifications, repository README files, `SPEC_INDEX.md`, and `harness-13` schema contracts.

#### Scenario: Spec index and README synchronization
- **WHEN** an operator runs `shb-docs-sync --check`
- **THEN** the utility checks all 12 repositories to verify that their `SPEC_INDEX.md` and `README.md` match current central OpenSpec store definitions
- **AND** reports any drifted or missing documentation blocks
