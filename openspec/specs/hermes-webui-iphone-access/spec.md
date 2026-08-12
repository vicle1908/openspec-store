# hermes-webui-iphone-access Specification

## Purpose
TBD - created by archiving change verify-hermes-webui-iphone-access. Update Purpose after archive.
## Requirements
### Requirement: HTTPS reachability from iPhone
The configured Tailscale Serve HTTPS endpoint SHALL be reachable from an iPhone on the same tailnet via Safari.

#### Scenario: Health check from iPhone Safari
- **WHEN** an iPhone connected to the victory1908 tailnet opens https://iosteam-mac-mini.tailc6b508.ts.net/health in Safari
- **THEN** the browser SHALL receive an HTTP 200 response
- **AND** the response body SHALL contain "status":"ok"

### Requirement: Hermex authenticated chat
The Hermex iOS app SHALL be able to authenticate and exchange messages through the Hermes WebUI Tailscale endpoint.

#### Scenario: Authenticated message exchange
- **WHEN** Hermex is configured with the server URL and password
- **AND** the user sends a test message
- **THEN** Hermex SHALL receive a response from Hermes Agent
