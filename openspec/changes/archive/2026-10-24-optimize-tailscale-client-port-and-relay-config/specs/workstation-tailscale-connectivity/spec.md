# workstation-tailscale-connectivity Specification

## ADDED Requirements

### Requirement: Randomized WireGuard client port and DERP 20 regional convergence

The workstation SHALL avoid static UDP `:41641` LAN source-port collisions by enabling WireGuard client port randomization (`RandomizeClientPort: true` via the `randomize-client-port` node attribute) and rebinding `magicsock`, and the tailnet policy SHALL suppress `DERP 3` (`sin`) in `derpMap` so Hanoi nodes converge on `DERP 20` (`hkg`) while preserving `RelayServerPort: 41642` and `RelayServerStaticEndpoints: ["1.54.174.244:41642"]`.

#### Scenario: Client port randomization eliminates LAN 41641 source-port collision after rebind
- **WHEN** the `randomize-client-port` node attribute is applied in the tailnet policy and the tunnel is rebound and checked via `tailscale netcheck`
- **THEN** `tailscale debug control-knobs` SHALL report `"RandomizeClientPort": true`
- **AND** `SelfNode.Endpoints` in `tailscale debug netmap` SHALL bind an ephemeral local UDP port (`!= 41641`) that maps to a non-1024 external STUN port on `1.54.174.244` without colliding with other LAN Tailscale devices (`iphone-15-pro-max`)

#### Scenario: DERP 3 suppression converges Hanoi peers on DERP 20 while preserving peer-relay prefs
- **WHEN** `"derpMap": {"Regions": {"3": null}}` is configured in the tailnet policy and `tailscale debug netmap` and `tailscale debug prefs` are inspected
- **THEN** `DERPMap.Regions` in `tailscale debug netmap` SHALL omit region `3` (`sin`) and `SelfNode.HomeDERP` SHALL be `20` (`hkg`)
- **THEN** `DERPMap.Regions` in `tailscale debug netmap` SHALL omit region `3` (`sin`) and `Self.Relay` in `tailscale status --json` SHALL be `"hkg"`
