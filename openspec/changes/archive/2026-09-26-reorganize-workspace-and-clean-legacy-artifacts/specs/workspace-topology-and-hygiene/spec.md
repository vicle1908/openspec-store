## Purpose

Defines the architectural namespace topology, hygiene boundaries, file placement rules, and naming standards for the multi-repo developer workspace.

## ADDED Requirements

### Requirement: Workspace domain taxonomy isolation
The workspace root at `~/Developer/` SHALL maintain dedicated domain subtrees (`legacy/`, `apps/`, `study/`, `ai-tooling/`, `migration-archives/`) alongside existing subtrees (`mobile/`, `infra/`, `ops-tools/`), and SHALL NOT store unclassified standalone projects or static assets flat at the workspace root.

#### Scenario: Categorizing unclustered projects into domain subtrees
- **WHEN** standalone projects or migrated assets are introduced to the workspace
- **THEN** they SHALL be placed in their designated domain directory (`legacy/` for inactive checkouts, `apps/` for standalone client tools, `study/` for reference code, `ai-tooling/` for agent tools, or `migration-archives/` for migration receipts)
- **AND** they SHALL NOT reside unclassified at the top-level `~/Developer/` directory

### Requirement: Root cache and ephemeral scrap prevention
The workspace root SHALL NOT contain test caches, linter caches, temporary execution probes, or dead test repositories. All test and linting operations SHALL execute within their respective repository directories.

#### Scenario: Detecting and rejecting root cache artifacts
- **WHEN** linting, testing, or exploratory scripts are executed in the workspace
- **THEN** cache artifacts (`.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`) SHALL NOT be committed or persisted at `~/Developer/`
- **AND** any existing root-level cache artifacts or test scratch directories SHALL be purged during workspace hygiene cycles

### Requirement: Loose configuration file confinement
Configuration files, lockfiles, and architectural contracts SHALL NOT sit loose at the top-level workspace root. They SHALL reside within their owning repository, within `~/.config/`, or within canonical documentation directories.

#### Scenario: Relocating loose configuration files
- **WHEN** a configuration file or contract is present at the workspace root
- **THEN** it SHALL be moved to its owning component or designated documentation tree
- **AND** `qi_config.yaml` SHALL be stored under `qi-bridge/` with valid local paths
- **AND** `skills-lock.json` SHALL be stored under `.agents/`
- **AND** architectural contracts SHALL be stored under `docs/contracts/`

### Requirement: Repository naming disambiguation
Workspace repositories and project directories SHALL follow lowercase kebab-case naming and SHALL NOT share ambiguous names that collide with active core services.

#### Scenario: Disambiguating legacy service repositories
- **WHEN** an inactive repository has a name identical or confusingly similar to an active production service
- **THEN** the inactive repository SHALL be renamed to reflect its legacy or technology status
- **AND** the legacy Java Kafka repo `microservices/` SHALL be named `legacy/kafka-microservices/` to eliminate confusion with `go-microservices/`
