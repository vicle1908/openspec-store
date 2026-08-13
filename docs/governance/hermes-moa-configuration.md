# Hermes Mixture of Agents Configuration

## Purpose

This runbook defines the validated Mixture of Agents (MoA) setup for the active Hermes `default` profile. The canonical requirements are in `openspec/specs/hermes-moa-configuration/spec.md` after the associated OpenSpec change is archived.

Official reference: <https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents>

## Runtime Architecture

MoA is a virtual provider, not an HTTP endpoint. For each advisor refresh:

1. reference models receive trimmed user/assistant conversation text without tool schemas;
2. references run in parallel and return private advice;
3. Hermes appends the advice at the tail of the aggregator input;
4. the aggregator writes the assistant response and owns tool calls;
5. Hermes executes requested tools and returns results to the aggregator.

## Aggregator Role Research

The official Hermes guide defines the aggregator as the acting model: it receives private reference outputs, receives the normal Hermes tool schema, writes the user-visible response, and continues after tool results. The official benchmark example also uses a dedicated aggregator over references. The published MoA research recommends selecting roles using both demonstrated performance and output diversity, while noting that proposer and aggregator strengths can differ.

This profile therefore assigns `shopapikey:fable-5` to the normal default aggregation path and `giaoduc:Advance` to the deep aggregation path by explicit operator choice. The research supports separating roles, but no public benchmark was found for these private provider endpoints; direct inference proves availability, not comparative answer quality.

Sources:

- <https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents>
- <https://arxiv.org/html/2406.04692v1>

This preserves the main prompt-cache prefix. A reference failure does not by itself abort the turn: Hermes retains the degraded result and continues when the aggregator and remaining references are available.

## Default Model Selection

```yaml
model:
  provider: moa
  default: default

moa:
  default_preset: default
  privacy_filter: ''
```

`hermes moa list` may show `Active in config: (off)` when `moa.active_preset` is empty. That line describes the optional config-level active-preset override. It does **not** disable MoA when `model.provider` is `moa` and `model.default` selects a preset.

## Presets

| Preset | References | Aggregator | Limits and cadence | Use |
|---|---|---|---|---|
| `default` | `giaoduc:Advance` high; `cockpit:gpt-5.6-sol` high | `shopapikey:*** xhigh | refs 1000, output 8192, temp 0.6/0.4, `every_n:3` | normal/default route |
| `deep` | `shopapikey:fable-5` high; `cockpit:gpt-5.6-sol` high; `giaoduc:Advance` high | `giaoduc:Advance` max | refs 800, output 8192, temp 0.6/0.3, `per_iteration` | difficult architecture, review, and research |
| `fast` | `cockpit:gpt-5.6-sol` high | `shopapikey:fable-5` high | refs 300, output 4096, temp 0.6/0.4, `user_turn` | lower-latency work |

Every preset has `degraded_reference_policy: loud` and `enabled: true`. Reference calls add latency and provider usage. `user_turn` runs advisors once for the turn; `per_iteration` refreshes on every tool iteration; `every_n:3` refreshes on the first iteration and every third tool iteration. The slowest advisor usually determines fan-out latency.

## Specialist Role Separation

The current configuration intentionally separates cockpit's MoA slot model (`gpt-5.6-sol`) from its direct-provider default and fallback model (`gpt-5.6-luna`). MoA presets use `gpt-5.6-sol` as reasoning reference advisors. The direct cockpit provider default (`providers.cockpit.model`) and the fallback chain use `gpt-5.6-luna`. These are independent configuration surfaces; the cockpit model name in `providers.cockpit.model` does not constrain which model names appear in MoA presets, and vice versa.

## Selecting and Inspecting Presets

Persistent session selection:

```text
/model default --provider moa
/model deep --provider moa
/model fast --provider moa
```

One-shot default-preset use:

```text
/moa analyze this failure and propose the safest fix
```

Inspection:

```bash
hermes config get model
hermes config get moa
hermes moa list
hermes fallback list
```

## MoA Root Normalization

The `moa` configuration root contains exactly three keys:

1. `default_preset`
2. `privacy_filter`
3. `presets`

No legacy flat-level operational fields (`reference_models`, `aggregator`, `reference_temperature`, `aggregator_temperature`, `degraded_reference_policy`, `max_tokens`, `reference_max_tokens`, `fanout`, `enabled`) exist directly under `moa`. All tuning is owned by each preset entry under `moa.presets`.

## Context Windows

Context length belongs to real provider/model configuration, not MoA slots. The providers used by these presets declare `context_length: 1000000` at the provider level, and the used models resolve the same one-million-token window. Do not add `context_length` to reference or aggregator entries.

The cockpit provider retains both `gpt-5.6-sol` and `gpt-5.6-luna` in its model catalog. The provider default is `gpt-5.6-luna`. No active MoA slot uses `gpt-5.6-luna`.

Auxiliary operations do not run advisor fan-out. When the main route is MoA, Hermes unwraps the preset to its real aggregator for compression, title generation, vision, and similar auxiliary tasks.

## Privacy and Traces

`moa.privacy_filter` is configured as the literal empty string (`''`). This runbook does not claim display-mode filtering or any redaction guarantee; privacy behavior requires separate runtime verification.

`save_traces` is disabled in the validated setup. Never enable traces casually: they can retain full prompts, advisor outputs, aggregator inputs, usage, and cost metadata.

## Fallback Chain

The validated direct-provider chain is:

1. `shopapikey:fable-5` (`xhigh`)
2. `giaoduc:Advance` (`xhigh`)
3. `cockpit:gpt-5.6-luna` (`max`)

Do not add `moa:default` as the first fallback while it is also primary. Hermes identifies it as the same deployment and skips it before advancing.

## Validation

### Structural checks

```bash
hermes config check
hermes config get model
hermes config get moa
hermes moa list
hermes fallback list
```

Parse `~/.hermes/config.yaml` with `yaml.safe_load` and assert:

- primary is `moa:default`;
- presets are exactly `default`, `deep`, and `fast`;
- every cockpit MoA slot spells the model `gpt-5.6-sol`;
- no legacy flat `moa.reference_models` or `moa.aggregator` exists;
- `moa` root contains exactly `default_preset`, `privacy_filter`, and `presets`;
- `moa.privacy_filter` is the literal empty string;
- no MoA slot contains `context_length`;
- real providers and used models declare `1000000` context;
- fallback entries are distinct from the primary route.

### Provider inference

Resolve credentials from the provider's `key_env` name without printing either the name's value or authorization headers. Send a short non-streaming request to:

- cockpit / `gpt-5.6-sol`;
- cockpit / `gpt-5.6-luna`;
- shopapikey / `fable-5`;
- giaoduc / `Advance`.

Record only success/failure, provider/model, latency, and sanitized response shape.

### Real MoA tool-call smoke test

Start a fresh session explicitly on the preset and require a harmless terminal call:

```bash
hermes chat -Q --provider moa -m default \
  -q 'Use the terminal tool to run printf "MOA_TOOL_OK\\n". Then reply exactly MOA_SMOKE_OK.'
```

Success requires transcript/runtime evidence that the aggregator emitted the terminal tool call and continued after its result. Running a shell command outside the MoA session is not evidence.

## Rollback

Before mutation, keep a local timestamped backup under `~/.hermes/backups/` and verify its SHA-256. Do not commit the backup.

To switch away temporarily, use `/model` with a verified direct provider. To roll back persistent reconciliation, restore only the removed direct-model metadata or fallback entry if evidence shows they are required, or restore the local backup. Then rerun structural, direct-provider, and MoA smoke checks.

Secrets remain in `~/.hermes/.env`; settings remain in `~/.hermes/config.yaml`.
