# jira-client-pattern Specification

## Purpose

Define the canonical pattern for Jira client creation in jira-skill and related Python packages. All Jira client instantiation MUST use `JiraClientFactory` from `tdt_core.clients.jira`.

## ADDED Requirements

### Requirement: Use JiraClientFactory for all client creation
All Jira client creation in jira-skill SHALL use `JiraClientFactory` from `tdt_core.clients.jira`. Direct instantiation of the `atlassian-python-api` `Jira` class is prohibited.

#### Scenario: Create client from environment
- **WHEN** code needs a Jira client
- **THEN** it SHALL call `JiraClientFactory.from_env()` or `JiraClientFactory.create(config)`
- **AND** MUST NOT instantiate `atlassian.Jira` directly

#### Scenario: Use PatchedJira type annotations
- **WHEN** declaring a variable that holds a Jira client
- **THEN** the type annotation SHALL be `PatchedJira` from `tdt_core.clients.jira`
- **AND** MUST NOT use `Any` or raw `Jira` type

### Requirement: Remove create_with_options factory bypass
The `create_with_options()` method in `JiraClientFactory` SHALL be removed. This method was deprecated and bypassed tdt-core's PatchedJira.

#### Scenario: Remove deprecated method
- **WHEN** migrating jira-skill to canonical pattern
- **THEN** the `create_with_options()` method SHALL be removed from `jira_skill/config.py`
- **AND** all callers SHALL use `create()` instead

#### Scenario: No external callers found
- **WHEN** searching for callers of `create_with_options`
- **THEN** if no external callers exist, the method SHALL be marked for removal
- **AND** a deprecation period of one release SHOULD be observed

### Requirement: Type imports in TYPE_CHECKING blocks
Type-only imports for `atlassian.Jira` SHALL remain in `TYPE_CHECKING` blocks for static type checking, but runtime usage MUST use `PatchedJira`.

#### Scenario: Type annotation with deferred evaluation
- **WHEN** using `from __future__ import annotations`
- **THEN** `atlassian.Jira` may be imported in `TYPE_CHECKING` for type hints
- **AND** the actual runtime type MUST be `PatchedJira`

## REMOVED Requirements

### Requirement: create_with_options bypass method
**Reason**: This method was a deprecated bypass that did not add value over `create()`. It created confusion about which factory to use.
**Migration**: Use `JiraClientFactory.create(config)` or `JiraClientFactory.from_env()`.

## Implementation Notes

- `PatchedJira` extends the base Jira client with v3-specific methods: `jql()`, `add_comment_adf()`, `delete_comment()`, `get_issue_changelog()`
- Factory handles env loading via `ensure_env_loaded()`
- All jira-skill modules MUST import from `tdt_core.clients.jira`
