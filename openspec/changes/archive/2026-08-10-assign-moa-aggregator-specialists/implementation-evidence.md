# Implementation Evidence: Specialist MoA Aggregator Assignment

Evidence captured on 2026-08-10. Credentials and authorization headers are excluded.

## Research

- Official Hermes MoA guide: <https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents>
  - Hermes runs references first without tools; the aggregator receives private reference context, owns the normal tool schema, writes the actual response, and continues after tool results.
  - The official benchmark example uses a dedicated aggregator over references.
- Wang et al., *Mixture-of-Agents Enhances Large Language Model Capabilities*: <https://arxiv.org/html/2406.04692v1>
  - Role selection should consider model performance and output diversity.
  - Proposer and aggregator strengths can differ; direct provider health is not a quality benchmark.

## Pre-Change State

- Primary route: `model.provider: moa`, `model.default: default`.
- `default` aggregator: `cockpit:gpt-5.6-luna`, `max`, temperature 0.4, output cap 4096.
- `deep` aggregator: `cockpit:gpt-5.6-luna`, `max`, temperature 0.3, output cap 8192.
- `fast` aggregator: `shopapikey:fable-5`, `high`; unchanged by this change.
- Store had unrelated untracked changes under `consolidate-ecosystem-shared-code` and `ecosystem-standardization`; neither was edited or staged.

## Applied State

Only these aggregator assignments changed:

- `default.aggregator`: `cockpit:gpt-5.6-luna` -> `shopapikey:fable-5`, effort remains `max`.
- `deep.aggregator`: `cockpit:gpt-5.6-luna` -> `giaoduc:Advance`, effort remains `max`.

References, temperatures, token caps, fanout, privacy, degraded-reference policy, contexts, fallback order, and `fast` remain unchanged. The `moa` section remained a YAML mapping after mutation.

## Provider Health

Fresh direct non-streaming checks passed before mutation and again after mutation:

| Provider/model | Post-change result | HTTP | Post-change latency |
|---|---|---:|---:|
| shopapikey / `fable-5` | PASS | 200 | 2054 ms |
| giaoduc / `Advance` | PASS | 200 | 1927 ms |
| cockpit / `gpt-5.6-luna` | PASS | 200 | 1454 ms |

These checks establish availability and response shape, not comparative answer quality.

## Real MoA Smoke Tests

### Default / fable aggregator

Session: `@session:default/20260810_115127_7994ba`

- Assistant emitted a real terminal call.
- Tool returned `MOA_DEFAULT_FABLE_OK`, exit code 0.
- Aggregator continued with `MOA_DEFAULT_FABLE_SMOKE_OK`.

### Deep / Advance aggregator

Session: `@session:default/20260810_115258_77d580`

- Assistant emitted a real terminal call after all three references ran.
- Tool returned `MOA_DEEP_ADVANCE_OK`, exit code 0.
- Aggregator continued with `MOA_DEEP_ADVANCE_SMOKE_OK`.

## Rollback

Backup created before mutation:
`/Users/androidteam/.hermes/backups/config-before-aggregator-specialists-20260810-114828.yaml`

The backup SHA-256 matched the source at creation and remains outside Git. Restore it atomically, or set only the two aggregator provider/model pairs back to cockpit Luna at max, then rerun structural, provider, and smoke validation.
