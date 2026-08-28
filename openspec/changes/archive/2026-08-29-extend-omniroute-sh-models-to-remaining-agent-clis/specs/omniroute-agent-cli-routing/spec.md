## ADDED Requirements

### Requirement: Codex registration SHALL use model_providers with env_key indirection

If Codex is mutated by this change, the omniroute `model_provider` entry in ~/.codex/config.toml SHALL set base_url `http://localhost:20128/v1`, wire_api `responses`, and env_key `OMNIROUTE_API_KEY`, SHALL make the live `sh/*` model IDs selectable, and SHALL leave the global default model unchanged. Codex is outside the nine-consumer registry, so this requirement lives in the routing capability.

#### Scenario: codex provider added without default change

- **WHEN** ~/.codex/config.toml is inspected after mutation
- **THEN** a `model_provider` named omniroute SHALL exist with base_url `http://localhost:20128/v1`, wire_api `responses`, and env_key `OMNIROUTE_API_KEY`
- **AND** the top-level model field SHALL remain `gpt-5.6-sol`
