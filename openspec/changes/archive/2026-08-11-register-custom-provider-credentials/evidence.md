# Evidence: register-custom-provider-credentials

## Implementation

| Repo | Commit | Description |
|---|---|---|
| `tdt-core` (pre-integration) | `2897df7` | 3 credential entries added to `environment-key-registry.json` + 12 focused tests |
| `tdt-core` (integrated) | `d63aa08` | Cherry-pick of `2897df7` onto tdt-core main |

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
cd ~/Developer/tdt-core
uv run pytest tests/test_custom_provider_credentials.py -v
→ 12 passed
```

**Existing tdt-core config tests (unchanged):**

```
uv run pytest tests/test_config_primitives.py tests/test_llm_profile_v2.py -q
→ 60 passed
```

**Full tdt-core suite on integrated main (no PYTHONPATH override):**

```
cd ~/Developer/tdt-core
uv run pytest -q --junitxml=/tmp/tdt-core-main.xml
→ tests=618 passed=612 failures=0 errors=0 skipped=6
```

## Downstream validation — integrated, no PYTHONPATH

All downstream suites ran against the integrated tdt-core main (`d63aa08`) through the normal `pyproject.toml` editable dependency (`tdt-core = { path = "../tdt-core", editable = true }`). No `PYTHONPATH` override used.

```bash
# How downstream tests were run
cd ~/Developer/agent-core && uv run pytest -q --junitxml=/tmp/agent-core-integrated.xml
cd ~/Developer/agent-harness && uv run pytest -q --junitxml=/tmp/agent-harness-integrated.xml
cd ~/Developer/agent-docs-sync && uv run pytest -q --junitxml=/tmp/agent-docs-sync-integrated.xml
```

| Repo | SHA | Tests | Passed | Failed | Errors | Skipped |
|---|---|---|---|---|---|---|
| `tdt-core` | `d63aa08` | 618 | 612 | 0 | 0 | 6 |
| `agent-core` | `e5fb49d` | 746 | 746 | 0 | 0 | 0 |
| `agent-harness` | `0ad49d2` | 343 | 343 | 0 | 0 | 0 |
| `agent-docs-sync` | `e0ba600` | 245 | 245 | 0 | 0 | 0 |
| **Total** | | **1952** | **1946** | **0** | **0** | **6** |

### Consumer import verification

Each consumer resolves tdt-core from the integrated main:

```
agent-core:       /Users/androidteam/Developer/tdt-core/src/tdt_core/__init__.py
agent-harness:    /Users/androidteam/Developer/tdt-core/src/tdt_core/__init__.py
agent-docs-sync:  /Users/androidteam/Developer/tdt-core/src/tdt_core/__init__.py
```

All consumers point to the same integrated path. The editable install `tdt-core = { path = "../tdt-core", editable = true }` in each `pyproject.toml` resolves to `~/Developer/tdt-core`, which now contains `d63aa08`.

## What is NOT proven

1. The fix is pushed to origin — `d63aa08` is local only. Consumers that re-clone or re-install from origin will not have the fix until it is pushed.
2. Other `HERMES_CUSTOM_*` credential keys not in `config.yaml` — only the three needed keys are registered.
3. The YAML `providers/models/defaults` migration — that is a separate change.

## OpenSpec validation

- `openspec validate register-custom-provider-credentials` → valid
- `openspec validate --all --store openspec-store` → 360 passed, 0 failed

## Risk assessment

- **Blast radius**: cross-repository (tdt-core shared by 3 consumers)
- **Risk**: LOW — additive data, no code path change, no schema change
- **Backward compatible**: yes — existing entries unchanged, new entries are additive
- **Rollback**: remove the 3 entries from the JSON file, no code revert needed
