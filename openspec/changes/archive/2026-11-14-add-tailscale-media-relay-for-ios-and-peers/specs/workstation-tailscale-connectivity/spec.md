# Spec Delta

## ADDED Requirements

### Requirement: Media relay Split DNS and 198.18.0.0/16 route coexistence across tailnet peers

The tailnet mesh SHALL support Split DNS (`198.18.0.53`) and static `198.18.0.0/16` subnet routing from `tag:media-relay` concurrently with SHB corporate Split DNS (`shb.com.vn`, `shbho.shb.vn`, `shb.vn`), surgical `/32` routes from `macbook-pro-m5` (`100.106.143.78`), and `iosteam-mac-mini` (`100.70.16.83`) host `utun2` and 6-port Tailscale Serve listeners.

#### Scenario: AcceptDNS peers resolve allowlisted media domains and corporate SHB domains without interference
- **WHEN** `iosteam-mac-mini` (`100.70.16.83`, `AcceptDNS: true`, `RouteAll: true`) or an iOS tailnet peer resolves any of the 12 allowlisted Medium or Reddit suffixes and an internal SHB domain (`gitlab-nhs.shb.com.vn`)
- **THEN** MagicDNS (`100.100.100.100`) SHALL forward the 12 allowlisted suffixes to `198.18.0.53` returning a `198.18.128.0/17` FakeIP routed via `tag:media-relay`, while continuing to resolve `shb.com.vn`, `shbho.shb.vn`, and `shb.vn` via `10.4.82.20`, `10.4.82.21`, and `10.4.82.23` routed via `macbook-pro-m5`
- **AND** `iosteam-mac-mini`'s host `utun2` (`100.70.16.83`) and 6-port Tailscale Serve configuration (`:20128`, `:20129`, `:20132`, `:3111` L4 TCP + `:443`, `:8443` HTTPS) SHALL remain unchanged with zero health warnings

#### Scenario: Paired macbook-pro-ca-l-1 CorpDNS-false coexistence respects peer-owned resolver boundary
- **WHEN** `macbook-pro-m5` (`macbook-pro-ca-l-1`, `100.106.143.78`) operates with `CorpDNS: false` (`--accept-dns=false`) and surgical `/etc/resolver/{shb.com.vn,shbho.shb.vn,shb.vn,tailc6b508.ts.net}` files
- **THEN** enabling tailnet `splitDns` for the 12 allowlisted Medium and Reddit suffixes SHALL NOT alter `macbook-pro-ca-l-1` DNS resolution unless opted in via the paired `add-tailscale-media-relay-for-ios-and-peers` change in `macbook-pro-ca-l-1`'s `shb-specs` store
- **AND** `198.18.0.0/16` SHALL have zero CIDR overlap with `macbook-pro-ca-l-1`'s advertised corporate `/32` routes (`10.*` and `172.16.0.0/12`, consolidated to 5 active `/32` routes: `10.4.82.20/32`, `10.4.82.21/32`, `10.4.82.23/32`, `10.4.99.40/32`, `172.16.3.10/32`)
