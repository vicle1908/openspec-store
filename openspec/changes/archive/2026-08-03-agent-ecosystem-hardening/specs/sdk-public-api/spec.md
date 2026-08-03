# sdk-public-api Delta Specification

## ADDED Requirements

### Requirement: SDK re-exports lifecycle identity and settings symbols

The SDK SHALL re-export the following symbols so consumers import only from
`agent_core.sdk`, never from internal modules:

| Symbol | Origin module |
|--------|---------------|
| `Settings` | `agent_core.foundation.settings` |
| `AuthenticatedSubject` | `agent_core.lifecycle_identity` |
| `ConfigFileResolver` | `agent_core.lifecycle_identity` |
| `IdentityStatus` | `agent_core.lifecycle_identity` |
| `SignedSubjectAssertion` | `agent_core.lifecycle_identity` |
| `SubjectResolutionRequest` | `agent_core.lifecycle_identity` |
| `SubjectResolutionResult` | `agent_core.lifecycle_identity` |

#### Scenario: Settings available from SDK
- **WHEN** a consumer imports `from agent_core.sdk import Settings`
- **THEN** the import SHALL succeed
- **AND** `Settings` SHALL be the same class as `agent_core.foundation.settings.Settings`

#### Scenario: Lifecycle identity symbols available from SDK
- **WHEN** a consumer imports `from agent_core.sdk import SubjectResolutionRequest, SubjectResolutionResult`
- **THEN** the imports SHALL succeed
- **AND** the classes SHALL be the same as their `agent_core.lifecycle_identity` originals

#### Scenario: Auth lifecycle symbols available from SDK
- **WHEN** a consumer imports `from agent_core.sdk import AuthenticatedSubject, ConfigFileResolver, IdentityStatus, SignedSubjectAssertion`
- **THEN** the imports SHALL succeed
- **AND** each class SHALL be the same as its `agent_core.lifecycle_identity` original

#### Scenario: Re-exports appear in __all__
- **WHEN** `agent_core.sdk.__all__` is inspected
- **THEN** all 7 symbols SHALL be listed in `__all__`
