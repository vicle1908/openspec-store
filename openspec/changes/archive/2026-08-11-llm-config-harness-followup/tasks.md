# Tasks: llm-config-harness-followup

Corrective change for the unimplemented Phase 4 of `llm-config-standardization`.
Supersedes the archived change's Phase 4 tasks. Does NOT modify the archived change.

## Phase 1: tdt-core — Loader primitives

- [x] 1.1 Add `load_config_mapping(path: Path) -> dict[str, Any]` to `tdt_core/config_loader.py` — secure, uncached YAML-to-mapping loader; empty/missing file → `{}`, malformed YAML → `ConfigError`, non-mapping → `ConfigError`; calls `_reject_secrets()` for secret enforcement; add to `__all__`
- [x] 1.2 Add `load_agent_overlay(agent_name: str, *, config_path: Path | None = None, allowed_keys: Collection[str] | None = None) -> dict` to `tdt_core/config_loader.py` — reads ONLY the agent YAML file via `load_config_mapping()` (never global config); validates top-level keys against `allowed_keys` (default: `{"model", "runtime"}`); missing file → `{}`; add to `__all__`
- [x] 1.3 Add `allowed_overlay_keys: Collection[str] | None = None` parameter to `load_agent_config()` — changes validation policy only; extra permitted keys are accepted by overlay validation but NOT merged into global config result; default `None` → `{"model", "runtime"}` (strict); cache key includes `frozenset(allowed_overlay_keys)`
- [x] 1.4 Write unit tests for `load_config_mapping()` — test: valid mapping, empty file, missing file, malformed YAML, non-mapping YAML, secret rejection (token/password/api_key/dsn), `api_key_env` under `providers.<name>` accepted, `api_key_env` with invalid name rejected, nested secret in domain section rejected
- [x] 1.5 Write unit tests for `load_agent_overlay()` — test: returns only agent YAML keys, missing file → `{}`, unknown key rejected, allowed_keys override works, secret validation inherited, source provenance (global config keys absent from result)
- [x] 1.6 Write unit tests for `load_agent_config()` cache isolation — test: strict call does not poison permissive call, permissive call does not poison strict call, different allowed_keys produce independent cache entries

## Phase 2: agent-harness — HarnessConfig composition

- [x] 2.1 Refactor `HarnessConfig.load()` in `agent_harness/config.py` — call `load_agent_config("agent-harness")` for merged LLM config (model + runtime); call `load_agent_overlay("agent-harness", config_path=config_path)` for domain sections; extract `HARNESS_DOMAIN_KEYS` from overlay only; never read global config for domain sections
- [x] 2.2 Remove `_load_yaml_section()` helper from `agent_harness/config.py` — replaced by `load_config_mapping()` from tdt-core
- [x] 2.3 Preserve explicit `config_path` — pass through to both `load_agent_config()` and `load_agent_overlay()`; legacy `$TDT_HOME/harness/config.yaml` never auto-read
- [x] 2.4 Reject legacy `harness:` wrapper in explicit config_path files — raise `ConfigMigrationError` directing operator to use top-level sections
- [x] 2.5 Ensure no mutation of cached dicts — `HarnessConfig.load()` reads from `load_agent_config()` result without `.pop()` or `.update()`; regression test confirms two consecutive loads preserve identical keys and values

## Phase 3: Tests and docs

- [x] 3.1 Write isolated `TDT_HOME` tests — create temp directory with agent-harness.yaml containing gate/persistence/authority sections; verify harness config resolves from overlay only; verify global config does not contribute domain sections
- [x] 3.2 Fix the 6 pre-existing agent-harness test failures — update `test_cli_lifecycle.py` (3 tests) and `test_postgres_integration.py` (3 tests) to use isolated `TDT_HOME` with agent overlay containing gate/persistence sections
- [x] 3.3 Update `agent-harness/docs/configuration.md` — document the two-plane loading strategy, the standard agent YAML path, and the migration from `$TDT_HOME/harness/config.yaml`
- [x] 3.4 Update `agent-harness/docs/example-config.yaml` — replace `harness:` wrapper with top-level sections matching `~/.tdt/agents/agent-harness.yaml`

## Phase 4: Validation

- [x] 4.1 Run `openspec validate llm-config-harness-followup` — change passes validation
- [x] 4.2 Run focused tdt-core tests (`uv run pytest tests/ -q -k 'agent_config or config_loader or config_resolution'`) — all pass
- [x] 4.3 Run focused agent-harness tests (`uv run pytest tests/test_config.py tests/test_cli_lifecycle.py -q`) — all pass (including the 6 previously-failing tests)
- [x] 4.4 Run full test suites for tdt-core, agent-core, agent-docs-sync, agent-harness — all pass with honest exit codes
- [x] 4.5 Run `uv run ruff check src/ tests/` and `uv run mypy src/ --strict` across all 4 repos — clean
- [x] 4.6 Run real LLM smoke test through all 3 provider paths — `openai-chat:fable-5`, `nhà cung cấp dịch vụ AI:Advance`, `nhà cung cấp dịch vụ AI-responses:fable-5` — all return `VERIFICATION_PASSED` with non-zero token usage
- [x] 4.7 Run `openspec validate --all` — full store passes
