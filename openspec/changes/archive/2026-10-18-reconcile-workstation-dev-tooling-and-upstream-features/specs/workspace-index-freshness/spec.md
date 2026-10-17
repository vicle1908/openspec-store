# workspace-index-freshness Specification Delta

## MODIFIED Requirements

### Requirement: Official provider identity

The workspace refresh mechanism SHALL use GitNexus `1.6.12` and Graphify from `https://github.com/Graphify-Labs/graphify`, package `graphifyy`, CLI `graphify`, pinned at `0.9.92`.

#### Scenario: Provider identity is verified

- **WHEN** the refresh script starts
- **THEN** it SHALL verify the installed GitNexus (`1.6.12`) and Graphify (`0.9.92`) executable versions
- **AND** it SHALL fail closed for a provider version mismatch unless the operation is explicitly diagnostic
- **AND** it SHALL NOT invoke an alternate Graphify package or provider

#### Scenario: Graphify 0.9.42 features are available

- **WHEN** a Graphify refresh runs on `0.9.92`
- **THEN** non-regular files SHALL be skipped without hanging extraction
- **AND** same-length rewrites SHALL be detected by incremental update
- **AND** graph provenance SHALL be derived from the analyzed repository
- **AND** canonical POSIX source paths SHALL be used

## ADDED Requirements

### Requirement: Graphify platform skill version parity and Wiki entity currency

Installed Graphify platform skills across all 5 installed surfaces (`~/.agents/skills/graphify`, `~/.factory/skills/graphify`, `~/.kiro/skills/graphify`, `~/.copilot/skills/graphify`, and `~/.codebuddy/skills/graphify`) SHALL match the active `graphifyy` package version (`0.9.92`), and workspace wiki entity pages (`wiki/entities/{graphify,agentmemory,notion-cli,docker-workstation}.md`) SHALL record current installed versions and configuration state.

#### Scenario: Graphify CLI executes without stale platform skill warnings
- **WHEN** `graphify --version` or `graphify status` is executed
- **THEN** no stderr warning regarding outdated `0.9.74` skills in `.agents`, `.factory`, `.kiro`, `.copilot`, or `.codebuddy` SHALL be emitted

#### Scenario: AgentMemory embedding status verification accounts for CLI display bug
- **WHEN** AgentMemory embedding health is verified on `@agentmemory/agentmemory@0.9.30`
- **THEN** verification SHALL query `http://localhost:3111/agentmemory/config/flags` (expecting `embeddingProvider: "openai (768 dims)"`) and `http://127.0.0.1:11434/api/tags` (`nomic-embed-text:latest`) rather than relying solely on `agentmemory status` text output
