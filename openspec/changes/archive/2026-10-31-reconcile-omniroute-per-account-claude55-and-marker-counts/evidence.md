# Evidence: reconcile-omniroute-per-account-claude55-and-marker-counts

## 1. Per-Account Claude 5.5 Step Alignment (`38782750-7a60-46d4-ae3f-e8c13cda296b` / `vicgnome19096@gmail.com`)

- **Catalog Inspection (`key_value` `namespace = 'syncedAvailableModels'`)**:
  - `agy:38782750-7a60-46d4-ae3f-e8c13cda296b`: `["claude-opus-5-5-low", "claude-sonnet-5-5-low", "claude-sonnet-5-5-medium", "claude-opus-5-5-medium", "claude-opus-5-5-high", "claude-sonnet-5-5-high"]` (`outputTokenLimit: 128000`).
  - Remaining 14 active `agy` connections: `["claude-opus-4-6-thinking", "claude-sonnet-4-6"]` (`outputTokenLimit: 64000`).
- **Combo Update & Live Probes**:
  - `PUT /api/combos/4b2430da-0b3b-4b0e-9773-ec0f97adc252` (`claude-opus-5.5`) -> `200 OK` (step `[1]` set to `agy/claude-opus-5-5-high`, 14 remaining active steps on `agy/claude-opus-4-6-thinking`, `0` `combo-ref` steps, full `config` preserved).
  - `PUT /api/combos/9447399c-856b-4f52-8820-b3bf3dc3f132` (`claude-sonnet-5.5`) -> `200 OK` (step `[1]` set to `agy/claude-sonnet-5-5-high`, 14 remaining active steps on `agy/claude-sonnet-4-6`, full `config` preserved).
  - Direct pinned probe on `38782750-7a60-46d4-ae3f-e8c13cda296b` (`POST /v1/chat/completions` with `x-omniroute-connection: 38782750-7a60-46d4-ae3f-e8c13cda296b`, `model: "agy/claude-opus-5-5-high"`, `"What is 14 * 15?"`): `HTTP 200`, `text: "210"`.
  - Direct pinned probe on `38782750-7a60-46d4-ae3f-e8c13cda296b` (`model: "agy/claude-sonnet-5-5-high"`, `"What is 19 * 23?"`): `HTTP 200`, `text: "437"`.
  - 5-call `POST /v1/messages` sweep on `claude-opus-5.5`: `5/5` returned `HTTP 200` (`"51"`, `"52"`, `"53"`, `"54"`, `"55"`) with `0` synthetic deprecation responses.

## 2. Compatibility Script & Documentation Synchronization (`51` Modifications / `60` Markers Across `24` Compiled Files)

- **Host & Container Bind-Mount Parity (`/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` vs `omniroute:/app/container-entrypoint-compat.sh`)**:
  - Size: `43,267` bytes, `nlink: 1`, SHA-256: `d8658728fc0e96cc3502ba133270081e69bb29b3167db6b2a3f252caf7a96ee1`.
  - Non-chunk patches: `3` (`N1`–`N3`).
  - Chunk/route replacement rules: `48` (`R1`–`R48` = `51` total modifications).
  - Fail-closed markers: `3` `requiredNonChunkMarkers` + `57` `requiredMarkers` across `21` unique server chunk files = `60` total fail-closed markers across `24` compiled files (`60/60` active on disk in `omniroute`).
- **Helper & Wiki Verification**:
  - `bash -n /Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh` -> `exit 0`.
  - `/Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh` -> `Muse Code wire-compat normalization verified (already_ok)` (`exit 0`).
  - Updated `/Users/androidteam/Developer/wiki/entities/omniroute.md:44,67,73`.
