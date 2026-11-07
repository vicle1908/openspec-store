# Spec Delta: workstation-tailscale-connectivity

## MODIFIED Requirements

### Requirement: Active Tailscale Network Extension tunnel, MagicDNS, and Tailscale Serve routing

The workstation's Tailscale Network Extension (`io.tailscale.ipn.macsys.network-extension`) SHALL maintain `BackendState: "Running"` with active `utun` IPv4/IPv6 addressing, MagicDNS resolution for `tailc6b508.ts.net`, Tailscale Serve HTTPS proxying, and raw L4 TCP forwarding for OmniRoute inference and AgentMemory mesh traffic.

#### Scenario: Post-upgrade tunnel and MagicDNS verification
- **WHEN** `tailscale-app` is upgraded or restarted on macOS
- **THEN** `tailscale status --json` SHALL report `BackendState: "Running"` and `Self.Online: true` with zero health warnings (`Health: []`)
- **AND** the host `utun` interface SHALL carry `100.70.16.83` (`fd7a:115c:a1e0::a938:1053`)
- **AND** `scutil --dns` SHALL register `100.100.100.100` (`fd7a:115c:a1e0::53`) as the scoped resolver for `tailc6b508.ts.net`

#### Scenario: Tailscale Serve HTTPS proxy remains active
- **WHEN** `tailscale serve status --json` is queried
- **THEN** `https://iosteam-mac-mini.tailc6b508.ts.net` (port `443`, tailnet-only) SHALL proxy `/` to `http://127.0.0.1:20128`
- **AND** the upstream loopback health endpoint `http://127.0.0.1:20128/api/monitoring/health` SHALL return HTTP `200`

#### Scenario: Tailscale Serve exposes raw L4 TCP port 3111 for AgentMemory mesh traffic
- **WHEN** `tailscale serve status --json` is inspected on `iosteam-mac-mini` or `macbook-pro-m5`
- **THEN** TCP port `3111` SHALL be actively mapped to `127.0.0.1:3111` under the tailnet-only listener table (`tcp://100.70.16.83:3111` and `tcp://100.101.64.56:3111`)
- **AND** remote tailnet peers SHALL be able to establish TCP connections to `:3111` without physical LAN interfaces exposing the port
