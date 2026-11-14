# Evidence: `add-tailscale-media-relay-for-ios-and-peers`

- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Primary Relay Host**: `iosteam-mac-mini` (`100.70.16.83`, Tailnet `tailc6b508.ts.net`)
- **Last Verified**: `2026-11-14T03:35Z`

## 1. Compose Stack & `sing-box` `v1.14.4` Configuration (Tasks 1.1, 1.2)

- Authored `/Users/androidteam/Developer/docker/ts-media-relay/sing-box/config.json`, `/Users/androidteam/Developer/docker/ts-media-relay/docker-compose.yml`, and `/Users/androidteam/Developer/docker/ts-media-relay/.gitignore` alongside existing mode-`0600` `.env` (`TS_AUTHKEY`, untracked).
- `docker run --rm -v /Users/androidteam/Developer/docker/ts-media-relay/sing-box/config.json:/etc/sing-box/config.json:ro ghcr.io/sagernet/sing-box:v1.14.4 check -c /etc/sing-box/config.json` -> exit `0`.
- `docker compose -f /Users/androidteam/Developer/docker/ts-media-relay/docker-compose.yml config -q` -> exit `0`.
- `stat -f '%Lp' /Users/androidteam/Developer/docker/ts-media-relay/.env` -> `600`.
- `/Users/androidteam/Developer/scripts/docker-standardize-check.sh --strict` -> exit `0` (`Validating: /Users/androidteam/Developer/docker/ts-media-relay/docker-compose.yml`, `0` failures, `0` warnings).
- Pulled `tailscale/tailscale:v1.104.7` (`sha256:72c1e19e0aedca96b8533bbb0b4368564410ff20b17e53b804eb6c1f04a31be4`) with temporary `DOCKER_CONFIG/config.json` setting `{"auths":{"https://index.docker.io/v1/":{}},"credsStore":""}` to bypass locked `osxkeychain` (`-25293`).

## 2. Live Relay Stack, Host `utun2` Coexistence & Split DNS (Tasks 2.1, 2.2, 2.3)

- `ts-media-relay` (`100.77.46.87`, node ID `nf6PgwN47M11CNTRL`, `Tags: ["tag:media-relay"]`, `PrimaryRoutes: ["198.18.0.0/16"]`, `Online: true`) and `singbox-media-relay` both report `healthy`.
- `docker exec ts-media-relay test -s /var/lib/tailscale/tailscaled.state` -> exit `0` (`TAILSCALED_STATE_OK`).
- `docker exec ts-media-relay sysctl -n net.ipv4.ip_forward` -> `1`.
- `docker exec ts-media-relay ip route show 198.18.0.0/16` -> `198.18.0.0/16 dev sb0 proto kernel scope link src 198.18.0.1`.
- `iosteam-mac-mini` host `utun2` (`100.70.16.83`, `Health: []`) and 6-port `/usr/local/bin/tailscale serve status --json` (`TCP: ["3111","20128","20129","20132"]`, `Web: ["iosteam-mac-mini.tailc6b508.ts.net:443","iosteam-mac-mini.tailc6b508.ts.net:8443"]`) remain intact.
- `GET /api/v2/tailnet/-/acl` (`HTTP 200`) and `POST /api/v2/tailnet/-/acl/validate` (`HTTP 200 {}`): `tagOwners["tag:media-relay"] = ["autogroup:admin"]`, `autoApprovers.routes["198.18.0.0/16"] = ["tag:media-relay"]`, inbound-only `autogroup:member` grants (`198.18.0.53/32` `udp:53,tcp:53`; `198.18.128.0/17` `tcp:80,tcp:443,udp:443`), zero `src: ["tag:media-relay"]` entries, zero `src: ["*"]` wildcard entries, `tests_count: 2`.
- Mode-`0600` preimage backups mirrored locally under `/Users/androidteam/.local/state/tailscale/preimages/`: `tailscale_acl_preimage_20261114T020610Z.json` (`1100` B, `sha256: cabc18ea9152...`) and `tailscale_split_dns_preimage_20261114T020610Z.json` (`229` B, `sha256: 2b2be0ba87f7...`).
- `GET /api/v2/tailnet/-/dns/split-dns` (`HTTP 200`): 15 domain mappings active — 12 allowlisted Medium/Reddit suffixes (`betterprogramming.pub`, `itnext.io`, `levelup.gitconnected.com`, `medium.com`, `medium.systems`, `netflixtechblog.com`, `redd.it`, `reddit.app.link`, `reddit.com`, `redditmedia.com`, `redditstatic.com`, `towardsdatascience.com` -> `["198.18.0.53"]`) alongside SHB corporate suffixes (`shb.com.vn`, `shbho.shb.vn`, `shb.vn` -> `["10.4.82.20", "10.4.82.21", "10.4.82.23"]`).

## 3. Compose Lifecycle, Provenance Mirror & Wiki/Notion Sync (Tasks 3.1, 3.2)

- Registered `/Users/androidteam/Developer/docker/ts-media-relay` in `COMPOSE_STACKS` inside `/Users/androidteam/Developer/scripts/docker-service.sh` and `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh`.
- `cmp -s` PASS (`sha256: c512fc63c799872da51599b16676256d3613cd1473d6b050b5ec32929d699328`).
- `/Users/androidteam/Developer/scripts/docker-service.sh status --json` reports `{"path":"/Users/androidteam/Developer/docker/ts-media-relay","running_containers":2}`.
- Updated `/Users/androidteam/Developer/wiki/entities/tailscale.md` (`updated: 2026-11-14`) and ran `/Users/androidteam/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh` -> exit `0` (updated Notion page `403c4b21-deb4-814c-8638-d6870676368f`).

## 4. Relay, Security, Split DNS & TLS 1.3 Verification (Task 4.1)

- `dig @198.18.0.53` `A` (`TTL=60`): `medium.com -> 198.18.128.2`, `api.medium.com -> 198.18.128.3`, `www.reddit.com -> 198.18.128.4`, `gql.reddit.com -> 198.18.128.5`, `styles.redditmedia.com -> 198.18.128.6`, `events.redditmedia.com -> 198.18.128.7`.
- `dig @198.18.0.53 medium.com` `AAAA`, `TYPE65` (`HTTPS`), `TYPE64` (`SVCB`), `TXT` -> `NOERROR` (`ANSWER: 0`).
- `dig @198.18.0.53 example.com A` -> `REFUSED`.
- FakeIP mappings (`198.18.128.2`, `198.18.128.6`, `198.18.128.7`) persisted across `docker compose restart singbox-media-relay`.
- `docker compose restart ts-media-relay` preserved node ID `nf6PgwN47M11CNTRL` / `100.77.46.87` (`TS_AUTH_ONCE=true`), triggered `singbox-media-relay` netns self-healing (`RestartCount=1` -> `healthy`), and continued resolving `medium.com -> 198.18.128.2`.
- Security & fallback rejections:
  - `UDP :443` (`198.18.128.2:443`) -> `ECONNREFUSED` (`ICMP Port Unreachable` in `3.35ms`).
  - Raw non-TLS TCP (`198.18.128.2:443`), non-allowlisted SNI (`example.com`), and unmapped FakeIPs (`198.18.0.99:443` timeout, `198.18.128.250:443` `ConnectionRefusedError`) rejected.
  - Outbound tailnet isolation from `ts-media-relay`: `wget --timeout=3 http://100.70.16.83:20128/api/monitoring/health` timed out (`OUTBOUND_DENIED_OK`).
- `/usr/local/bin/tailscale dns query`:
  - `medium.com` -> `198.18.0.53` -> `198.18.128.2` (`TTL 60`)
  - `gql.reddit.com` -> `198.18.0.53` -> `198.18.128.5` (`TTL 60`)
  - `styles.redditmedia.com` -> `198.18.0.53` -> `198.18.128.6` (`TTL 60`)
  - `events.redditmedia.com` -> `198.18.0.53` -> `198.18.128.7` (`TTL 60`)
  - `gitlab-nhs.shb.com.vn` -> `10.4.82.20/21/23` -> `172.16.3.10` (`TTL 18000`)
- Live host system DNS (`dscacheutil`) + `/opt/homebrew/opt/curl/bin/curl -I --http2` (no `--resolve`):
  - `medium.com` (`198.18.128.2`) -> `HEAD /` `HTTP/2 403`, `GET /robots.txt` `HTTP/2 200` (`cf-ray: a5a2bc1cc890107e-HKG`), origin `TLSv1.3` (`X25519MLKEM768`), `ALPN=h2`
  - `api.medium.com` (`198.18.128.3`) -> `HTTP/2 200`, origin `TLSv1.3`, `ALPN=h2`
  - `www.reddit.com` (`198.18.128.4`) -> `HTTP/2 200`, origin `TLSv1.3`, `ALPN=h2`
  - `gql.reddit.com` (`198.18.128.5`) -> `HTTP/2 404`, origin `TLSv1.3`, `ALPN=h2`
  - `styles.redditmedia.com` (`198.18.128.6`) -> `HTTP/2 404`, origin `TLSv1.3` (`X25519MLKEM768`), `ALPN=h2`
  - `events.redditmedia.com` (`198.18.128.7`) -> `HTTP/2 404`, origin `TLSv1.3` (`x25519`), `ALPN=h2`
  - `https://gitlab-nhs.shb.com.vn/users/sign_in` (`--http1.1 --retry 4 --retry-delay 1 --retry-all-errors`) -> `HTTP 200`

## 5. Cross-Machine & iOS Peer Verification (Task 4.2)

- **`macbook-pro-ca-l-1` (`100.106.143.78`, `shb-specs` paired change `add-tailscale-media-relay-for-ios-and-peers`)**:
  - `network_baseline_capture.py --check --json` -> `{"status": "converged", "gaps": [], "media_relay": {"dns_vip": "198.18.0.53", "cidr": "198.18.0.0/16", "peer_route_present": true, "corp_dns_enabled": false, "enabled_media_resolvers": []}}`.
  - `medium_cli.py auth --json` -> `{"authenticated": true, "entitled": true, "isMember": true, "profile": "Default"}`.
  - `route -n get 198.18.0.53` -> `interface: utun7`, `mtu: 1280`.
  - `dig @198.18.0.53 +short medium.com A` -> `198.18.128.2`, `dig @198.18.0.53 +short gql.reddit.com A` -> `198.18.128.5`, `dig @10.4.82.20 +short gitlab-nhs.shb.com.vn A` -> `172.16.3.10`, `tailscale dns status` -> `Tailscale DNS: disabled.` (`CorpDNS: false` preserved).
  - `nhs-foundation/skills/shb-skills`: `411 passed` (`pytest`), `ruff check` / `mypy` / `basedpyright` / `ty check` `0` errors, `shb-skills validate` (`200` skills), `catalog --check`, `scan-secrets`, `sync --direction repo-to-ws`, and `bridge --check` (`healthy=329`) all green.
- **`iphone-15-pro-max` (`100.118.93.42`, `AcceptDNS: true`)**:
  - Operator and coordinator confirmed native iOS **Medium** and **Reddit** apps load feeds, articles, images (`cdn-images-1.medium.com`, `preview.redd.it`, `styles.redditmedia.com`), and comments (`gql-fed.reddit.com`, `gql.reddit.com`) over **both Wi-Fi and 4G/5G cellular** without HTTP/2 `500`/`421` coalescing errors.
  - Relay-side telemetry on `iosteam-mac-mini`: `ts-media-relay` peer stats `rx=1,671,368` B / `tx=22,013,328` B, live `ESTABLISHED` conntrack flow `100.118.93.42:59027 -> 198.18.128.11:443`, `14` distinct Medium/Reddit FQDNs persisted in `/var/lib/sing-box/cache.db` (`198.18.128.2`–`198.18.128.15`), and `0` `singbox-media-relay` errors since `02:33:51Z`.

## 6. Review Remediation & `docker-service.sh drain`/`up` Named-Volume Persistence

- **Compose hardening (`/Users/androidteam/Developer/docker/ts-media-relay/docker-compose.yml`)**:
  - Marked `env_file` as `[{path: .env, required: false}]` (verified via `docker compose config` and `docker-standardize-check.sh --strict` with `.env` absent in temp validation) so `docker compose up -d` / `docker-service.sh up` continue cleanly after initial enrollment (`TS_AUTH_ONCE="true"`).
  - Guarded `singbox-media-relay` PID-1 self-heal with tmpfs marker `/dev/shm/.ts_up` (`test -d /sys/class/net/sb0 && { test -d /sys/class/net/tailscale0 && touch /dev/shm/.ts_up || { test -f /dev/shm/.ts_up && kill -TERM 1; exit 1; }; }`), avoiding premature `SIGTERM` during slow initial `tailscale0` bring-up while resetting cleanly on container restart (verified `/dev/shm` clears on `docker restart` unlike overlayfs `/tmp`).
  - Verified self-healing on `docker restart ts-media-relay`: `singbox-media-relay` `RestartCount` incremented `0 -> 1`, recreated `/dev/shm/.ts_up`, recovered to `healthy`, and served `https://medium.com/robots.txt` (`HTTP 200`).
- **`docker-service.sh` `--status running` & `drain`/`up` persistence (`/Users/androidteam/Developer/scripts/docker-service.sh` & `openspec-store` mirror)**:
  - Updated `status_json` and `cmd_status` to use `docker compose --project-directory "$stack_dir" ps -q --status running` (verified with a `restart: unless-stopped` crash-looping container that `ps -q` reports `1` while `ps -q --status running` reports `0`).
  - `cmp -s` + `shasum -a 256` (`87ce75893a7e92c6f9911621ac702da968d5104200bd8db3568303f952d49043`) identical across `/Users/androidteam/Developer/scripts/docker-service.sh` and `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh`.
  - Executed full `/Users/androidteam/Developer/scripts/docker-service.sh drain` -> `status --json` (`running_containers: 0` across all 3 stacks) -> `/Users/androidteam/Developer/scripts/docker-service.sh up` -> `status --json` (`running_containers: 2` across all 3 stacks; `ts-media-relay`, `singbox-media-relay`, `omniroute`, `shb-schedule-scheduler-1` all `running healthy`):
    - `ts-media-relay-state` preserved node ID `nf6PgwN47M11CNTRL`, `TailscaleIPs: ["100.77.46.87", "fd7a:115c:a1e0::1938:2e58"]`, `Online: true`, `PrimaryRoutes: ["198.18.0.0/16"]`.
    - `singbox-media-cache` preserved FakeIPs `medium.com -> 198.18.128.2`, `styles.redditmedia.com -> 198.18.128.6`, `events.redditmedia.com -> 198.18.128.7`.
    - Live HTTPS probes returned `200` on `https://medium.com/robots.txt`, `https://www.reddit.com/robots.txt`, and `https://gitlab-nhs.shb.com.vn/users/sign_in`.
- **`sing-box` allowlist deduplication (`/Users/androidteam/Developer/docker/ts-media-relay/sing-box/config.json`)**:
  - Deduplicated the 4x repeated 12-domain Medium/Reddit `domain_suffix` allowlist into a single `route.rule_set` (`type: "inline"`, `tag: "media-domains"`, `201 -> 173` lines, `-28` lines) referenced via `rule_set: ["media-domains"]` across `dns.rules` (rules 1 & 2) and `route.rules` (rules 6 & 8); verified `sing-box check` (`0`), recreated `singbox-media-relay` (`running healthy`, `/dev/shm/.ts_up` present, `0` log warnings/errors), `AAAA` & `TYPE65` `NOERROR` (`ANSWER: 0`), `example.com` `REFUSED`, `UDP :443` `ICMP Port Unreachable` (`1.99 ms`), and `TLSv1.3` + `ALPN=h2` across `medium.com` (`198.18.128.2`), `www.reddit.com` (`198.18.128.4`), `styles.redditmedia.com` (`198.18.128.6`), and `events.redditmedia.com` (`198.18.128.7`).
