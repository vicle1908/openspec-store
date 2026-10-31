# Evidence: reconcile-omniroute-spec-and-combo-consistency

## 1. Execution Summary

- **Change**: `reconcile-omniroute-spec-and-combo-consistency`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **External Implementation Root**: `/Users/androidteam/Omniroute` (OmniRoute `v3.8.52`, container `omniroute`, volume `omniroute-data` `/app/data/storage.sqlite`) and `/Users/androidteam/Developer/wiki/entities/omniroute.md`
- **Timestamp (UTC)**: `2026-10-31`

---

## 2. Section 1 Evidence: Live SQLite `omniroute-data` Combo & Account Pool Reconciliation (`1.1`–`1.5`)

### 2.1 Pre-Apply Snapshot (`1.1`)
- Captured read-only value-blind backup snapshot of `provider_connections` (`provider = 'agy'`) and `combos` (`gemini-3.8-flash-high`, `claude-opus-5.5`, `claude-sonnet-5.5`) inside `omniroute:/tmp/pre-apply-combos-snapshot.json`.
- Verified `provider_connections` (`provider = 'agy'`) distribution (`16` total connections):
  - **12 active `g1-pro-tier` (`Pro`) connections** (`is_active = 1`):
    1. `ea0d6c23-85c0-42c8-abdf-8186effd3371` (`vinhbk20906@gmail.com`)
    2. `38782750-7a60-46d4-ae3f-e8c13cda296b` (`vicgnome1908@gmail.com`)
    3. `a59369ac-c8a9-40f7-ad21-fc7c7bc7a4a9` (`vicgnome19089@gmail.com`)
    4. `9d66311f-9db7-49b2-90f5-277c5f311f2a` (`vicgnome19092@gmail.com`)
    5. `615a4993-68ce-4a6b-be58-ed376be8ae63` (`vicgnome19093@gmail.com`)
    6. `20369f65-4fae-4fa0-b02b-4f15047bee79` (`vicgnome19081@gmail.com`)
    7. `d5c3465f-9797-4b4b-a937-c3e653e168fb` (`vicgnome19095@gmail.com`)
    8. `d71506bf-5952-4805-82e0-125cef2941ce` (`vicgnome19096@gmail.com`)
    9. `cdac4585-b65a-4134-aa11-9544f7e42245` (`vuvinh190899@gmail.com`)
    10. `ce95e1cb-27a4-433f-9c50-bdb6ad0b6b6b` (`vicgnome19097@gmail.com`, upgraded to `g1-pro-tier`)
    11. `d902fb26-520d-4316-9f2c-6e52c5da7b74` (`vinhvugit@gmail.com`)
    12. `e85dd569-0271-4974-bcd9-b250295e6810` (`hongsonle19081952@gmail.com`)
  - **3 active `g1-ultra-tier` (`Ultra`) connections** (`is_active = 1`):
    1. `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`vicgnome19094@gmail.com`)
    2. `0532bad4-2486-4286-8f06-510e9c678620` (`vinhvumobile@gmail.com`)
    3. `338764b8-1cd7-4946-b789-ee5dad4c5073` (`vinhghtk1908@gmail.com`)
  - **1 inactive/banned connection** (`is_active = 0`, `test_status = "banned"`, `last_error_type = "account_deactivated"`):
    1. `47f334b1-b801-41f6-a709-4ebabb7a86d6` (`vicgnome19091@gmail.com`)

### 2.2 Combo & Rate-Limit Updates (`1.2`–`1.5`)
- Executed SQLite + authenticated `PUT /api/combos/{id}` updates (preserving full `current.config`) and `POST /api/rate-limits`:
  ```json
  {
    "putResults": [
      {
        "id": "7555d851-b4f3-44c6-b1fb-c6fdceabf388",
        "name": "gemini-3.8-flash-high",
        "status": 200,
        "stepCount": 12,
        "context_cache_protection": false,
        "targetTimeoutMs": 25000,
        "predictiveTtftMs": 25000
      },
      {
        "id": "4b2430da-0b3b-4b0e-9773-ec0f97adc252",
        "name": "claude-opus-5.5",
        "status": 200,
        "stepCount": 15,
        "context_cache_protection": false,
        "targetTimeoutMs": 180000,
        "predictiveTtftMs": 60000
      },
      {
        "id": "9447399c-856b-4f52-8820-b3bf3dc3f132",
        "name": "claude-sonnet-5.5",
        "status": 200,
        "stepCount": 15,
        "context_cache_protection": false,
        "targetTimeoutMs": 120000,
        "predictiveTtftMs": 45000
      }
    ],
    "rlpOk": 15,
    "totalActiveAgy": 15,
    "flags": [
      { "key": "ANTIGRAVITY_ACCOUNT_LEASE_ENABLED", "value": "false" },
      { "key": "COMBO_AUTO_PRUNE_STALE_STEPS", "value": "false" }
    ]
  }
  ```

---

## 3. Section 2 Evidence: Helper Comment & Wiki Synchronization (`2.1`–`2.2`)

- **Task `2.1` (`/Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh:4-14`)**:
  - Updated comment block to document all `3` non-chunk patches (`N1`–`N3`) + `43` chunk/route replacement rules (`R1`–`R43` = `46` total modifications) guarded by `49` fail-closed markers across `19` compiled files (`3` non-chunk + `46` chunk across `16` server chunk files).
  - Verified syntax and execution:
    - `bash -n /Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh` -> `exit 0`
    - `/Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh` -> `Muse Code wire-compat normalization verified (already_ok)` (`exit 0`)
- **Task `2.2` (`/Users/androidteam/Developer/wiki/entities/omniroute.md:6,44,67,73,74`)**:
  - Updated `updated: 2026-10-31`, Gate 4b (`43` chunk/route rules, `46` total modifications, `49` fail-closed markers across `19` compiled files), `gemini-3.8-flash-high` (`12`-account `g1-pro-tier` pool out of `15` active `agy` accounts), In-Container Wire & Resilience Normalization (`46` modifications, `49` fail-closed markers), and OpenSpec Archive Tracking.

---

## 4. Section 3 Evidence: Runtime Readback, Live Probes & Strict Validation (`3.1`–`3.2`)

- **`GET http://127.0.0.1:20128/api/combos` Readback**:
  - `bannedRefsAcrossAllCombos`: `[]` (`0` combos reference banned connection `47f334b1-b801-41f6-a709-4ebabb7a86d6`).
  - `gemini-3.8-flash-high`: `strategy: "auto"`, `context_cache_protection: false`, `stepCount: 12` (includes `ce95e1cb-27a4-433f-9c50-bdb6ad0b6b6b` and `e85dd569-0271-4974-bcd9-b250295e6810`, `0` Ultra accounts, `0` banned accounts), full `config` preserved (`targetTimeoutMs: 25000`, `predictiveTtftMs: 25000`, `candidatePool: ["agy"]`, `zeroLatencyOptimizationsEnabled: true`, `resetAwareQuotaCacheTtlMs: 300000`, `resetWindowQuotaCacheTtlMs: 300000`).
  - `claude-opus-5.5`: `strategy: "auto"`, `context_cache_protection: false`, `stepCount: 15`, `comboRefCount: 0`, `hasBanned47f3: false`, `hasHongsonle: true`, full `config` preserved (`nestedComboMode: "flatten"`, `targetTimeoutMs: 180000`, `predictiveTtftMs: 60000`).
  - `claude-sonnet-5.5`: `strategy: "auto"`, `context_cache_protection: false`, `stepCount: 15`, `comboRefCount: 0`, `hasBanned47f3: false`, `hasHongsonle: true`, full `config` preserved (`nestedComboMode: "flatten"`, `targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`, `maxRetries: 1`).
  - `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`: `strategy: "auto"`, `context_cache_protection: false`, `stepCount: 3` (`3` Ultra accounts), `targetTimeoutMs: 180000`, `predictiveTtftMs: 60000`.
- **Live Inference Probes (`POST /v1/chat/completions` and `POST /v1/responses` with `x-omniroute-no-cache: true`)**:
  - `POST /v1/chat/completions` (`model: "gemini-3.8-flash-high"`): `HTTP 200`, `text: "PONG"`
  - `POST /v1/responses` (`model: "gemini-3.8-flash-high"`): `HTTP 200`, `text: "PONG"`
  - `POST /v1/chat/completions` (`model: "claude-sonnet-5.5"`): `HTTP 200`, `model: "claude-sonnet-4-6"`, `text: "PONG"`
  - `POST /v1/chat/completions` (`model: "gemini-4-argon-low"`): `HTTP 200`, `model: "gemini-4-argon-low"`, `text: "PONG"`
- **OpenSpec Strict Validation & Archive Readiness**:
  - `openspec validate reconcile-omniroute-spec-and-combo-consistency --type change --strict --store openspec-store` -> `Change 'reconcile-omniroute-spec-and-combo-consistency' is valid` (`exit 0`).
  - Prospective main-spec merge validation (`buildUpdatedSpec` + `new Validator(true).validateSpecContent`) across `omniroute-runtime-customization`, `omniroute-compression-and-routing`, `omniroute-agent-cli-routing`, and `omniroute-closure-integrity` -> `valid: true` (`0` errors, `0` warnings across all 82 total requirements).
  - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/validate-archive-readiness.py --change reconcile-omniroute-spec-and-combo-consistency --strict` -> `STATUS: READY` (`9/9` tasks completed, `evidence.md` present, `exit 0`).
