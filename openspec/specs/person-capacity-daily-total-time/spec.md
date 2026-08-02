# person-capacity-daily-total-time Specification

## Purpose
TBD - created by archiving change person-capacity-daily-total-time. Update Purpose after archive.
## Requirements
### Requirement: Daily Ticket Details SHALL show total time per day

The Daily Ticket Details column SHALL display the total hours/minutes at the start of each day line, followed by individual ticket details.

#### Scenario: Multiple tickets per day

- **WHEN** a person has multiple tickets logged on a single day
- **THEN** the line SHALL display: `YYYY-MM-DD: Hh Mm | TICKET1 (Hh Mm), TICKET2 (Hh Mm), ...`
- **AND** the total SHALL be the sum of all ticket times for that day

#### Scenario: Single ticket per day

- **WHEN** a person has only one ticket logged on a single day
- **THEN** the line SHALL display: `YYYY-MM-DD: Hh Mm | TICKET (Hh Mm)`
- **AND** the total SHALL equal the single ticket time

#### Scenario: No tickets on a day

- **WHEN** a person has no tickets logged on a day
- **THEN** the day SHALL be skipped (not displayed)
- **AND** SHALL NOT show an empty line

### Requirement: Total time format SHALL be consistent

The total time SHALL be formatted using the same `format_seconds()` function used for individual tickets.

#### Scenario: Time formatting

- **WHEN** total seconds is 30600 (8h 30m)
- **THEN** the total SHALL display as "8h 30m"
- **AND** SHALL use the same format as individual ticket times

