# Design: Factory Droid BYOK Provider Registration

## Source of Truth

`~/.factory/settings.json` — the sole configuration surface for Droid CLI personal settings.

## Change Strategy

**Additive merge.** Parse the existing JSON, preserve every top-level key and value, append three model entries to the `customModels` array. No keys removed, no keys added at top level, no nested values modified.

## Verified Provider Matrix

| Provider | `provider` | `model` | `baseUrl` | Auth env var |
|---|---|---|---|---|
| shopapikey | `anthropic` | `fable-5` | `https://api.phanmemvip.shop/v1` | `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` |
| giaoduc | `anthropic` | `Advance` | `https://api.giaoduc.online` | `HERMES_CUSTOM_GIAODUC_API_KEY` |
| cockpit | `openai` | `gpt-5.6-sol` | `http://localhost:51006/v1` | `HERMES_CUSTOM_COCKPIT_API_KEY` |

All three env vars confirmed available in fresh zsh shell. Droid resolves `${VAR}` references at parse time.

## Credential Strategy

New entries use `${HERM..._KEY}` environment-variable references. The existing model retains its hardcoded key unchanged — no silent rotation.

## What Is Preserved (Untouched)

| Setting | Current Value | Preserved |
|---|---|---|
| existing `customModels[0]` | `dlg/deepseek-v4-pro` via OmniRoute | ✅ |
| `sessionDefaultSettings` | `autonomyLevel: high` | ✅ |
| `missionModelSettings` | All pointing to `custom:dlg/deepseek-v4-pro-0` | ✅ |
| `missionOrchestratorModel` | `custom:dlg/deepseek-v4-pro-0` | ✅ |
| `hooks` | 8 lifecycle events (orca agent hooks) | ✅ |
| `enabledPlugins` | `core@factory-plugins` | ✅ |
| `compactionTokenLimit` | 400000 | ✅ |
| `ideAutoConnect` | true | ✅ |
| `showThinkingInMainView` | true | ✅ |
| `showTokenUsageIndicator` | true | ✅ |
| `includeCoAuthoredByDroid` | false | ✅ |
| `logoAnimation` | off | ✅ |

## What Is NOT Changed

- No default model change
- No mission/spec/worker role assignment
- No autonomy level change
- No hook modification
- No plugin change
- No explicit `id` or `index` fields (Droid auto-generates selectors like `custom:fable-5`)

## Backup and Rollback

1. Before application: backup created at `~/.factory/settings.json.pre-droid-provider-registration-20260821-173612`
2. Restore: `cp ~/.factory/settings.json.pre-droid-provider-registration-20260821-173612 ~/.factory/settings.json`
3. Existing backup: `~/.factory/settings.json.bak` (preserved as-is)

## Verification Plan

1. Build candidate from live settings (not sparse replacement)
2. Validate JSON structure: all keys preserved, 4 custom models
3. `droid exec --settings <candidate>` for each new model: basic text
4. `droid exec --settings <candidate>` for each new model: tool round-trip
5. Review candidate diff before approval
6. Apply only after explicit user approval
7. Re-run checks against live configuration after application

## Security Constraints

- Never print or commit resolved secret values
- Env-var references in settings are safe for version control
- Candidate file at `/tmp/` is ephemeral — not committed

## Known Issues (Not Introduced by This Change)

- Existing model (`dlg/deepseek-v4-pro`) timed out during complete-candidate test — pre-existing diagnostic issue
- Cockpit streaming: 1/3 timeout observed, 2/3 pass — marked intermittent
- Giaoduc prompt caching: `cache_read = 0` — not a blocker, just an observation
