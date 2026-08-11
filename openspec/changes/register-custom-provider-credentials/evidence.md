# Evidence: register-custom-provider-credentials

## Implementation

| Repo | Commit | Description |
|---|---|---|
| `tdt-core` (worktree) | `2897df7` | 3 credential entries added to `environment-key-registry.json` + 12 focused tests |

### Registry changes

| Entry added | `canonical_key` | `provider` | `secret` |
|---|---|---|---|
| `credential.giaoduc.api_key` | `HERMES_CUSTOM_GIAODUC_API_KEY` | `giaoduc` | `true` |
| `credential.shopapikey.api_key` | `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` | `shopapikey` | `true` |
| `credential.cockpit.api_key` | `HERMES_CUSTOM_COCKPIT_API_KEY` | `cockpit` | `true` |

- Registry: 17 → 20 entries
- Format: minified JSON (matches main branch convention)
- Existing entries: all unchanged

### Test evidence

**New focused tests (12, all pass):**

```
cd ~/Developer/tdt-core-register-credentials
uv run pytest tests/test_custom_provider_credentials.py -v
→ 12 passed
```

**Existing tdt-core config tests (unchanged):**

```
uv run pytest tests/test_config_primitives.py tests/test_llm_profile_v2.py -q
→ 60 passed
```

**Full tdt-core suite (JUnit XML):**

```
uv run pytest -q --junitxml=/tmp/tdt-core-reg.xml
→ tests=618 passed=612 failures=0 errors=0 skipped=6
```

**Import verification (all 6 credential entries):**

```
tdt_core from: /Users/androidteam/Developer/tdt-core-register-credentials/src/tdt_core/__init__.py
HERMES_CUSTOM_GIAODUC_API_KEY -> provider=giaoduc, secret=True
HERMES_CUSTOM_SHOPAPIKEY_API_KEY -> provider=shopapikey, secret=True
HERMES_CUSTOM_COCKPIT_API_KEY -> provider=cockpit, secret=True
ANTHROPIC_API_KEY -> provider=anthropic, secret=True
OPENAI_API_KEY -> provider=openai-chat, secret=True
MODEL_API_KEY -> provider=None, secret=True
```

## Downstream validation

All downstream suites were run against the **isolated tdt-core worktree** (`~/Developer/tdt-core-register-credentials/src`) via `PYTHONPATH` override. This proves the patch works but does NOT mean it is integrated into the normal `../tdt-core` editable dependency.

```bash
# How downstream tests were run
PYTHONPATH=~/Developer/tdt-core-register-credentials/src uv run pytest -q --junitxml=<path>
```

| Repo | SHA | Tests | Passed | Failed | Errors | Skipped |
|---|---|---|---|---|---|---|
| `tdt-core` (full) | `2897df7` | 618 | 612 | 0 | 0 | 6 |
| `agent-core` | `e5fb49d` | 746 | 746 | 0 | 0 | 0 |
| `agent-harness` | `0ad49d2` | 343 | 343 | 0 | 0 | 0 |
| `agent-docs-sync` | `e0ba600` | 245 | 245 | 0 | 0 | 0 |

**Total: 1952 tests, 1946 passed, 0 failures, 0 errors, 6 skipped (all in tdt-core scheduler tests)**

### Downstream import verification

Each consumer was verified to load the fixed tdt-core from the isolated worktree before running tests:

```
agent-core:       tdt_core from: .../tdt-core-register-credentials/src/tdt_core/__init__.py
agent-harness:    tdt_core from: .../tdt-core-register-credentials/src/tdt_core/__init__.py
agent-docs-sync:  tdt_core from: .../tdt-core-register-credentials/src/tdt_core/__init__.py
```

## What is NOT proven

1. The fix is integrated into `tdt-core/main` — it is on an isolated branch (`2897df7`) only.
2. Downstream consumers pass without `PYTHONPATH` override — not tested after main integration.
3. Other credential keys (e.g. `HERMES_CUSTOM_*` not currently in `config.yaml`) are not registered — only the three needed keys.
4. The YAML `providers/models/defaults` migration is implemented — that is a separate change.

## OpenSpec validation

- `openspec validate register-custom-provider-credentials` → valid
- `openspec validate --all --store openspec-store` → 360 passed, 0 failed

## Risk assessment

- **Blast radius**: cross-repository (tdt-core shared by 3 consumers)
- **Risk**: LOW — additive data, no code path change, no schema change
- **Backward compatible**: yes — existing entries unchanged, new entries are additive
- **Rollback**: remove the 3 entries from the JSON file, no code revert needed
