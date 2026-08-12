# Specs: setup-hermes-webui-tailscale-access

## ADDED Requirements

### Requirement: Authenticated Tailscale access
The system SHALL expose Hermes WebUI through a tailnet-only HTTPS endpoint and require application password authentication.

#### Scenario: Authorized iPhone access
- **WHEN** an iPhone connected to the same tailnet opens the configured HTTPS URL
- **THEN** Hermes WebUI SHALL present its authentication flow
- **AND** a valid password SHALL establish an authenticated session

#### Scenario: Wrong password rejected
- **WHEN** an incorrect password is submitted to /api/auth/login
- **THEN** the server SHALL return HTTP 401
- **AND** no session cookie SHALL be issued

### Requirement: Loopback-only backend
The system SHALL bind Hermes WebUI to loopback and use Tailscale Serve as the remote-access proxy.

#### Scenario: Direct tailnet-port access
- **WHEN** a peer attempts to connect directly to the Mac's Tailscale IP on port 8787
- **THEN** the connection SHALL be refused (loopback-only binding)
- **AND** remote access SHALL use the HTTPS Tailscale Serve hostname

### Requirement: Reboot persistence
The system SHALL run Hermes WebUI under a macOS LaunchAgent with restart-on-exit behavior.

#### Scenario: WebUI process exits
- **WHEN** the supervised WebUI process exits or is killed
- **THEN** launchd SHALL start a replacement process
- **AND** the replacement SHALL listen on loopback port 8787
- **AND** the replacement SHALL respond to /health with status=ok

### Requirement: Adapter port preservation
The Claude code provider adapter SHALL be preserved on a non-conflicting host port.

#### Scenario: Adapter health after port remap
- **WHEN** the adapter container is running on host port 8788
- **THEN** http://127.0.0.1:8788/health SHALL return adapter status=ok
- **AND** all adapter consumers SHALL reference port 8788
