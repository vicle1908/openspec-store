## 1. Set WS Bridge Secret (official: required in production)

- [x] 1.1 Generate strong secret: `openssl rand -hex 32`
- [x] 1.2 Set `OMNIROUTE_WS_BRIDGE_SECRET=<secret>` in `~/Omniroute/.env` (was commented out)
- [x] 1.3 Verify: `docker exec omniroute printenv OMNIROUTE_WS_BRIDGE_SECRET` returns the stable secret

## 2. Bind Ports to Loopback (official hardened pattern)

- [x] 2.1 Add `ports: !override` with `127.0.0.1:` prefixes for 20128/20129/20132 in `docker-compose.override.yml`
- [x] 2.2 Verify rendered config: `docker compose --profile base config` shows `host_ip: 127.0.0.1` for all three ports
- [x] 2.3 Apply: `cd ~/Omniroute && docker compose --profile base up -d --no-build`

## 3. End-to-End Verification

- [x] 3.1 Wait for healthy (container needs ~2-3 min warm-up for model sync)
- [x] 3.2 Dashboard: `curl http://127.0.0.1:20128/` = 307; login POST = `{"success":true}`
- [x] 3.3 LAN isolation: `curl http://<LAN-IP>:20128/` unreachable (000)
- [x] 3.4 `docker port omniroute` shows 127.0.0.1 bindings only

## 4. Update Documentation

- [x] 4.1 Update `openspec-store/openspec/config.yaml` OmniRoute section: loopback binding + WS secret set
- [x] 4.2 Update memory `omniroute-docker-deployment.md` with the hardening facts

## 5. Archive

- [x] 5.1 `openspec validate harden-omniroute-docker-per-official-guide --type change --strict --store openspec-store`
- [x] 5.2 `openspec archive harden-omniroute-docker-per-official-guide --store openspec-store --yes`
- [x] 5.3 Commit archived change dir + config.yaml only
