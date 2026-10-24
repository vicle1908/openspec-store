# Proposal: Refine Tailscale Connectivity Spec Scenarios for Ephemeral LAN Ports and DERP 20 Assertions

## Why

Post-archive verification (`/opsx:verify`) of `workstation-tailscale-connectivity` identified two minor scenario wording redundancies in `openspec/specs/workstation-tailscale-connectivity/spec.md` and `wiki/entities/tailscale.md`: (1) `Scenario: DERP 3 suppression converges Hanoi peers on DERP 20 while preserving peer-relay prefs` (`spec.md:86-87`) contains a duplicate `- **THEN**` line referencing `SelfNode.HomeDERP` alongside `Self.Relay: "hkg"`; and (2) `Scenario: Peer relay avoids blackholing under unforwarded double NAT` (`spec.md:72-73` and `wiki/entities/tailscale.md:43`) still cites `192.168.10.67:41641` and `DERP(sin)` instead of randomized ephemeral LAN UDP ports and `DERP(hkg)`.

## What Changes

- **Deduplicate `DERP 3` Suppression Scenario Assertion (`workstation-tailscale-connectivity`)**:
  - Update `Requirement: Randomized WireGuard client port and DERP 20 regional convergence` via `## MODIFIED Requirements` to remove the redundant `- **THEN**` line referencing `SelfNode.HomeDERP` while retaining `DERPMap.Regions` omitting region `3` (`sin`), `Self.Relay: "hkg"`, and `.Peers[].HomeDERP: 20`.
- **Update LAN Peer Port & `DERP(hkg)` Wording (`workstation-tailscale-connectivity` & `wiki/entities/tailscale.md`)**:
  - Update `Requirement: Permanent node key expiry disablement and double-NAT peer-relay gating` (`spec.md:72-73`) and `wiki/entities/tailscale.md:43` to reference randomized ephemeral LAN UDP ports on `192.168.10.67` and `DERP(hkg)` relay routing.

## Non-Goals

- Editing any file under `openspec/changes/archive/` (archived changes remain strictly immutable).
- Changing any live Tailscale daemon configuration, tailnet policy, or CLI wrapper state.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `workstation-tailscale-connectivity`: Refines scenario wording in `Requirement: Permanent node key expiry disablement and double-NAT peer-relay gating` and `Requirement: Randomized WireGuard client port and DERP 20 regional convergence`.

## Impact

- **Ownership Boundary**: `openspec/specs/workstation-tailscale-connectivity/spec.md` in `/Users/androidteam/Developer/platform/openspec-store` and `entities/tailscale.md` / `log.md` in `/Users/androidteam/Developer/wiki`.
