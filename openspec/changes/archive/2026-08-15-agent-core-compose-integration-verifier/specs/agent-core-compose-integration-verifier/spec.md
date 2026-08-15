## ADDED Requirements

### Requirement: The local agent-core verifier exposes a stable CLI

The platform SHALL build `platform/cmd/agent-core` as a binary that exposes `version` and `health` commands. `version` SHALL exit zero and print a version identifier. `health` SHALL print a JSON report and SHALL exit zero only when every selected local dependency is healthy.

#### Scenario: Version command is available

- **WHEN** the built binary is invoked as `agent-core version`
- **THEN** it prints a version identifier and exits zero

#### Scenario: Health command reports all selected dependencies

- **WHEN** the Compose records for postgres, kafka, temporal, and mailpit are running and healthy
- **THEN** `agent-core health` emits one report containing all four services and exits zero

### Requirement: Compose health parsing fails closed

The verifier SHALL parse both the single-object and array forms of `docker compose ps --format json`. Empty output, malformed JSON, missing requested service records, stopped containers, and non-healthy health values SHALL produce an unhealthy service result and a non-zero health command exit. A missing `Health` field SHALL be accepted when the container state is `running`.

#### Scenario: Array-form Compose output is accepted

- **WHEN** Compose returns a JSON array containing running records for every selected service
- **THEN** the verifier reports all services healthy and exits zero

#### Scenario: Empty Compose output fails

- **WHEN** Compose returns no records for a requested service
- **THEN** the verifier reports that service as unhealthy and exits non-zero

#### Scenario: Malformed Compose output fails

- **WHEN** Compose returns invalid JSON
- **THEN** the verifier reports a parse failure and exits non-zero rather than treating the service as healthy

#### Scenario: Stopped or unhealthy containers fail

- **WHEN** a selected container is stopped or has a health value other than `healthy` or empty
- **THEN** the verifier reports the observed state and exits non-zero

### Requirement: The integration script is portable and bounded

The integration script SHALL derive its repository root from its own path, use repository-relative Compose defaults, accept an executable `AGENT_CORE_BIN` override, build from `platform/cmd/agent-core` when no override is supplied, poll health with a bounded timeout, and run with Bash strict mode. It SHALL clean up the Compose project it started and SHALL remove only binaries it built itself.

#### Scenario: Script runs from another working directory

- **WHEN** the script is invoked from outside the repository with no binary override
- **THEN** it resolves the repository root, builds from the platform module, and uses the repository's Compose file and env file

#### Scenario: Caller-owned binary is preserved

- **WHEN** the script is given an executable `AGENT_CORE_BIN`
- **THEN** it uses that binary and does not remove it during cleanup

#### Scenario: Invalid override fails before Compose mutation

- **WHEN** `AGENT_CORE_BIN` points to a missing or non-executable path
- **THEN** the script exits non-zero with an actionable error before starting Compose

#### Scenario: Empty or invalid Compose status does not pass

- **WHEN** the Compose status command fails, returns invalid JSON, or returns an empty record set
- **THEN** the script reports the failure and does not claim that services are healthy

### Requirement: Integration verifier behavior has deterministic regression coverage

The repository SHALL provide deterministic regression tests for the binary's Compose parser and the shell script's portability, strict mode, override validation, cleanup ownership, timeout handling, and exit-code propagation. These tests SHALL run without Docker, credentials, or network access.

#### Scenario: Focused regression suite is environment independent

- **WHEN** the regression suite runs on a host without a Compose stack
- **THEN** it uses temporary fixtures and exits zero only when all portability and safety assertions pass
