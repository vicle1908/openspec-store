# Evidence: verify-hermes-webui-iphone-access

**Date:** 2026-08-12
**Verifier:** operator confirmation (victory1908)
**Change:** verify-hermes-webui-iphone-access

---

## 1. iPhone acceptance (user confirmed)

- **Operator confirmed:** iPhone Safari opened `/health` via Tailscale HTTPS, received `{"status":"ok"}`
- **Operator confirmed:** Hermex configured with server URL and password
- **Operator confirmed:** Authenticated test message sent and response received

## 2. Non-disruptive server state

```
HERMES: ok
ADAPTER: ok
LAUNCHD: state = running
TAILSCALE: https://iosteam-mac-mini.tailc6b508.ts.net (tailnet only)
```

## 3. Security

- Server URL: `https://iosteam-mac-mini.tailc6b508.ts.net`
- Password not included in this evidence artifact ✅
