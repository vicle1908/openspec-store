## 1. Flavor timeout fix
- [x] 1.1 Update doc_generator timeout_seconds from 180.0 to 300.0 in flavors.py

## 2. DSV path fix
- [x] 2.1 Update DSV path in test_cli_json_output.py to use Path(__file__).parents[1]

## 3. Version baseline
- [x] 3.1 Update pydantic-ai version in test_dependency_baseline.py (2.18.0 → 2.31.0)

## 4. Validation
- [x] 4.1 Run agent-docs-sync test suite (280 passed)
- [x] 4.2 Run full sync pipeline (1075s, 0 agent_timeout, 1 doc generated)
- [x] 4.3 Verify stdout clean (0 log messages)
