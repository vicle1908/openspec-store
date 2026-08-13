## Purpose
Defines always-apply rules loaded from a local RULES.md file and enforces tool approval gates so that destructive or disallowed bash commands require explicit user consent before execution.

## Requirements

### Requirement: RULES.md existence
A file `~/.omp/agent/RULES.md` SHALL exist and be loaded as always-apply context at session startup. The harness SHALL read this file before any tool invocation and inject its contents into the agent context.

#### Scenario: RULES.md is loaded at startup
- **WHEN** a new session starts and `~/.omp/agent/RULES.md` exists
- **THEN** the file contents SHALL be loaded into the agent context and available for every subsequent interaction

#### Scenario: RULES.md is missing
- **WHEN** `~/.omp/agent/RULES.md` does not exist
- **THEN** the harness SHALL log a warning that RULES.md was not found and continue the session without it

#### Scenario: RULES.md is empty
- **WHEN** `~/.omp/agent/RULES.md` exists but contains no content
- **THEN** it SHALL still be loaded without error, contributing zero additional rules to the context

### Requirement: RULES.md mandatory content
`RULES.md` SHALL contain at minimum the following guardrails: (1) no `.env` file commits to version control, (2) no `git push` without explicit user approval, (3) no `rm -rf` without user confirmation.

#### Scenario: Mandatory guardrails are present
- **WHEN** `RULES.md` is loaded and contains the three mandatory guardrails
- **THEN** each guardrail SHALL be enforced during the session as an always-apply rule

#### Scenario: Mandatory guardrails are absent
- **WHEN** `RULES.md` exists but is missing one or more mandatory guardrails
- **THEN** the harness SHALL emit a warning identifying which guardrails are missing, but the session SHALL still proceed

### Requirement: tools.approval bash gating
`tools.approval` SHALL be configured to gate bash commands that match deny patterns (e.g. `rm -rf`, `git push`, `force` flags, destructive git operations). A matching command SHALL block execution and prompt the user for explicit approval before proceeding.

#### Scenario: Destructive bash command is attempted
- **WHEN** a bash tool invocation contains a command matching a deny pattern (e.g. `rm -rf /path`, `git push --force`)
- **THEN** execution SHALL be paused and the user SHALL be prompted with the exact command and a confirmation dialog before it is allowed to proceed

#### Scenario: Safe bash command is attempted
- **WHEN** a bash tool invocation does not match any deny pattern
- **THEN** the command SHALL execute immediately without prompting

#### Scenario: User denies a gated command
- **WHEN** the user declines the approval prompt for a gated command
- **THEN** the command SHALL NOT be executed and the harness SHALL report that the operation was cancelled by the user