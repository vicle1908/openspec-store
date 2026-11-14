# Proposal

## Why

FPT Telecom (`AS18403`) DNS sinkholing (`*.medium.com` -> `127.0.0.1`/`::1`) and active TCP RST injection on single-record TLS ClientHello packets break Medium and Reddit connectivity on iOS and tailnet peers, while naive single-IP SNI proxies or Tailscale classic App Connectors either trigger permanent HTTP/2 connection-coalescing `500` errors across Fastly/AWS `*.redditmedia.com` origins or stall macOS `utun` interfaces via runtime `/32` route churn (`tailscale#21733`).

Provisioning an isolated, zero-MITM containerized Tailscale + `sing-box` media relay on `iosteam-mac-mini` (`100.70.16.83`) with a static RFC 2544 `198.18.0.0/16` subnet, deterministic Split DNS (`198.18.0.53`), per-FQDN FakeIP allocation (`198.18.128.0/17`), Cloudflare DoH (`1.1.1.1`), and 2-record TLS ClientHello fragmentation restores full E2E TLS 1.3 + `ALPN=h2` access for iOS and tailnet peers across 12 curated Medium and Reddit domain suffixes without touching host `utun2`, Tailscale Serve listeners, or SHB corporate Split DNS.

## What Changes

- **Add Containerized Tailscale + `sing-box` Media Relay Stack (`tailscale-media-relay`)**:
  - Provision a 2-container Docker Compose stack at `~/Developer/docker/ts-media-relay/docker-compose.yml` and `~/Developer/docker/ts-media-relay/sing-box/config.json` (`tailscale/tailscale:v1.104.7` with `TS_USERSPACE=false`, `TS_STATE_DIR=/var/lib/tailscale`, `TS_AUTH_ONCE=true`, `TS_HOSTNAME=ts-media-relay`, `TS_ENABLE_HEALTH_CHECK=true` on `127.0.0.1:9002/healthz`, `cap_add: ["NET_ADMIN", "NET_RAW"]`, `sysctls: ["net.ipv4.ip_forward=1"]`, and mode-`0600` untracked `.env` `TS_AUTHKEY`, paired with `ghcr.io/sagernet/sing-box:v1.14.4` via `network_mode: "service:ts-media-relay"`, `depends_on: service_healthy`, and shared-netns self-healing healthcheck) with named volumes and zero host `ports:`.
  - Partition RFC 2544 `198.18.0.0/16` into `198.18.0.1/16` (`sb0` gVisor TUN, `mtu: 1280`), `198.18.0.53` (closed Split DNS VIP), and `198.18.128.0/17` (`32,766` persisted per-FQDN FakeIPv4 addresses), enforcing the 12-suffix Medium/Reddit allowlist (`A -> dns-fakeip` `rewrite_ttl: 60`, non-`A` `NODATA`, fallback `REFUSED`), pre-sniff UDP `:443` `ICMP Port Unreachable` (`no_drop: true`), `protocol: ["tls", "http"]` gating on allowlist `resolve` (Cloudflare DoH `1.1.1.1`) and `direct-out` (`tls_record_fragment: true`), and anti-rebinding rejection (see `specs/tailscale-media-relay/spec.md`).
- **Govern Tailscale ACLs, Inbound-Only Grants, and Split DNS Coexistence (`tailscale-media-relay`, `workstation-tailscale-connectivity`)**:
  - Register `tagOwners["tag:media-relay"] = ["autogroup:admin"]`, `autoApprovers.routes["198.18.0.0/16"] = ["tag:media-relay"]`, narrow default wildcard `src: ["*"]` grants to `src: ["autogroup:member"]` on peer/corporate destinations so `tag:media-relay` inherits zero outbound rights, and add inbound-only `autogroup:member` grants to `198.18.0.53/32` (`udp:53`, `tcp:53`) and `198.18.128.0/17` (`tcp:80`, `tcp:443`, `udp:443`) with zero `src: ["tag:media-relay"]` rules via `POST /api/v2/tailnet/-/acl/validate` (requiring HTTP `200` with empty `{}` body) and `POST /api/v2/tailnet/-/acl` (`If-Match` ETag).
  - Map the 12 allowlisted suffixes in `splitDns` (`PATCH /api/v2/tailnet/-/dns/split-dns` merge; mode-`0600` `tailscale_{acl,split_dns}_preimage_*.json` backups with `PUT /api/v2/tailnet/-/dns/split-dns` full-map rollback) while preserving SHB corporate Split DNS (`shb.com.vn`, `shbho.shb.vn`, `shb.vn`), `iosteam-mac-mini` `utun2` / 6-port Serve, and paired `macbook-pro-ca-l-1` (`CorpDNS: false`) `shb-specs` governance.
- **Register Media Relay Compose Lifecycle (`docker-lifecycle`)**:
  - Update `COMPOSE_STACKS` in `~/Developer/scripts/docker-service.sh` (mirrored byte-identically at `platform/openspec-store/scripts/docker-service.sh` per `config/script-provenance-manifest.tsv`), while verifying `~/Developer/docker/ts-media-relay/docker-compose.yml` read-only via `~/Developer/scripts/docker-standardize-check.sh --strict`.

### Non-Goals

- Full-tunnel exit-node routing (`0.0.0.0/0`, `::/0`) or proxying non-allowlisted domains through `iosteam-mac-mini`.
- TLS interception, MITM certificate generation, or custom root CA installation on iOS, macOS, or tailnet peers.
- Using Tailscale classic App Connectors (which inject dynamic CDN `/32` routes into macOS `utun` and trigger `tailscale#21733` tunnel resets) or modifying `iosteam-mac-mini`'s host `tailscale-app` Cask daemon.
- Enabling outbound tailnet initiation (`src: ["tag:media-relay"]`) from the relay container to any tailnet device or SHB corporate `/32` endpoint.
- Mutating `macbook-pro-ca-l-1`-local `/etc/resolver/*` files or `shb-medium-member` (`medium_cli.py`) from `iosteam-mac-mini` (owned by the paired `add-tailscale-media-relay-for-ios-and-peers` change in `macbook-pro-ca-l-1`'s `shb-specs` store).

## Capabilities

### New Capabilities
- `tailscale-media-relay`: Containerized Tailscale (`tag:media-relay`) and `sing-box` (`v1.14.4`) Split-DNS + FakeIP (`198.18.0.0/16`) E2E TLS 1.3 media relay for curated Medium and Reddit domains, including allowlist DNS/SNI/anti-rebinding enforcement and Tailscale policy governance.

### Modified Capabilities
- `workstation-tailscale-connectivity`: Tailnet Split DNS and static `198.18.0.0/16` subnet-route coexistence with SHB corporate Split DNS (`shb.com.vn`, `shbho.shb.vn`, `shb.vn`), surgical `/32` routes, host `utun2`, 6-port Tailscale Serve, and paired `macbook-pro-ca-l-1` (`CorpDNS: false`) client behavior.
- `docker-lifecycle`: Registration of `/Users/androidteam/Developer/docker/ts-media-relay` in `COMPOSE_STACKS` within `docker-service.sh` (and its provenance-tracked mirror in `openspec-store`) for automated drain, restart, and status checks.

## Impact

- **OpenSpec Specifications (`openspec-store`)**: New `openspec/specs/tailscale-media-relay/spec.md`; delta updates to `openspec/specs/workstation-tailscale-connectivity/spec.md` and `openspec/specs/docker-lifecycle/spec.md`.
- **Host Docker Stack & Lifecycle (`iosteam-mac-mini`)**: `~/Developer/docker/ts-media-relay/docker-compose.yml`, `~/Developer/docker/ts-media-relay/sing-box/config.json`, untracked `~/Developer/docker/ts-media-relay/.env` (`0600`), and `~/Developer/scripts/docker-service.sh` (plus `openspec-store` mirror).
- **Tailscale Control Plane (`tailc6b508.ts.net`)**: Tailnet HuJSON policy (`POST /api/v2/tailnet/-/acl` with `If-Match` ETag after `/acl/validate`) and `splitDns` mapping (`PATCH` merge, `PUT` preimage rollback).
- **Documentation & Wiki (`iosteam-mac-mini`)**: `~/Developer/wiki/entities/tailscale.md` and Notion Knowledge Hub sync (`sync-notion-knowledge.sh`) during apply.

### Ownership Boundaries

- **Central Planning Store (`iosteam-mac-mini` `openspec-store`, `/Users/androidteam/Developer/platform/openspec-store`)**: Owns `iosteam-mac-mini` specifications, planning artifacts, and the recorded script mirror `scripts/docker-service.sh`. `actionContext.allowedEditRoots` covers `openspec-store` only; external host/API apply actions require explicit apply authorization and separate git commits per repository.
- **External Host Runtime Root (`iosteam-mac-mini` `/Users/androidteam/Developer`)**: Owns `~/Developer/docker/ts-media-relay/` and the executed `~/Developer/scripts/docker-service.sh`.
- **External Control Plane (`tailc6b508.ts.net` Admin API)**: Owns tailnet ACLs, route auto-approvers, grants, and Split DNS mappings shared across all tailnet peers (`iosteam-mac-mini`, iOS devices, and `macbook-pro-ca-l-1`).
- **Paired Peer Store (`macbook-pro-ca-l-1` `shb-specs`)**: Owns the sibling change `add-tailscale-media-relay-for-ios-and-peers` governing `macbook-pro-ca-l-1` (`100.106.143.78`, `CorpDNS: false`) opt-in `/etc/resolver/*` management and `shb-medium-member` (`medium_cli.py`) sinkhole/FakeIP fallback.
