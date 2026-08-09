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

This preserves the main prompt-cache prefix. A reference failure does not by itself abort the turn: Hermes retains the degraded result and continues when the aggregator and remaining references are available.

## Default Model Selection

```yaml
model:
  provider: moa
  default: default

moa:
  default_preset: default
  privacy_filter: display
```

`hermes moa list` may show `Active in config: (off)` when `moa.active_preset` is empty. That line describes the optional config-level active-preset override. It does **not** disable MoA when `model.provider` is `moa` and `model.default` selects a preset.

## Presets

| Preset | References | Aggregator | Limits and cadence | Use |
|---|---|---|---|---|
| `default` | `shopapikey:fable-5` high; `cockpit:gpt-5.6-sol` high | `cockpit:gpt-5.6-sol` xhigh | refs 600, output 4096, temp 0.6/0.4, `user_turn` | normal high-quality work |
| `deep` | `shopapikey:fable-5` xhigh; `cockpit:gpt-5.6-sol` xhigh; `giaoduc:Advance` high | `cockpit:gpt-5.6-sol` max | refs 800, output 8192, temp 0.6/0.3, `every_n:3` | difficult architecture, review, and research |
| `fast` | `cockpit:gpt-5.6-sol` medium | `shopapikey:fable-5` high | refs 300, output 4096, temp 0.6/0.4, `user_turn` | lower-latency work |

Reference calls add latency and provider usage. `user_turn` runs advisors once for the turn; `every_n:3` refreshes on the first iteration and every third tool iteration. The slowest advisor usually determines fan-out latency.

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

## Context Windows

Context length belongs to real provider/model configuration, not MoA slots. The providers used by these presets declare `context_length: 1000000`, and the used models resolve the same one-million-token window. Do not add `context_length` to reference or aggregator entries.

Auxiliary operations do not run advisor fan-out. When the main route is MoA, Hermes unwraps the preset to its real aggregator for compression, title generation, vision, and similar auxiliary tasks.

## Privacy and Traces

`privacy_filter: display` redacts emails, formatted phone numbers, and centrally recognized credential shapes from user-visible reference blocks and saved traces. The aggregator still receives raw advisor text to preserve quality.

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
- no MoA slot contains `context_length`;
- real providers and used models declare `1000000` context;
- fallback entries are distinct from the primary route.

### Provider inference

Resolve credentials from the provider's `key_env` name without printing either the name's value or authorization headers. Send a short non-streaming request to:

- cockpit / `gpt-5.6-sol`;
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
