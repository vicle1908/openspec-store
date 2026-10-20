# Spec Delta

## MODIFIED Requirements

### Requirement: OmniRoute Muse Code compatibility layer SHALL persist across container recreations without dirtying upstream git

Any OmniRoute compatibility layer required by Meta Muse Code (`/muse-code` catalog path rewrite and full `response.in_progress` keepalive envelope on `/v1/responses`) SHALL be wired through untracked deployment overrides (`docker-compose.override.yml` and host-mounted runtime scripts) rather than ephemeral writable-layer container edits or modifications to git-tracked upstream source files in `~/Omniroute`.

#### Scenario: Compatibility layer survives compose down and up lifecycle
- **WHEN** `~/Developer/scripts/docker-service.sh stop` and `~/Developer/scripts/docker-service.sh start` (or `docker compose --profile base down` followed by `docker compose --profile base up -d`) recreate the `omniroute` container without invoking `~/Omniroute/scripts/update.sh`
- **THEN** `GET http://127.0.0.1:20128/v1/muse-code/models` and `GET http://127.0.0.1:20128/muse-code/models` SHALL both return HTTP 200 with a JSON `data` array containing the `muse-spark-1.3` model entry (even when `0` `muse-code` provider connections exist and `muse-spark-1.3` is served via an OmniRoute combo)
- **AND** `POST http://127.0.0.1:20128/v1/responses` pre-flight keepalive frames SHALL normalize both legacy `id:null` and `v3.8.52+` `id:"resp_keepalive_omniroute"` payloads to `response:{id:"resp_keepalive",object:"response",status:"in_progress",output:[],error:null}` compatible with Muse Code's Rust SSE decoder

#### Scenario: Upstream OmniRoute git worktree remains clean
- **WHEN** `git -C ~/Omniroute status --porcelain --untracked-files=no` is executed
- **THEN** the output SHALL be empty with zero modified tracked files (`open-sse/utils/sseHeartbeat.ts` and `scripts/dev/peer-stamp.mjs` restored to `HEAD`)
- **AND** this compose-mounted runtime override SHALL supersede the legacy transient bundle-patch prohibition for the Muse Code compatibility surface

### Requirement: Container lifecycle helpers SHALL preserve OmniRoute Gate 4b SSE compatibility patches

Workstation container lifecycle scripts (`~/Developer/scripts/docker-service.sh` and `~/Developer/scripts/omniroute-watchdog.sh`) SHALL pass `--profile base` when managing `~/Omniroute` and invoke `~/Omniroute/scripts/ensure-muse-wire-compat.sh` whenever the `omniroute` container is started or recreated so the Gate 4b `muse-wire-compat` SSE keepalive and `/v1/muse-code/models` normalization remains applied.

#### Scenario: Container recreate via docker-service or watchdog preserves Muse wire compatibility
- **WHEN** `docker-service.sh up` or `omniroute-watchdog.sh` starts or recreates the `omniroute` container with `--profile base`
- **THEN** `~/Omniroute/scripts/ensure-muse-wire-compat.sh` SHALL verify that neither `response:{id:null,status:"in_progress"}` nor unexpanded `response:{id:"resp_keepalive_omniroute",status:"in_progress"}` remains in `/app/.build/next/server/chunks/*.js` and that `/v1/muse-code/models` and `/muse-code/models` both return HTTP 200 advertising `muse-spark-1.3`
