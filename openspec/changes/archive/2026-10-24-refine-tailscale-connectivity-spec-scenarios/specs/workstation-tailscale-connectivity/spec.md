# workstation-tailscale-connectivity Specification

## MODIFIED Requirements

### Requirement: Permanent node key expiry disablement and double-NAT peer-relay gating

The workstation node (`iosteam-mac-mini`) SHALL maintain disabled key expiry (`KeyExpiry: null` / `Never`) on its rotated node key and SHALL withhold tailnet-wide `tailscale.com/cap/relay` ACL grants while upstream double-NAT gateways lack external `UDP 41642` port forwarding.

#### Scenario: Permanent key expiry disablement is active
- **WHEN** `tailscale debug netmap` and `tailscale status --json` are queried for `SelfNode` / `Self`
- **THEN** `Self.PublicKey` SHALL be `nodekey:875e7cbbafcdf9d9498cc1c1728f5bb4e196c81e6a3889a5cf7b4c059119a108`
- **AND** `KeyExpiry` SHALL evaluate to `null` (omitted, corresponding to `Key expiry: Never` in the Tailscale client UI)

#### Scenario: Peer relay avoids blackholing under unforwarded double NAT
- **WHEN** `tailscale debug portmap` reports `{PCP:false PMP:false UPnP:false}` behind double-NAT gateways (`192.168.10.1` and `192.168.1.1`) without inbound `UDP 41642` port forwarding
- **THEN** `iosteam-mac-mini` SHALL keep local `RelayServerPort: 41642` bound on `udp4:41642` and `udp6:41642` while `tailscale debug peer-relay-servers` remains empty (`[]`) so remote symmetric-NAT peers route cleanly through `DERP(hkg)` without timeout penalties
- **AND** LAN peers (`iphone-15-pro-max` on `192.168.10.67` ephemeral UDP port) SHALL connect directly over UDP (`<10ms` RTT)

### Requirement: Randomized WireGuard client port and DERP 20 regional convergence

The workstation SHALL avoid static UDP `:41641` LAN source-port collisions by enabling WireGuard client port randomization (`RandomizeClientPort: true` via the `randomize-client-port` node attribute) and rebinding `magicsock`, and the tailnet policy SHALL suppress `DERP 3` (`sin`) in `derpMap` so Hanoi nodes converge on `DERP 20` (`hkg`) while preserving `RelayServerPort: 41642` and `RelayServerStaticEndpoints: ["1.54.174.244:41642"]`.

#### Scenario: Client port randomization eliminates LAN 41641 source-port collision after rebind
- **WHEN** the `randomize-client-port` node attribute is applied in the tailnet policy and the tunnel is rebound and checked via `tailscale netcheck`
- **THEN** `tailscale debug control-knobs` SHALL report `"RandomizeClientPort": true`
- **AND** `SelfNode.Endpoints` in `tailscale debug netmap` SHALL bind an ephemeral local UDP port (`!= 41641`) that maps to a non-1024 external STUN port on `1.54.174.244` without colliding with other LAN Tailscale devices (`iphone-15-pro-max`)

#### Scenario: DERP 3 suppression converges Hanoi peers on DERP 20 while preserving peer-relay prefs
- **WHEN** `"derpMap": {"Regions": {"3": null}}` is configured in the tailnet policy and `tailscale debug netmap` and `tailscale debug prefs` are inspected
- **THEN** `DERPMap.Regions` in `tailscale debug netmap` SHALL omit region `3` (`sin`), `Self.Relay` in `tailscale status --json` SHALL be `"hkg"`, and online Hanoi peers (`Peers[].HomeDERP`) SHALL report `20`
- **AND** `tailscale debug prefs` SHALL preserve `RelayServerPort: 41642` and `RelayServerStaticEndpoints: ["1.54.174.244:41642"]`
