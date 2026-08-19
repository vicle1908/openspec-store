## 1. Token tracking fix
- [x] 1.1 Read input_tokens/output_tokens from RunUsage in hooks.py
- [x] 1.2 Verify token counts are non-zero on live inference

## 2. Stderr logging
- [x] 2.1 Change StreamHandler(sys.stdout) to StreamHandler(sys.stderr) in logging.py
- [x] 2.2 Verify sync stdout contains only report output (0 log messages)

## 3. deps_type fix
- [x] 3.1 Pass deps_type=AgentRuntimeDeps to pydantic-ai Agent in agent.py
- [x] 3.2 Add hasattr(ctx, "deps") type guard in _prepare_tools
- [x] 3.3 Add hasattr(ctx, "deps") type guard in _run_via_registry
- [x] 3.4 Verify grep_search error is eliminated in live sync

## 4. Version baseline
- [x] 4.1 Update pydantic-ai version in test_dependency_baseline.py (2.18.0 → 2.31.0)

## 5. Validation
- [x] 5.1 Run agent-core test suite (644 passed)
- [x] 5.2 Run live LLM call to verify token tracking
- [x] 5.3 Run docs-sync check to verify stderr routing
