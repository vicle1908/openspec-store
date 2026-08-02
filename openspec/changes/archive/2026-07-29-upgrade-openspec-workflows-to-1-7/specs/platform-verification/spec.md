## MODIFIED Requirements

### Requirement: OpenSpec validation is part of the release gate (Phase 2 extended)
Pull-request and release gates SHALL install the exact repository-approved
OpenSpec CLI version on a compatible pinned Node.js runtime, assert the resolved
CLI version, and run `openspec validate --strict --all --no-interactive`. The
gate MUST fail when installation, version assertion, or validation fails and
MUST NOT silently skip validation because the command is absent.

#### Scenario: OpenSpec validation is green before release tag
- **WHEN** the release-evidence workflow runs against a `v*` tag
- **THEN** it installs and verifies the repository-approved OpenSpec version, runs strict non-interactive validation for all changes and specs, and fails the tag if any step exits non-zero

#### Scenario: Pull-request runner lacks OpenSpec
- **WHEN** the normal verification workflow starts on a runner without the OpenSpec command
- **THEN** it installs the exact approved version and runs strict validation instead of reporting a successful skip

#### Scenario: Installed OpenSpec version drifts
- **WHEN** the resolved CLI version differs from the repository-approved version
- **THEN** the gate fails before validation and reports both versions without modifying the repository pin
