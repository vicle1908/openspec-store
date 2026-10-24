# Tasks: Refine Tailscale Connectivity Spec Scenarios for Ephemeral LAN Ports and DERP 20 Assertions

## 1. Spec Scenario & Wiki Refinement

- [x] 1.1 Update `wiki/entities/tailscale.md` (`L43`) and `wiki/log.md` to reference randomized ephemeral LAN UDP ports on `192.168.10.67` and `DERP(hkg)` relay routing
- [x] 1.2 Record verification evidence in `evidence.md`, verify `openspec/changes/archive/` has zero modifications (`git status --short -- openspec/changes/archive`), and validate `refine-tailscale-connectivity-spec-scenarios` strictly via `openspec validate refine-tailscale-connectivity-spec-scenarios --strict --json --store openspec-store`
