# agent-core-sdk-public-api Delta Specification

## MODIFIED Requirements

### Requirement: SDK re-exports complete public surface

The SDK SHALL re-export all symbols that consumer repos need, so consumers
import only from `agent_core.sdk` — never from internal modules.

#### Scenario: Settings available from SDK
- **WHEN** a consumer imports `from agent_core.sdk import Settings`
- **THEN** the import SHALL succeed
- **AND** `Settings` SHALL be the same class as `agent_core.foundation.settings.Settings`

#### Scenario: lifecycle_identity symbols available from SDK
- **WHEN** a consumer imports `from agent_core.sdk import SubjectResolutionRequest, SubjectResolutionResult`
- **THEN** the imports SHALL succeed
- **AND** the classes SHALL be the same as their `agent_core.lifecycle_identity` originals
