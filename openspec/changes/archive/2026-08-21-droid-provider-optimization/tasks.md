# Tasks

## Phase 1: Additive Provider Registration

- [x] Create timestamped backup of `~/.factory/settings.json` before mutation.
  - Backup: `~/.factory/settings.json.pre-droid-provider-registration-20260821-173612`
  - Restore command: `cp '/Users/androidteam/.factory/settings.json.pre-droid-provider-registration-20260821-173612' '/Users/androidteam/.factory/settings.json'`

- [x] Parse live settings and append three verified custom model entries to `customModels` array.
  - Live models count: 1 → 4 (3 new entries appended)
  - Atomic installation via same-directory temp file + `os.replace()`

- [x] Preserve existing model entry (`dlg/deepseek-v4-pro`), hooks, plugins, mission settings, autonomy, and all unrelated keys unchanged.
  - Structural comparison live vs backup: all 12 non-customModels keys are identical
  - Hooks: 8 lifecycle events preserved
  - Plugins: `core@factory-plugins` preserved
  - Autonomy: `high` preserved
  - MissionModel: `custom:dlg/deepseek-v4-pro-0` preserved
  - Orchestrator: `custom:dlg/deepseek-v4-pro-0` preserved

- [x] Validate resulting JSON: exactly 4 custom models, all original top-level keys present.
  - 4 models present, 12 top-level keys preserved
  - File permissions: `0600`
  - File size: 6243 bytes

- [x] Confirm provider assignments: shopapikey → `anthropic`, giaoduc → `anthropic`, cockpit → `openai`.
  - Verified in live settings after installation

- [x] Confirm all new credentials use `${ENV_VAR}` references; no secret values emitted.
  - `ShopAPIKey · Fable 5`: `${HERMES_CUSTOM_SHOPAPIKEY_API_KEY}` ✅
  - `Giaoduc · Advance`: `${HERMES_CUSTOM_GIAODUC_API_KEY}` ✅
  - `Cockpit · GPT 5.6 Sol`: `${HERMES_CUSTOM_COCKPIT_API_KEY}` ✅

- [x] Run read-only `droid exec` smoke tests for each new model selector.
  - `custom:fable-5`: PASS, 5467ms, `LIVE_FABLE_OK`
  - `custom:Advance`: PASS, 7565ms, `LIVE_ADVANCE_OK`
  - `custom:gpt-5.6-sol`: PASS, 6160ms, `LIVE_COCKPIT_OK`

- [x] Run tool round-trip smoke test for each new model.
  - `custom:fable-5`: PASS, 2 turns, `EMPTY_DIR`, 6373ms
  - `custom:Advance`: PASS, 2 turns, `EMPTY_DIR`, 8689ms
  - `custom:gpt-5.6-sol`: PASS, 2 turns, `EMPTY_DIR`, 6168ms

- [x] Record cockpit streaming intermittency as operational caveat.
  - Documented in design.md and proposal.md

- [x] Verify rollback by confirming backup exists and documenting restore command.
  - Backup exists at `~/.factory/settings.json.pre-droid-provider-registration-20260821-173612`
  - Restore: `cp '/Users/androidteam/.factory/settings.json.pre-droid-provider-registration-20260821-173612' '/Users/androidteam/.factory/settings.json'`

- [x] Obtain explicit approval before applying candidate to live settings file.
  - User approved: "Approve — apply the 3 models now"

## Evidence Collected

| Provider | Droid selector | Live text | Live tool RT | Duration |
|---|---|---|---|---|
| shopapikey | `custom:fable-5` | ✅ `LIVE_FABLE_OK` | ✅ 2 turns, `EMPTY_DIR` | 6373ms |
| giaoduc | `custom:Advance` | ✅ `LIVE_ADVANCE_OK` | ✅ 2 turns, `EMPTY_DIR` | 8689ms |
| cockpit | `custom:gpt-5.6-sol` | ✅ `LIVE_COCKPIT_OK` | ✅ 2 turns, `EMPTY_DIR` | 6168ms |

## Not In Scope

- Default model change
- Mission/spec/worker role assignment
- Autonomy level change
- Existing model health diagnosis
- Credential rotation
- Explicit `id`/`index` fields
