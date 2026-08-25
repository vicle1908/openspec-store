# Migrate missed CLI surfaces to phanmemvip (opencode, droid, cline)

## Why

The giaoduc retirement (`replace-giaoduc-with-phanmemvip`) and the
`Claude-Fable` canonicalization (`canonicalize-claude-fable-and-responses`)
missed three consumer CLI surfaces: **opencode** (default model AND
`small_model` are still `giaoduc/Advance`; shopapikey model still `fable-5`;
no phanmemvip provider), **droid/Factory** (`customModels` still contains
`Advance` @ giaoduc.online and stale `fable-5`), and **cline**
(`lastUsedProvider: giaoduc` with a stored giaoduc provider entry). A
re-audit confirmed goose, pi, omp, and prime-agent are fully migrated (zero
giaoduc/Advance/fable-5 residue). This change completes the migration for the
missed surfaces and codifies the expected end-state for all seven consumer
CLIs in a new capability.

## What Changes

- **opencode** (`~/.config/opencode/opencode.json`): remove the `giaoduc`
  provider; add a `phanmemvip` provider (`baseURL:
  https://api.phanmemvip.shop/v1`, `api: "responses"`, key
  `HERMES_CUSTOM_PHANMEMVIP_API_KEY`, model `gpt-5.6-sol`); rename the
  shopapikey model `fable-5` → `Claude-Fable`; set `model` and `small_model`
  from `giaoduc/Advance` to `phanmemvip/gpt-5.6-sol`.
- **droid** (`~/.factory/settings.json`): remove the `Advance` custom model;
  rename the `fable-5` custom model to `Claude-Fable` (keeps its `anthropic`
  provider type against `https://api.phanmemvip.shop` — the correct transport
  for Claude models); add a `gpt-5.6-sol` custom model (`openai` provider
  type, `https://api.phanmemvip.shop/v1`, Responses).
- **cline**: re-register providers via `cline auth` — `openai-native` →
  phanmemvip `gpt-5.6-sol` (Responses); remove the stored giaoduc provider
  entry from `~/.cline/data/settings/providers.json`.
- **goose, pi, omp, prime-agent**: no config changes (verified zero residue);
  their expected state is codified in the new capability.
- **New capability** `coding-cli-provider-registry`: the expected
  provider/model/transport state for all seven consumer CLIs — giaoduc absent,
  phanmemvip present via the OpenAI Responses API, shopapikey Claude model
  named `Claude-Fable`.

Non-goals:

- No changes to omp, goose, pi, or prime-agent configs (already correct).
- No changes to droid mission models (`claude-opus-5` built-ins).
- No OmniRoute repair; no phanmemvip Claude Code launcher.

## Capabilities

### New Capabilities
- `coding-cli-provider-registry`: expected provider registration state for the
  seven consumer coding CLIs (omp, goose, pi, prime-agent, opencode, droid,
  cline) after the giaoduc retirement.

### Modified Capabilities
- None. (`omp-provider-routing` already carries the phanmemvip Responses-only
  transport requirement; the new capability covers the remaining CLIs.)

## Impact

- **Config files**: `~/.config/opencode/opencode.json`,
  `~/.factory/settings.json`, `~/.cline/data/settings/providers.json`.
- **OpenSpec**: 1 new capability spec.
- **Risk**: opencode `api: "responses"` support is verified by smoke test;
  droid's anthropic-type Claude-Fable entry keeps the proven Messages
  transport. All three surfaces have timestamped backups.
