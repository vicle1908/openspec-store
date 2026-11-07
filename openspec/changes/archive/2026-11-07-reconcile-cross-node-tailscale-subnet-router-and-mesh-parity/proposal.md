# Proposal

## Why

Transitioning `macbook-pro-m5` (`macbook-pro-ca-l-1`) from the macOS System Extension (`io.tailscale.ipn.macsys`, `100.101.64.56`) to standalone `tailscaled-on-macOS` (`1.104.5`, `100.106.143.78`, `nKXQthqsNM11CNTRL`) enabled userspace `gVisor netstack` `/32` subnet routing (`10.4.82.20/21/23` + 9 internal SHB hosts) and Split DNS (`shb.com.vn`, `shbho.shb.vn`, `shb.vn`), but left `iosteam-mac-mini`'s specifications, `setup-macbook-omniroute-client.sh`, Orca environment, AgentMemory mesh peer, SSH keepalives, wiki entities, and managed skills pinned to the retired `100.101.64.56` (`macsys`) assumptions. Reconciling these cross-workstation contracts eliminates false audit failures on `setup-macbook-omniroute-client.sh --check` (`Self.Relay in {"hkg", "tok"}`, dual-variant CLI resolution) and restores seamless AgentMemory mesh synchronization (`:3111`), Orca remote collaboration (`:6768`), and zero-configuration internal SHB host access across the tailnet.

## What Changes

- **Reconcile `workstation-tailscale-connectivity` Specification for Dual-Profile Cross-Workstation Topology**:
  - Update `Single-authority Tailscale Cask installation and shell wrapper CLI` to distinguish between the `iosteam-mac-mini` Server Host profile (Homebrew Cask `tailscale-app` via `/usr/local/bin/tailscale`) and the `macbook-pro-m5` Subnet Router Client profile (standalone `tailscaled-on-macOS` via `/Library/LaunchDaemons/sh.brew.tailscale.plist` and socket-aware `/opt/homebrew/bin/tailscale` / `/usr/local/bin/tailscale`).
  - Update `Active Tailscale Network Extension tunnel, MagicDNS, and Tailscale Serve routing`, `Idempotent macbook-pro-m5 remote OmniRoute client provisioning and verification`, and `Cross-node SSH keepalive and background peer dialer DERP queue hygiene` to target `macbook-pro-m5`'s active IP `100.106.143.78`, accept `Self.Relay` in `{"hkg", "tok"}`, require `tailscale serve --bg --tcp=3111 127.0.0.1:3111` on both nodes, and verify zero-configuration `/32` subnet routing and Split DNS resolution from `iosteam-mac-mini`.
- **Update `~/Developer/scripts/setup-macbook-omniroute-client.sh`**:
  - Update `CLIENT_TS_IP="100.106.143.78"` (while retaining legacy `100.101.64.56` in SSH keepalive host patterns for backward compatibility).
  - Allow valid Homebrew formula `tailscale` binaries/wrappers alongside `/usr/local/bin/tailscale` while still rejecting raw symlinks pointing directly to `/Applications/Tailscale.app/Contents/MacOS/Tailscale`.
  - Accept `Self.Relay in ("hkg", "tok")` so Viettel FTTH dynamic East Asia routing to Tokyo (`tok`) or Hong Kong (`hkg`) passes `--check`, and verify the 6-port Tailscale Serve topology (`20128`, `20129`, `20132`, `3111` L4 TCP + `443`, `8443` HTTPS) on `iosteam-mac-mini`.
- **Synchronize Cross-Node Runtime Bindings, Wiki Entities & Managed Skills**:
  - Update `~/Library/Application Support/orca/orca-environments.json` (`ws://100.106.143.78:6768`), `~/.ssh/config`, and AgentMemory mesh peer registration (`http://100.106.143.78:3111`).
  - Update `~/Developer/wiki/entities/tailscale.md`, `~/Developer/wiki/entities/agentmemory.md`, and the 3 OMP managed skills (`tailscale-macos-cross-node-optimization`, `tailscale-macos-mesh-and-nat-audit`, `agentmemory-tailnet-mesh-sync`), then synchronize to Notion via `sync-notion-knowledge.sh`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `workstation-tailscale-connectivity`: Reconcile CLI binary resolution, Tailscale Serve `:3111` L4 TCP forwarding, `macbook-pro-m5` IP (`100.106.143.78`), `Self.Relay` (`hkg`/`tok`), SSH/Orca keepalive hygiene, and zero-configuration `/32` subnet routing + Split DNS verification across `iosteam-mac-mini` and `macbook-pro-m5`.

## Impact

- **Specifications**: `platform/openspec-store/openspec/specs/workstation-tailscale-connectivity/spec.md`
- **Scripts & Configs**: `~/Developer/scripts/setup-macbook-omniroute-client.sh`, `~/.ssh/config`, `~/Library/Application Support/orca/orca-environments.json`
- **Knowledge & Skills**: `~/Developer/wiki/entities/tailscale.md`, `~/Developer/wiki/entities/agentmemory.md`, `~/.omp/agent/managed-skills/{tailscale-macos-cross-node-optimization,tailscale-macos-mesh-and-nat-audit,agentmemory-tailnet-mesh-sync}/SKILL.md`
