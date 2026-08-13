# standardize-agent-llm-environment-resolution-v2

## What this change is

Corrective v2 of the agent LLM environment-resolution standardization. It aligns the TDT Python agent ecosystem with a provider/model/default YAML configuration pattern and the canonical six-layer resolver.

## Status

**Implementation and consumer wiring complete.** Phase 6 consumer work was completed in successor change `integrate-canonical-cli-projections-v1`; both changes remain unarchived until the final OpenSpec archive/sync operation.

## Completed evidence

| Artifact | SHA | Evidence | Status |
|---|---:|---|---|
| YAML provider/model/default schema parser + resolver | `21dcd5b` lineage, current tdt-core `75cd519` | 46 parser tests + resolver/contract tests | ✅ |
| Public canonical CLI selection/projection API | `75cd519` | `CanonicalCLISelection`, `select_canonical_cli_provider()`, `project_canonical_cli_profile()` | ✅ |
| Credential registry compatibility fix | `d63aa08` lineage | 12 focused tests | ✅ |
| tdt-core full suite | `75cd519` | 721 collected, 715 passed, 0 failed, 6 skipped | ✅ |
| ai-harness-skills runtime wiring | `02d0410` | 606 collected, 602 passed, 0 failed, 4 skipped | ✅ |
| ai-review runtime wiring | `bd27767` | 183 passed, 0 failed; Ruff + mypy + source compilation clean | ✅ |
| agent-core downstream | `e5fb49d` | 746/746 | ✅ |
| agent-harness downstream | `0ad49d2` | 343/343 | ✅ |
| agent-docs-sync downstream | `e0ba600` | 245/245 | ✅ |
| Live dual-consumer Codex acceptance | current acceptance harness | nonce `TDT_PHASE6_AI_REVIEW_4cbec67f`; ai-review 15.71s; ai-harness 7.76s; process status 0 | ✅ |

## Live acceptance artifact

Durable harness:

```text
~/Developer/tdt-cli-acceptance/verify_phase6_live.py
```

It writes an isolated new-schema YAML profile, resolves the profile through `tdt-core`, exercises the actual ai-review reviewer launch boundary and the actual ai-harness `CodexAdapter`, verifies the canonical wire model `gpt-5.6-sol`, reasoning effort `low`, nonce propagation, structured output, and credential non-disclosure. No credential values are persisted in the artifact.

## Registry decision

The registry is retained for legacy aliases, CLI capability metadata, and legacy environment-key lookup. New-schema `auth_env` remains provider-local. Registry removal is deferred until all legacy consumers migrate.

## Specs

The change reconciles the existing resolver/provider specs and adds:

- `cli-provider-profile-resolution`
- `provider-model-profile-resolution`

## Successor change

The cross-repository consumer wiring was isolated in `integrate-canonical-cli-projections-v1`, which is now implemented and ready for the normal archive/synchronize lifecycle.
