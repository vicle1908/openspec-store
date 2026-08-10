## Why

The active MoA topology currently uses `cockpit:gpt-5.6-luna` as the aggregator for both the `default` and `deep` presets. The user wants role specialization: `shopapikey:fable-5` should aggregate the normal default route, while `giaoduc:Advance` should aggregate the deep route.

Official Hermes guidance confirms that the aggregator is the acting model: it receives the normal tool schema, writes the user-visible response, and continues the tool loop. The official example uses a dedicated aggregator over reference models. Research on MoA likewise supports choosing roles using both model quality and output diversity. Both requested direct models passed fresh HTTP 200 inference checks, so the requested reassignment is operationally available.

## What Changes

- Change the `default` aggregator from `cockpit:gpt-5.6-luna` to `shopapikey:fable-5`.
- Change the `deep` aggregator from `cockpit:gpt-5.6-luna` to `giaoduc:Advance`.
- Preserve `reasoning_effort: max` for both aggregators.
- Preserve all references, token caps, temperatures, fanout cadence, privacy filtering, degraded-reference behavior, context declarations, fallback order, and the `fast` preset.
- Synchronize the canonical MoA specification and maintained runbook.
- Record official documentation, academic research, provider health, and real MoA smoke evidence.

## Goals

- Make the live default and deep aggregators match the requested specialist assignment.
- Keep aggregator tool-call ownership and the existing MoA loop intact.
- Maintain a reproducible contract across config, spec, docs, and runtime evidence.

## Non-Goals

- Do not modify Hermes source code or provider endpoints.
- Do not change reference models or their reasoning levels.
- Do not change `fast`, fallback routes, context length, temperatures, token limits, privacy, or credentials.
- Do not rewrite archived historical changes or unrelated untracked OpenSpec work.

## Trade-offs

The official guide and MoA literature establish the aggregator role, not a quality ranking for these private provider models. The requested assignment is therefore treated as an explicit operator decision, not as a benchmark-proven superiority claim. Direct health checks establish availability only; they do not substitute for a task-quality benchmark.

## Rollback

Create and hash a local backup before mutation. Rollback restores the backup or sets only the two aggregator provider/model pairs back to cockpit Luna at max, then reruns structural checks, direct inference, and the real MoA tool-call smoke test.
