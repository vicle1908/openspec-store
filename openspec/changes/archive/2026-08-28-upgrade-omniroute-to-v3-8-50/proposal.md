# Upgrade OmniRoute to v3.8.50

## Problem Statement

The deployed OmniRoute runtime is v3.8.49 (image RepoDigest
`sha256:92c768c56e2de32c51a0621ef182835018b00b288c9bb235c5c5e4514658c1a1`)
while upstream released v3.8.50 on 2026-08-26. Docker Hub `latest` and `3.8.50`
tags both resolve to index digest
`sha256:085c57adf499a8aaa9f35ccde95c0df9c11bd9ecd18d6c9edbf3b68b8079ba9d`
(published 2026-08-27T04:23Z). The update-tracking LaunchAgent
(`com.omniroute.update-check`) flagged the new version on 2026-08-27 22:05 and
wrote `~/.omniroute/update-available`.

Two latent defects surface alongside the upgrade:

1. `~/Omniroute/scripts/update.sh` can report success after failure — it warns
   and proceeds when the DB snapshot fails, when the container never becomes
   healthy, and when endpoint checks fail; it never verifies the pulled digest
   equals the flagged target; it clears the flag and sends a success
   notification unconditionally.
2. The canonical `bifrost-gateway` spec has drifted from the deployment
   standardized on 2026-08-24: it still describes bind-mount persistence
   (`~/Omniroute/data` → `/app/data`) and upstream healthcheck timing
   (5s timeout, 15s start period), while the real deployment uses the named
   volume `omniroute-data` and relaxed override timing (15s timeout, 120s
   start period).

## Why

v3.8.50 is a patch release over v3.8.49: 12 commits, dominated by dependency
and security bumps (nanoid, dompurify, Dependabot + audit cleanup) plus four
runtime fixes directly relevant to this deployment:

- Hide health-check-excluded models from `/v1/models` (#10026)
- Memoize `getModelsDevPricing` — event-loop / `/healthz` relief (#10055)
- Honor shared passthrough providers (#11075)
- Route Ollama models by advertised capability (#11088)

No breaking changes are documented; DB migrations run inside the app at
startup and the release cycle already shipped the migration-collision fixes.
Of the 64 keys set in the deployment `.env`, 59 are present in the v3.8.50
`.env.example`; the remaining 5 (`GEMINI_CLI_OAUTH_CLIENT_ID`, `GEMINI_CLI_OAUTH_CLIENT_SECRET`, `GEMINI_CLI_USER_AGENT`, `QWEN_OAUTH_CLIENT_ID`, `QWEN_USER_AGENT`) are absent from BOTH the v3.8.49
and v3.8.50 examples — pre-existing custom/legacy variables, not v3.8.50
removals. The 4 vars removed upstream between the two examples are absent
from the deployment `.env`. All 15 deployment-critical keys (ports, Redis,
secrets, SOCKS5, LiveWS, quota store) were explicitly verified present. The
upgrade path is the established on-demand Docker flow from the
`standardize-omniroute-docker-deployment` and
`optimize-omniroute-update-tracking` changes: pull the Hub image, recreate
the container, verify.

The updater hardening is required before this upgrade runs through
`update.sh`: a false success would clear the update flag and mask a failed or
partial upgrade — exactly the failure mode the update-tracking change was
built to prevent.

## What Changes

- **Upgrade the OmniRoute runtime from v3.8.49 to v3.8.50** via the Docker Hub
  image, service-targeted so the Redis container is never touched:
  `docker compose --profile base pull omniroute-base` then
  `docker compose --profile base up -d --no-build --pull never --no-deps
  --force-recreate omniroute-base` from `~/Omniroute`, preserving every
  deployment invariant: loopback-only ports 20128/20129/20132, named volume
  `omniroute-data` → `/app/data`, Redis unpublished on the compose network,
  secrets in untracked `.env`, SOCKS5 proxy disabled.
- **Harden `~/Omniroute/scripts/update.sh` to fail closed**: pre-pull snapshot
  + `integrity_check` gate, pulled-digest-equals-flagged-target gate,
  healthy-within-timeout gate, in-image package-version gate, running-container
  image-id gate, endpoint gates (`/healthz`, dashboard, monitoring health,
  `/v1/models`), and post-deploy DB integrity + persistence-indicator gates.
  The update flag is cleared and success notified only after ALL gates pass;
  any failed gate stops the run, retains the flag, and logs the failure.
- **Correct `bifrost-gateway` spec drift via delta**: persistence requirement
  rewritten to the named-volume reality (bind mounts corrupt SQLite WAL on
  Docker Desktop virtiofs; Redis uses its named volume and is not
  host-published), healthcheck requirement rewritten to the deployed timing
  (30s interval, 15s timeout, 3 retries, 120s start period), and a new
  fail-closed, evidence-gated image-upgrade contract requirement added.
- **Update the store `config.yaml`** OmniRoute section to record v3.8.50,
  the upgrade date, and the target digest.

## Non-Goals

- **No Redis major-version change.** The deployment stays on
  `redis:7-alpine`. Upstream compose now ships `redis:8.6.5-alpine`; that
  migration is a separate infrastructure change, not part of an application
  image upgrade.
- **No new Compose profiles or sidecars** (`codex-app-server`,
  `codex-web-codex-browser`, `memory`/Qdrant, `bifrost`, `cliproxyapi` all
  remain off). New common env/volumes for the codex-app-server sidecar are
  inert unless that profile is activated.
- **No source-checkout update.** No `git pull` in `~/Omniroute` — the checkout
  carries unrelated local modifications and untracked deployment
  infrastructure; the deployment is image-based per the 2026-08-24
  standardization.
- **No `.env` changes.** All deployed keys remain valid in v3.8.50 (59 of 64
  documented in the v3.8.50 example; the 5 undocumented ones are
  backward-compatible residue — see research).
- **Adopt upstream's active runtime memory change**: v3.8.50 upstream compose
  sets `NODE_OPTIONS=--max-old-space-size=2048` (image default is 1024).
  Since the local compose stays at v3.8.49, this is applied via the
  deployment-owned `docker-compose.override.yml` and verified through
  rendered config + `docker inspect` after deploy.
- **No changes to tracked upstream files** (compose files, Dockerfile, source).
  Only two untracked deployment-owned files are edited: `scripts/update.sh`
  (hardened) and `docker-compose.override.yml` (NODE_OPTIONS adoption).
- **No fix for the archived `ops-health-omniroute-degradation-contract`
  canonical-merge anomaly** — that concerns `ai-review` degradation behavior
  and is recorded as a separate follow-up.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bifrost-gateway` — persistence requirement corrected to named-volume
  reality; healthcheck requirement corrected to deployed timing; new
  fail-closed image-upgrade contract requirement added.

## Impact

- **Runtime**: `omniroute` container recreated on the v3.8.50 image; brief
  downtime during cutover (healthy typically within the 120s start period).
- **Files**: `~/Omniroute/scripts/update.sh` (hardened; untracked deployment
  infrastructure), `~/Omniroute/docker-compose.override.yml` (NODE_OPTIONS
  2048 MB adoption; untracked deployment infrastructure),
  `openspec/config.yaml` (version note), canonical
  `specs/bifrost-gateway/spec.md` (via archive merge of the delta).
- **Rollback**: pre-update SQLite snapshot in `~/.omniroute/snapshots/` plus
  the old image ID recorded before pull; rollback = redeploy old image and,
  if data was migrated, restore the snapshot.
- **Consumers**: agent-core / CLI consumers hitting
  `http://127.0.0.1:20128/v1` see unchanged OpenAI-compatible behavior; the
  `/v1/models` catalog may shrink slightly (health-check-excluded models now
  hidden — intended upstream fix #10026).
