# Design

## Context

The dual-workstation Tailscale mesh spans:
1. **`iosteam-mac-mini` (`100.70.16.83`, Server Host)**: Runs Homebrew Cask `tailscale-app` (`io.tailscale.ipn.macsys` Network Extension), exposes `/usr/local/bin/tailscale` shell wrapper, `CorpDNS: true`, `RouteAll: true`, and 6-port Tailscale Serve (`20128`, `20129`, `20132`, `3111` L4 TCP + `443`, `8443` HTTPS).
2. **`macbook-pro-m5` (`macbook-pro-ca-l-1`, `100.106.143.78`, Node ID `nKXQthqsNM11CNTRL`, Subnet Router Client)**: Transitioned from the macOS System Extension (`100.101.64.56`) to standalone `tailscaled-on-macOS` (`1.104.5`, `/Library/LaunchDaemons/sh.brew.tailscale.plist`) so `cmd/tailscaled/tailscaled.go:812-835` (`handleSubnetsInNetstack() == true`) forwards 12 surgical `/32` routes (`10.4.82.20/21/23` corporate DNS + 9 internal SHB endpoints) through `gVisor netstack` over corporate Ethernet (`en7`/`en8`) with `--accept-dns=false` (`CorpDNS: false`), native `/etc/resolver/*`, and `sysctl net.inet.ip.forwarding=0`.

## Goals / Non-Goals

**Goals:**
- Reconcile `setup-macbook-omniroute-client.sh`, `workstation-tailscale-connectivity/spec.md`, `orca-environments.json`, `~/.ssh/config`, AgentMemory mesh peers, wiki entities, and managed skills with `macbook-pro-m5`'s standalone `tailscaled` architecture (`100.106.143.78`).
- Ensure `tailscale serve --bg --tcp=3111 127.0.0.1:3111` is active on both workstations and bidirectional AgentMemory mesh synchronization succeeds with zero errors.
- Coordinate with the active OMP session on `macbook-pro-m5` (`enable-workstation-tailnet-subnet-routing`) so both OpenSpec stores (`openspec-store` and `shb-specs`) share identical IP, `/32` route, Split DNS, and Tailscale Serve `:3111` contracts.

**Non-Goals:**
- Switching `iosteam-mac-mini` away from `tailscale-app` Cask (since `iosteam-mac-mini` does not advertise subnet routes over a secondary corporate Ethernet interface).
- Advertising broad RFC1918 supernets (`10.0.0.0/8`, `172.16.0.0/12`) or enabling kernel IP forwarding.

## Decisions

### Decision 1: Dual-Profile CLI Resolution in `setup-macbook-omniroute-client.sh`
Rather than rejecting all symlinks (`[[ -L "${ts_bin}" ]]`), `resolve_ts_bin()` in `setup-macbook-omniroute-client.sh` will resolve the symlink target via `python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))'` and fail **only** if `ts_bin` is a symlink pointing directly to `/Applications/Tailscale.app/Contents/MacOS/Tailscale` (which triggers `BundleIdentifiers.swift:49: Fatal error`). Valid shell wrappers (`/usr/local/bin/tailscale`, `/opt/homebrew/bin/tailscale`) and pure-Go Homebrew Cellar binaries (`/opt/homebrew/Cellar/tailscale/*/bin/tailscale`) pass cleanly.

### Decision 2: Regional DERP Tolerance (`hkg` and `tok`) & 6-Port Serve Audit
On Viettel FTTH (`AS7552`) in Hanoi, `tailscale netcheck` dynamically selects Tokyo (`tok`, `111.7ms`) or Hong Kong (`hkg`, `130.0ms`) depending on submarine cable latency, whereas FPT FTTH (`AS18403`) on `iosteam-mac-mini` selects `hkg`. `setup-macbook-omniroute-client.sh` will accept `relay in ("hkg", "tok")` and verify all 4 L4 TCP ports (`20128`, `20129`, `20132`, `3111`) plus 2 HTTPS ports (`443`, `8443`) on the host node.

### Decision 3: Cross-Node IP Cutover (`100.106.143.78`)
Update `CLIENT_TS_IP="100.106.143.78"` in `setup-macbook-omniroute-client.sh`, `ws://100.106.143.78:6768` in `~/Library/Application Support/orca/orca-environments.json`, `http://100.106.143.78:3111` in AgentMemory `mem:mesh`, and `Host 100.70.16.83 iosteam-mac-mini* 100.106.143.78 100.101.64.56 macbook-pro*` in `~/.ssh/config`.
