# Proposal

## Why

OmniRoute `v3.8.52` shipped dedicated `typesafe` specialty provider registration (`APIKEY_PROVIDERS.typesafe`), live System One connection validation (`validateTypesafeProvider` probing `POST https://api.typesafe.ai/v1/systemone`), and the internal System One client (`open-sse/services/typesafe/systemOne.ts`), while upstream PR `#15279` (`feat(routing): add jev combo strategy driven by TypeSafe Jev`) consumes `getProviderCredentials("typesafe")` directly from OmniRoute's SQLite `provider_connections` store. However, our local OmniRoute instance (`127.0.0.1:20128`) currently has zero `typesafe` provider connections provisioned, leaving the workstation's valid `TYPESAFE_API_KEY` unregistered in OmniRoute and risking custom boot-patch drift if an unofficial `/v1/systemone` reverse-proxy shim were injected into `scripts/container-entrypoint-compat.sh`.

## What Changes

- **Zero-Customization Dedicated `typesafe` Provider Registration in OmniRoute**:
  - Provision a dedicated `typesafe` (`authType: "apikey"`, `provider: "typesafe"`) provider connection in OmniRoute via `POST http://127.0.0.1:20128/api/providers` (with header `x-skip-model-sync: true` and `Authorization: Bearer $OMNIROUTE_API_KEY`, bypassing un-intercepted host CLI subcommands) using the operator's `TYPESAFE_API_KEY` resolved from `~/.zshenv` (`mode 0600`) without echoing or logging secret values.
  - Verify OmniRoute's built-in TypeSafe System One validation via `POST http://127.0.0.1:20128/api/providers/validate` (`valid: true`, `method: "typesafe_systemone"`) and confirm via `GET http://127.0.0.1:20128/api/providers/{id}` (polling the auto-test on creation before falling back to `POST /api/providers/{id}/test` with `valid: true` and `diagnosis.type: "ok"`) that `.connection` transitions to `isActive: true` and `testStatus: "active"` in `/app/data/storage.sqlite` with `.connection.apiKey` masked.
- **Clean Boundary Between OmniRoute Jev Combo Routing and Direct System One Clients**:
  - Document and enforce the zero-customization architectural boundary: OmniRoute owns `typesafe` credentials in `provider_connections` for native `strategy: "jev"` combo target ordering (`getProviderCredentials("typesafe")` -> `evaluateSystemOneChoice`), whereas external System One SDK consumers (`shb-core` `JevDecisionClient`, OMP `typesafe/jev-1.14.0` judge) connect directly to `https://api.typesafe.ai/v1/systemone` over HTTP/2 with native `zstd` compression rather than routing non-chat System One payloads through custom `container-entrypoint-compat.sh` monkeypatches.
  - Ensure `typesafe` (`serviceKinds: []`) remains excluded from `/v1/models` chat-selectable model lists so coding-agent CLIs never mistake `typesafe` for an OpenAI Chat Completions or Responses generation endpoint.
- **Automated Value-Blind Governance & Readiness Verification**:
  - Add a value-blind verification test in `/Users/androidteam/Developer/platform/openspec-store/tests/test_omniroute_typesafe_provider.py` that verifies the `typesafe` specialty provider contract, active connection status, and zero-monkeypatch invariant in `~/Omniroute/scripts/container-entrypoint-compat.sh`.

## Non-Goals

- Modifying any git-tracked source files in `/Users/androidteam/Omniroute` or building custom local Docker images for OmniRoute.
- Adding custom `POST /v1/systemone` reverse-proxy hooks to `~/Omniroute/scripts/container-entrypoint-compat.sh` or `/app/peer-stamp.mjs` (upstream closed issue `#13987` as `NOT_PLANNED` and is shipping native `strategy: "jev"` in PR `#15279`).
- Exposing `typesafe/jev-*` models as chat-selectable generative endpoints on `/v1/chat/completions`, `/v1/responses`, or `/v1/messages`.
- Modifying `tdt/agent-core`, `tdt-core`, or any frozen `~/Developer/tdt/*` repository.

## Affected Ownership Boundaries

- **OmniRoute Runtime State (`/app/data/storage.sqlite` on `omniroute-data` named volume)**: Encrypted `typesafe` row in `provider_connections` managed via the authenticated `/api/providers` REST API on `127.0.0.1:20128`.
- **OmniRoute Deployment Directory (`/Users/androidteam/Omniroute`)**: Read-only verification that `git status` remains clean and `scripts/container-entrypoint-compat.sh` remains free of brittle `/v1/systemone` monkeypatches across `scripts/update.sh` pulls.
- **OpenSpec Governance Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Delta specification in `specs/bifrost-gateway/spec.md` and behavioral verification test in `tests/test_omniroute_typesafe_provider.py`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bifrost-gateway`: Add requirements for provisioning and validating `typesafe` as a dedicated System One specialty provider connection in OmniRoute (`serviceKinds: []`, `method: "typesafe_systemone"`), preserving the zero-customization upgrade path for native `strategy: "jev"` combo routing while keeping external System One SDK clients pointed directly at `https://api.typesafe.ai`.

## Impact

- **Immediate `v3.8.52` Readiness & Zero Upgrade Drift**: Registers and encrypts `TYPESAFE_API_KEY` inside OmniRoute's native SQLite credential store (`provider: "typesafe"`, `isActive: true`, `testStatus: "active"`) using 100% built-in `v3.8.52` features, requiring zero tracked file edits and surviving every `~/Omniroute/scripts/update.sh` Docker Hub upgrade.
- **Seamless `v3.8.53+` (`strategy: "jev"`) Cutover**: Because upstream PR `#15279` (`open-sse/services/combo/jevAsk.ts`) resolves `getProviderCredentials("typesafe")` directly from `provider_connections`, `strategy: "jev"` combos can be enabled immediately upon upstream image release without credential migration or entrypoint script teardown.
