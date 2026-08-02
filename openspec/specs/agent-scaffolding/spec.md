# agent-scaffolding Specification

## Purpose
Defines the `agent-core init` command that scaffolds new agent projects from discoverable templates, with composition-first customization and reference-adapter guidance.
## Requirements
### Requirement: The CLI provides an `init` command that scaffolds new agent projects
The system MUST expose an `agent-core init <name>` subcommand that generates a working agent project skeleton from a template.

#### Scenario: init canonicalizes the package name
- **WHEN** `agent-core init my-reviewer` is run
- **THEN** the directory is named `my-reviewer` and the Python package becomes `my_reviewer`

#### Scenario: init creates a new project directory with required files
- **WHEN** `agent-core init my-reviewer` is run in an empty directory
- **THEN** a `my-reviewer/` directory is created containing `pyproject.toml`, `README.md`, `src/my_reviewer/`, `tests/`, `.agents/skills/`, and a starter agent module

#### Scenario: init refuses to overwrite an existing directory
- **WHEN** `agent-core init my-reviewer` is run and `my-reviewer/` already exists with files
- **THEN** the command exits non-zero with an error message and does not modify any existing files

#### Scenario: init allows an existing empty directory when explicitly permitted
- **WHEN** `agent-core init my-reviewer --allow-existing-empty` is run in an empty pre-created directory
- **THEN** the command reuses the directory and writes the generated files into it

#### Scenario: init supports a template flag for different agent shapes
- **WHEN** `agent-core init my-explorer --template explorer` is run
- **THEN** the generated skeleton is configured for an explorer-flavored agent (read-only tools, longer iterations) rather than the default reviewer template

#### Scenario: init uses deterministic template defaults in non-interactive mode
- **WHEN** `agent-core init my-agent --no-interactive` is run without `--template`
- **THEN** the reviewer template is selected without prompting

#### Scenario: Generated projects pass their own quality gates
- **WHEN** the generated project's `uv sync && uv run pytest` is run immediately after `init`
- **THEN** the starter test suite passes without modification

### Requirement: Agent project templates ship as a discoverable set
The system MUST list available templates and use a deterministic default.

#### Scenario: Listing templates shows available shapes
- **WHEN** `agent-core init --list-templates` is run
- **THEN** the command prints the list of available templates (at minimum: `reviewer`, `explorer`, `proposer`) in deterministic order and exits successfully

#### Scenario: Omitting --template uses the reviewer default
- **WHEN** `agent-core init my-agent` is run without specifying a template
- **THEN** the `reviewer` template is used and the choice is logged

#### Scenario: JSON mode returns a stable manifest
- **WHEN** `agent-core --json init my-agent` is run
- **THEN** the command returns `created`, `template`, and a sorted `files` list and does not emit prompt text

### Requirement: Generated agents follow integration contract
Generated agent projects SHALL align with the workspace integration contract and use profile-based skills plus composition-first specialization.

#### Scenario: Generated config uses profiles
- **WHEN** `agent-core init <name>` creates a project
- **THEN** the generated config uses `skills.active_profile` and `skills.profiles`

#### Scenario: Generated docs avoid subclass guidance
- **WHEN** generated project docs describe customization
- **THEN** they guide users toward flavors, tools, hooks, and profiles rather than subclassing `BaseAgent`

### Requirement: The reference adapter documents the consumer adapter pattern
Generated-project and scaffolding guidance SHALL point to the Phase 2 reference adapter as the canonical example of translating domain concepts into an `AgentRequest` and `BaseAgent` configuration.

#### Scenario: Scaffolding guidance links the reference adapter
- **WHEN** a developer reads scaffolding or building-agents guidance about consuming agent-core
- **THEN** it links the `agent-core/examples/code_reviewer/` reference adapter and shows the domain → `AgentRequest` → `AgentResult` mapping

#### Scenario: Guidance keeps composition-first framing
- **WHEN** the adapter pattern is described
- **THEN** it specializes via flavors, tools, hooks, and `skill_profile` through `AgentRequest`, not by subclassing `BaseAgent`

