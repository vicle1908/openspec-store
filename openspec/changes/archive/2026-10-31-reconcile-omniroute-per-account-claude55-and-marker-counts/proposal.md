# Proposal

## Why

End-to-end verification and `/opsx:verify` after commit `e34b62f3` identified two post-archive evolutions in the live OmniRoute v3.8.52 deployment:
1. **Per-account upstream Claude 5.5 migration on connection `38782750-7a60-46d4-ae3f-e8c13cda296b` (`vicgnome19096@gmail.com`)**: In `key_value` (`namespace = 'syncedAvailableModels'`), upstream Google Cloud Code migrated account `38782750-7a60-46d4-ae3f-e8c13cda296b` from `claude-opus-4-6-thinking` / `claude-sonnet-4-6` (64K output limit) to `claude-opus-5-5-high` / `claude-sonnet-5-5-high` (128K output limit) while the remaining 14 active `agy` accounts continue advertising `claude-opus-4-6-thinking` and `claude-sonnet-4-6`. Calling `claude-opus-4-6-thinking` or `claude-sonnet-4-6` on `38782750-7a60-46d4-ae3f-e8c13cda296b` returns a synthetic HTTP 200 deprecation message (`"Claude Opus 4.6 is no longer available. Please switch to Claude Opus 5.5."`), whereas calling `agy/claude-opus-5-5-high` and `agy/claude-sonnet-5-5-high` on `38782750-7a60-46d4-ae3f-e8c13cda296b` returns genuine Claude 5.5 completions (`HTTP 200`, `"210"` / `"391"` / `"437"`).
2. **Compatibility script rule and marker counts after OpenAI Responses RTK `skipFilters` additions (`R44`–`R48`)**: `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` now contains **`3` non-chunk patches (`N1`–`N3`) + `48` chunk/route replacement rules (`R1`–`R48`) = `51` total modifications**, guarded by **`3` `requiredNonChunkMarkers` + `57` `requiredMarkers` across `21` server chunk files = `60` fail-closed marker assertions across `24` compiled files**.

## What Changes

- **Align `claude-opus-5.5` and `claude-sonnet-5.5` combo steps with per-account `syncedAvailableModels`**:
  - Configure step `[1]` (`38782750-7a60-46d4-ae3f-e8c13cda296b` / `vicgnome19096@gmail.com`) to target `agy/claude-opus-5-5-high` in `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) and `agy/claude-sonnet-5-5-high` in `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`) while keeping the remaining 14 active `agy` accounts on `agy/claude-opus-4-6-thinking` and `agy/claude-sonnet-4-6` (`0` `combo-ref` steps), eliminating 100% of synthetic HTTP 200 deprecation messages.
- **Reconcile `51` modifications (`3` non-chunk + `48` chunk/route rules) and `60` fail-closed markers (`3` non-chunk + `57` chunk across `21` server chunk files / `24` compiled files)**:
  - Update `omniroute-runtime-customization`, `omniroute-compression-and-routing`, and `omniroute-agent-cli-routing` specifications, `/Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh:6,15`, and `/Users/androidteam/Developer/wiki/entities/omniroute.md:44,67,73`.

## Capabilities

### New Capabilities

*(None)*

### Modified Capabilities
- `omniroute-runtime-customization`: Update compatibility ledger counts in `Compatibility Behavior and Patch Retirement Gates` to `3` non-chunk patches and `48` chunk/route replacements (`51` modifications) guarded by `60` fail-closed markers (`3` non-chunk and `57` chunk markers across `24` compiled files).
- `omniroute-compression-and-routing`: Update `Multi-Account Claude Opus and Sonnet Combo Pooling across Antigravity Accounts` so each of the 15 active `agy` steps targets its connection's `syncedAvailableModels` identifier (`agy/claude-opus-5-5-high` / `agy/claude-sonnet-5-5-high` on migrated connection `38782750-7a60-46d4-ae3f-e8c13cda296b` and `4-6` on the remaining 14 active connections).
- `omniroute-agent-cli-routing`: Update `Muse Code entrypoint compatibility` (`48` non-Muse runtime rules across `21` server chunk files, `57` chunk markers / `60` total markers across `24` compiled files) and `15-Account Antigravity Auto Pools for claude-opus-5.5 and claude-sonnet-5.5`.

## Impact

- **OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Delta specs for `omniroute-runtime-customization`, `omniroute-compression-and-routing`, and `omniroute-agent-cli-routing`.
- **OmniRoute Live SQLite (`omniroute-data` `/app/data/storage.sqlite`)**: Step `[1]` (`38782750-7a60-46d4-ae3f-e8c13cda296b`) in `claude-opus-5.5` and `claude-sonnet-5.5`.
- **OmniRoute Helper & Wiki Documentation**: `/Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh:6,15` and `/Users/androidteam/Developer/wiki/entities/omniroute.md:44,67,73`.
