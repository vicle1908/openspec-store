# agent-docs-sync Delta Specification

## ADDED Requirements

### Requirement: Consumer imports use SDK facade only

agent-docs-sync SHALL import all agent-core symbols through `agent_core.sdk`,
never from internal modules like `agent_core.agent_base`,
`agent_core.foundation.settings`, or `agent_core.lifecycle_identity`.

#### Scenario: No non-SDK imports at runtime
- **WHEN** an AST-based check scans all `agent_docs_sync` Python files for `from agent_core.*` imports
- **THEN** every import SHALL be from `agent_core.sdk` only
- **AND** no imports SHALL reference `agent_core.agent_base`, `agent_core.foundation`, or `agent_core.lifecycle_identity`

#### Scenario: Import check catches aliases and bare imports
- **WHEN** a file uses `import agent_core.lifecycle_identity as lifecycle` or `from agent_core.foundation import settings`
- **THEN** the AST-based check SHALL flag these as violations
