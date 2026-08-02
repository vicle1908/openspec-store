# agent-cli Specification

## Purpose
Defines the agent-core CLI surface including the `init` scaffolding subcommand, CLI documentation alignment, and machine-readable output support.
## Requirements
### Requirement: The CLI exposes an `init` subcommand for agent scaffolding
The system MUST add an `init` subcommand to the existing Typer CLI surface that generates new agent project skeletons.

#### Scenario: init appears in help output
- **WHEN** `agent-core --help` is run
- **THEN** the `init` subcommand is listed alongside existing commands (config, health, skills, review, propose, explore, repl)

#### Scenario: init accepts a project name as positional argument
- **WHEN** `agent-core init my-agent` is run
- **THEN** the command uses `my-agent` as both the directory name and the Python package name (converted to `my_agent`)

#### Scenario: init respects --json flag for machine-readable output
- **WHEN** `agent-core --json init my-agent` is run
- **THEN** the command outputs a JSON object with `{"created": "my-agent", "template": "reviewer", "files": [...]}` instead of human-readable text and the file list is sorted deterministically

#### Scenario: init respects --no-interactive flag
- **WHEN** `agent-core --no-interactive init my-agent` is run
- **THEN** the command uses all defaults without prompting for template selection or configuration

#### Scenario: init exposes template listing and empty-directory reuse flags
- **WHEN** `agent-core init --list-templates` or `agent-core init my-agent --allow-existing-empty` is run
- **THEN** the CLI supports deterministic template discovery and explicit reuse of a pre-created empty target directory

### Requirement: CLI documentation matches current command surface
The agent-core CLI documentation SHALL describe current commands and avoid stale aliases.

#### Scenario: Skills commands document profiles and doctor
- **WHEN** a developer reads CLI docs for skills
- **THEN** the docs include `skills list --profile`, `skills reload --profile`, and `skills doctor`

#### Scenario: Schedule trigger command is documented
- **WHEN** a developer reads CLI docs for schedules
- **THEN** the docs use `schedules trigger <name>` and do not recommend `schedules run <name>`

#### Scenario: JSON examples match current shapes
- **WHEN** CLI docs include JSON automation examples
- **THEN** those examples match current command output shapes or explicitly say they are illustrative

