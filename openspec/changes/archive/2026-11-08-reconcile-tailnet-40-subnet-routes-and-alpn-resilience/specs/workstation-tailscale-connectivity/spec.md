# workstation-tailscale-connectivity Delta Specification

## MODIFIED Requirements

### Requirement: Zero-configuration Tailscale Split DNS and surgical /32 subnet routing from macbook-pro-m5

The workstation mesh SHALL allow `iosteam-mac-mini` (`100.70.16.83`, `AcceptDNS: true`, `RouteAll: true`) and authorized mobile/desktop peers to resolve internal SHB domains (`shb.com.vn`, `shbho.shb.vn`, `shb.vn` via `10.4.82.20`, `10.4.82.21`, `10.4.82.23`) and reach approved internal `/32` SHB endpoints advertised by `macbook-pro-m5` (`macbook-pro-ca-l-1`, `100.106.143.78`) over userspace `gVisor netstack` without local `/etc/hosts` or static route overrides on peer nodes.

#### Scenario: Zero-configuration internal host DNS resolution and HTTPS reachability from iosteam-mac-mini
- **WHEN** `macbook-pro-m5` (`100.106.143.78`) has an active corporate Ethernet attachment (`en7`/`en8`) and advertises all 40 approved surgical `/32` routes (3 DNS resolvers `10.4.82.20/32`, `10.4.82.21/32`, `10.4.82.23/32` and 37 internal SHB host endpoints)
- **THEN** `tailscale dns query gitlab-nhs.shb.com.vn A` on `iosteam-mac-mini` SHALL return `172.16.3.10` via internal resolvers `10.4.82.20`, `10.4.82.21`, and `10.4.82.23`
- **AND** `route -n get 172.16.3.10` on `iosteam-mac-mini` SHALL route via the Tailscale `utun` interface
- **AND** `sysctl net.inet.ip.forwarding` on `macbook-pro-m5` SHALL remain `0`

#### Scenario: HTTP/1.1 ALPN enforcement and transient handshake reset absorption
- **WHEN** `iosteam-mac-mini` sends HTTPS requests to corporate internal endpoints (`gitlab-nhs.shb.com.vn`, `office.shb.com.vn`) through the subnet router
- **THEN** client connections SHALL offer ALPN `http/1.1` and avoid defaulting to `h2` to prevent TLS handshake termination by upstream perimeter reverse proxies
- **AND** client tooling SHALL absorb transient initial TCP connection resets on read-only requests using a bounded retry loop of up to 4 retries with deterministic backoff (0.5s, 1.0s, 1.0s, 1.0s) yielding an eventual HTTP `200` or `302` response
