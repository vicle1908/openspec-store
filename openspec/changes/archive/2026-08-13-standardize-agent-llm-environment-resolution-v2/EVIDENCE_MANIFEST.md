# Evidence Manifest: standardize-agent-llm-environment-resolution-v2

## Scope

Corrective v2 of the agent LLM environment-resolution standardization. The canonical YAML provider/model/default schema, six-layer resolver, per-CLI selection, and consumer projection are implemented across the TDT ecosystem.

Cross-repository consumer wiring was completed in successor change `integrate-canonical-cli-projections-v1`.

## Current implementation provenance

### tdt-core

| Commit | Description |
|---|---|
| `d63aa08` lineage | Registered custom provider credentials for legacy compatibility |
| `21dcd5b` lineage | New-schema YAML, resolver integration, strict Codex acceptance |
| `75cd519` | Public canonical CLI selection/projection API and final tdt-core implementation checkpoint |

Important public symbols on current main:

- `resolve_agent_profile()` — canonical six-layer resolution boundary
- `CanonicalCLISelection` — immutable secret-free selection result
- `select_canonical_cli_provider()` — independent per-CLI selection
- `project_canonical_cli_profile()` — validated CLI projection
- `CLIProviderProfile` — provider-neutral consumer profile

### ai-harness-skills

| Commit | Description |
|---|---|
| `0508b0e` | TDT projection bridge and editable tdt-core dependency |
| `5946814` | `build_runtime()` canonical per-adapter wiring |
| `02d0410` | StageId Python 3.14 runtime-import correction; final Phase 6A main |

### ai-review

| Commit | Description |
|---|---|
| `dec288f` | Initial canonical projection bridge and reviewer launch wiring |
| `10b470d` | Relaxed flaky concurrency timing assertion |
| `c60a706` | Canonical profile resolution at reviewer construction boundary |
| `0fb2b69` | Corrected source-level Python 3.14 exception syntax |
| `f31e73b` | Projected canonical reasoning effort into Claude/Codex reviewer commands |
| `bd27767` | Made local review-context fixtures deterministic and offline; final main |

## Test evidence

| Repository | Commit | Result |
|---|---:|---|
| tdt-core | `75cd519` | 721 collected, 715 passed, 0 failed, 6 skipped |
| ai-harness-skills | `02d0410` | 606 collected, 602 passed, 0 failed, 4 skipped |
| ai-review | `bd27767` | 183 passed, 0 failed |
| agent-core | `e5fb49d` | 746/746 |
| agent-harness | `0ad49d2` | 343/343 |
| agent-docs-sync | `e0ba600` | 245/245 |

ai-review gates:

```text
python3 -m py_compile src/ai_review/providers/tdt_projection.py \
  src/ai_review/reviewers/command.py \
  src/ai_review/review_flow/orchestrator.py \
  tests/test_review_context.py
uv run ruff check src/ai_review/providers/tdt_projection.py \
  src/ai_review/reviewers/command.py \
  src/ai_review/review_flow/orchestrator.py \
  tests/test_tdt_projection.py tests/test_review_context.py
uv run mypy src/ai_review/providers/tdt_projection.py \
  src/ai_review/reviewers/command.py \
  src/ai_review/review_flow/orchestrator.py
uv run pytest -q --tb=short --no-cov
→ all checks passed; 183 passed
```

The `test_review_context.py` fixture now explicitly disables live GitLab calls for local-only scenarios while preserving dedicated mocked tests for GitLab fallback and diff-version caching.

## Live dual-consumer acceptance

Durable harness:

```text
~/Developer/tdt-cli-acceptance/verify_phase6_live.py
```

Latest run:

| Item | Value |
|---|---|
| Canonical provider | `codex-native` (`cli_provider: codex`) |
| Canonical alias | `codex-default` |
| Wire model | `gpt-5.6-sol` |
| Reasoning effort | `low` |
| ai-review command | `codex exec --json --skip-git-repo-check --config model_reasoning_effort="low" --model gpt-5.6-sol` |
| ai-review result | completed; 15.71s; nonce verified |
| ai-harness result | process status 0; 7.76s; structured artifact nonce verified |
| Nonce | `TDT_PHASE6_AI_REVIEW_4cbec67f` |
| Credential leakage | none observed |
| Consumer SHAs | ai-review `bd27767`; ai-harness-skills `02d0410`; tdt-core `75cd519` |

## Registry decision

The registry remains authoritative for legacy aliases, CLI capability metadata, and legacy environment-key lookup. New-schema `auth_env` remains provider-local. Removal is deferred until all legacy consumers migrate.

## Archive status

Implementation and live acceptance are complete. The successor and v2 changes require final focused/full-store validation, archive, and canonical spec synchronization before closure.
