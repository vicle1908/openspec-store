# Tasks

## 1. Cross-Node Runtime & Tailscale Serve Convergence

- [x] 1.1 Update `~/Library/Application Support/orca/orca-environments.json` (`macbook-pro-m5` endpoint `ws://100.106.143.78:6768`) and `~/.ssh/config` (`Host 100.70.16.83 iosteam-mac-mini* 100.106.143.78 100.101.64.56 macbook-pro*`), and verify `orca terminal list --environment macbook-pro-m5 --json` succeeds
- [x] 1.2 Enable `tailscale serve --bg --tcp=3111 127.0.0.1:3111` on `macbook-pro-m5` (`100.106.143.78`), replace the stale `100.101.64.56:3111` AgentMemory peer on `iosteam-mac-mini` with `http://100.106.143.78:3111`, and verify `POST http://localhost:3111/agentmemory/mesh/sync` completes with `errors: []`
- [x] 1.3 Collaborate with the active OMP session on `macbook-pro-m5` (`term_e8efcadd-aa4c-4b63-b841-80b1f47ae3cb`, `enable-workstation-tailnet-subnet-routing`) to codify the 12 approved `/32` routes, Tailscale Serve `:3111` preservation, and `user-dial-routes` mobile DNS guidance across `shb-specs`, `shb-skills`, and `shb-docs`

## 2. Provisioning Script, Managed Skills & Knowledge Hub Synchronization

- [x] 2.1 Update `~/Developer/scripts/setup-macbook-omniroute-client.sh` (`CLIENT_TS_IP="100.106.143.78"`, bundle-safe `resolve_ts_bin()` allowing standalone Go CLI and shell wrappers while rejecting raw symlinks to `Tailscale.app/Contents/MacOS/Tailscale`, `relay in ("hkg", "tok")`, and 6-port Tailscale Serve check including `3111`) and verify `~/Developer/scripts/setup-macbook-omniroute-client.sh --check` exits `0` on both `iosteam-mac-mini` and `macbook-pro-m5`
- [x] 2.2 Update `~/Developer/wiki/entities/tailscale.md`, `~/Developer/wiki/entities/agentmemory.md`, and OMP managed skills (`tailscale-macos-cross-node-optimization`, `tailscale-macos-mesh-and-nat-audit`, `agentmemory-tailnet-mesh-sync`) to reflect `macbook-pro-m5` (`100.106.143.78`, `1.104.5` standalone `tailscaled`, 12 `/32` subnet routes, Split DNS, and `:3111` mesh sync)
- [x] 2.3 Run `openspec validate reconcile-cross-node-tailscale-subnet-router-and-mesh-parity --strict --store openspec-store`, `python3 ~/Developer/platform/openspec-store/scripts/validate-archive-readiness.py --change reconcile-cross-node-tailscale-subnet-router-and-mesh-parity --store /Users/androidteam/Developer/platform/openspec-store --strict`, and `~/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh`
