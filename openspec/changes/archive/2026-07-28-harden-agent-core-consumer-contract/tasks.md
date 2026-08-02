## 1. Safety Baseline

- [x] 1.1 In agent-core, rerun GitNexus impact for build_agent, AgentRuntime._prepare_tools, and AgentRuntime.restrict_tools; record current LOW risk and stop for approval if the refreshed index reports HIGH or CRITICAL.
- [x] 1.2 Add characterization tests in tests/sdk/ and tests/_ai/ for omitted, explicit-empty, bounded, static/run-scoped intersection, deny, approval, and unknown-name behavior before changing implementation.
- [x] 1.3 Add serialization/config fixtures proving a missing legacy tools_allowed field is distinguishable from an explicit empty collection.

## 2. Tool Policy Contract

- [x] 2.1 Update src/agent_core/sdk/config.py so the immutable profile represents omitted allowlist policy explicitly while preserving missing-field compatibility.
- [x] 2.2 Update src/agent_core/sdk/agents.py to propagate None, empty, and bounded policies without truthiness fallback to all registry tools.
- [x] 2.3 Update src/agent_core/_ai/agent.py static and run-scoped preparation to intersect policies and preserve explicit deny-all.
- [x] 2.4 Add negative tests proving no fabricated/unknown tool name broadens access and an empty policy exposes zero registry tools.

## 3. Step Persistence Contract

- [x] 3.1 Add tests proving implicit InMemoryStepStore is classified as same-process only and a declared persistent store failure never falls back to memory.
- [x] 3.2 Add a persistent SqliteStepStore reconstruction fixture that rebuilds the agent in a separate process and uses the public upstream continuation API with the same run/store identity.
- [x] 3.3 Update agent-step persistence, configuration, building-agent, and integration documentation to show explicit capability composition and distinguish agent steps from LangGraph checkpoints.
- [x] 3.4 Confirm no new TDT persistence abstraction or consumer workflow model was introduced.

## 4. Compatibility and Release Evidence

- [x] 4.1 Run frozen sync, Ruff check/format, strict mypy over source and tests, and the full agent-core pytest coverage gate.
- [x] 4.2 Run consumer contract suites in agent-docs-sync and agent-harness against the candidate core without removing the harness sentinel yet; record the required consumer migration.
- [x] 4.3 Run fresh GitNexus change detection in agent-core and verify only intended tool-policy/persistence symbols and processes changed.
- [x] 4.4 Exercise rollback with a prior core build and document that persistent consumer state is preserved and omitted legacy profiles remain usable.
- [x] 4.5 Validate harden-agent-core-consumer-contract with strict OpenSpec validation.
