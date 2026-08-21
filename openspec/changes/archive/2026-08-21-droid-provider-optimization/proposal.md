# Proposal: Factory Droid BYOK Provider Registration

## Why

The current Droid CLI configuration routes all sessions through a single custom model (`dlg/deepseek-v4-pro` via OmniRoute at `localhost:20128/v1`). This creates a single point of failure. We have three additional provider endpoints available that have been independently verified through both direct API calls and Droid CLI integration. This change registers them as custom models.

## What Changes

Add three custom models to `~/.factory/settings.json`. The existing model entry is preserved unchanged. All unrelated settings are preserved.

### Verified Provider Mapping

| Provider | Droid `provider` | `model` field | Base URL | Auth env var |
|---|---|---|---|---|
| shopapikey | `anthropic` | `fable-5` | `https://api.phanmemvip.shop/v1` | `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` |
| giaoduc | `anthropic` | `Advance` | `https://api.giaoduc.online` | `HERMES_CUSTOM_GIAODUC_API_KEY` |
| cockpit | `openai` | `gpt-5.6-sol` | `http://localhost:51006/v1` | `HERMES_CUSTOM_COCKPIT_API_KEY` |

### Evidence

| Test | shopapikey | giaoduc | cockpit |
|---|---|---|---|
| Direct HTTP text (512 tokens) | ✅ `end_turn` 12.9s | ✅ `end_turn` 10.8s | ✅ completed 5.8s |
| Direct HTTP tools | ✅ `tool_use` | ✅ `tool_use` | ✅ `function_call` |
| Direct HTTP streaming | ✅ SSE | ✅ SSE | ✅ event stream |
| Droid sparse text (isolated) | ✅ `SHOP_TEXT_OK` | ✅ `GIAODUC_TEXT_OK` | ✅ `COCKPIT_TEXT_OK` |
| Droid tool round-trip (isolated) | ✅ 7 turns | ✅ 2 turns | ✅ 2 turns |
| Droid env-var credential | ✅ resolved | ✅ resolved | ✅ resolved |
| Droid streaming (isolated) | ✅ 5920ms | ✅ 5347ms | ⚠️ intermittent (1/3 timeout) |

### What Is Preserved (Untouched)

- Existing model entry (`dlg/deepseek-v4-pro`)
- `sessionDefaultSettings` (autonomy level remains `high`)
- `missionModelSettings` (all pointing to existing model)
- `missionOrchestratorModel`
- `hooks` (8 lifecycle events)
- `enabledPlugins`
- `compactionTokenLimit`
- All other settings

### What Is NOT Changed

- No default model change
- No mission/spec/worker role assignment
- No autonomy level change
- No explicit `id` or `index` fields (Droid auto-generates selectors)
- No credential rotation for existing model

## Acceptance Criteria

1. All 3 new models appear in `droid` model selector
2. Each model responds to a basic text prompt via `droid exec`
3. Each model executes a tool call via `droid exec`
4. Existing model selector unchanged (health not established by this change)
5. Structural comparison: non-customModels keys identical to backup, original model preserved, model count 1→4

## Known Issues (Not Introduced by This Change)

- Existing model timed out during complete-candidate test — pre-existing
- Cockpit streaming: 1/3 timeout observed — intermittent
- Giaoduc prompt caching: `cache_read = 0` — observation only

## Rollback

Restore `~/.factory/settings.json` from `~/.factory/settings.json.pre-droid-provider-registration-20260821-173612` backup.
