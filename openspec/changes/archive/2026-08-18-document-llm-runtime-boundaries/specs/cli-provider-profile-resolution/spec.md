## MODIFIED Requirements

### Requirement: Separate runtime boundaries remain explicit

Runtimes with their own model registry or provider-infrastructure role SHALL not be forced through this profile unless a later change defines a versioned bridge. The standard SHALL document the exclusion reason and owner.

#### Scenario: prime-agent boundary

- **WHEN** prime-agent resolves models from its TypeScript model registry and its own credential directory
- **THEN** this change SHALL treat it as a separate runtime boundary
- **AND** it SHALL not redirect its credentials into TDT configuration

#### Scenario: Provider adapter boundary

- **WHEN** claude-code-provider-adapter translates provider protocols
- **THEN** it SHALL remain provider infrastructure rather than a per-agent CLI-profile consumer

#### Scenario: omp boundary

- **WHEN** omp (oh-my-pi) resolves models from its own `models.yml` provider blocks, role allocation, and credential env-var references
- **THEN** it SHALL be treated as a separate runtime boundary governed by the `omp-provider-routing` capability
- **AND** it SHALL NOT be forced through this CLI-profile contract
- **AND** its credential env-var references SHALL NOT be redirected into TDT canonical configuration
