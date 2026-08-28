# Design: OmniRoute `sh/*` Model Routing Across Agent CLIs

## Principles

1. **Official mechanisms only.** Use each CLI's documented provider/model configuration; do not patch framework source or invent adapters.
2. **Classification before mutation.** Installed does not imply configurable, and a successful CLI call does not prove arbitrary provider support.
3. **Registration is not default selection.** Adding a provider/model catalog entry SHALL NOT change an existing default unless separately approved.
4. **Clean-break inference namespace.** Active OmniRoute inference routes SHALL use live `sh/*` IDs. Retired `dlg/*` IDs SHALL NOT be added to target configs.
5. **Credential indirection.** Configs SHALL reference `OMNIROUTE_API_KEY` through the CLI's supported environment mechanism; literal credential values are prohibited.
6. **One writer per file.** Each configuration is backed up, atomically replaced, parsed, and smoke-tested before the next file.

## Live OmniRoute baseline

At planning time (2026-08-28T15:00:34+07:00), `GET http://localhost:20128/v1/models` returned 966 total models, including exactly 14 unique `sh/*` IDs (sorted, deduplicated):

```text
sh/Claude-Fable
sh/Claude-Opus
sh/Claude-Sonnet
sh/codex
sh/codex-5.6
sh/codex-x
sh/default
sh/gpt-4o
sh/gpt-5.4
sh/gpt-5.5
sh/gpt-5.6
sh/gpt-5.6-sol
sh/o3
sh/o4-mini
```

The registry is evidence for model availability only. Each consumer still needs protocol and provider compatibility verification.

## Canonical initial role map

```yaml
primary_coding: sh/codex
small_default: sh/default
claude_compatible: sh/Claude-Fable
reasoning: sh/o3
fallback: sh/codex
```

The role map is a proposed catalog policy. It SHALL NOT override a CLI's current default without a separate approval row.

## Configuration surfaces and decision rules

| Surface | Required inspection | Mutation allowed only if |
|---|---|---|
| Codex | `model_providers`, `base_url`, `wire_api`, `env_key`/equivalent, Responses compatibility | official provider entry maps to OmniRoute and real read-only call passes |
| OpenCode | provider ID, base URL, API-key env reference, model IDs, API dialect | native provider schema accepts endpoint and `sh/*` call passes |
| Pi | provider/model catalog, API mode, env template, role selectors | resolver and real call accept the chosen protocol/model |
| Droid | `customModels`, `apiKey` `${VAR}` interpolation, provider type, exact model ID | official BYOK schema and real call pass |
| Goose | provider name, base URL, API-key environment path, model ID | official provider supports an OpenAI-compatible dialect |
| Cline | provider settings/profile, base URL, API key environment support, model ID | official provider supports endpoint without literal secret |
| AGY/Qoder | official custom-provider documentation and local config shape | documented mechanism exists and sentinel passes |
| Claude Code | API mode and provider-protocol compatibility | exact protocol compatibility is proven; otherwise classify only |
| Copilot | supported model/provider catalog and custom endpoint policy | official mechanism supports the endpoint; otherwise no mutation |
| Cursor/Auggie | login/auth state and provider customization support | user authentication and documented mechanism exist; otherwise no mutation |

## Prime Agent overlap

`add-omniroute-prime-agent-provider` is a separate narrow change with only metadata currently visible. This broader change treats Prime Agent as separate-change-owned and pending reconciliation, and excludes it from apply ownership. The narrow change SHALL NOT be deleted, archived, or edited by this change without explicit reconciliation approval.

## Verification contract

For each mutated CLI:

1. capture a mode-600 backup and hash;
2. write atomically using the CLI's official config surface;
3. parse/lint the resulting file;
4. run one isolated, read-only, one-turn sentinel in a disposable directory;
5. require exact sentinel output, exit 0, and no authentication/reconnect error;
6. verify the selected model route and endpoint without printing credentials;
7. roll back that file immediately if any gate fails;
8. record evidence with values omitted.

Final verification SHALL include a live-literal credential sweep, preservation of existing providers/defaults, exact `sh/*` namespace checks, and an OpenSpec `detect_changes` gate before commit.

## Rollback

Rollback is per file, not global: restore the mode-600 backup atomically, parse-check, and rerun the baseline sentinel for that CLI. A failed CLI SHALL NOT block verification of independent CLIs, but it SHALL remain unconfigured and be reported as a blocker.

## Out of scope

- provider-side credential rotation;
- framework source changes;
- arbitrary custom endpoints for unsupported CLIs;
- changes to Kilo or Prime Agent baselines;
- changing defaults without explicit per-CLI approval;
- modifications to unrelated OpenSpec changes or canonical specs.

## Evidence-backed support matrix (2026-08-28)

Captured from read-only, redacted inspections with mode and hash baselines. This table supersedes the initial classification in proposal.md.

| CLI | Config surface | OmniRoute state | Credential form | Classification | Apply action |
|---|---|---|---|---|---|
| Kilo | ~/.config/kilo/kilo.jsonc | default omniroute/sh/codex; 6 sh models; 0 dlg | env-backed | configured baseline | verify only |
| Pi | ~/.pi/agent/models.json | omniroute provider; 2 sh + 4 ollamacloud models; default shopapikey/Claude-Fable | ${ENV} interpolation | configured | verify only |
| OMP | ~/.omp/agent/models.yml | omniroute provider; full 14 sh catalog | env name OMNIROUTE_API_KEY | configured | verify only |
| grok | ~/.grok-code/config.toml | omniroute provider type=codex; 2 sh models; default sh-claude-fable via shopapikey | literal api_key (pre-existing finding, len=35) | configured with finding | verify only; document literal key as follow-up |
| Goose | ~/.config/goose/custom_providers/custom_omniroute.json + config.yaml | 2 sh + 4 dlg + 2 ollamacloud; selected model gpt-5.6 matches no catalog name (catalog declares sh/gpt-5.6); active_provider=codex | api_key_env OMNIROUTE_API_KEY | supported; dlg retirement needed | remove 4 dlg/* entries; add sh/codex + sh/default; align selected model to sh/codex |
| OpenCode | ~/.config/opencode/opencode.json | no omniroute provider; defaults phanmemvip/gpt-5.6 | n/a | supported candidate | add provider with {env:OMNIROUTE_API_KEY} and 4 sh models |
| Codex | ~/.codex | only cockpit local-access provider; model gpt-5.6 | env_key indirection supported | supported candidate | add model_providers.omniroute (responses wire_api, env_key OMNIROUTE_API_KEY) |
| grok | ~/.grok/config.toml | no omniroute provider; default shopapikey-claude-fable | env_key indirection supported | supported candidate | add model_providers.omniroute plus one model alias |
| Droid | ~/.factory/settings.json | 3 customModels; none omniroute | ${VAR} interpolation supported | supported candidate | add one omniroute customModel (sh/codex) |
| Cline | ~/.cline/data/settings/providers.json | phanmemvip entry with literal apiKey; no env field found in schema | literal | blocked | no mutation; document |
| Copilot | ~/.config/github-copilot/ | auth.db only; no custom provider surface | vendor auth | blocked | no mutation |
| Cursor Agent | ~/.cursor/cli-config.json | no provider surface; login required | vendor auth | unconfigured | no mutation |
| Auggie | ~/.augment/.auggie.json | session metadata only | vendor auth | unconfigured | no mutation |
| AGY | ~/.antigravity/ | IDE extensions only; no agent config | n/a | unsupported | no mutation |
| Qoder | ~/.qoder/settings.json | vendor model qmodel_38max only | vendor | unsupported | no mutation |
| Claude Code | ~/.claude/settings.json | apiKeyHelper + launcher wrappers | wrapper-owned | protocol-dependent | no mutation |
| Prime Agent | ~/.prime/agent/ | separate change add-omniroute-prime-agent-provider owns it | n/a | separate-change-owned | no mutation |

Approved apply set (registration only, no default changes): Goose, OpenCode, Codex, grok, Droid.
Verify-only set: Kilo, Pi, OMP, grok.
Unchanged set: Cline, Copilot, Cursor Agent, Auggie, AGY, Qoder, Claude Code, Prime Agent.

Pre-existing security findings to document (not fixed by this change): grok literal api_key; cline literal apiKey; goose/opencode/omp config files mode 644.
