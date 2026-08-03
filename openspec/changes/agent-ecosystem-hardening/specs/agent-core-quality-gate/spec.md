# agent-core-quality-gate Delta Specification

## ADDED Requirements

### Requirement: CI workflow includes secret scanning

Every repository in the three-repository verification set (`agent-core`,
`agent-docs-sync`, `agent-harness`) SHALL have a `.github/workflows/ci.yml`
that includes gitleaks secret scanning with `fetch-depth: 0` and the pinned
gitleaks image version. This requirement operationalizes the existing
"No hardcoded secrets" requirement with a specific CI mechanism.

#### Scenario: CI workflow exists with gitleaks config
- **WHEN** `test_secret_scanning_policy.py` reads `.github/workflows/ci.yml`
- **THEN** the file SHALL contain `fetch-depth: 0`
- **AND** the file SHALL reference the pinned gitleaks image (`docker://ghcr.io/gitleaks/gitleaks:v8.30.1`)
- **AND** the file SHALL contain `git --redact=100 --no-banner --verbose .`
- **AND** the test SHALL pass

#### Scenario: CI workflow passes actionlint validation
- **WHEN** `actionlint .github/workflows/ci.yml` is run in any of the three repositories
- **THEN** the command SHALL exit with code 0

#### Scenario: CI secret scan does not produce false positives
- **WHEN** the gitleaks CI workflow runs against the full git history
- **THEN** the scan SHALL complete with zero findings
- **AND** any deterministic non-secret findings SHALL be resolved through
  exact-fingerprint `.gitleaksignore` entries per the existing exception policy
