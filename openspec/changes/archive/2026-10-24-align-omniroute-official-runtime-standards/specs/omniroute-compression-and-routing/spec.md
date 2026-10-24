# Spec Delta

## ADDED Requirements

### Requirement: Gemini 4 Trailing Model Turn Stripping, Exact-Model Lockout Scoping on agy, Slow SQLite Telemetry, and Unified Database Semantic Cache Config

The OmniRoute gateway SHALL strip trailing `role: "model"` turns on `gemini-4-*` requests, SHALL exclude `"model turn"` HTTP 400 responses from model-access-denied lockout classifiers, SHALL scope `agy` per-model lockouts to the exact model, and SHALL configure `OMNIROUTE_SQLITE_SLOW_MS=200` with unified `database_settings.cache` limits.

#### Scenario: Trailing model turn stripped on gemini-4-argon requests
- **WHEN** a coding client or advisor submits a request targeting `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low` whose translated Gemini `contents` array ends with one or more `role: "model"` entries (and `contents.length > 1`)
- **THEN** OmniRoute SHALL strip the trailing `role: "model"` entries before sending the payload to Cloud Code so upstream does not reject the turn with HTTP 400

#### Scenario: Request-shape model-turn 400 does not trigger 1-hour model_capacity lockout
- **WHEN** an upstream target returns HTTP 400 with `"Requests ending with a model turn are not supported"`
- **THEN** both `isModelScoped400` and `isProviderModelUnsupported400` SHALL return `false` and OmniRoute SHALL NOT lock the model or `family:gemini` for 1 hour (`model_capacity`)

#### Scenario: Per-model lockouts on agy connections scope to the exact model
- **WHEN** `lockModelIfPerModelQuota` records a per-model lockout for provider `"agy"`
- **THEN** OmniRoute SHALL invoke `lockExactModel` for the specific model ID rather than locking the entire `family:gemini` quota family across the connection

#### Scenario: Synchronous SQLite stall telemetry and unified database semantic cache settings
- **WHEN** `OMNIROUTE_SQLITE_SLOW_MS=200` is configured and `/api/settings/database` is queried
- **THEN** OmniRoute SHALL emit a diagnostic `[SQLITE-SLOW]` warning (without query parameters or prompt content) whenever a synchronous SQLite operation exceeds 200 milliseconds, and `GET /api/settings/database` SHALL report `cache.semanticCacheMaxSize: 1000` and `cache.semanticCacheTTL: 18000000` matching `GET /api/settings`
