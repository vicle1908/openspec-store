## ADDED Requirements

### Requirement: Local MCP runners SHALL use deterministic local binary paths

When an MCP server is configured in `mcp_servers` and has a locally installed global or project CLI binary, Hermes SHALL be configured to execute the local binary directly rather than invoking dynamic package runners (`npx`, `uvx`) on each startup.

#### Scenario: Local MCP runner is configured
- **WHEN** an MCP server entry (such as `mcp-router`) is declared in `~/.hermes/config.yaml`
- **AND** a matching CLI binary exists locally in a sanctioned path (such as `~/.npm-global/bin/mcpr`)
- **THEN** `command` SHALL specify the absolute path to the local binary
- **AND** dynamic download or execution flags (such as `npx -y`) SHALL NOT be used.

### Requirement: MCP server credentials SHALL use environment variable interpolation

When an MCP server declared in `mcp_servers` requires an authentication token, API key, or credential, the credential SHALL be isolated outside non-secret configuration files and referenced using environment variable interpolation.

#### Scenario: MCP server requires authentication token
- **WHEN** an MCP server entry in `~/.hermes/config.yaml` declares an environment variable holding an authentication secret (such as `MCPR_TOKEN`)
- **THEN** the value in `config.yaml` SHALL use environment variable interpolation syntax (such as `${MCPR_TOKEN}`)
- **AND** the actual secret value SHALL be stored in `~/.hermes/.env` or exported by the shell environment.

### Requirement: Source update state and locks SHALL remain clean

Hermes runtime directory SHALL NOT retain orphaned update locks, interrupted sync markers, or unfinalized asset compilations across active agent sessions.

#### Scenario: Interrupted source update is detected
- **WHEN** an interrupted source update leaves stale locks or pending dependencies in `~/.hermes/`
- **THEN** running `hermes update --check` SHALL resolve unfinalized dependencies and clear stale update locks before runtime operations proceed.
