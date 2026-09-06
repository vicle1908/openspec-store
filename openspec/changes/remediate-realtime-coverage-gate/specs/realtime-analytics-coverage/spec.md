## Purpose

This capability defines an evidence-based coverage gate for the realtime frontend so CI reports actionable coverage debt without blocking a fully passing test suite on aspirational, unachievable thresholds.

## ADDED Requirements

### Requirement: Coverage thresholds SHALL reflect an evidence-based baseline

Coverage enforcement SHALL use thresholds justified by the latest measured repository coverage and SHALL NOT claim coverage completion for untested components. Threshold changes MUST preserve a ratchet path toward the intended quality target.

#### Scenario: Current coverage baseline is below aspirational thresholds

- **WHEN** the canonical test command reports green tests but Analytics coverage is approximately 22.83% lines and global coverage is approximately 41.32% lines
- **THEN** CI SHALL report the measured baseline and SHALL apply only thresholds approved by this corrective change, without deleting coverage instrumentation

#### Scenario: Coverage improves

- **WHEN** a later change raises coverage above the approved baseline
- **THEN** the approved thresholds SHALL remain enforceable and SHALL be raised through a reviewed OpenSpec change rather than silently changing the policy

### Requirement: Test and coverage results SHALL be reported separately

Verification evidence SHALL distinguish test pass/fail results from coverage threshold results, including the command, measured values, configured thresholds, and the reason for any nonzero exit status.

#### Scenario: Tests pass but coverage fails

- **WHEN** all test files and tests pass but a coverage threshold is unmet
- **THEN** verification SHALL report the test gate as green, the coverage gate as failed, and the exact unmet threshold without misclassifying test behavior

#### Scenario: Both tests and coverage pass

- **WHEN** all tests pass and all approved thresholds are met
- **THEN** the canonical command SHALL exit successfully and verification SHALL record both gates as green
