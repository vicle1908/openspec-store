# exception-handling-standards Specification

## Purpose

Define standards for exception handling in jira-skill and related Python packages. All exception handling MUST use specific exception types with proper error context.

## ADDED Requirements

### Requirement: Use specific exception types instead of bare except
Code SHALL NOT use bare `except Exception:` without specific exception type handling. All bare `except Exception:` blocks MUST be replaced with specific exception types.

#### Scenario: Replace silent except in workflow/client.py
- **WHEN** catching exceptions in `workflow/client.py`
- **THEN** use `requests.RequestException` for network errors
- **AND** use `JiraAPIError` for API-specific errors
- **AND** use exception types from `jira_skill.workflow.exceptions` for domain errors

#### Scenario: Replace silent except in analysis modules
- **WHEN** catching exceptions in `analysis/` modules
- **THEN** use `JiraOperationError` base class for Jira-specific errors
- **AND** use `NetworkError` for connectivity issues
- **AND** never use bare `except Exception: pass`

### Requirement: Propagate context in exception chains
When catching and re-raising exceptions, code SHALL preserve the exception chain using `raise ... from e` syntax.

#### Scenario: Preserve exception chain
- **WHEN** catching an exception and re-raising as a domain-specific exception
- **THEN** use `raise DomainException() from e` to preserve the original traceback
- **AND** never use bare `raise` without context

#### Scenario: No silent exception swallowing
- **WHEN** catching an exception that indicates a failure condition
- **THEN** the exception SHALL be logged or re-raised
- **AND** MUST NOT use `except Exception: pass` to silently swallow errors

### Requirement: Use jira-skill domain exceptions
Code SHALL use domain-specific exceptions from `jira_skill.workflow.exceptions` and `jira_skill.exceptions` instead of raw SDK exceptions.

#### Scenario: Permission denied handling
- **WHEN** API returns 403 Forbidden
- **THEN** raise `PermissionDeniedError` from `jira_skill.workflow.exceptions`
- **AND** include the operation that was attempted

#### Scenario: Rate limit handling
- **WHEN** API returns 429 Too Many Requests
- **THEN** raise `RateLimitError` from `jira_skill.workflow.exceptions`
- **AND** include retry-after information if available

#### Scenario: Version conflict handling
- **WHEN** API returns 409 Conflict (version mismatch)
- **THEN** raise `VersionConflictError` from `jira_skill.workflow.exceptions`
- **AND** include the expected and actual versions

### Requirement: Log exceptions with context
When catching exceptions that are not re-raised, code SHALL log the exception with sufficient context for debugging.

#### Scenario: Log with contextual information
- **WHEN** catching an exception that is handled gracefully
- **THEN** log at appropriate level (warning/info/debug)
- **AND** include relevant identifiers (issue key, filter ID, etc.)
- **AND** use structured logging format

## Implementation Notes

Domain exceptions are defined in:
- `jira_skill.workflow.exceptions`: `PermissionDeniedError`, `RateLimitError`, `VersionConflictError`, `WorkflowValidationError`
- `jira_skill.exceptions`: `JiraOperationError`, `JiraConfigurationError`

Network exceptions from `requests` library:
- `requests.ConnectionError`: Network connectivity issues
- `requests.Timeout`: Request timeout
- `requests.HTTPError`: HTTP error responses (check `.response.status_code`)
