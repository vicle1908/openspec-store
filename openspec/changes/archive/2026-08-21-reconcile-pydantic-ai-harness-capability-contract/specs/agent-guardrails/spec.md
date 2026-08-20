## MODIFIED Requirements

### Requirement: Docs-sync write-capable agents install bounded tool guardrails

Write-capable documentation generation and full-sync agents SHALL install
bounded tool-argument, shell-command, and result-redaction guardrails in
addition to existing containment hooks and approval gates. These guardrails
SHALL be derived from the supplied production tool registry and SHALL use the
exact registered tool selectors and argument keys. The write guard SHALL cover
`write_doc.path` and `sync_spec.main_path`; `sync_spec.delta_path` remains a
read input governed by read authority rather than a write target. The shell
guard SHALL cover `shell_execute.command` whenever that tool is visible to the
mode.

#### Scenario: Generation mode composition

- **WHEN** docs-sync constructs a generation or full-sync agent with a supplied registry and bounded documentation root
- **THEN** the capability set SHALL include write-path, shell-command, and result-redaction tool guardrails
- **AND** the configured selectors and argument keys SHALL match the supplied production registry exactly
- **AND** the existing write-containment and approval hooks SHALL remain installed

#### Scenario: Registry replacement is respected

- **WHEN** a caller supplies a registry with a custom or reduced visible tool set
- **THEN** guardrail registration SHALL use that registry's canonical tool identities
- **AND** the builder SHALL not construct or silently substitute a second registry

#### Scenario: Read-only mode composition

- **WHEN** docs-sync constructs check or discovery-only behavior
- **THEN** write-capable tool guardrails SHALL not grant write authority
- **AND** read-only tool visibility and authority policy SHALL remain unchanged

## ADDED Requirements

### Requirement: Explicit workspace-root policy for write-capable docs-sync

Write-capable docs-sync construction SHALL require a concrete workspace root
and at least one bounded documentation root expressed relative to that
workspace. The policy SHALL reject missing, ambiguous, absolute, escaping, or
unbounded documentation roots before model or write-capable tool execution.

#### Scenario: Concrete workspace and bounded root are accepted

- **WHEN** generation is constructed with an existing workspace root and a documentation root such as `docs/`
- **THEN** the workspace root SHALL anchor canonical path resolution
- **AND** writes SHALL remain confined to the configured workspace-relative documentation root

#### Scenario: Workspace root is missing

- **WHEN** a write-capable mode is constructed without a concrete workspace root
- **THEN** construction SHALL fail with an actionable configuration error
- **AND** no model or write-capable tool SHALL execute

#### Scenario: Documentation root escapes the workspace

- **WHEN** a configured documentation root is absolute, traverses outside the workspace, or cannot be bounded after canonical and symlink checks
- **THEN** construction SHALL fail closed
- **AND** the diagnostic SHALL not expose credentials, secrets, or raw sensitive path data

