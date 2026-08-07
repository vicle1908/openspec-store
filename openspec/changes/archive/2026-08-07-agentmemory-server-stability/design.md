# Design: agentmemory Server Stability

## Architecture

```
launchd (macOS)
  |
  +-- com.agentmemory.server.plist
  |     StartAtLoad, KeepAlive (restart on crash)
  |     /opt/homebrew/bin/node .../cli.mjs
  |     -> agentmemory (PID)
  |       -> iii engine (child, port 3111/3112/49134)
  |         -> REST API routes registered via WebSocket
  |
  +-- com.agentmemory.watchdog.plist
        StartInterval=300 (every 5 min)
        -> agentmemory-healthcheck.sh
          -> curl /agentmemory/health
          -> if empty/unhealthy: kill + restart
```

## Root Cause Analysis

The agentmemory server communicates with the iii engine via WebSocket (port 49134).
The iii engine exposes HTTP on port 3111, but routes are only registered when
workers connect via WebSocket. When the WebSocket connection degrades (OTel errors,
1650+ reconnect attempts), the HTTP routes become unregistered — port 3111 is
listening but returns 404 or empty for all paths.

The previous setup had no auto-restart mechanism. A single WebSocket failure
required manual intervention.

## Fix Strategy

1. **Immediate:** Kill broken processes, start fresh with clean WebSocket connections
2. **Persistent:** launchd with KeepAlive ensures auto-restart on crash
3. **Resilient:** Watchdog catches silent WebSocket degradation that doesn't crash the process
4. **Observable:** Health check script with logging for debugging

## Trade-offs

- Watchdog kills the server during active operations — acceptable for a memory
  service where data persistence survives restart (iii state stored on disk)
- launchd `SuccessfulExit=false` restarts on ALL non-zero exits, including
  intentional shutdown — `launchctl unload` is the correct way to stop
