# Evidence Manifest: reconcile-canonical-cli-fail-closed-acceptance-v1

## Scope

Post-archive correction of two implementation gaps identified after the parent
(`standardize-agent-llm-environment-resolution-v2`) and successor
(`integrate-canonical-cli-projections-v1`) changes were archived at `9565197`.

## Implementation evidence

| Repo | Final SHA | Description |
|------|-----------|-------------|
| `tdt-core` | `75cd519` | Unchanged. Canonical `CLIProviderProfile`, `select_canonical_cli_provider()`, `project_canonical_cli_profile()` — no fix needed |
| `ai-harness-skills` | `02d0410` | Audited: `tdt_projection.py` already propagates `ProfileResolutionError` without catching it. No code change required |
| `ai-review` | `f1b6e0f` | Fail-closed fix (`26ed9f9`) + durable acceptance script (`26ed9f9`, `51b55b1`, `f1b6e0f`) |

## Fail-closed fix (`26ed9f9`)

**Before:** `resolve_canonical_overrides()` caught both `OSError` and
`ProfileResolutionError`, returning `{}` for either. This suppressed invalid
canonical configs that the spec requires to fail before process launch.

**After:** Only `OSError` is caught (missing TDT_HOME, absent config file).
`ProfileResolutionError` propagates, halting reviewer/adapter construction.

**ai-harness audit:** `ai_harness.providers.tdt_projection.get_canonical_overrides()`
calls `project_canonical_cli_profile()` without any try/except. Errors propagate
naturally. No change needed.

## Durable acceptance (`f1b6e0f`)

**Before:** Acceptance harness lived at `/private/tmp/tdt-phase6-acceptance-*`
(ephemeral, no version control).

**After:** `ai-review/scripts/verify_phase6_live_acceptance.py` — version-controlled,
structured error returns (no assert-based control flow), `finally` cleanup,
`_SENTINEL` machine-parseable output, post-finally cleanup verification.

## Verification (all from `f1b6e0f`)

| Check | Result |
|-------|--------|
| `py_compile` (3 files) | Pass |
| `ruff format --check` (6 files) | Pass |
| `ruff check` (6 files) | Pass |
| `mypy` (3 source files) | Pass, no issues |
| `pytest` (full suite) | 200 collected, all pass |
| Live acceptance | `LIVE_ACCEPTANCE_PASS`, EXIT=0 |
| Cleanup verification | `CLEANUP_OK` — no `/private/tmp/tdt-phase6-acceptance-*` after `finally` block |

## Latest live acceptance (from committed `f1b6e0f`)

```
provider=codex-native cli_provider=codex alias=codex-default
wire_model=gpt-5.6-sol effort=low
ai_review_elapsed=30.51s ai_harness_elapsed=7.49s
nonce=TDT_PHASE6_AI_REVIEW_18243507 credential_leak=none
LIVE_ACCEPTANCE_PASS
```
