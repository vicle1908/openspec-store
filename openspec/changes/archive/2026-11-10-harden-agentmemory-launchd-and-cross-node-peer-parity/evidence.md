# Verification & Operating Evidence Ledger: harden-agentmemory-launchd-and-cross-node-peer-parity

## 1. AgentMemory LaunchAgent Plist Configuration & Engine Daemon Verification

### 1.1 `com.agentmemory.server.plist` Environment & Path Validation (`iosteam-mac-mini`)
```bash
grep -A 2 "<key>PATH</key>" ~/Library/LaunchAgents/com.agentmemory.server.plist
```
Output:
```xml
        <key>PATH</key>
        <string>/Users/androidteam/.agentmemory/bin:/Users/androidteam/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
```
Verification:
- `/usr/sbin:/sbin` is explicitly included in `PATH`, ensuring `/usr/sbin/lsof` is resolved by `readMacProcessExecutable()` in `@agentmemory/agentmemory/dist/cli.mjs` without `ENOENT`.
- `AGENTMEMORY_URL` is omitted from `EnvironmentVariables`, preventing self-directed loopback HTTP recursion.

### 1.2 AgentMemory Local Server Healthcheck Probe
```bash
curl -s -H "Authorization: Bearer $(cat ~/.agentmemory/secret)" http://127.0.0.1:3111/agentmemory/health | jq '{health: {connectionState: .health.connectionState, kvConnectivity: .health.kvConnectivity.status}, metrics: [.functionMetrics[].functionId]}'
```
Output:
```json
{
  "health": {
    "connectionState": "connected",
    "kvConnectivity": "ok"
  },
  "metrics": [
    "mem::compress",
    "mem::summarize"
  ]
}
```

### 1.3 Mesh Patches Parity in `@agentmemory/agentmemory@0.9.33` (`dist/index.mjs`)
- **Fix #1 (`syncStartedAt`)**:
  Line 19919: `const syncStartedAt = (new Date()).toISOString();`
  Line 19977: `if (result.errors.length === 0) peer.lastSyncAt = syncStartedAt;`
- **Fix #2 (`isAllowedUrl` IPv6 bracket stripping)**:
  Line 19778: `const host = parsed.hostname.toLowerCase().replace(/^\[|\]$/g, "");`
- **Fix #3 (`pinGraphState` in `mem::mesh-remove` + `DELETE /agentmemory/mesh/peers/:id`)**:
  Line 20036: `const kv = await pinGraphState(state);` inside `mem::mesh-remove`
  Line 29945: `api_path: "/agentmemory/mesh/peers/:id", http_method: "DELETE"`

## 2. Cross-Node Parity & Mesh Reachability (`macbook-pro-m5` - `100.106.143.78`)

### 2.1 Tailscale Serve L4 TCP Forwarding (Port 3111)
```bash
tailscale serve status --json | jq '.TCP["3111"]'
```
Output:
```json
{
  "TCPForward": "127.0.0.1:3111"
}
```

### 2.2 Bidirectional Tailnet L4 Reachability Probe to `macbook-pro-m5`
```bash
nc -zv -G 3 100.106.143.78 3111
```
Output:
```
Connection to 100.106.143.78 port 3111 [tcp/wsynch] succeeded!
```

### 2.3 Remote Toolchain & Muse Code Invariants on `macbook-pro-m5`
- `muse-code 1.4.14-R7309.1`: Configured with `api_endpoint` pointing to `http://100.70.16.83:20128/v1` in `~/.config/muse/settings.json`.
- File-backed credentials: `~/.config/muse/auth.json` (mode `0600`, `schema_version: 1`, `TBH_CREDENTIAL_BACKEND=file`) bypassing macOS Keychain and eliminating `SecurityAgent` prompts.
- Canonical CLI alignment: `claude 2.1.322`, `ntn 0.23.28`, `pnpm 12.18.0`, `browser-use 1.0.0` GA, and `graphify 0.9.105`.
- Git synchronization on remote repositories committed cleanly:
  - `/Users/vinhlk/Developer/shb/shb-docs`: commit `cb5acaf`
  - `/Users/vinhlk/Developer/shb/shb-specs`: commit `e5ca1f5`

## 3. macOS `securityd` Thread Limit Hygiene & Prober Termination

### 3.1 `securityd` Thread Count Audit
```bash
ps -M -p $(pgrep securityd) | wc -l
```
Output:
```
3
```
Current thread count: 3 worker threads (substantially below the macOS 100-thread ceiling).

### 3.2 Stale Keychain Probers Audit
```bash
pgrep -fl "security find-generic-password|docker-credential-osxkeychain" || echo "None found"
```
Output:
```
None found
```
Zero orphaned background probers running; zero `SecurityAgent` modal dialogs present.

## 4. OpenSpec Archive Readiness & Validation

- `openspec validate harden-agentmemory-launchd-and-cross-node-peer-parity --strict --store openspec-store`: Passed with 0 errors and 0 warnings.
- `python3 scripts/validate-archive-readiness.py --change harden-agentmemory-launchd-and-cross-node-peer-parity --store /Users/androidteam/Developer/platform/openspec-store --strict`: Verified `status: "ready"`, exit code 0.
