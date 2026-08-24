## 1. Diagnose Port Conflict — ✅ COMPLETED

- [x] 1.1 Confirmed server listening on :20128 but returning 404 for all paths
- [x] 1.2 Traced LiveWS daemon binding `127.0.0.1:20128` before Next.js binds `0.0.0.0:20128`
- [x] 1.3 Identified `.env` `LIVE_WS_PORT=20128` as the conflicting value

## 2. Fix Port Conflict — ✅ COMPLETED

- [x] 2.1 Changed `LIVE_WS_PORT=20128` → `LIVE_WS_PORT=20132` in `~/Omniroute/.env`
- [x] 2.2 Restarted dev server; confirmed LiveWS now on :20132, Next.js on :20128
- [x] 2.3 Verified `/` returns 307 → `/dashboard` → `/login` (200)

## 3. Reset Admin Password — ✅ COMPLETED

- [x] 3.1 Ran `node bin/reset-password.mjs --password-stdin` with password `31122019`
- [x] 3.2 Restarted server to reload bcrypt hash from SQLite (stale hash caused 429)
- [x] 3.3 Verified `POST /api/auth/login` returns `{"success":true}` (HTTP 200)

## 4. Verify API — ✅ COMPLETED

- [x] 4.1 Confirmed `/api/v1/models` returns model catalog (171KB, 200)
- [x] 4.2 Confirmed login page renders full HTML

## 5. Document Deployment State — ✅ COMPLETED

- [x] 5.1 Identified launchd `com.omniroute.server` crash-looping (no production build)
- [x] 5.2 Identified `com.omniroute.updater` running hourly (no new version found)
- [x] 5.3 Noted OpenSpec store `config.yaml` OmniRoute section is stale (says Docker, actual is launchd)
- [ ] 5.4 Archive the OpenSpec change
