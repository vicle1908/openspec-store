# Proposal

## Why

Following the live end-to-end operational verification across `iosteam-mac-mini` (`100.70.16.83`) and `macbook-pro-m5` (`100.106.143.78`), two critical architectural realities must be reconciled in the central `workstation-tailscale-connectivity` specification and associated ecosystem documentation:

1. **Expansion from 12 to 40 Surgical `/32` Subnet Routes**: `macbook-pro-ca-l-1`'s standalone `tailscaled-on-macOS` subnet router now advertises all 40 approved surgical `/32` CIDRs (3 corporate DNS servers `10.4.82.20/21/23` + 37 internal SHB host endpoints across `10.4.27.*`, `10.4.88.*`, `10.4.97.*`, `10.4.98.*`, `10.4.99.*`, `10.4.198.*`, `10.4.218.*`, `10.204.*`, `10.210.*`, `172.16.*`, `172.25.*`), rather than the earlier 12-route prototype.
2. **HTTP/1.1 ALPN Enforcement & Handshake Reset Absorption Contract**: Corporate gateway infrastructure (F5/WAF reverse proxies for internal SHB services such as `gitlab-nhs.shb.com.vn` and `office.shb.com.vn`) drops HTTP/2 ALPN handshakes (`LibreSSL SSL_connect: SSL_ERROR_SYSCALL`) and exhibits transient TCP connection resets on initial handshakes. End-to-end access requires HTTP/1.1 wire transport (`--http1.1`) and a bounded retry loop (up to 4 retries with 0.5s/1.0s backoff) for read/GET operations.
3. **End-to-End Bidirectional Verification Baseline**: Live cross-node verification proves 100% operational status for MagicDNS/Split DNS, direct IP routing over `utun2`, AgentMemory mesh sync on port `3111`, Orca WebSocket on port `6768`, CMUX relay on port `4399`, and reverse OmniRoute inference and model catalog access (`100.70.16.83:20128`).

## What Changes

- **Update `workstation-tailscale-connectivity` Specification**:
  - Reconcile the subnet route inventory from 12 prototype routes to the 40 approved surgical `/32` CIDRs (`PrimaryRoutes`).
  - Add explicit normative requirements and scenarios for HTTP/1.1 ALPN enforcement and transient handshake reset absorption when connecting to corporate services via subnet routing.
  - Document zero-kernel forwarding (`sysctl net.inet.ip.forwarding == 0`) and userspace gVisor netstack auto-SNAT invariants.
- **Update Wiki Entity `~/Developer/wiki/entities/tailscale.md`**:
  - Update route tables and cross-workstation parity matrix to reflect the 40 `/32` routes and HTTP/1.1 ALPN transport requirements.
- **Consolidate & Enhance Managed Skills**:
  - Update `tailscale-macos-cross-node-optimization` and `tailscale-macos-mesh-and-nat-audit` with the 40-route inventory, ALPN HTTP/1.1 enforcement, bounded handshake retry loop, and cross-node verification recipes.
- **Synchronize Knowledge & Memories**:
  - Persist findings to AgentMemory, Notion Knowledge Hub via `sync-notion-knowledge.sh`, and OMP long-term memory.

## Capabilities

### Modified Capabilities
- `workstation-tailscale-connectivity`: Update surgical `/32` route count to 40 CIDRs, codify HTTP/1.1 ALPN transport requirement, and add bounded handshake retry scenarios for internal SHB services.

## Impact

- **Specs**: `platform/openspec-store/openspec/specs/workstation-tailscale-connectivity/spec.md`
- **Docs & Wiki**: `~/Developer/wiki/entities/tailscale.md`
- **Managed Skills**: `~/.omp/agent/managed-skills/{tailscale-macos-cross-node-optimization,tailscale-macos-mesh-and-nat-audit}/SKILL.md`
- **Knowledge Bases**: AgentMemory, Notion Knowledge Hub
