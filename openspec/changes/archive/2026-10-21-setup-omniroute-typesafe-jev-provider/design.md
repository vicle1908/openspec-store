# Design

## Context

See `proposal.md` — Why for motivation and `specs/bifrost-gateway/spec.md` for normative requirements.

In OmniRoute `v3.8.52` (merged via upstream PR `#15278`), TypeSafe AI is registered as a dedicated API-key specialty provider (`APIKEY_PROVIDERS.typesafe` in `src/shared/constants/providers/apikey/specialty-media.ts:172-185`):
- `id: "typesafe"`, `alias: "typesafe"`, `serviceKinds: []` (intentionally empty so `typesafe` is never exposed in `/v1/models` chat pickers or mistaken for an OpenAI-compatible generative endpoint).
- `validateTypesafeProvider` (`src/lib/providers/validation/typesafe.ts`) validates credentials by calling `evaluateSystemOneChoice` (`open-sse/services/typesafe/systemOne.ts`) against `POST https://api.typesafe.ai/v1/systemone` with `model: "jev-latest"`, `state: "ping"`, and a 2-option choice rubric (`ok` vs `other`).
- Upstream PR `#15279` (`feat(routing): add jev combo strategy driven by TypeSafe Jev`, branch `miguelenes:feat/jev-combo`) wires `strategy: "jev"` into OmniRoute's combo router (`open-sse/services/combo/jevAsk.ts` and `jevStrategy.ts`), resolving the TypeSafe API key at request time via `getProviderCredentials("typesafe", null, args.apiKeyAllowedConnections ?? null)` from SQLite `provider_connections`.
- Meanwhile, external System One consumers on the workstation (`shb-core`'s `JevDecisionClient` in `~/Developer/shb/shb-core/src/shb_core/jev.py` and OMP's built-in `typesafe/jev-1.14.0` judge provider) natively speak TypeSafe's `POST https://api.typesafe.ai/v1/systemone` protocol (including HTTP/2 multiplexing and `Content-Encoding: zstd` payload compression) using `TYPESAFE_API_KEY` from `~/.zshenv` (`mode 0600`).

## Goals / Non-Goals

**Goals:**
- Provision and validate a dedicated `typesafe` provider connection in OmniRoute (`127.0.0.1:20128`) using OmniRoute's native `/api/providers` and `/api/providers/{id}/test` endpoints so the credential is stored encrypted at rest (`enc:v1:...`) in `/app/data/storage.sqlite` (`provider_connections`) with `isActive: true` and `testStatus: "active"`.
- Maintain 0 lines of custom code or boot-time monkeypatching in `~/Omniroute` (`scripts/container-entrypoint-compat.sh` and tracked files stay untouched) so automated `~/Omniroute/scripts/update.sh` upgrades remain completely conflict-free and `strategy: "jev"` works out of the box when upstream PR `#15279` ships in `v3.8.53+`.
- Establish a deterministic, value-blind pytest verification suite (`tests/test_omniroute_typesafe_provider.py`) in `platform/openspec-store` verifying the `typesafe` connection health, `/v1/models` exclusion invariant, and zero-monkeypatch boundary.

**Non-Goals:**
- Intercepting `POST /v1/systemone` in `~/Omniroute/scripts/container-entrypoint-compat.sh` or `/app/peer-stamp.mjs`.
- Adding `typesafe/jev-*` models to `STATIC_MODEL_PROVIDERS` or `/v1/models`.
- Modifying `shb-core` or OMP to route `POST /v1/systemone` through `127.0.0.1:20128` (they connect directly to `https://api.typesafe.ai`).

## Decisions

### Decision 1: Provision `typesafe` via Native `/api/providers` SQLite Store Instead of `container-entrypoint-compat.sh` Hook

```text
+-----------------------------------------------------------------------------------+
|            ZERO-CUSTOMIZATION JEV + OMNIROUTE ARCHITECTURAL BOUNDARY              |
+-----------------------------------------------------------------------------------+

  1. OMNIROUTE GATEWAY (127.0.0.1:20128, v3.8.52+)
  ================================================
  ~/.zshenv (TYPESAFE_API_KEY, mode 0600)
       |
       | (One-time value-blind provisioning via POST /api/providers)
       v
  /app/data/storage.sqlite :: provider_connections (provider="typesafe")
       |-- Encrypted at rest (AES-256-GCM enc:v1:...)
       |-- Validated via POST /api/providers/validate (method="typesafe_systemone")
       |-- Tested via auto-test / POST /api/providers/{id}/test (valid=true, diagnosis.type="ok")
       |-- .connection.isActive: true, .connection.testStatus: "active", .connection.apiKey masked
       |-- Consumed natively by getProviderCredentials("typesafe") in strategy: "jev"

  2. DIRECT SYSTEM ONE SDK CONSUMERS (shb-core, OMP judge/find)
  =============================================================
  [shb-core JevDecisionClient] ---+
  [OMP typesafe/jev-1.14.0]    ---+--> Direct HTTP/2 + zstd --> https://api.typesafe.ai/v1/systemone
```

- **Rationale**:
  1. **Upstream Alignment**: Upstream PR `#15278` (shipped in `v3.8.52`) and PR `#15279` (`strategy: "jev"`) read the TypeSafe key from `provider_connections` (`provider = 'typesafe'`) via `getProviderCredentials("typesafe")`, *not* from an unindexed process environment variable or pre-Next HTTP hook.
  2. **Security & Governance**: Storing the credential via `POST /api/providers` encrypts `apiKey` at rest in `/app/data/storage.sqlite`, masks the key on all `GET /api/providers` responses, integrates with `omniroute providers list`, and runs `validateTypesafeProvider` (`method: "typesafe_systemone"`).
  3. **Upgrade Immunity**: A pre-Next hook in `scripts/container-entrypoint-compat.sh` would have to string-patch `/app/peer-stamp.mjs`, bypass Next.js `enforceApiKeyPolicy` and `resolveKeyConnectionScope`, and risk breaking on every 12-hour `update.sh` pull. By using the native `typesafe` provider connection for OmniRoute and direct `https://api.typesafe.ai` connections for external System One SDK clients, customization in `~/Omniroute` is reduced to **zero lines**.
- **Alternatives Considered**:
  - *Option A (`container-entrypoint-compat.sh` `/v1/systemone` passthrough)*: Rejected because upstream explicitly closed `/v1/systemone` passthrough (`#13987`) as `NOT_PLANNED`, pre-Next hooks cannot safely reuse Next.js auth/policy/SQLite encryption layers without brittle bundle imports, and `shb-core` / OMP already talk to `https://api.typesafe.ai` directly with native HTTP/2 and `zstd` compression.
  - *Option B (Forking `~/Omniroute` tracked TypeScript files)*: Rejected because `~/Omniroute` runs pre-built `diegosouzapw/omniroute:latest` images updated by `~/Omniroute/scripts/update.sh`, so local source edits are ignored by the container and dirty the git checkout.

### Decision 2: Idempotent, Value-Blind Credential Provisioning & Verification Transaction Boundary

- **Transaction Boundary**:
  1. Call `POST http://127.0.0.1:20128/api/providers/validate` directly over HTTP with `Authorization: Bearer $OMNIROUTE_API_KEY` (and without `x-omniroute-cli-token`; never use un-intercepted `omniroute providers add` or `omniroute providers test` CLI subcommands, which read an empty `/tmp/omniroute-cli-bridge-*` SQLite DB and generate a mismatched CLI salt). Assert `valid === true` and `method === "typesafe_systemone"`.
  2. Query `GET http://127.0.0.1:20128/api/providers?limit=5000` (authenticated with `OMNIROUTE_API_KEY`) and filter `.connections[] | select(.provider == "typesafe")`.
  3. If no `typesafe` connection exists, read `TYPESAFE_API_KEY` from `~/.zshenv` (`mode 0600`) in memory without echoing it to stdout/stderr, and send `POST http://127.0.0.1:20128/api/providers` with header `x-skip-model-sync: true` and body `{"provider": "typesafe", "name": "typesafe-primary", "apiKey": "<in-memory-key>", "priority": 1}`.
  4. Because `POST /api/providers` triggers an asynchronous background `testSingleConnection(newConnection.id)` call (`src/app/api/providers/route.ts:437`), poll `GET http://127.0.0.1:20128/api/providers/{id}` for up to 3 seconds (every 500ms) until `.connection.testStatus === "active"` and `.connection.isActive === true`. Only if `.connection.testStatus` is not `"active"` after polling (or when verifying an existing inactive connection), invoke `POST http://127.0.0.1:20128/api/providers/{id}/test` and assert `valid === true` and `diagnosis.type === "ok"` (noting that `buildApiKeyConnectionTestResult` in `apiKeyTestResult.ts:57-77` strips `method` on `/test`).
  5. Re-query `GET http://127.0.0.1:20128/api/providers/{id}` and assert `.connection.provider === "typesafe"`, `.connection.isActive === true`, `.connection.testStatus === "active"`, and that `.connection.apiKey` is masked (`"***"` via `maskStoredApiKey`) and never equals the raw `TYPESAFE_API_KEY`. Also verify `omniroute providers list --output json` includes the active `typesafe` row.

## Risks / Trade-offs

- **Risk**: Creating a connection via `POST /api/providers` starts with `isActive: false` (`src/app/api/providers/route.ts:366`) while the background `testSingleConnection` auto-test runs asynchronously; immediately firing a manual `POST /api/providers/{id}/test` would race two concurrent probes to `api.typesafe.ai` and two health writes to SQLite.
  - **Mitigation**: Pass `x-skip-model-sync: true` on `POST /api/providers` and poll `GET /api/providers/{id}` for up to 3 seconds for the background auto-test to settle before falling back to an explicit `POST /api/providers/{id}/test`.
- **Risk**: Upstream `api.typesafe.ai` transient rate-limiting (`HTTP 429`) during connection test.
  - **Mitigation**: `validateTypesafeProvider` (`src/lib/providers/validation/typesafe.ts:47-54`) explicitly treats `HTTP 429` as `valid: true` with a rate-limit warning so valid credentials still activate cleanly.
