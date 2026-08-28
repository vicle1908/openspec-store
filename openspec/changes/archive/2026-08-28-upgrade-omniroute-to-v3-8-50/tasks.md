# Tasks

## 1. Planning & research

- [x] 1.1 Verify upstream release state: v3.8.50 tag + GitHub release (published 2026-08-26T19:30:30Z, not prerelease), Docker Hub `latest`/`3.8.50` index digest `sha256:085c57ad...` (research/upstream-v3.8.50.md)
- [x] 1.2 Compare v3.8.49..v3.8.50: 12 commits, compose/env/Dockerfile diffs, breaking-change scan (none found)
- [x] 1.3 Verify deployment `.env` compatibility: 64 deployed keys — 59 present in v3.8.50 `.env.example`; 5 (`GEMINI_CLI_OAUTH_CLIENT_ID`, `GEMINI_CLI_OAUTH_CLIENT_SECRET`, `GEMINI_CLI_USER_AGENT`, `QWEN_OAUTH_CLIENT_ID`, `QWEN_USER_AGENT`) absent from BOTH v3.8.49 and v3.8.50 examples (pre-existing custom/legacy, not removals); 4 upstream-removed vars absent from deployment `.env`; all 15 deployment-critical keys explicitly verified
- [x] 1.4 Identify `bifrost-gateway` canonical spec drift (bind-mount persistence, upstream healthcheck timing)

## 2. Baseline evidence (pre-mutation)

- [x] 2.1 Record runtime version, container/image IDs, RepoDigests, container health, endpoint responses (evidence.md §1)
- [x] 2.2 Record rendered Compose invariants: loopback ports 20128/20129/20132, `omniroute-data` → `/app/data`, redis unpublished (evidence.md §1)
- [x] 2.3 Record SQLite baseline: `integrity_check` ok, table count, `api_keys`, `provider_connections` (evidence.md §1)

## 3. Harden the updater

- [x] 3.1 Rewrite `~/Omniroute/scripts/update.sh` fail-closed: gates 0–9 per design D2; flag retained on any failure; success path only after all gates
- [x] 3.2 Syntax-check the rewritten script (`bash -n` + `shellcheck`)
- [x] 3.3 Apply `NODE_OPTIONS=--max-old-space-size=2048` in `docker-compose.override.yml` (upstream v3.8.50 runtime setting); verify rendered config shows it AND all critical env keys/ports/volumes/redis invariants unchanged

## 4. Execute the upgrade

- [x] 4.1 Run hardened `update.sh 3.8.50` once
- [x] 4.2 Confirm all gates passed and the flag was cleared by the script (not manually)

## 5. Post-upgrade verification (independent of the updater)

- [x] 5.1 Container `healthy`; `/app/package.json` version = 3.8.50; `/api/monitoring/health` reports healthy + setupComplete=true (v3.8.50 no longer exposes version to unauthenticated callers — package.json gate is authoritative)
- [x] 5.2 Running container image ID == pulled `latest` image ID; RepoDigest == `sha256:085c57ad...`
- [x] 5.3 Endpoints: `/healthz` = ok, dashboard 200/307, `HEAD /v1/models` = 200, anonymous `GET /v1/models` = 401 (catalog auth opt-out in v3.8.50) with authenticated in-container GET = 200 + non-empty catalog
- [x] 5.4 SQLite: `integrity_check` ok, `api_keys` and `provider_connections` at or above their captured pre-state baselines (1 and 12)
- [x] 5.5 Invariants: loopback bindings, `omniroute-data` volume, redis unpublished + still 7-alpine + healthy, SOCKS5 flags false, container env has `NODE_OPTIONS=--max-old-space-size=2048`, only base-profile services running
- [x] 5.6 Record post-upgrade evidence (evidence.md §2)

## 6. Close out

- [x] 6.1 Update store `config.yaml` OmniRoute section (v3.8.50, upgrade date, digest)
- [x] 6.2 `openspec validate --strict upgrade-omniroute-to-v3-8-50` (valid)
- [x] 6.3 Archive the change; verify the `bifrost-gateway` delta merged into the canonical spec
- [x] 6.4 Validate canonical specs strictly (389/389 passed); scoped commit (archived change + `bifrost-gateway` spec + `config.yaml` only — no unrelated dirty files)
- [x] 6.5 Remove temporary artifact `~/Omniroute/scripts/update.sh.bak-20260828` (pre-hardening backup; kept only until the upgrade succeeds)
