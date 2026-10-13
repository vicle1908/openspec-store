# Evidence: harden-omniroute-watchdog-deadlock-recovery

## 1. Container & Daemon State Verification

### Container Health Status
```bash
$ docker ps --filter "name=omniroute"
CONTAINER ID   IMAGE                           COMMAND                  CREATED         STATUS                   PORTS                                                                NAMES
77d0068b38fc   diegosouzapw/omniroute:latest   "/app/check-permissi…"   4 minutes ago   Up 2 minutes (healthy)   127.0.0.1:20128-20129->20128-20129/tcp, 127.0.0.1:20132->20132/tcp   omniroute
2f2734fd4c12   redis:7-alpine                  "docker-entrypoint.s…"   4 minutes ago   Up 2 minutes (healthy)   6379/tcp                                                             omniroute-redis
```

### Healthz HTTP Probe
```bash
$ curl -I http://127.0.0.1:20128/healthz
HTTP/1.1 200 OK
Connection: close
content-length: 3
content-type: text/plain; charset=utf-8
Date: Tue, 13 Oct 2026 23:32:04 GMT
```

### API Port Responsiveness
```bash
$ curl -s http://127.0.0.1:20129/v1/models
{"error":{"message":"Authentication required","type":"invalid_api_key","code":"invalid_api_key"}}
```

## 2. Watchdog Self-Healing Script Execution

```bash
$ ~/Developer/scripts/omniroute-watchdog.sh
# Exit code: 0
# No errors or warnings logged in ~/.omniroute/watchdog.log
```

## 3. Workstation VM Resource Recovery

- Lingering builder prune PID 53696 terminated.
- 31 idle containers from `microservices-platform-e2e` stopped.
- Docker Desktop cleanly restarted without LinuxKit zombie processes.
- Memory usage stabilized; SQLite 3.58 GB storage hydration completes without disk sleep lockups.
