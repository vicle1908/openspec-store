# Evidence

## Execution Summary

- **Change**: `add-omniroute-gemini-4-hydrogen-and-sync-fleet`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Timestamp**: `2026-11-13T12:05:00Z`
- **Host**: `iosteam-mac-mini` (`100.70.16.83`, macOS arm64)
- **Status**: All 10 tracked tasks complete (`10/10`) with zero failures across all 4 execution phases.

## Phase 1: Pre-Flight Backups & SQLite Snapshot

- **Backup Directory**: `/Users/androidteam/.omniroute/backups/add-omniroute-gemini-4-hydrogen-and-sync-fleet/` (`mode 0700`, `files/` `mode 0700`)
- **Manifest**: `sha256-manifest.json` (`mode 0600`) recording source paths, backup paths, sizes, and SHA-256 hashes for 16 companion configuration files + 4 gateway JSON endpoints (`gateway-combos.json`, `gateway-model-capability-overrides.json`, `gateway-reasoning-routing-rules.json`, `gateway-context-combos.json`).
- **SQLite Snapshot**: `/Users/androidteam/.omniroute/snapshots/pre-hydrogen-fleet-20261113-175208.sqlite` (`mode 0600`, 240 MB, `journal_mode=delete`, `PRAGMA quick_check = ok`, exactly 5 `.sqlite` files retained, 0 sidecars).
- **OmniRoute Git Status**: `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` -> `0` lines (clean).

## Phase 2: OmniRoute Gateway Provisioning & Mesh Handoff

- **Model Synchronization**: `POST http://127.0.0.1:20128/api/providers/62af823b-f3d7-4e6b-87a9-98069167d4f6/sync-models` -> HTTP `200 OK`.
- **Cooldown Reset**: `DELETE http://127.0.0.1:20128/api/resilience/model-cooldowns` (`{"all": true}`) -> HTTP `200 OK` (`clearedAll: true`).
- **Capability Overrides**: 16 single-key `PATCH /api/model-capability-overrides` calls verified:
  - Models: `gemini-4-hydrogen-{low,medium,high,xhigh}`
  - `context_length`: `1048576`
  - `max_input_tokens`: `1048576`
  - `max_output_tokens`: `262144`
  - `reasoning_efforts`: `"low,medium,high,xhigh"`
- **Combo UUIDs Provisioned (`strategy: "priority"`, WTU-Pro-first step order, `failoverBeforeRetry: true`)**:
  - `gemini-4-hydrogen-xhigh`: `fd5706a2-c52e-456e-9cf8-3b71e494c781`
  - `gemini-4-hydrogen-high`: `7ca84ebf-3f43-46a2-954c-1538c13ad2f9`
  - `gemini-4-hydrogen-medium`: `69251d75-a304-4ff2-a32f-70764dd6b630`
  - `gemini-4-hydrogen-low`: `a2620b38-da16-4a21-a4f2-793063f24f6a`
  - `gemini-4-hydrogen` (top-level combo-ref): `7a175b10-14c5-4eda-a825-f4b2f5b40864`
- **Reasoning-Routing Rules (`scope: "combo"`, `effortMode: "inherit"`)**:
  - `gemini-4-hydrogen-low`: `217e65cb-5d61-42b6-9f26-1cb60a03040c` -> `gemini-4-hydrogen-low`
  - `gemini-4-hydrogen-medium`: `48ec6175-277d-49a5-aff6-16769e064d75` -> `gemini-4-hydrogen-medium`
  - `gemini-4-hydrogen-xhigh`: `bead247b-76a7-4110-a132-36dd0830a8fc` -> `gemini-4-hydrogen-xhigh`
  - Default `"high"`: falls through unmatched to `gemini-4-hydrogen-high`.
- **`default-caveman` Assignments**: Reconciled to all 19 active combo UUIDs via `PUT /api/context/combos/default-caveman/assignments` (`total: 19`, `unique: 19`, `orphans: 0`).
- **`/v1/models` Download Invariant**: `curl --compressed` payload size = `33,049` bytes (asserted `<= 35,000` bytes). All 5 combos advertise `max_output_tokens: 262144`.
- **Protocol-Exact Live Probes (`max_output_tokens: 32768`)**:
  - `POST /v1/responses` (`gemini-4-hydrogen`, `high` & `gemini-4-hydrogen-xhigh`, `xhigh`) -> HTTP `200`
  - `POST /v1/chat/completions` (`gemini-4-hydrogen`, `high` & `gemini-4-hydrogen-xhigh`, `xhigh`) -> HTTP `200`
  - `POST /v1/messages` (`gemini-4-hydrogen`, `high` & `gemini-4-hydrogen-xhigh`, `xhigh`) -> HTTP `200`
  - `call_logs` attribution confirmed: `gemini-4-hydrogen-high` and `gemini-4-hydrogen-xhigh`.
- **AgentMemory Mesh Handoff**:
  - `POST http://127.0.0.1:3111/agentmemory/remember` -> HTTP `201`
  - `POST http://127.0.0.1:3111/agentmemory/signals/send` -> HTTP `201` (`to: macbook-pro-m5`)
  - Bidirectional mesh sync (`POST http://127.0.0.1:3111/agentmemory/mesh/sync` & `POST http://100.106.143.78:3111/agentmemory/mesh/sync`) -> HTTP `200` (`errors: []`).

## Phase 3: OMP Role Promotion & 15-Client Fleet Rollout

- **Isolated Smoke Profile**: Seeded `~/.omp/profiles/hydrogen-smoke/agent/` (`agent.db`, `models.db`, `skill-descriptions.db` via `.backup`). Isolated probe (`omp --profile hydrogen-smoke --model "omniroute/gemini-4-hydrogen:high" -p "reply only: HYDROGEN_SMOKE_OK"`) passed with `provider: "omniroute"` and zero fallback events.
- **Live Promotion**: Atomically replaced `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml` (`mode 0600`).
  - `modelRoles.default: omniroute/gemini-4-carbon`
  - `modelRoles.task: omniroute/gemini-4-hydrogen:high`
  - `retry.fallbackChains` configured for all 5 Hydrogen models and wired into `default`, `carbon*`, and `argon*` chains.
  - `omp models --kind all --json` reports 100 total models (9 Hydrogen models across `google-antigravity` and `omniroute`).
- **14 Companion Coding Agents & Editors**:
  - `~/.pi/agent/models.json` (`0600`): all 19 combos under `omniroute-responses`.
  - `~/.prime/agent/models.json` (`0600`): all 19 combos under `omniroute-responses`.
  - `~/.hermes/config.yaml` (`0600`): 19 combos in `models[]` + 5 `agent.reasoning_overrides`.
  - `~/.config/opencode/opencode.json` (`0600`): 19 combos in `omniroute-responses`.
  - `~/.config/kilo/kilo.jsonc` (`0600`): 19 combos in `omniroute-responses`.
  - `~/.codex/cockpit-model-catalog.json` (`0644`): 5 Hydrogen models added (priorities `1025`–`1029`).
  - `~/.factory/settings.json` (`0600`): 5 custom models added.
  - `~/.claude/profiles/omniroute-pm.json` (`0600`): 5 overrides + 5 picker options added.
  - `~/.kimi-code/config.toml` (`0600`): 5 `[models."gemini-4-hydrogen*"]` blocks added.
  - `~/.grok/config.toml` (`0600`): 5 `[model.omniroute-gemini-4-hydrogen*]` blocks added.
  - `~/.config/goose/custom_providers/custom_omniroute.json` (`0600`): 5 models added.
  - `~/.config/muse/settings.json` (`0600`): 5 `model_reasoning_efforts` + 5 `model_catalog` entries added (`schema_version: 1` in `auth.json` verified).
  - `~/.qwen/settings.json` (`0600`): 5 models in `modelProviders.openai`.
  - `~/.config/zed/settings.json` (`0600`): 5 models in `available_models`.
  - `setup-macbook-omniroute-client.sh --check` (`openspec-store/scripts/` + `~/Developer/scripts/`): both exit `0` (`SUCCESS`).
  - `/Users/androidteam/Developer/wiki/entities/omniroute.md`: updated to 19 active combos with Hydrogen architecture entry.

## Phase 4: Cross-Surface Integration Gate & Verification

- **Compat Patch**: `docker exec omniroute sh /app/container-entrypoint-compat.sh --patch-only` -> `already_ok`.
- **4-Way Concurrent Burst**: 4 simultaneous requests against `gemini-4-hydrogen` -> `4/4` HTTP `200` (`call_logs` confirmed WTU Pro dispatch `38782750`).
- **Live OMP Task Role Probe**: Executed `omp --model "omniroute/gemini-4-hydrogen:high" -p "reply only: TASK_HYDROGEN_OK"` -> returned `"TASK_HYDROGEN_OK"` served directly by `provider: omniroute`, `model: gemini-4-hydrogen` with zero fallback events.
- **Model Catalog Parity**: All 19 required combos active in `/v1/models`.
- **OmniRoute Source Purity**: `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` -> empty.

## Post-Verification Hygiene

- **OMP Model Name Normalization**: Normalized `providers.omniroute.models` `gemini-4-hydrogen` `name` to `gemini-4-hydrogen` (`~/.omp/agent/models.yml`, mode `0600`) matching all sibling `gemini-4-{argon,carbon,hydrogen}*` entries while preserving provider-level `compat.supportsDeveloperRole: false`.
- **Artifact & Throwaway Script Cleanup**: Removed temporary `omp-staged/`, `verify-phase{2-and-mesh,3-fleet,4-burst}.py`, `/tmp/omp-smoke-*.json`, and `$TMPDIR` smoke overlay `.yml` files so `/Users/androidteam/.omniroute/backups/add-omniroute-gemini-4-hydrogen-and-sync-fleet/` retains only immutable backups (`files/`, `gateway-*.json`, `sha256-manifest.json`) and verification reports (`provisioned-hydrogen-ids.json`, `phase2-verification-report.json`).
