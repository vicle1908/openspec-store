# Verification Evidence: `harden-docker-helper-and-omniroute-entrypoint-atomicity`

## 1. Docker Desktop `4.99.0` Socket Helper & Plist Verification

- `/Library/LaunchDaemons/com.docker.socket.plist`:
  ```xml
  <key>ProgramArguments</key>
  <array>
    <string>/Library/PrivilegedHelperTools/com.docker.socket</string>
    <string>androidteam</string>
  </array>
  ```
- `/var/run/docker.sock`:
  `lrwxr-xr-x 1 root daemon 42 Nov 10 09:01 /var/run/docker.sock -> /Users/androidteam/.docker/run/docker.sock`
- `~/Developer/scripts/docker-service.sh status`:
  ```text
  Docker Desktop Status:
    Status: running
    Session ID: e4c45b47-43d3-49d6-9b6e-509098aedc12
    Socket: /Users/androidteam/.docker/run/docker.sock (exists=true)
    Context: desktop-linux
    Helpers:
      com.docker.socket: active (symlink verified)
    Registered Stacks:
      /Users/androidteam/Omniroute: 2 running
      /Users/androidteam/Developer/shb/shb-schedule: 2 running
  ```

## 2. OmniRoute Container Recovery & Atomic Entrypoint Verification

- Recreated `omniroute` cleanly via `docker compose --profile base up -d --no-build --pull never --force-recreate omniroute-base`:
  - `omniroute`: `Up (healthy)` (`127.0.0.1:20128-20129->20128-20129/tcp, 127.0.0.1:20132->20132/tcp`)
  - `omniroute-redis`: `Up (healthy)` (`6379/tcp`)
- `/Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh omniroute`:
  `Muse Code wire-compat normalization verified (already_ok)`
- In-container `/app/peer-stamp.mjs`:
  `peer-stamp.mjs bytes: 17166 has_v3_marker: true`
- SHA-256 digests:
  - `~/Omniroute/scripts/container-entrypoint-compat.sh`: `52f93daba07a6e46786e4994a4c3349f7fc36d6bcfd5f1363b83d32ffb3553c4` (`225` lines)
  - `~/Omniroute/scripts/ensure-muse-wire-compat.sh`: `76eea7dc88a635ccd7633115b0d496cb0f9a9916c38673d919aebd83f08c835c` (`47` lines)
- Script provenance parity:
  - `diff -u ~/Developer/scripts/docker-service.sh ~/Developer/platform/openspec-store/scripts/docker-service.sh` -> `0` diff
  - `diff -u ~/Developer/scripts/omniroute-watchdog.sh ~/Developer/platform/openspec-store/scripts/omniroute-watchdog.sh` -> `0` diff

## 3. Automated Test Suite

- `cd ~/Developer/shb/shb-schedule && uv run pytest -p no:cacheprovider tests/test_workstation_update_workflow.py -q`:
  `42 passed`
