# Design: agent-docs-sync-config-and-report-hardening

## 1. Config precedence test strategy

The 4-layer precedence:
1. `DOCS_SYNC_*` environment variables
2. `{repo}/config.yaml` (per-repo overrides)
3. `~/.tdt/config.yaml` via `load_settings()` (global TDT defaults)
4. Code defaults in `DocsSyncConfig`

### Test matrix

| Test | Config state | Expected |
|------|-------------|----------|
| test_env_var_overrides_repo_config | DOCS_SYNC_MODEL=x, config.yaml model=y | model=x |
| test_repo_config_overrides_tdt_global | config.yaml model=x, TDT model=y | model=x |
| test_tdt_global_overrides_code_default | TDT model=x, no repo config | model=x |
| test_code_default_used_when_all_absent | Nothing configured | default model |
| test_alternate_tdt_home | TDT_HOME=/tmp/alt | Uses alt config |
| test_missing_global_config_graceful | TDT_HOME missing | Falls back to code defaults |
| test_malformed_yaml_raises | config.yaml invalid | Raises error |
| test_env_var_int_coercion | DOCS_SYNC_MAX_ITERATIONS=10 | max_iterations=10 |
| test_env_var_float_coercion | DOCS_SYNC_TIMEOUT_SECONDS=30.5 | timeout_seconds=30.5 |
| test_invalid_env_var_type | DOCS_SYNC_MAX_ITERATIONS=abc | Raises ValueError |
| test_with_overrides_creates_copy | config.with_overrides(model=x) | Original unchanged |

## 2. Report semantics test strategy

Exit code mapping:
- exit 0: compliant AND execution succeeded AND generation completed
- exit 1: noncompliant OR generation failure
- exit 2: execution failure

### Test matrix

| Test | Report state | Expected |
|------|-------------|----------|
| test_generation_failure_with_gaps | generation_error + gaps | exit 1 |
| test_generation_timeout | generation_reason=timeout | exit 1 |
| test_generation_max_iterations | generation_reason=max_iterations | exit 1 |
| test_provider_error | generation_provider_error set | exit 1 |
| test_generation_completed_false | generation_completed=False | exit 1 |
| test_execution_failure | execution_succeeded=False | exit 2 |
| test_compliant_run | documentation_compliant=True | exit 0 |
| test_generation_failure_masks_compliance | generation_error + compliant=True | exit 1 |

## 3. Cleanup strategy

- `.scratch/e2e_test.py`: Inspect for valid tests, move to tests/ if valid
- `doc-sync/SKILL.md`: Remove placeholder stub (295 bytes of boilerplate)
