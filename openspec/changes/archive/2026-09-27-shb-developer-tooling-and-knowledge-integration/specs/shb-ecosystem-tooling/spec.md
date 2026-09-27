# Spec Delta: shb-ecosystem-tooling

## MODIFIED Requirements

### Requirement: Code Intelligence and Knowledge Refresh Registration
The SHB repositories SHALL be registered in `~/Developer/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` to ensure inclusion in nightly GitNexus code intelligence and Graphify knowledge graph indexing, and every active repository SHALL maintain up-to-date semantic and structural knowledge indices.

#### Scenario: Knowledge refresh inventory verification
- **WHEN** the knowledge refresh audit script `knowledge-status.sh` is executed
- **THEN** all 12 active SHB repositories are reported as valid managed targets eligible for automated indexing

#### Scenario: GitNexus semantic index freshness
- **WHEN** `gitnexus status` is executed within any SHB repository root
- **THEN** the analyzer SHALL report status as up-to-date and matching the current repository HEAD commit

#### Scenario: Global knowledge graph registration
- **WHEN** `graphify global list` is executed
- **THEN** all 12 SHB repositories SHALL appear in the global graph registry with non-zero node counts

## ADDED Requirements

### Requirement: In-Repository Knowledge Configuration and Git Hygiene
Every SHB repository SHALL include an in-repo `.gitnexusrc` configuration file specifying local embedding models and concurrency parameters, SHALL maintain a tracked `graphify-out/graph.json` AST knowledge graph with automated merge drivers, and SHALL configure `.gitignore` to prevent tracking of LadybugDB vector indexes.

#### Scenario: GitNexus configuration presence
- **WHEN** inspecting the root of any SHB repository
- **THEN** a `.gitnexusrc` file SHALL exist containing `embeddings: true`, `embeddingBaseUrl` pointing to Ollama, and `embeddingModel` set to `nomic-embed-text`

#### Scenario: Graphify hook and gitignore hygiene
- **WHEN** Git operations occur within any SHB repository
- **THEN** the `.gitnexus/` directory SHALL be ignored by `.gitignore`
- **AND** `graphify-out/graph.json` SHALL be tracked in version control while `graphify-out/20*/` snapshots are ignored
- **AND** a Graphify post-commit hook SHALL be installed in `.git/hooks/`

### Requirement: Developer Toolchain Standardization and Feature Enablement
Development across the SHB ecosystem SHALL standardize on modernized developer tooling with all feature capabilities enabled, specifically Notion CLI (`ntn`) v0.23.10+, Graphify v0.9.69+ with complete optional extras, GitNexus v1.6.12+ with native vector support, and AgentMemory v0.9.29+ with B+ flags activated.

#### Scenario: Notion CLI setup verification
- **WHEN** `ntn doctor` is executed in the developer environment
- **THEN** it SHALL verify CLI version v0.23.10 or higher, valid workspace resolution, and successful Workers and Public API authentication

#### Scenario: AgentMemory full feature activation
- **WHEN** `agentmemory doctor` is executed
- **THEN** all 9 server diagnostics SHALL pass including observation compression, knowledge graph extraction, memory consolidation, and context injection
