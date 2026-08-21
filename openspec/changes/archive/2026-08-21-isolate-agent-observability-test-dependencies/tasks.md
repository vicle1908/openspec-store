# Tasks: Isolate Agent Core Observability Test Dependencies

## 1. Test Isolation and Fixture Sandboxing

- [x] 1.1 Draft proposal and design for test dependency isolation and verify with `openspec status --change isolate-agent-observability-test-dependencies --store openspec-store`
- [x] 1.2 Author technical design detailing fixture isolation and timeout margins, and verify file presence
- [x] 1.3 Add pytest fixture to sandbox `Settings` and environment variables in `agent-core/tests/test_observability.py`, and verify unit test passes
- [x] 1.4 Adjust CLI flush timeout headroom in short-lived export test, and verify export test passes
- [x] 1.5 Validate change proposal strictly using `openspec validate isolate-agent-observability-test-dependencies --strict --store openspec-store`

## 2. Full Suite Verification

- [x] 2.1 Run full `agent-core` test suite and verify 100% passing tests
- [x] 2.2 Verify full store validity using `openspec validate --all --strict --store openspec-store`
