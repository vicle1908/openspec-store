# Spec Delta

## MODIFIED Requirements

### Requirement: Continuous supervisor watchdog monitoring

A periodic system supervisor (`com.omniroute.watchdog`) SHALL monitor the health of the Docker daemon and local gateway stacks, serialize its entire cycle via a non-blocking `/usr/bin/lockf` kernel lock on `~/.omniroute/update.lock` at Step 0, omit decommissioned sidecar endpoints, and run a bounded 6-hour read-only SQLite `PRAGMA integrity_check` (`~/.omniroute/integrity-last-ok`) without restarting a healthy gateway on integrity failure.

#### Scenario: Unhealthy or halted container auto-recovery
- **WHEN** `omniroute` container is halted or fails HTTP health probes outside the startup grace period
- **THEN** `omniroute-watchdog.sh` SHALL evaluate container status: if the container is running but unhealthy, it SHALL execute `docker compose restart omniroute-base`
- **AND** if the container is halted or not running, it SHALL execute `docker compose up -d` in the respective stack directory to restore service availability.

#### Scenario: Container startup grace period observed
- **WHEN** `omniroute` is in the `starting` health status during initial boot
- **THEN** the supervisor SHALL NOT trigger redundant restarts, allowing the container to complete internal model route initialization.

#### Scenario: Down daemon recovery attempt
- **WHEN** Docker daemon is unreachable during supervisor execution
- **THEN** the supervisor SHALL invoke `docker-service.sh start` before attempting container checks.

#### Scenario: Supervisor probes primary gateway without sidecars
- **WHEN** `omniroute-watchdog.sh` executes its periodic health probe cycle
- **THEN** it SHALL evaluate Docker daemon socket availability and OmniRoute `/healthz` on port 20128
- **AND** it SHALL NOT probe port 8788 or trigger restarts for `claude-code-provider-adapter`.

#### Scenario: Active update or maintenance lock suppresses watchdog restarts
- **WHEN** `omniroute-watchdog.sh` starts at Step 0 (before Docker daemon or container checks), opens persistent `~/.omniroute/update.lock` (`umask 077`) on file descriptor `9` (`exec 9>>"$LOCK_FILE"`), and invokes `/usr/bin/lockf -s -t 0 9`
- **THEN** if `/usr/bin/lockf` returns exit code `75` (`EX_TEMPFAIL` because `update.sh`, manual `/usr/bin/lockf -k -t 0 ~/.omniroute/update.lock` maintenance, or another watchdog instance holds the kernel lock), `omniroute-watchdog.sh` SHALL log that the maintenance lock is active and exit `0` without starting the daemon, restarting `omniroute`, or running `docker compose up -d`
- **AND** if `/usr/bin/lockf` fails with any other non-zero exit code, `omniroute-watchdog.sh` SHALL log an error and fail closed with a non-zero exit code
- **AND** when the kernel lock is acquired (`rc = 0`), `omniroute-watchdog.sh` SHALL retain open FD `9` across its entire cycle until process exit (closing `9>&-` on child invocations), SHALL ignore file contents/mtime without parsing PID/epoch metadata or expiring live locks by age, SHALL NEVER unlink `~/.omniroute/update.lock`, and SHALL remain byte-identical to `/Users/androidteam/Developer/platform/openspec-store/scripts/omniroute-watchdog.sh` per `config/script-provenance-manifest.tsv`.

#### Scenario: Periodic read-only SQLite integrity check runs every 6 hours without restarting a healthy gateway
- **WHEN** `omniroute` is `running`, `State.Health.Status != starting`, and `http://127.0.0.1:20128/healthz` returns HTTP 200 under the Step 0 FD `9` kernel lock, and `~/.omniroute/integrity-last-ok` is missing or its mtime is `>= 21600` seconds (6 hours) old
- **THEN** `omniroute-watchdog.sh` SHALL execute a read-only full `PRAGMA integrity_check` (`better-sqlite3` `{readonly:true, fileMustExist:true, timeout:15000}`, no `autoRepair`) bounded by an in-container child timeout of `110s` (`SIGKILL`) and outer `gtimeout --signal=TERM --kill-after=5s 120s`
- **AND** it SHALL update `~/.omniroute/integrity-last-ok` only when all returned rows equal `'ok'`, and on any integrity failure or timeout it SHALL log `ERROR` and exit non-zero without restarting the otherwise healthy `omniroute` container.
