## ADDED Requirements

### Requirement: Documentation reflects current implementation

All agent-core documentation SHALL accurately reflect the current codebase implementation, including all harness capabilities and their configuration options.

#### Scenario: harness-integration.md documents all parameters
- **WHEN** a developer reads docs/harness-integration.md
- **THEN** all FileSystem parameters (root_dir, allowed_patterns, denied_patterns, protected_patterns, max_read_lines, max_search_results, max_find_results) SHALL be documented
- **AND** all Shell parameters (cwd, allowed_commands, denied_commands, denied_operators, default_timeout, max_output_chars, persist_cwd, allow_interactive) SHALL be documented
- **AND** each parameter SHALL have a description and default value

#### Scenario: configuration.md documents harness config keys
- **WHEN** a developer reads docs/configuration.md
- **THEN** all 14 harness capability config keys SHALL be documented
- **AND** each config key SHALL have a description, parameters, and example
- **AND** a reference to config.yaml.example SHALL be provided

#### Scenario: architecture.md reflects current module structure
- **WHEN** a developer reads docs/architecture.md
- **THEN** the _ai/ module SHALL be visible in the capability stack diagram
- **AND** harness capabilities SHALL be listed in module summaries
- **AND** dependency rules SHALL include _ai/ module

#### Scenario: builtin-tools.md explains alternatives
- **WHEN** a developer reads docs/builtin-tools.md
- **THEN** a note SHALL explain that harness FileSystem/Shell provide alternatives with better security features
- **AND** guidance SHALL be provided on when to use built-in vs harness tools
- **AND** a reference to harness-integration.md SHALL be provided
