# Sprint Sheet Freshness State Persistence

## ADDED Requirements

### Requirement: Freshness State Error Handling

The system SHALL log all freshness state write operations with sufficient detail for diagnostics.

### `_write_freshness_state()` function

- SHALL log `freshness_state_written` on success with path and run_id
- SHALL log `freshness_state_write_failed` on failure with path and error
- SHALL re-raise exception after logging for caller handling

#### Scenario: Freshness state write succeeds
- **Given** a successful sprint sheet write
- **When** `_write_freshness_state()` is called
- **Then** the state file is written with run_id, source, timestamps, and spreadsheet_id
- **And** a `freshness_state_written` INFO log is emitted

#### Scenario: Freshness state write fails
- **Given** a disk full or permission error
- **When** `_write_freshness_state()` is called
- **Then** a `freshness_state_write_failed` ERROR log is emitted with path and error
- **And** the exception is re-raised
- **But** the caller (`write_sheet`) catches the exception and continues
- **So** the Sprint Report and Person Capacity sheets are still written
