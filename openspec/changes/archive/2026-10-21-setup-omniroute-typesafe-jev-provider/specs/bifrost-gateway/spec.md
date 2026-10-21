# Spec Delta

## ADDED Requirements

### Requirement: OmniRoute SHALL provision and validate TypeSafe as a dedicated System One specialty provider

The deployment SHALL provision `typesafe` (`serviceKinds: []`) in OmniRoute's SQLite `provider_connections` store via `/api/providers`, validate it via `/api/providers/validate` (`method: "typesafe_systemone"`) and `/api/providers/{id}/test` (`diagnosis.type: "ok"`), and exclude `typesafe` from `/v1/models` and `container-entrypoint-compat.sh` hooks.

#### Scenario: Dedicated TypeSafe provider connection is created and validated via native System One probe

- **WHEN** the operator validates `TYPESAFE_API_KEY` via `POST http://127.0.0.1:20128/api/providers/validate` and provisions `provider: "typesafe"` via `POST http://127.0.0.1:20128/api/providers` (with `Authorization: Bearer $OMNIROUTE_API_KEY` and `x-skip-model-sync: true`, polling `GET /api/providers/{id}` for the background auto-test before falling back to `POST /api/providers/{id}/test`)
- **THEN** `/api/providers/validate` SHALL return `valid: true` and `method: "typesafe_systemone"`, and OmniRoute SHALL store the credential encrypted at rest in `/app/data/storage.sqlite` (`provider_connections`) and transition `.connection` to `isActive: true` and `testStatus: "active"` (`diagnosis.type: "ok"` on `/api/providers/{id}/test`)
- **AND** `GET http://127.0.0.1:20128/api/providers/{id}` SHALL return `{"connection": {"provider": "typesafe", "isActive": true, "testStatus": "active", ...}}` with `.connection.apiKey` masked (`"***"`), never exposing the plaintext API key

#### Scenario: TypeSafe specialty provider remains excluded from chat-selectable model catalogs and entrypoint monkeypatches

- **WHEN** an authenticated client queries `GET http://127.0.0.1:20128/v1/models` or inspects `~/Omniroute/scripts/container-entrypoint-compat.sh`
- **THEN** `typesafe` (`serviceKinds: []`) SHALL NOT advertise chat-selectable models in `/v1/models` so coding-agent CLIs never route OpenAI Chat Completions or Responses generation requests to `typesafe`
- **AND** `~/Omniroute/scripts/container-entrypoint-compat.sh` and `~/Omniroute` tracked files SHALL contain zero custom `/v1/systemone` reverse-proxy monkeypatches, preserving clean zero-drift compatibility across `~/Omniroute/scripts/update.sh` upgrades and native `strategy: "jev"` combo routing (`getProviderCredentials("typesafe")`)

#### Scenario: Invalid or missing TypeSafe API key fails validation cleanly without activating the connection

- **WHEN** `POST http://127.0.0.1:20128/api/providers/{id}/test` is invoked for a `typesafe` connection whose API key is invalid (`HTTP 401` / `HTTP 403` from `https://api.typesafe.ai/v1/systemone`) or empty
- **THEN** validation SHALL return `valid: false` with a sanitized error message (`"Invalid API key"` or `"API key is required"`)
- **AND** the connection SHALL NOT be marked `isActive: true` with `testStatus: "active"`
