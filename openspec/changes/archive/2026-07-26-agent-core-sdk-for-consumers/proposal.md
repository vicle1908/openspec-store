## Why

agent-core has 7 public modules used by consumers, but no explicit SDK boundary. Consumers import directly from internal modules (`agent_core.tool_registry`, `agent_core.agent_base`, etc.), creating tight coupling to implementation details. With a second consumer (code-daily-scan) and more planned, the framework needs:

1. A stable public API surface that separates "what consumers use" from "how it's implemented"
2. Composable configuration — consumers need their own settings while inheriting framework config (gateway, observability, secrets)
3. Helper utilities that eliminate boilerplate (tool registration, agent construction, memory init, observability setup, workspace discovery)

The existing `agent-core-integration-contract` and `public-api` specs define the contract; this change provides the concrete SDK implementation.

## What Changes

- **NEW: `agent_core.sdk` package** — Dedicated public API module with re-exports and helpers
  - `ConsumerConfig` — Composable base class (composes `Settings`, not inherits)
  - `build_toolkit()` — Tool registry construction with hooks
  - `build_agent()` — Agent construction from config + tools
  - `create_consumer_memory()` — Memory init with auto-configured scratch paths
  - `init_observability()` — One-liner logging + tracing setup
  - `discover_repos()` — Dynamic workspace repo discovery
- **BREAKING: agent-docs-sync** — Full migration to SDK imports (32 files)
  - Replace `LlmConfig` with `DocsSyncConfig(ConsumerConfig)`
  - Replace hardcoded `TDT_REPOS` with `discover_repos()`
  - Simplify observability/memory init to one-liners
  - Update all tool/agent/workflow imports to `agent_core.sdk.*`

## Capabilities

### New Capabilities
- `sdk-public-api`: Dedicated SDK module re-exporting stable consumer-facing symbols and providing helper utilities (ConsumerConfig, build_toolkit, build_agent, create_consumer_memory, init_observability, discover_repos)
- `consumer-config-composition`: Composable ConsumerConfig base class that wraps agent-core Settings, letting consumers add domain-specific config while inheriting gateway/observability/secrets

### Modified Capabilities
- `agent-docs-sync`: Migrate all 32 importing files from internal agent_core.* modules to agent_core.sdk.* — no behavioral change, pure import migration + config refactor

## Impact

- **agent-core**: 7 new files in `src/agent_core/sdk/`, zero changes to existing modules
- **agent-docs-sync**: ~25 files updated (imports + config refactor), 1 file deleted (`llm/config.py`)
- **Dependencies**: agent-docs-sync pins `agent-core>=0.2.0` (already the case)
- **Risk**: LOW — additive SDK layer, existing internal imports remain functional
- **Blast radius**: agent-core's public symbols (BaseTool, BaseAgent, etc.) are re-exported unchanged; SDK is a thin wrapper, not a replacement
