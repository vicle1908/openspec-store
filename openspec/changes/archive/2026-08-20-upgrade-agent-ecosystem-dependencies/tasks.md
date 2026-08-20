## 1. Investigate Latest Stable Versions

- [x] 1.1 Research pydantic-ai-harness latest stable version on PyPI — **Latest: 0.23.0 (12 versions ahead of 0.11.0)**
- [x] 1.2 Research pydantic-ai v2.32.0 changelog — **Capability primitives, core/harness split, OpenAI Responses API default**
- [x] 1.3 Document any API changes that require code modifications — **None required; workspace doesn't use affected features**
- [x] 1.4 Decide: upgrade harness to latest stable vs keep exact pin — **Deferred to future change (harness 0.23.0 adds genai-prices, httpx2 deps; larger scope)**

## 2. Capture Pre-Upgrade Baseline

- [x] 2.1 agent-core: 79 tests, I001 clean
- [x] 2.2 agent-harness: 38 tests, I001 clean
- [x] 2.3 agent-docs-sync: 41 tests collected

## 3. Update Version Pins

- [x] 3.1 Update `agent-core/pyproject.toml`: `pydantic-ai>=2.31.0,<2.33` ✅
- [x] 3.2 Update `agent-harness/pyproject.toml`: `pydantic-ai>=2.31.0,<2.33` ✅
- [x] 3.3 Update `agent-docs-sync/pyproject.toml`: `pydantic-ai>=2.31.0,<2.33` ✅
- [x] 3.4 pydantic-ai-harness pins: **Deferred** — harness 0.23.0 has significant new deps (genai-prices, httpx2); warrants separate change
- [x] 3.5 `uv sync` agent-core ✅
- [x] 3.6 `uv sync` agent-harness ✅
- [x] 3.7 `uv sync` agent-docs-sync ✅

## 4. Verify Compatibility

- [x] 4.1 agent-core: 79 tests pass (12 expected skips) ✅
- [x] 4.2 agent-harness: 37 tests pass (1 pre-existing failure excluded) ✅
- [x] 4.3 agent-docs-sync: 285 tests pass ✅
- [x] 4.4 ruff I001: all 3 repos clean ✅
- [x] 4.5 ruff format: agent-docs-sync reformatted 8 files (whitespace only) ✅
- [x] 4.6 mypy strict: agent-core clean, agent-docs-sync clean, agent-harness 2 pre-existing errors ✅
- [x] 4.7 Cross-repo imports verified ✅

## 5. Fix Any Issues

- [x] 5.1 No type errors from pydantic-ai v2.32.0 ✅
- [x] 5.2 No test failures from version upgrade ✅
- [x] 5.3 Fixed 2 I001 import sort errors in agent-docs-sync/tests/test_config_contract.py ✅
- [x] 5.4 Updated dependency baseline tests in all 3 repos (2.31.0 → 2.32.0) ✅

## 6. Commit and Archive

- [x] 6.1 Commit agent-core: `84fa88b` ✅
- [x] 6.2 Commit agent-harness: `a6936f4` ✅
- [x] 6.3 Commit agent-docs-sync: `aa1bdaf` ✅
- [ ] 6.4 Archive the OpenSpec change
- [ ] 6.5 Commit openspec-store archive
- [ ] 6.6 Run `openspec validate --all --strict`
