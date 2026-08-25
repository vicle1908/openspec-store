## 1. Diagnose

- [x] 1.1 Confirm container unhealthy: `docker inspect omniroute --format '{{json .State.Health}}'` shows FailingStreak + 15s timeouts
- [x] 1.2 Measure endpoint latency: `/`, `/login`, `/api/v1/models`, `/api/monitoring/health`
- [x] 1.3 Identify `PROXY_UNREACHABLE` + credential health timeouts in `docker logs omniroute`
- [x] 1.4 Rule out event loop starvation (fresh node probe: 19ms lag) and DB issues (1ms queries, 14.9MB DB)
- [x] 1.5 Locate misconfiguration: `ENABLE_SOCKS5_PROXY=true` in `.env` with all proxy URLs commented out

## 2. Fix

- [x] 2.1 Set `ENABLE_SOCKS5_PROXY=false` and `NEXT_PUBLIC_ENABLE_SOCKS5_PROXY=false` in `~/Omniroute/.env`
- [x] 2.2 Recreate container: `cd ~/Omniroute && docker compose --profile base up -d --no-build`

## 3. Verify

- [x] 3.1 Container returns to `healthy`
- [x] 3.2 Endpoints fast when warm: `/` <0.1s, `/login` <2s, `/api/monitoring/health` <1s
- [x] 3.3 Login works: POST `/api/auth/login` returns 200
- [x] 3.4 No `PROXY_UNREACHABLE` errors in logs after restart

## 4. Document

- [x] 4.1 Update `openspec-store/openspec/config.yaml` OmniRoute section: proxy must be fully disabled or fully configured
- [x] 4.2 Update memory `omniroute-docker-deployment.md`: proxy half-enable gotcha

## 5. Archive

- [x] 5.1 `openspec validate fix-omniroute-socks5-proxy-hang --type change --strict --store openspec-store`
- [x] 5.2 `openspec archive fix-omniroute-socks5-proxy-hang --store openspec-store --yes`
- [x] 5.3 Commit archived change + config.yaml
