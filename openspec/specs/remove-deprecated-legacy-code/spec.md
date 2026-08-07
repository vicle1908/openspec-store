# remove-deprecated-legacy-code Specification

## Purpose
Define the removal of deprecated legacy code that was superseded by pydantic-settings migration.
## Requirements
### Requirement: Clean Public API

The tdt_core public API SHALL only export active, non-deprecated functions.

#### Scenario: No deprecated exports

- **GIVEN** a function is marked deprecated
- **WHEN** all external consumers have migrated
- **THEN** the function SHALL be removed from `__all__` exports
- **AND** the function MAY remain in the module for backward compat

