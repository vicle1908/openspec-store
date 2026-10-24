# Evidence: refine-tailscale-connectivity-spec-scenarios

**Date:** 2026-10-24
**Change:** `refine-tailscale-connectivity-spec-scenarios`

---

## 1. Immutable Archive & Scenario Verification

- Verified `git diff --name-only HEAD -- openspec/changes/archive` is empty (`0` modified archived files).
- Deduplicated `- **THEN**` assertion in `Scenario: DERP 3 suppression converges Hanoi peers on DERP 20 while preserving peer-relay prefs` (`Self.Relay: "hkg"`, `DERPMap.Regions["3"] == null`, `Peers[].HomeDERP == 20`).
- Updated `Scenario: Peer relay avoids blackholing under unforwarded double NAT` (`spec.md:72-73`) and `wiki/entities/tailscale.md:43` to reflect randomized ephemeral LAN UDP ports (`192.168.10.67:52744`) and `DERP(hkg)` convergence.
