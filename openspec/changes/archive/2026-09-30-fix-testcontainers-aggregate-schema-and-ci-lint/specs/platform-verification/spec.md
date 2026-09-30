# Spec Delta: Platform Verification CI Toolchain Patch

## Purpose

Ensures CI workflow verification gates use patched Go runtime patch releases (>= 1.26.6) to prevent false-positive vulnerability reports in Go standard library packages during `govulncheck` execution.

## MODIFIED Requirements

### Requirement: Pull requests pass deterministic fast gates

Every pull request SHALL pass formatting, generated-code cleanliness, dependency and architecture checks, Buf lint and breaking checks, migration parsing, unit tests, race-enabled tests for concurrent packages, and required integration tests. CI SHALL use the pinned Go toolchain (at patch level 1.26.6 or later within the Go 1.26 line), SHALL disable result caching for release-significant test runs, and SHALL publish machine-readable test and coverage output.

#### Scenario: Go toolchain incorporates security patch releases
- **WHEN** pull request verification gates execute in CI with vulnerability scanning (`govulncheck`)
- **THEN** CI SHALL provision Go 1.26.6 or higher so that standard library packages (`net/http`) contain official vulnerability resolutions.

#### Scenario: Pull request changes command concurrency
- **WHEN** a pull request changes command handling, repository concurrency, consumer receipt handling, or worker lifecycle code
- **THEN** the relevant race-enabled and integration suites run and block merge on failure
