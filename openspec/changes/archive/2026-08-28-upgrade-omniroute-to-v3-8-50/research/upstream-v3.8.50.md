# Research — OmniRoute v3.8.50 upstream state

Collected 2026-08-28 (Asia/Ho_Chi_Minh). Sources: GitHub Releases API,
GitHub compare API (v3.8.49...v3.8.50), raw.githubusercontent.com at both
tags, Docker Hub registry API, `docker buildx imagetools inspect`, local
deployment state.

## Release facts

| Item | Value |
|---|---|
| Latest release tag | `v3.8.50` |
| Published | 2026-08-26T19:30:30Z (prerelease: false) |
| Release URL | https://github.com/diegosouzapw/OmniRoute/releases/tag/v3.8.50 |
| Docker Hub `latest` index digest | `sha256:085c57adf499a8aaa9f35ccde95c0df9c11bd9ecd18d6c9edbf3b68b8079ba9d` (pushed 2026-08-27T04:23Z) |
| Docker Hub `3.8.50` index digest | identical to `latest` |
| 3.8.50 image size | ≈ 1.24 GB (3.8.49 was ≈ 483 MB) |
| Running version (pre-upgrade) | 3.8.49 |
| Running RepoDigest (pre-upgrade) | `sha256:92c768c56e2de32c51a0621ef182835018b00b288c9bb235c5c5e4514658c1a1` |
| Update flag | written 2026-08-27 22:05:01 by `com.omniroute.update-check` LaunchAgent; content = target digest |

## v3.8.49..v3.8.50 tag delta (12 commits)

```
e6523da2a fix(ci): unblock the npm publish — dynamic runner + reuse CI's next-build (#8941)
9233a9483 fix(deps): bump transitive deps for 6 Dependabot + remaining audit vulns on main
153f453b0 fix(deps): bump deps for 13 Dependabot + audit cleanup on main
b090b601a fix(deps): bump nanoid, dompurify for 2 new Dependabot alerts (#189, #190)
026e1cada fix(deps): bump nanoid, dompurify for Dependabot #189, #190
918fba5e3 fix(repo): harden .gitignore to also ignore a _tasks symlink (/_tasks)
5f0a39409 Hide health-check excluded models from /v1/models catalog (#10026)
ca23eed77 fix(models): memoize getModelsDevPricing (event loop / healthz) (#10055)
c68cda7df fix(resilience): honor shared passthrough providers (#11075)
65e81158a fix(ollama): route models by advertised capability (#11088)
b4ec7807a Release v3.8.50
5458026c2 docs(changelog): aggregate the ten v3.8.50 fragments into CHANGELOG.md (#11683)
```

Runtime-relevant for this deployment: #10026 (cleaner `/v1/models`), #10055
(event-loop/healthz latency), #11075 (passthrough providers), #11088 (Ollama
capability routing — deployment uses ollama-cloud connection). Rest is
dependency/security hygiene.

The GitHub release body is a full-cycle changelog (cycle open `ed2db6cb19` →
tip; 1,714 commits) — the tag-to-tag delta above is what actually changes
between the two deployed images.

## Breaking-change scan

- No "Breaking Changes" section in the release notes; the only "breaking"
  occurrences are "Non-breaking — existing onResponse hooks ... remain
  unchanged" and an unrelated test-commit title.
- No manual migration steps documented for Docker deployments; DB migrations
  run at app startup (release cycle includes migration version-collision
  fixes #9745, #9884, #9965).

## docker-compose.yml diff (v3.8.49 → v3.8.50)

- `redis` image: `redis:7-alpine` → `redis:8.6.5-alpine`; published port now
  defaults to `${REDIS_BIND_HOST:-127.0.0.1}` (loopback hardening).
  **Deferred** — we do not git-pull the checkout; rendered compose keeps
  `redis:7-alpine`, and our override already resets redis ports to
  unpublished.
- Common anchor gains `NODE_OPTIONS=--max-old-space-size=2048` (an ACTIVE
  runtime change — the image bakes a 1024 MB heap ceiling via
  `ENV OMNIROUTE_MEMORY_MB=1024` + `ENV NODE_OPTIONS`, and upstream compose
  overrides it to 2048) and codex-app-server env vars
  (`OMNIROUTE_CODEX_APPSERVER_WS`, token-file path) which are inert unless
  the `codex-app-server` profile is activated.
- Common anchor also gains volumes `codex-appserver-token` and
  `codex-appserver-home`. In the UPSTREAM compose these are inherited by
  `omniroute-base` (they are not inherently profile-inert). Because this
  deployment does not git-pull the checkout, the rendered local compose does
  NOT introduce them — no change here.
- **NODE_OPTIONS adoption**: since the local compose stays at v3.8.49, the
  2048 MB runtime setting is applied via the deployment-owned
  `docker-compose.override.yml` (`omniroute-base` environment) and verified
  through rendered compose config + `docker inspect` after deploy.
- `omniroute-base` service shape unchanged: same 3 ports, `base` profile,
  `container_name: omniroute`.
- Top-level volumes gain codex-app-server + codex-web-codex-browser entries
  (created lazily only by their profiles).

## Dockerfile / healthcheck

- v3.8.50 Dockerfile still copies `scripts/dev/healthcheck.mjs` →
  `/app/healthcheck.mjs` and sets `HEALTHCHECK CMD ["node", "healthcheck.mjs"]`
  with upstream timing (interval 30s, timeout 5s, start-period 15s, retries 3).
- `healthcheck.mjs` is not at repo root in either tag (raw fetch 404) — it is
  baked into the image at build time; the running container executes it today.
- The deployment override's relaxed timing (timeout 15s, start_period 120s)
  therefore remains necessary and valid on v3.8.50.

## .env compatibility

Normalized comparison of `.env.example` at both tags (commented +
uncommented variable names):

- v3.8.49: 596 distinct vars → v3.8.50: 783 distinct vars.
- ~187 added: new providers (Adobe Firefly, Alibaba free tier, DeepAI,
  Naga.ac, Soniox, Raycast...), CLI_* binary paths, Conductor/Devin-bridge,
  inspector/chat-log tuning — ALL optional, none required for base profile.
- 4 removed: `ALLOW_CHANGELOG_REMOVALS`,
  `ALLOW_MULTI_CONNECTIONS_PER_COMPAT_NODE`, `OMNIROUTE_PLUGINS_ALLOW_EXEC`,
  `WINDSURF_FIREBASE_API_KEY` — **none present** in the deployment `.env`.

Full deployed-`.env` comparison (64 keys set in `~/Omniroute/.env`):

- 59 of 64 present in the v3.8.50 `.env.example`.
- 5 absent from BOTH the v3.8.49 and v3.8.50 examples — pre-existing
  custom/legacy variables, not v3.8.50 removals:
  `GEMINI_CLI_OAUTH_CLIENT_ID`, `GEMINI_CLI_OAUTH_CLIENT_SECRET`, `GEMINI_CLI_USER_AGENT`, `QWEN_OAUTH_CLIENT_ID`, `QWEN_USER_AGENT`.
  Per-variable source verification against both fetched tags (`git grep`,
  excluding i18n reference docs, `.env*` examples, CHANGELOG, and quality
  allowlists):
  - `GEMINI_CLI_OAUTH_CLIENT_ID`, `GEMINI_CLI_OAUTH_CLIENT_SECRET`, `GEMINI_CLI_USER_AGENT`: ZERO application-source
    references in BOTH the v3.8.49 and v3.8.50 trees.
  - `QWEN_OAUTH_CLIENT_ID`, `QWEN_USER_AGENT`: no application-runtime references in
    either tag; remaining v3.8.50 mentions are i18n reference documentation
    only, and the v3.8.49 quality test-masking allowlist records that the
    corresponding OAuth config had already left the runtime at v3.8.49
    (#7866).
  - Conclusion: these five specific variables are backward-compatible
    configuration residue, not v3.8.50 removals; retaining them is safe and
    cleanup is optional future hygiene. (Per-variable finding — not a
    general claim that arbitrary unknown env vars are safe.)
- All 15 deployment-critical keys verified PRESENT in the v3.8.50 example:
  DASHBOARD_PORT, API_PORT, LIVE_WS_PORT, REDIS_URL,
  OMNIROUTE_WS_BRIDGE_SECRET, ENABLE_SOCKS5_PROXY,
  NEXT_PUBLIC_ENABLE_SOCKS5_PROXY, INITIAL_PASSWORD, JWT_SECRET,
  API_KEY_SECRET, STORAGE_ENCRYPTION_KEY, STORAGE_ENCRYPTION_KEY_VERSION,
  QUOTA_STORE_DRIVER, OMNIROUTE_ENABLE_LIVE_WS, LIVE_WS_ALLOWED_ORIGINS.

Conclusion: zero `.env` changes required.

## Deployment pre-state (2026-08-28)

- Container `omniroute`: Up ~47h, healthy; app version 3.8.49; node v26.5.0.
- `omniroute-redis`: redis:7-alpine, healthy, unpublished.
- Endpoints: `/healthz` → `ok`; dashboard → 307 (redirect to /login);
  `/api/monitoring/health` → 200 `{"status":"healthy",...,"version":"3.8.49"}`;
  `/v1/models` → 200 (catalog includes `auto/best-coding` combo).
- SQLite: integrity_check ok; 116 tables; api_keys=1; provider_connections=12;
  call_logs≈3480 (growing).
- Docker VM capacity: 610 GB free.
- Store state: 7 archived omniroute changes, none active; `bifrost-gateway`
  is the canonical spec governing this deployment.

## Known anomaly (out of scope, follow-up)

Archived change `2026-07-17-ops-scheduler-omniroute-jira-failures` carries a
delta `ops-health-omniroute-degradation-contract` that was never merged into
canonical specs (it concerns ai-review health degradation, not this
deployment). Recorded as a separate store-hygiene follow-up.
