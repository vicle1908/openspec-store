## ADDED Requirements

### Requirement: Skills use project-local runner

GitNexus skills SHALL document CLI commands using `node .gitnexus/run.cjs` instead of `npx gitnexus`.

#### Scenario: CLI commands use project-local runner
- **WHEN** a developer reads any GitNexus skill
- **THEN** CLI examples SHALL use `node .gitnexus/run.cjs <command>` format
- **AND** the pattern SHALL be consistent across all skills

### Requirement: --pdg flag is documented

GitNexus skills SHALL document the `--pdg` flag for building program-dependence layers.

#### Scenario: --pdg flag documented in analyze command
- **WHEN** a developer reads the gitnexus-cli skill
- **THEN** the `--pdg` flag SHALL be documented
- **AND** it SHALL explain that it builds taint, CDG, and REACHING_DEF layers

#### Scenario: --pdg enables explain and pdg_query
- **WHEN** a developer uses `node .gitnexus/run.cjs analyze --pdg`
- **THEN** the `explain` and `pdg_query` tools SHALL be available

### Requirement: augment command is documented

GitNexus skills SHALL document the `augment` command for hook integration.

#### Scenario: augment command documented
- **WHEN** a developer reads the gitnexus-cli skill
- **THEN** the `augment` command SHALL be documented
- **AND** it SHALL explain that it augments search patterns with graph context

### Requirement: MCP tools are documented

GitNexus skills SHALL document all MCP tools including pdg_query and explain.

#### Scenario: pdg_query tool documented
- **WHEN** a developer reads the gitnexus-guide skill
- **THEN** the pdg_query tool SHALL be documented
- **AND** it SHALL explain taint analysis capabilities

#### Scenario: explain tool documented
- **WHEN** a developer reads the gitnexus-guide skill
- **THEN** the explain tool SHALL be documented
- **AND** it SHALL explain code analysis capabilities
