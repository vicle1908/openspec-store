## ADDED Requirements

### Requirement: Public typed grid snapshot access
The `tdt-sheets` library SHALL expose an additive public `SheetsClient.read_grid_snapshot(spreadsheet_id, range_ref)` operation for consumers that require cell-level values and sheet structure in one bounded read. The returned transport-neutral model MUST contain spreadsheet ID, requested/resolved range, spreadsheet locale and timezone, selected sheet identity and grid bounds, merge ranges intersecting the selected sheet, and selected cells with zero-based coordinates plus effective and formatted values. It MUST NOT expose the raw Google API response or require callers to access private backend members.

#### Scenario: SDK grid snapshot succeeds
- **WHEN** an authenticated SDK-backed client requests a valid bounded A1 range
- **THEN** one `spreadsheets.get` request returns the fields required by the typed grid snapshot
- **AND** the client converts the response into public frozen/immutable models
- **AND** the caller can inspect cell coordinates, effective values, formatted values, merges, locale, and timezone without raw service access

#### Scenario: Range selects one plan tab
- **WHEN** a caller requests a range such as `'Epic Plan'!A1:ZZ500`
- **THEN** the response contains only the requested bounded grid data needed for that range
- **AND** unrelated workbook cell contents are not materialized in the snapshot

#### Scenario: Snapshot backend is unsupported
- **WHEN** `read_grid_snapshot` is invoked through a backend that cannot provide the complete contract
- **THEN** the client raises `BackendNotAvailableError` or `NotImplementedError`
- **AND** it does not return an empty or partial snapshot as success

#### Scenario: Existing client behavior remains compatible
- **WHEN** consumers continue using `read`, `batch_read`, metadata, or write operations
- **THEN** their existing signatures and result shapes remain unchanged
- **AND** backend-equivalence expectations for those existing operations remain unchanged

### Requirement: Grid snapshot error translation and bounded data handling
The SDK grid snapshot implementation SHALL use the existing service-account credentials, request tracking, service cache, and Google API error-translation conventions. It MUST use a field mask and caller-supplied bounded range, MUST avoid logging cell contents or credentials, and MUST translate authorization, rate-limit, and network failures through existing `tdt-sheets` exception types.

#### Scenario: Authorization fails
- **WHEN** Google Sheets returns an authorization or not-found response
- **THEN** the operation raises the existing translated permission exception without exposing credentials

#### Scenario: Rate limit or network failure occurs
- **WHEN** the API returns a rate-limit or other transport failure
- **THEN** the operation raises the existing translated `tdt-sheets` exception type
- **AND** no partial snapshot is returned

#### Scenario: Field mask is applied
- **WHEN** the SDK requests a grid snapshot
- **THEN** the request selects only spreadsheet locale/timezone, selected sheet properties, merges, grid start coordinates, and cell effective/formatted values required by the public model
- **AND** formatting, notes, formulas, charts, and unrelated metadata are excluded from the snapshot contract

#### Scenario: Retry-after type is invalid
- **WHEN** a translated rate-limit response provides a non-integer retry-after value
- **THEN** the SDK uses the existing default retry delay
- **AND** it raises the existing `RateLimitError` rather than leaking a parsing exception
