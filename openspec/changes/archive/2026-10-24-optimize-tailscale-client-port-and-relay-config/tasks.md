# Tasks: Optimize Tailscale Client Port Randomization and Hanoi DERP 20 Convergence

## 1. Tailnet Policy Update (`randomize-client-port` & `derpMap` Region 3 Suppression)

- [x] 1.1 Update the tailnet policy file in the Tailscale Admin Console (`https://login.tailscale.com/admin/acls/file`) via the operator's authenticated `victory1908@gmail.com` Chrome profile to include `"randomize-client-port"` in `nodeAttrs` targeting `autogroup:member` and `"derpMap": {"Regions": {"3": null}}` at the top level
- [x] 1.2 Cycle/rebind `magicsock` and refresh STUN endpoints (`tailscale down && tailscale up && tailscale netcheck`), verify `RelayServerPort: 41642` and `RelayServerStaticEndpoints: ["1.54.174.244:41642"]` in `tailscale debug prefs`, and verify `tailscale debug control-knobs | jq .RandomizeClientPort` (`true`), `Self.Relay` (`"hkg"`), and `SelfNode.Endpoints` (`192.168.10.78:52816` -> `1.54.174.244:52816`) in `tailscale debug netmap`

## 2. Verification, Wiki Sync, and OpenSpec Validation

- [x] 2.1 Record live verification outputs in `evidence.md`, update `~/Developer/wiki/entities/tailscale.md` to document `RandomizeClientPort: true` and `DERP 20` (`hkg`) convergence, and validate `optimize-tailscale-client-port-and-relay-config` with `openspec validate optimize-tailscale-client-port-and-relay-config --strict --json --store openspec-store`
