# Realized P/L Merged View

## ADDED Requirements

### Requirement: Unified Realized P/L Calculation

The system SHALL calculate realized profit/loss by combining stocks and options transactions in a single view.

#### Scenario: Stocks P/L calculation
- **WHEN** user has closed stock positions with realized gains/losses
- **THEN** system SHALL display accurate realized P/L for each closed trade

#### Scenario: Options P/L calculation
- **WHEN** user has closed options positions (exercised, assigned, or expired)
- **THEN** system SHALL calculate realized P/L including premium income/expense

#### Scenario: Combined P/L display
- **WHEN** user views realized P/L in Merged UX
- **THEN** system SHALL show combined stocks + options realized P/L

### Requirement: Realized P/L Classification

Realized P/L items SHALL be classified by instrument type (stock vs option) for detailed view.

#### Scenario: Classification in detailed view
- **WHEN** user expands realized P/L section
- **THEN** each item SHALL display instrument type (STOCK or OPTION)

#### Scenario: Filtering by type
- **WHEN** user wants to see only stock or option P/L
- **THEN** filter SHALL allow filtering by instrument type

### Requirement: Realized P/L Time Period

The system SHALL support realized P/L calculation for configurable time periods (day, week, month, year, all-time).

#### Scenario: Monthly P/L
- **WHEN** user selects monthly view
- **THEN** system SHALL calculate realized P/L for current calendar month

#### Scenario: Custom date range
- **WHEN** user specifies custom date range
- **THEN** system SHALL calculate realized P/L within that range

### Requirement: Realized P/L Currency Handling

Realized P/L SHALL be displayed in account base currency with proper conversion for multi-currency accounts.

#### Scenario: USD base currency
- **WHEN** account base currency is USD
- **THEN** realized P/L SHALL be displayed in USD without conversion

#### Scenario: Multi-currency conversion
- **WHEN** options trade settles in different currency
- **THEN** system SHALL convert to base currency using daily exchange rate

### Requirement: Realized P/L Edge Cases

The system SHALL handle edge cases including:
- Partial exercises
- Multi-leg options strategies (spreads, straddles)
- Assignment scenarios
- Expiration worthless

#### Scenario: Spread P/L
- **WHEN** user closes a bull call spread
- **THEN** realized P/L SHALL be net of all legs

#### Scenario: Assignment P/L
- **WHEN** user is assigned on a short option
- **THEN** system SHALL include assignment-related costs in P/L
