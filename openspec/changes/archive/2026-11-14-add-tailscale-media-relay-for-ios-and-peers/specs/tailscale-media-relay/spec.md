# Spec Delta

## Purpose

Provides an isolated containerized Tailscale (`tag:media-relay`) and `sing-box` (`v1.14.4`) Split-DNS and per-FQDN FakeIP (`198.18.0.0/16`) relay on `iosteam-mac-mini` that restores end-to-end TLS 1.3 (`ALPN=h2`) access to 12 allowlisted Medium and Reddit domain suffixes for iOS and tailnet peers without MITM certificates or host `utun` route churn.

## ADDED Requirements

### Requirement: Isolated two-container media relay stack and namespace isolation

The media relay SHALL run on `iosteam-mac-mini` at `~/Developer/docker/ts-media-relay/docker-compose.yml` as a two-container stack (`ts-media-relay` on `tailscale/tailscale:v1.104.7` with persisted state, single-auth enrollment, and IPv4 forwarding, plus `singbox-media-relay` on `ghcr.io/sagernet/sing-box:v1.14.4` via `network_mode: "service:ts-media-relay"` and `depends_on` `service_healthy`), using named volumes, healthchecks, `restart: unless-stopped`, and zero published host ports.

#### Scenario: Containerized kernel TUN isolation avoids host utun route churn
- **WHEN** `ts-media-relay` starts or restarts with `TS_USERSPACE=false`, `TS_STATE_DIR=/var/lib/tailscale`, `TS_AUTH_ONCE=true`, `TS_HOSTNAME=ts-media-relay`, `TS_ENABLE_HEALTH_CHECK=true`, `TS_LOCAL_ADDR_PORT=127.0.0.1:9002`, `sysctls: ["net.ipv4.ip_forward=1"]`, `cap_add: ["NET_ADMIN", "NET_RAW"]`, `devices: ["/dev/net/tun:/dev/net/tun"]`, `TS_ROUTES=198.18.0.0/16`, `TS_ACCEPT_DNS=false`, and `TS_EXTRA_ARGS=--advertise-tags=tag:media-relay --snat-subnet-routes=false --accept-routes=false`
- **THEN** WireGuard and `sb0` TUN interfaces SHALL remain confined inside the LinuxKit container network namespace without injecting dynamic CDN `/32` routes or triggering `setTunnelNetworkSettings` resets on `iosteam-mac-mini`'s host `utun2`
- **AND** named volumes `ts-media-relay-state:/var/lib/tailscale` (`TS_STATE_DIR=/var/lib/tailscale`, `TS_AUTH_ONCE=true`) and `singbox-media-cache:/var/lib/sing-box` (`experimental.cache_file` enabled at `/var/lib/sing-box/cache.db` with `store_fakeip: true` and `store_dns: true`) SHALL persist node state and FakeIP mappings across container restarts without re-consuming `TS_AUTHKEY`

#### Scenario: Shared network namespace self-healing and unattended image pulls
- **WHEN** `ts-media-relay` restarts or is recreated into a new network namespace, or images are pulled from an unattended session where macOS `osxkeychain` is locked (`-25293`)
- **THEN** `singbox-media-relay` SHALL gate startup on `ts-media-relay`'s `http://127.0.0.1:9002/healthz` (`service_healthy`) and run a sysfs healthcheck (`test -d /sys/class/net/sb0 && { test -d /sys/class/net/tailscale0 && touch /dev/shm/.ts_up || { test -f /dev/shm/.ts_up && kill -TERM 1; exit 1; }; }`) that waits cleanly during slow initial `tailscale0` bring-up and terminates PID 1 only when `tailscale0` disappears after having been active so `restart: unless-stopped` re-attaches `singbox-media-relay` to the new namespace automatically
- **AND** unattended `docker compose pull` / `up -d` invocations SHALL support an unauthenticated temporary `DOCKER_CONFIG` directory so public Docker Hub pulls do not fail on locked Keychain credentials

#### Scenario: Zero host port bindings preserve workstation listeners and standardize checks
- **WHEN** `~/Developer/docker/ts-media-relay/docker-compose.yml` is scanned by `~/Developer/scripts/docker-standardize-check.sh --strict`
- **THEN** `docker-standardize-check.sh` SHALL match `docker-compose.yml` directly and verify that neither `ts-media-relay` nor `singbox-media-relay` publishes host `ports:` bindings or host SQLite bind mounts
- **AND** existing `iosteam-mac-mini` listeners (`100.70.16.83:443` OmniRoute, `:8443` Hermes WebUI, `:3111` AgentMemory, `:20128`, `:20129`, `:20132`) SHALL remain completely unaffected

#### Scenario: Untracked mode-0600 auth key enrollment
- **WHEN** `ts-media-relay` authenticates to the tailnet using `TS_AUTHKEY` (a non-ephemeral `tag:media-relay` auth key or OAuth client secret with `?ephemeral=false`)
- **THEN** `TS_AUTHKEY` SHALL be read exclusively from an untracked mode-`0600` `~/Developer/docker/ts-media-relay/.env` file (`env_file` `required: false` after initial enrollment) that is excluded from version control

### Requirement: Deterministic RFC 2544 subnet addressing and per-FQDN FakeIP allocation

The media relay SHALL partition `198.18.0.0/16` deterministically into `198.18.0.1/16` for `sing-box` TUN `sb0` (`stack: "gvisor"`, `mtu: 1280`, `auto_route: false`, `strict_route: false`), `198.18.0.53` as the dedicated Split DNS virtual IP, and `198.18.128.0/17` (`32,766` addresses) as the `fakeip` `inet4_range`.

#### Scenario: Split DNS virtual IP avoids container port 53 socket conflicts and WireGuard fragmentation
- **WHEN** a tailnet peer sends UDP or TCP port `53` DNS queries to `198.18.0.53`
- **THEN** container routing (`198.18.0.0/16 dev sb0`, non-`RTN_LOCAL`) SHALL forward the packets into `tun-in` `hijack-dns` without binding `:53` sockets that conflict with Docker DNS (`127.0.0.11:53`) or Tailscale MagicDNS (`100.100.100.100:53`)
- **AND** `sb0` (`mtu: 1280`) SHALL match WireGuard's `1280`-byte MTU so encapsulated TCP segments avoid inner IP fragmentation

#### Scenario: Per-FQDN FakeIPv4 addresses eliminate HTTP/2 connection coalescing errors
- **WHEN** an iOS or tailnet peer resolves `styles.redditmedia.com` (Fastly) and `events.redditmedia.com` (AWS), or multiple `*.medium.com` subdomains, through `198.18.0.53`
- **THEN** `dns-fakeip` SHALL return distinct IPv4 addresses within `198.18.128.0/17` (`198.18.128.2`–`198.18.255.254`) with `rewrite_ttl: 60`
- **AND** client HTTP/2 stacks (`URLSession`) SHALL establish separate origin TLS sessions per FQDN without wildcard certificate coalescing `500` or `421` errors

### Requirement: Closed allowlist Split DNS resolution for Medium and Reddit suffixes

The `tun-in` DNS pipeline SHALL answer only the 12 allowlisted suffixes (`medium.com`, `medium.systems`, `towardsdatascience.com`, `netflixtechblog.com`, `itnext.io`, `betterprogramming.pub`, `levelup.gitconnected.com`, `reddit.com`, `redd.it`, `redditmedia.com`, `redditstatic.com`, `reddit.app.link`) and SHALL NOT combine deprecated `dns.rules[].strategy` with `query_type`.

#### Scenario: Allowlisted A queries allocate persisted FakeIPs
- **WHEN** a DNS query on `tun-in` (`198.18.0.53:53`) matches one of the 12 allowlisted suffixes with `query_type: ["A"]`
- **THEN** `sing-box` SHALL route the query to `dns-fakeip` (`198.18.128.0/17`) with `rewrite_ttl: 60` and return `RCODE=NOERROR`

#### Scenario: Allowlisted non-A queries return NODATA
- **WHEN** a DNS query on `tun-in` matches one of the 12 allowlisted suffixes with any non-`A` query type (`AAAA`, `HTTPS`, `SVCB`, `SOA`, `TXT`, `NS`)
- **THEN** `sing-box` SHALL evaluate the `A -> dns-fakeip` rule first and match the catch-all allowlisted rule returning a predefined `RCODE=NOERROR` empty response (`NODATA`) so iOS `mDNSResponder` neither stalls on `SERVFAIL`/`REFUSED` nor bypasses IPv4 FakeIP routing via IPv6 or SVCB/ECH hints

#### Scenario: Non-allowlisted domains are refused by closed Split DNS
- **WHEN** a DNS query on `tun-in` does not match any of the 12 allowlisted suffixes
- **THEN** `sing-box` SHALL return a predefined `RCODE=REFUSED` response without allocating a FakeIP or querying upstream resolvers

### Requirement: End-to-end TLS 1.3 forwarding with DPI record fragmentation, fast QUIC rejection, and anti-rebinding guards

In `route.rules`, `sing-box` SHALL hijack `198.18.0.53/32:53`, reject UDP `:443` (`no_drop: true`) before `sniff`, reject non-TCP/non-`[80, 443]` and unmapped `198.18.0.0/16` destinations before `resolve`, sniff TLS/HTTP (`300ms`), gate allowlisted `resolve` (DoH `1.1.1.1`, `ipv4_only`) and `direct-out` (`tls_record_fragment: true`) on `protocol: ["tls", "http"]`, and reject private/CGNAT/benchmark IPs.

#### Scenario: Fragmented ClientHello restores end-to-end TLS 1.3 and HTTP/2 over FPT AS18403
- **WHEN** a tailnet peer opens a TCP `:443` connection to an allocated FakeIP in `198.18.128.0/17` carrying an allowlisted TLS SNI (or TCP `:80` with an allowlisted HTTP `Host`)
- **THEN** `sing-box` SHALL match `protocol` in `["tls", "http"]`, resolve the origin IPv4 via `dns-doh` (`type: "https"`, `server: "1.1.1.1"`, `server_port: 443`, `path: "/dns-query"`, `strategy: "ipv4_only"`), and forward via `direct-out` with `tls_record_fragment: true`
- **AND** the client SHALL complete an authentic end-to-end TLS 1.3 (`ALPN=h2`) handshake against the upstream origin without FPT DPI TCP `RST` injection or custom CA trust

#### Scenario: Pre-sniff UDP 443 rejection triggers sub-2ms QUIC fallback to HTTP/2
- **WHEN** an iOS or macOS client sends UDP `:443` QUIC packets to `198.18.128.0/17`
- **THEN** a route rule evaluated before `sniff` (`network: ["udp"]`, `port: 443`, `action: "reject"`, `method: "default"`, `no_drop: true`) SHALL emit an immediate `ICMP Port Unreachable` packet so the client falls back to TCP `:443` HTTP/2 without waiting on QUIC timeouts

#### Scenario: Non-allowlisted SNI, raw TCP payloads, disallowed ports, and private/special destination IPs are rejected
- **WHEN** a connection to `198.18.0.0/16` targets an unallocated FakeIP, uses a non-TCP protocol (other than `198.18.0.53:53` or fast-rejected `udp:443`), targets a TCP port outside `[80, 443]`, fails `sniff` (`protocol` not in `["tls", "http"]`, blocking raw/idle TCP streams), presents a non-allowlisted TLS SNI or HTTP `Host`, or resolves to `ip_is_private: true` or `ip_cidr` in `["100.64.0.0/10", "198.18.0.0/15"]`
- **THEN** `sing-box` SHALL reject the flow and open zero outbound upstream sockets

### Requirement: Inbound-only Tailscale ACL grants and transactional Split DNS governance

Tailnet policy SHALL set `tagOwners["tag:media-relay"] = ["autogroup:admin"]` and `autoApprovers.routes["198.18.0.0/16"] = ["tag:media-relay"]`, narrow wildcard `src: ["*"]` grants to `src: ["autogroup:member"]` on peer/corporate destinations, grant `autogroup:member` inbound-only access to `198.18.0.53/32` (`53`) and `198.18.128.0/17` (`80`, `443`) with zero `src: ["tag:media-relay"]` rules, and map the 12 suffixes in `splitDns`.

#### Scenario: Declarative ACL validation enforces inbound-only access and denies relay lateral movement
- **WHEN** the tailnet policy is validated via `POST /api/v2/tailnet/-/acl/validate` with declarative `"tests"`
- **THEN** `autogroup:member` SHALL be allowed to reach `198.18.0.53:53` (`udp`, `tcp`) and `198.18.128.0/17` (`tcp:80`, `tcp:443`, `udp:443` so QUIC triggers immediate `sb0` ICMP rejection instead of silent WireGuard drop)
- **AND** default wildcard `src: ["*"]` grants SHALL be replaced by `src: ["autogroup:member"]` with zero `src: ["tag:media-relay"]` rules (`POST /api/v2/tailnet/-/acl/validate` returning HTTP `200` and empty `{}` JSON body), verifying that `tag:media-relay` is denied outbound connections to tailnet nodes (`100.70.16.83`, `100.106.143.78`) and SHB corporate `/32` routes

#### Scenario: Mode-0600 preimage backup and ETag concurrency protect policy and Split DNS updates
- **WHEN** tailnet ACLs or `splitDns` settings are updated via the Tailscale Admin API
- **THEN** the workflow SHALL capture non-pruned mode-`0600` `tailscale_acl_preimage_*.json` and `tailscale_split_dns_preimage_*.json` backups before mutation, validate ACL changes via `POST /api/v2/tailnet/-/acl/validate`, submit policy updates to `POST /api/v2/tailnet/-/acl` (`application/hujson`) with `If-Match` ETag concurrency control, merge Split DNS via `PATCH /api/v2/tailnet/-/dns/split-dns` (using `PUT /api/v2/tailnet/-/dns/split-dns` with the saved preimage JSON for full-map rollback), and preserve SHB corporate Split DNS (`shb.com.vn`, `shbho.shb.vn`, `shb.vn` -> `["10.4.82.20", "10.4.82.21", "10.4.82.23"]`)
