# Design

## Context

On `macbook-pro-m5` (`100.106.143.78`, `macbook-pro-ca-l-1`), the workstation runs standalone `tailscaled-on-macOS` (`1.104.5-t73a48057a`) under `/Library/LaunchDaemons/sh.brew.tailscale.plist` as an authorized Tailscale Subnet Router. By utilizing gVisor netstack in userspace (`UserspaceRouter: true`, `cmd/tailscaled/tailscaled.go:812-835`), the host forwards TCP/UDP traffic to corporate services over its `10.8.8.0/24` Ethernet link (`en7`/`en8`) with zero kernel IP forwarding (`sysctl net.inet.ip.forwarding == 0`), ensuring public Wi-Fi (`en0`) cannot bridge into the corporate perimeter.

During live operational testing from `iosteam-mac-mini` (`100.70.16.83`), all 40 advertised surgical `/32` routes attached cleanly to Darwin routing table `utun2`. Tailscale Split DNS correctly resolved corporate hostnames to their respective `/32` internal IPs. However, TLS probes uncovered that internal SHB reverse proxies and WAF gateways (such as for `gitlab-nhs.shb.com.vn` and `office.shb.com.vn`) do not support HTTP/2 ALPN negotiation and drop TLS handshakes with `SSL_ERROR_SYSCALL` when HTTP/2 is offered, as well as intermittently resetting initial TCP handshakes. Enforcing HTTP/1.1 (`--http1.1` in `curl` or HTTP/1.1 client profiles in CLI tools) alongside a bounded 5-attempt retry loop resolves all connection resets with `HTTP 200 OK`.

## Goals / Non-Goals

**Goals:**
- Formally codify the 40 approved surgical `/32` routes in `workstation-tailscale-connectivity`.
- Define normative requirements for HTTP/1.1 wire transport and transient handshake retry absorption for corporate endpoints accessed over Tailscale subnet routes.
- Update documentation in the wiki, AgentMemory, Notion, and managed skills to provide deterministic verification recipes.

**Non-Goals:**
- Modifying corporate gateway WAF/reverse proxy infrastructure at the banking perimeter.
- Advertising broad CIDRs (e.g. `/8` or `/16`), preserving `/32` surgical isolation.
- Altering kernel `ip.forwarding`, preserving zero-trust userspace auto-SNAT.

## Technical Details

### 1. Route Table Alignment
The 40 approved `/32` CIDRs consist of:
- 3 Corporate DNS servers: `10.4.82.20/32`, `10.4.82.21/32`, `10.4.82.23/32`
- 37 Internal SHB services: `10.4.27.30/32`, `10.4.27.54/32`, `10.4.27.76/32`, `10.4.27.79/32`, `10.4.82.11/32`, `10.4.82.12/32`, `10.4.82.13/32`, `10.4.82.14/32`, `10.4.82.15/32`, `10.4.88.24/32`, `10.4.88.29/32`, `10.4.88.33/32`, `10.4.88.130/32`, `10.4.88.142/32`, `10.4.88.180/32`, `10.4.88.200/32`, `10.4.97.45/32`, `10.4.97.54/32`, `10.4.97.68/32`, `10.4.97.69/32`, `10.4.97.72/32`, `10.4.97.80/32`, `10.4.97.160/32`, `10.4.97.225/32`, `10.4.98.118/32`, `10.4.98.189/32`, `10.4.98.201/32`, `10.4.99.37/32`, `10.4.99.40/32`, `10.4.198.200/32`, `10.4.218.60/32`, `10.204.40.215/32`, `10.204.42.233/32`, `10.210.4.14/32`, `172.16.3.10/32`, `172.16.3.11/32`, `172.25.4.4/32`.

### 2. HTTP/1.1 ALPN & Handshake Retry Invariant
- **ALPN**: Clients connecting to internal corporate hosts via the subnet router MUST offer `http/1.1` and avoid defaulting to `h2` unless specifically verified.
- **Handshake Retry Policy**: Read-only operations (`GET`, `HEAD`) MUST absorb transient TCP resets on initial handshakes using up to 4 retries (5 total attempts) with deterministic backoff (0.5s, 1.0s, 1.0s, 1.0s; max added sleep 3.5s).
