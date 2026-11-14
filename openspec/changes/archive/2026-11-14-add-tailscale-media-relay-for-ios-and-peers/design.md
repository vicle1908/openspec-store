# Design

## Context

See `proposal.md` - Why for the FPT Telecom (`AS18403`) DNS sinkhole and TLS ClientHello DPI problem statement, and `specs/tailscale-media-relay/spec.md` for normative behavioral contracts.

This design builds directly on three established workstation patterns on `iosteam-mac-mini` (`100.70.16.83`):
1. **Docker Desktop Lifecycle & Named-Volume Pattern (`docker-lifecycle`)**: Long-lived infrastructure services (`/Users/androidteam/Omniroute`, `/Users/androidteam/Developer/shb/shb-schedule`) run under Docker Desktop (`7.0.14-linuxkit`, `CONFIG_TUN=y` `/dev/net/tun` `10:200`), persist stateful databases on named Docker volumes rather than VirtioFS bind mounts, publish zero non-loopback ports (`~/Developer/scripts/docker-standardize-check.sh`), and register in `COMPOSE_STACKS` inside `~/Developer/scripts/docker-service.sh` (mirrored byte-identically at `platform/openspec-store/scripts/docker-service.sh` per `config/script-provenance-manifest.tsv`).
2. **Host Tailscale Coexistence Pattern (`workstation-tailscale-connectivity`)**: `iosteam-mac-mini` runs Homebrew Cask `tailscale-app` (`io.tailscale.ipn.macsys` Network Extension on `utun2`, `AcceptDNS: true`, `RouteAll: true`) serving 6 listeners (`:20128`, `:20129`, `:20132`, `:3111` L4 TCP + `:443` OmniRoute HTTPS, `:8443` Hermes WebUI HTTPS), while `macbook-pro-m5` (`macbook-pro-ca-l-1`, `100.106.143.78`) runs standalone `tailscaled` (`CorpDNS: false`) advertising 5 consolidated surgical `/32` SHB routes (`10.4.82.20/32`, `10.4.82.21/32`, `10.4.82.23/32`, `10.4.99.40/32`, `172.16.3.10/32`) and corporate Split DNS (`shb.com.vn`, `shbho.shb.vn`, `shb.vn` -> `10.4.82.20`, `10.4.82.21`, `10.4.82.23`).
3. **Cross-Machine OpenSpec Store Governance**: `iosteam-mac-mini` planning lives in `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`), aligned 1:1 with the paired change `add-tailscale-media-relay-for-ios-and-peers` in `macbook-pro-ca-l-1`'s `shb-specs` store.

```text
+-------------------------------------------------------------------------+
| Tailnet Peers (iPhone / iPad AcceptDNS=true, iosteam-mac-mini utun2,    |
| macbook-pro-ca-l-1 opt-in /etc/resolver/*)                              |
+--------------------+-----------------------------------+----------------+
                     | UDP/TCP :53 to 198.18.0.53        | TCP :80/:443, UDP :443
                     | (12 allowlisted suffixes via      | to 198.18.128.0/17
                     |  Tailscale Split DNS)             | (via 198.18.0.0/16 route)
                     v                                   v
+-------------------------------------------------------------------------+
| DockerStack: ~/Developer/docker/ts-media-relay/docker-compose.yml       |
| Shared LinuxKit Container Netns (zero host ports, zero utun2 mutation)  |
|                                                                         |
|  [ts-media-relay: tailscale/tailscale:v1.104.7]                         |
|    tailscale0 (tag:media-relay, TS_USERSPACE=false, ip_forward=1,       |
|                TS_STATE_DIR=/var/lib/tailscale, TS_AUTH_ONCE=true,      |
|                TS_HOSTNAME=ts-media-relay, 127.0.0.1:9002/healthz,      |
|                TS_ROUTES=198.18.0.0/16, --snat-subnet-routes=false,     |
|                --accept-routes=false, TS_ACCEPT_DNS=false)              |
|         |                                                               |
|         | kernel route: 198.18.0.0/16 dev sb0 (non-RTN_LOCAL)           |
|         v                                                               |
|  [singbox-media-relay: ghcr.io/sagernet/sing-box:v1.14.4]               |
|    network_mode: "service:ts-media-relay" (self-heal on netns loss)     |
|    sb0 TUN: 198.18.0.1/16, stack="gvisor", mtu=1280                     |
|      |-- 198.18.0.53:53  -> hijack-dns -> dns-fakeip (198.18.128.0/17)  |
|      |-- UDP :443        -> pre-sniff reject (no_drop=true -> ICMP)     |
|      +-- TCP :80/:443    -> sniff(tls,http 300ms) + protocol=[tls,http] |
|                          -> resolve via dns-doh (1.1.1.1 ipv4_only)     |
|                          -> anti-rebinding private/CGNAT/198.18 reject  |
|                          -> direct-out (tls_record_fragment=true)       |
+------------------------------------+------------------------------------+
                                     | E2E TLS 1.3 (2 outer 0x16 records)
                                     | ALPN=h2 over Docker NAT -> FPT FTTH
                                     v
                    [Upstream Medium & Reddit CDN Origins]
```

## Goals / Non-Goals

**Goals:**
- Isolate subnet-route advertisement (`198.18.0.0/16`) and packet processing inside a dedicated 2-container LinuxKit network namespace with zero host port bindings and zero changes to `iosteam-mac-mini`'s `tailscale-app` daemon.
- Guarantee deterministic 1:1 FQDN-to-FakeIP mapping across `32,766` IPv4 addresses (`198.18.128.0/17`) persisted on a named volume so HTTP/2 clients never coalesce distinct CDN origins onto one TCP connection.
- Achieve `<2ms` QUIC-to-HTTP/2 fallback on iOS/macOS and ~71ms E2E TLS 1.3 (`ALPN=h2`) handshakes across FPT `AS18403` DPI without MITM certificates.
- Enforce least-privilege network and transactional control-plane boundaries across Tailscale ACLs, Split DNS, Docker Compose lifecycle scripts, and paired workstation stores.

**Non-Goals:**
- Routing arbitrary internet traffic, IPv6 FakeIP pools (`fc00::/7`), or non-HTTP/HTTPS ports through `tag:media-relay`.
- Modifying `macbook-pro-ca-l-1` host files (`/etc/resolver/*` or `shb-medium-member`) from `iosteam-mac-mini` (governed by the paired `shb-specs` change).

## Decisions

### Decision 1: Shared-Netns Two-Container Stack (`ts-media-relay` + `singbox-media-relay`) with Kernel `/dev/net/tun`
- **Choice**: Deploy `tailscale/tailscale:v1.104.7` (matching `tailscale/tailscale:stable` digest `sha256:72c1e19e0aedca96b8533bbb0b4368564410ff20b17e53b804eb6c1f04a31be4`, since `v1.104.6` is unpublished on Docker Hub; with `env_file: [{path: .env, required: false}]`, `TS_USERSPACE=false`, `TS_STATE_DIR=/var/lib/tailscale`, `TS_AUTH_ONCE=true`, `TS_HOSTNAME=ts-media-relay`, `TS_ENABLE_HEALTH_CHECK=true`, `TS_LOCAL_ADDR_PORT=127.0.0.1:9002`, `sysctls: ["net.ipv4.ip_forward=1"]`, `cap_add: ["NET_ADMIN", "NET_RAW"]`, `devices: ["/dev/net/tun:/dev/net/tun"]`, `TS_ROUTES=198.18.0.0/16`, `TS_ACCEPT_DNS=false`, `TS_EXTRA_ARGS=--advertise-tags=tag:media-relay --snat-subnet-routes=false --accept-routes=false`, healthcheck `["CMD", "wget", "--spider", "-q", "http://127.0.0.1:9002/healthz"]`) alongside `ghcr.io/sagernet/sing-box:v1.14.4` (`network_mode: "service:ts-media-relay"`, `depends_on: {ts-media-relay: {condition: service_healthy}}`, `cap_add: ["NET_ADMIN"]`, `devices: ["/dev/net/tun:/dev/net/tun"]`, healthcheck `["CMD-SHELL", "test -d /sys/class/net/sb0 && { test -d /sys/class/net/tailscale0 && touch /dev/shm/.ts_up || { test -f /dev/shm/.ts_up && kill -TERM 1; exit 1; }; }"]`) at `~/Developer/docker/ts-media-relay/docker-compose.yml` with `restart: unless-stopped` and zero `ports:`. Setting `TS_STATE_DIR`, `TS_AUTH_ONCE=true`, `env_file` `required: false`, `TS_HOSTNAME`, and `net.ipv4.ip_forward=1` prevents `containerboot` (`tailscaled.go:63-74`, `settings.go:118`) from defaulting to `--state=mem:`, re-running `tailscale up --authkey` after 90-day key expiry, or failing `docker compose up` if `.env` is removed post-enrollment; guarding `kill -TERM 1` with `/dev/shm/.ts_up` (tmpfs cleared on container restart, unlike overlayfs `/tmp`) prevents premature self-termination during slow initial `tailscale0` bring-up while still re-attaching `singbox-media-relay` via `restart: unless-stopped` whenever `tailscale0` disappears from an established namespace. Unattended pulls on `iosteam-mac-mini` pass an empty temporary `DOCKER_CONFIG` directory when macOS `osxkeychain` (`~/.docker/config.json`) is locked (`-25293`).
- **Rationale**: Sharing `ts-media-relay`'s LinuxKit network namespace lets kernel packets arriving on `tailscale0` for `198.18.0.0/16` route directly into `sing-box`'s `sb0` interface (`198.18.0.1/16`) while egress `direct-out` sockets leave via Docker `eth0` NAT with zero routing loops (`auto_route: false`). Confining `tailscale0` and `sb0` to a container avoids mutating macOS routing tables or `iosteam-mac-mini`'s `utun2`. Setting `--accept-routes=false` and `--snat-subnet-routes=false` prevents `ts-media-relay` from importing SHB `/32` routes and preserves client tailnet source IPs inside `sb0` logs/diagnostics.
- **Alternatives Considered**:
  - *Tailscale classic App Connectors*: Rejected because dynamically learned CDN `/32` routes trigger macOS bug `tailscale#21733`, dropping `utun` IPs for ~126ms and stalling MagicDNS (`100.100.100.100`) for ~1s per new CDN IP.
  - *Host-level `sing-box` LaunchDaemon on macOS*: Rejected because creating a second host `utun` interface risks route-priority conflicts with `io.tailscale.ipn.macsys` (`RouteAll: true`) and violates workstation containerization boundaries.
  - *Userspace Tailscale (`TS_USERSPACE=true`) inside container*: Rejected because userspace netstack terminates TCP locally rather than forwarding routed `198.18.0.0/16` packets into the sibling container's `sb0` kernel TUN device.

### Decision 2: Deterministic RFC 2544 `198.18.0.0/16` Subnet Layout and Persisted `/17` FakeIP Pool
- **Choice**: Partition `198.18.0.0/16` into:
  - `198.18.0.1/16`: `sing-box` `tun-in` interface `sb0` (`stack: "gvisor"`, `mtu: 1280`, `auto_route: false`, `strict_route: false`).
  - `198.18.0.53`: Dedicated Split DNS virtual IP (not assigned as a local interface address, so Linux treats it as non-`RTN_LOCAL` and forwards `198.18.0.53:53` over `198.18.0.0/16 dev sb0` into `tun-in` `hijack-dns`).
  - `198.18.128.0/17`: `dns-fakeip` `inet4_range` (`32,766` host addresses `.128.2`-`.255.254`), persisted in named volume `singbox-media-cache:/var/lib/sing-box` (`experimental.cache_file`: `enabled: true`, `path: "/var/lib/sing-box/cache.db"`, `store_fakeip: true`, `store_dns: true`).
- **Rationale**: Routing `198.18.0.53` into `sb0` completely avoids UDP/TCP `:53` socket bind collisions with Docker's embedded resolver (`127.0.0.11:53`) and `tailscaled` (`100.100.100.100:53`). Setting `mtu: 1280` matches Tailscale WireGuard's `1280`-byte MTU, eliminating inner IPv4 fragmentation. Allocating a unique FakeIP per FQDN prevents iOS `URLSession` HTTP/2 connection coalescing across Fastly (`styles.redditmedia.com`) and AWS (`events.redditmedia.com`), which both present wildcard `*.redditmedia.com` certificates; coalescing `events.redditmedia.com` onto Fastly Varnish returns HTTP/2 `500` (not `421 Misdirected Request`), permanently breaking Reddit iOS telemetry/feed loading under single-IP SNI proxies. `198.18.0.0/16` also has zero overlap with LAN (`192.168.0.0/16`), Tailscale CGNAT (`100.64.0.0/10`), Docker bridges, or SHB `/32` routes (`10.*`, `172.16.0.0/12`).
- **Alternatives Considered**:
  - *Single-IP SNI splicing proxy*: Rejected due to permanent HTTP/2 wildcard coalescing `500` failures on `*.redditmedia.com`.
  - *Smaller `198.18.0.0/24` (`253`-IP) FakeIP pool*: Rejected because long-lived iOS/macOS sessions across dynamic `*.medium.com` and `*.redditmedia.com` subdomains benefit from a `32,766`-IP `/17` pool without LRU eviction churn.

### Decision 3: `sing-box` `v1.14.4` Closed Split DNS and 9-Stage Zero-MITM Route Pipeline
- **Choice**: Configure `~/Developer/docker/ts-media-relay/sing-box/config.json` using typed `v1.14.4` schemas (never combining deprecated `dns.rules[].strategy` with `query_type`):
  - **12 Allowlisted Domain Suffixes (`route.rule_set`)**: Declared once in `route.rule_set` (`{"type": "inline", "tag": "media-domains", "rules": [{"domain_suffix": ["medium.com", "medium.systems", "towardsdatascience.com", "netflixtechblog.com", "itnext.io", "betterprogramming.pub", "levelup.gitconnected.com", "reddit.com", "redd.it", "redditmedia.com", "redditstatic.com", "reddit.app.link"]}]}`) and referenced via `"rule_set": ["media-domains"]` across `dns.rules` (rules 1 & 2) and `route.rules` (rules 6 & 8) so `sing-box` compiles a single shared `domain.Matcher` trie (`mergeableRule`) without 4-way duplication.
  - **DNS Servers**: `dns-doh` (`type: "https"`, `server: "1.1.1.1"`, `server_port: 443`, `path: "/dns-query"`) and `dns-fakeip` (`type: "fakeip"`, `inet4_range: "198.18.128.0/17"`).
  - **DNS Rules (`inbound: ["tun-in"]`)**:
    1. `rule_set: ["media-domains"]` + `query_type: ["A"]` -> `{"action": "route", "server": "dns-fakeip", "rewrite_ttl": 60}`.
    2. `rule_set: ["media-domains"]` (all remaining non-`A` QTYPEs: `AAAA`, `HTTPS`, `SVCB`, `SOA`, `TXT`, `NS`) -> `{"action": "predefined", "rcode": "NOERROR"}` (`NODATA`, avoiding `sing-box` `fakeip.go` `SERVFAIL` on non-A/AAAA queries, preventing `REFUSED` on `SOA`/`TXT` probes, and blocking IPv6/ECH bypass).
    3. Any remaining `inbound: ["tun-in"]` query -> `{"action": "predefined", "rcode": "REFUSED"}`.
  - **Route Rules (`tun-in`)**:
    1. `ip_cidr: ["198.18.0.53/32"]`, `port: 53` -> `{"action": "hijack-dns"}`.
    2. `network: ["udp"]`, `port: 443` (placed strictly **before** `sniff`) -> `{"action": "reject", "method": "default", "no_drop": true}` so `gVisor` returns immediate `ICMP Port Unreachable` (`<2ms` iOS QUIC-to-HTTP/2 fallback).
    3. Non-TCP or port not in `[80, 443]` -> `{"action": "reject"}`.
    4. `ip_cidr: ["198.18.0.0/16"]` -> `{"action": "reject"}` (`IPCIDRItem.Match` checks `Destination.IsIP()` prior to `resolve`; allocated FakeIPs were already rewritten to `Destination.Fqdn` by `prepareMatchMetadata` and pass through, whereas unmapped `198.18.x.y` probes are rejected immediately without upstream DoH lookups).
    5. `{"action": "sniff", "sniffer": ["tls", "http"], "timeout": "300ms"}`.
    6. `protocol: ["tls", "http"]` + `rule_set: ["media-domains"]` -> `{"action": "resolve", "server": "dns-doh", "strategy": "ipv4_only"}`.
    7. `ip_is_private: true` or `ip_cidr: ["100.64.0.0/10", "198.18.0.0/15"]` -> `{"action": "reject"}` (DNS-rebinding and sinkhole defense if upstream ever returned `127.0.0.1`, RFC1918, CGNAT, or benchmark IPs).
    8. `protocol: ["tls", "http"]` + `rule_set: ["media-domains"]` -> `{"action": "route", "outbound": "direct-out", "tls_record_fragment": true}` (splits outer `0x16` TLS ClientHello into 2 records, defeating FPT `AS18403` stateless DPI TCP RST while keeping end-to-end TLS 1.3 + `ALPN=h2` intact).
    9. Default fallback -> `{"action": "reject"}`.
- **Rationale**: Every stage fails closed. Rule 4 rejects unmapped `198.18.0.0/16` IPs before `sniff`/`resolve`, and requiring `protocol: ["tls", "http"]` on rules 6 and 8 prevents raw/idle TCP connections to an already-allocated FakeIP from bypassing `sniff` via `sing-box` `v1.14.4`'s `DomainItem.Match` fallback to `Destination.Fqdn` (`rule_item_domain.go:60-69`, while `override_destination` is deprecated in `rule_action` `sniff`); non-allowlisted SNIs populate `metadata.Domain` and are rejected by rule 9. Placing `udp:443` `reject` (`no_drop: true`) before `sniff` avoids waiting 300ms+ on QUIC packets and prevents silent drops that stall iOS apps for seconds. Resolving upstream origins via Cloudflare DoH (`1.1.1.1`) bypasses local router DNS sinkholing (`192.168.10.1` -> `127.0.0.1`), while `tls_record_fragment: true` bypasses FPT DPI without terminating TLS.
- **Alternatives Considered**:
  - *Silent drop on `udp:443` (or blocking `udp:443` in Tailscale ACLs)*: Rejected because silent WireGuard drops force iOS `NWProtocolQUIC` to wait for retransmission timeouts before falling back to TCP `:443`, whereas permitting `udp:443` to reach `sb0` `no_drop: true` delivers immediate `ICMP Port Unreachable` over the tunnel.
  - *MITM forward/reverse TLS proxy*: Rejected because custom root CAs weaken endpoint security and fail certificate-pinned mobile clients.

### Decision 4: Inbound-Only Tailscale Policy, Provenance-Tracked Lifecycle, and Transaction Boundaries
- **Choice**:
  - **Tailscale Policy**: Declare `"tag:media-relay": ["autogroup:admin"]` in `tagOwners`, `"198.18.0.0/16": ["tag:media-relay"]` in `autoApprovers.routes`, narrow the existing default wildcard grant from `"src": ["*"], "dst": ["*"]` to `"src": ["autogroup:member"]` scoped to `"autogroup:member"` and approved corporate routes (`10.0.0.0/8`, `172.16.0.0/12`, or `ipset:shb-*` if `optimize-tailscale-control-plane-and-link-sync` was applied first), and add inbound-only `grants` from `autogroup:member` to `198.18.0.53/32` (`udp:53`, `tcp:53`) and `198.18.128.0/17` (`tcp:80`, `tcp:443`, `udp:443`), with **zero** `src: ["tag:media-relay"]` entries. Add `splitDns` mappings for all 12 suffixes -> `["198.18.0.53"]` alongside existing `shb.com.vn`, `shbho.shb.vn`, `shb.vn` -> `["10.4.82.20", "10.4.82.21", "10.4.82.23"]`.
  - **Compose Lifecycle & Standardization**: Append `"/Users/androidteam/Developer/docker/ts-media-relay"` to `COMPOSE_STACKS` in `~/Developer/scripts/docker-service.sh`, filter `status` / `status --json` container counts with `docker compose --project-directory "$stack_dir" ps -q --status running`, and copy byte-for-byte to `platform/openspec-store/scripts/docker-service.sh` (`config/script-provenance-manifest.tsv`). Naming the file `~/Developer/docker/ts-media-relay/docker-compose.yml` matches `docker-standardize-check.sh` directly under `STACK_ROOTS` (`~/Developer`, `maxdepth 3`) with zero edits to `docker-standardize-check.sh`.
  - **Transaction Boundaries**:
    1. *Tailscale Control-Plane Transaction*: Pre-mutation `GET /api/v2/tailnet/-/acl` (`Accept: application/hujson`, capturing `ETag`) and `GET /api/v2/tailnet/-/dns/split-dns` written as non-pruned mode-`0600` `tailscale_acl_preimage_*.json` and `tailscale_split_dns_preimage_*.json` backups -> `POST /api/v2/tailnet/-/acl/validate` (including positive member-to-relay and negative `tag:media-relay`-to-tailnet/SHB `"tests"`, requiring HTTP `200` with an empty `{}` JSON body) -> atomic `POST /api/v2/tailnet/-/acl` (`Content-Type: application/hujson`) with `If-Match: <ETag>` -> `PATCH /api/v2/tailnet/-/dns/split-dns` merging the 12 keys without clobbering `shb*` keys (Tailscale's `/dns/split-dns` OpenAPI v2 endpoint has no `ETag` header; full-map rollback uses `PUT /api/v2/tailnet/-/dns/split-dns` with the saved preimage JSON).
    2. *Container State Transaction*: `ts-media-relay-state` (`/var/lib/tailscale/tailscaled.state`) and `singbox-media-cache` (`/var/lib/sing-box/cache.db`) reside on independent Linux ext4 Docker named volumes, isolating `bbolt` page commits from macOS VirtioFS corruption and ensuring `docker-service.sh drain` (`docker compose down --timeout 65`) flushes state cleanly before VM stop.
    3. *Cross-Repository & Cross-Machine Governance Boundary*: `openspec-store` (`iosteam-mac-mini`), `~/Developer` host files (`iosteam-mac-mini`), and `shb-specs` (`macbook-pro-ca-l-1`) have independent Git histories and apply lifecycles; central planning in `openspec-store` never auto-mutates external roots or `macbook-pro-ca-l-1` `/etc/resolver/*`.
- **Alternatives Considered**:
  - *Editing Tailscale ACLs manually in Admin UI without ETag or `acl/validate` tests*: Rejected due to risk of accidentally dropping `derpMap`, `randomize-client-port`, or SHB `splitDns` entries.

## Risks / Trade-offs

- **[Risk] Custom Medium publication domains not in the 12-suffix allowlist will not traverse the relay** -> Mitigation: Curate the top 5 engineering publications (`towardsdatascience.com`, `netflixtechblog.com`, `itnext.io`, `betterprogramming.pub`, `levelup.gitconnected.com`) alongside `medium.com` / `medium.systems`; adding a suffix later requires only updating the single `media-domains` `route.rule_set` entry in `sing-box/config.json` and Tailscale `splitDns` without changing the `198.18.0.0/16` route or ACL grants.
- **[Risk] `no_drop: true` on `udp:443` was silent if Tailscale ACLs dropped `udp:443` at the WireGuard peer layer** -> Mitigation: Explicitly include `udp:443` in the `autogroup:member` -> `198.18.128.0/17` grant so QUIC Initial packets reach `sb0` and trigger immediate `<2ms` `ICMP Port Unreachable` rejection.
- **[Risk] Drift between executed `~/Developer/scripts/docker-service.sh` and `openspec-store/scripts/docker-service.sh` flags daily maintenance degradation** -> Mitigation: Require atomic `cp` + `shasum -a 256` equality verification against `config/script-provenance-manifest.tsv` in the apply tasks.
- **[Risk] `macbook-pro-ca-l-1` runs `CorpDNS: false`, so `100.100.100.100` returns `SERVFAIL` for Split DNS domains** -> Mitigation: Document and preserve this exact boundary; `macbook-pro-ca-l-1` consumes the relay only when opted in via its paired `shb-specs` change writing `nameserver 198.18.0.53` (routed over standalone `tailscaled` `utun`) into `/etc/resolver/<domain>` plus leak-free `medium_cli.py` sinkhole/FakeIP fallback.

## Migration Plan

1. **Stage Compose & `sing-box` Config Locally**: Create `~/Developer/docker/ts-media-relay/{docker-compose.yml,sing-box/config.json}` and mode-`0600` `.env` (`TS_AUTHKEY`, `.gitignore`-protected); validate config syntax offline via `docker run --rm -v .../config.json:/etc/sing-box/config.json:ro ghcr.io/sagernet/sing-box:v1.14.4 check -c /etc/sing-box/config.json` and `docker compose config -q`.
2. **Apply Tailscale ACL & Route Auto-Approver Policy (Pre-Split-DNS)**: Snapshot current ACLs + Split DNS (`0600`), validate new `tagOwners`, `autoApprovers.routes`, inbound-only `grants`, and declarative `"tests"` via `/api/v2/tailnet/-/acl/validate`, and apply with `If-Match`.
3. **Bring Up Stack & Verify Direct Relay Before Enabling Tailnet Split DNS**: Start `ts-media-relay` + `singbox-media-relay`, confirm `tag:media-relay` advertises `198.18.0.0/16` (approved), and smoke-test `dig @198.18.0.53 medium.com A`, `AAAA`/`HTTPS` `NODATA`, non-allowlisted `REFUSED`, `<2ms` UDP `:443` rejection, and `curl --resolve` E2E TLS 1.3 `ALPN=h2` against Medium and Reddit origins.
4. **Enable Tailnet `splitDns` & Register Lifecycle**: Patch `splitDns` to map the 12 suffixes to `["198.18.0.53"]` while verifying SHB `shb.com.vn` / `shbho.shb.vn` / `shb.vn` resolution and `iosteam-mac-mini` 6-port Tailscale Serve remain healthy; register `/Users/androidteam/Developer/docker/ts-media-relay` in `docker-service.sh` + `openspec-store` mirror.
5. **Rollback Strategy**: Restore `tailscale_split_dns_preimage_*.json` via `PUT /api/v2/tailnet/-/dns/split-dns` (or `PATCH` setting the 12 media keys to `null` -- never `PATCH` with the preimage alone, which only merges keys), immediately returning all peers to direct DNS resolution with zero downtime; then run `docker compose -f ~/Developer/docker/ts-media-relay/docker-compose.yml down` and `POST /api/v2/tailnet/-/acl` (`If-Match`) with `tailscale_acl_preimage_*.json` if full decommission is desired.
