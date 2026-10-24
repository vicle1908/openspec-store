# Design: Refine Tailscale Connectivity Spec Scenarios for Ephemeral LAN Ports and DERP 20 Assertions

## Context

See `proposal.md` — Why. Following the `/opsx:verify` audit of `2026-10-24-optimize-tailscale-client-port-and-relay-config` and the `openspec-immutable-archive-correction` workflow, archived change directories under `openspec/changes/archive/` must remain immutable while scenario refinements are applied via a corrective change targeting `workstation-tailscale-connectivity`.

## Goals / Non-Goals

- **Goals**:
  - Remove the duplicate `- **THEN**` line (`spec.md:86`) in `Scenario: DERP 3 suppression converges Hanoi peers on DERP 20 while preserving peer-relay prefs`.
  - Update `spec.md:72-73` and `wiki/entities/tailscale.md:43` to reflect randomized ephemeral LAN UDP ports on `192.168.10.67` and `DERP(hkg)` convergence.
  - Guarantee zero edits to `openspec/changes/archive/`.
- **Non-Goals**:
  - Modifying live Tailscale daemon or policy state (already verified compliant).

## Decisions

1. **Apply `## MODIFIED Requirements` on the two affected requirements in `workstation-tailscale-connectivity`**:
   - Updates `Requirement: Permanent node key expiry disablement and double-NAT peer-relay gating` and `Requirement: Randomized WireGuard client port and DERP 20 regional convergence` in `openspec/specs/workstation-tailscale-connectivity/spec.md` during `openspec archive` while keeping `openspec/changes/archive/*` untouched (`git diff --name-only HEAD -- openspec/changes/archive` empty).

## Transaction & Verification Boundaries

- Verified via `openspec validate workstation-tailscale-connectivity --strict --json --store openspec-store`, `git diff --name-only HEAD -- openspec/changes/archive`, and `wiki-lint.py`.
