# workspace-topology-and-hygiene Specification

## MODIFIED Requirements

### Requirement: Loose configuration file confinement
Configuration files, lockfiles, skill directories, and architectural contracts SHALL NOT sit loose at the top-level workspace root. They SHALL reside within their owning repository, within `~/.config/`, or within canonical hidden agent directories (`.agents/`), except `~/Developer/skills-lock.json` as the Skills CLI writable registry paired with the generated `.agents/skills-lock.json` replica. Redundant `skills/` or `agent/` trees SHALL NOT exist at the workspace root.

#### Scenario: Relocating loose configuration files
- **WHEN** a configuration file, skill directory, or contract is present at the workspace root
- **THEN** it SHALL be moved to its owning component or designated documentation tree
- **AND** `qi_config.yaml` SHALL be stored under `qi-bridge/` with valid local paths
- **AND** `skills-lock.json` at the workspace root SHALL be permitted only as the official Skills CLI's writable project registry paired with its generated read-only replica at `.agents/skills-lock.json`, while no other lockfile SHALL exist at root
- **AND** workspace skills SHALL reside exclusively in `.agents/skills/` with no root `skills/` or `agent/` directory trees
- **AND** architectural contracts SHALL be stored under `docs/contracts/`
- **AND** unclassified standalone project roots (`cursor-account-manager-build/`, `main-db-migrations/`, `ntu-keynote/`) SHALL be housed under designated domain subtrees (`apps/`, `legacy/`, `study/`)

#### Scenario: Root Skills CLI lockfile exception does not permit root skill trees
- **WHEN** workspace root hygiene is audited after official `skills` or `npx skills` project operations in `~/Developer/`
- **THEN** `~/Developer/skills-lock.json` SHALL be accepted as the sole writable project lockfile authority and `~/Developer/.agents/skills-lock.json` SHALL be verified as its generated read-only compatibility replica
- **AND** any root `skills/` directory, root `agent/` directory, or unrelated loose configuration file at `~/Developer/` SHALL fail hygiene verification

#### Scenario: Unverified or manual edits to the .agents lockfile replica are rejected
- **WHEN** `~/Developer/.agents/skills-lock.json` is modified directly or diverges from `~/Developer/skills-lock.json` outside a verified refresh or explicit acceptance/postcheck run
- **THEN** verification SHALL report registry replica drift rather than treating `.agents/skills-lock.json` as a second writable authority
- **AND** failed or partial refresh runs SHALL NOT publish an updated `.agents/skills-lock.json` replica
