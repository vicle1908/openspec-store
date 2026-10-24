# workstation-tailscale-connectivity Specification

## ADDED Requirements

### Requirement: Dual-port Tailscale Serve HTTPS proxying for OmniRoute and Hermes WebUI

The workstation SHALL expose both OmniRoute (`http://127.0.0.1:20128`) and Hermes WebUI (`http://127.0.0.1:8787`) concurrently over tailnet-only HTTPS via Tailscale Serve on ports `443` and `8443` respectively.

#### Scenario: Concurrent HTTPS serve routes on ports 443 and 8443
- **WHEN** `tailscale serve status --json` is inspected
- **THEN** TCP port `443` (`HTTPS: true`) SHALL map `iosteam-mac-mini.tailc6b508.ts.net:443` `/` to `http://127.0.0.1:20128`
- **AND** TCP port `8443` (`HTTPS: true`) SHALL map `iosteam-mac-mini.tailc6b508.ts.net:8443` `/` to `http://127.0.0.1:8787`
- **AND** both loopback backends (`http://127.0.0.1:20128/api/monitoring/health` and `http://127.0.0.1:8787/health`) SHALL return HTTP `200`

### Requirement: Permanent node key expiry disablement and double-NAT peer-relay gating

The workstation node (`iosteam-mac-mini`) SHALL maintain disabled key expiry (`KeyExpiry: null` / `Never`) on its rotated node key and SHALL withhold tailnet-wide `tailscale.com/cap/relay` ACL grants while upstream double-NAT gateways lack external `UDP 41642` port forwarding.

#### Scenario: Permanent key expiry disablement is active
- **WHEN** `tailscale debug netmap` and `tailscale status --json` are queried for `SelfNode` / `Self`
- **THEN** `Self.PublicKey` SHALL be `nodekey:875e7cbbafcdf9d9498cc1c1728f5bb4e196c81e6a3889a5cf7b4c059119a108`
- **AND** `KeyExpiry` SHALL evaluate to `null` (omitted, corresponding to `Key expiry: Never` in the Tailscale client UI)

#### Scenario: Peer relay avoids blackholing under unforwarded double NAT
- **WHEN** `tailscale debug portmap` reports `{PCP:false PMP:false UPnP:false}` behind double-NAT gateways (`192.168.10.1` and `192.168.1.1`) without inbound `UDP 41642` port forwarding
- **THEN** `iosteam-mac-mini` SHALL keep local `RelayServerPort: 41642` bound on `udp4:41642` and `udp6:41642` while `tailscale debug peer-relay-servers` remains empty (`[]`) so remote symmetric-NAT peers route cleanly through DERP (`sin` / `hkg`) without timeout penalties
- **AND** LAN peers (`iphone-15-pro-max` on `192.168.10.67:41641`) SHALL connect directly over UDP (`<10ms` RTT)
