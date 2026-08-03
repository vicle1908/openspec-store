# agent-docs-sync Delta Specification

## MODIFIED Requirements

### Requirement: Consumer imports use SDK facade only

agent-docs-sync SHALL import all agent-core symbols through `agent_core.sdk`,
never from internal modules like `agent_core.agent_base`,
`agent_core.foundation.settings`, or `agent_core.lifecycle_identity`.

#### Scenario: No non-SDK imports
- **WHEN** `grep -rn 'from agent_core.agent_base\|from agent_core.foundation\|from agent_core.lifecycle_identity' src/ --include='*.py'` is run
- **THEN** it SHALL return 0 matches
