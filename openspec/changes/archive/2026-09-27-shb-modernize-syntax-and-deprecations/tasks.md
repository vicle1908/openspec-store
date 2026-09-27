# Tasks: SHB Ecosystem Syntax Modernization and Deprecation Remediation

## 1. Core SDK and Agent Runtime Modernization

- [x] 1.1 Migrate legacy `typing` imports to builtin collections (PEP 585) and pipe unions (PEP 604) in `shb-agent-core` and verify with `uv run ruff check` and `uv run pytest`
- [x] 1.2 Modernize `shb-browser-cli` typing syntax and add explicit exception chaining (`raise ... from None`)
- [x] 1.3 Modernize `shb-core` typing syntax and remove empty f-string in `src/shb_core/cli.py`

## 2. Banking Tools, Review, and Ingress Cleanup

- [x] 2.1 Add explicit exception chaining in `shb-mcp-servers/src/shb_mcp/tools.py` and verify `shb-mcp` CLI
- [x] 2.2 Remove unused import in `shb-ai-review/src/shb_review/cli.py` and verify review test suite
- [x] 2.3 Remove unused import in `shb-observability/src/shb_observability/collector.py` and verify test suite
- [x] 2.4 Clean unused imports in `shb-webhook-receiver/src/shb_webhook/app.py` and verify FastAPI endpoints
- [x] 2.5 Reformat long Typer option in `shb-jira-tools/src/shb_jira/cli.py` to resolve line length `E501` and verify `shb-jira` CLI

## 3. Skills and Harness Modernization

- [x] 3.1 Replace deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)` in compliant user entity fixture in `shb-agent-skills`
- [x] 3.2 Upgrade Pydantic v1 `@validator` to `@field_validator` with `@classmethod` in `shb-agent-skills` integration tests
- [x] 3.3 Add explicit exception chaining in `shb-ai-harness-skills/src/shb_ai_harness/contracts.py`

## 4. Full Ecosystem Verification and OpenSpec Strict Validation

- [x] 4.1 Run unit test suite across all 12 repositories and verify 81/81 pass with zero `.pytest_cache` pollution
- [x] 4.2 Re-run `gitnexus analyze` and `graphify update` across all modified repositories and verify index freshness
- [x] 4.3 Validate the OpenSpec change strictly against store rules via `openspec validate --strict --store openspec-store`
