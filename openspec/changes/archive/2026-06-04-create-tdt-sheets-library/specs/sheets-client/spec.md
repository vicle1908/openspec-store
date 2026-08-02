## ADDED Requirements

### Requirement: Unified client interface

The system SHALL provide a unified SheetsClient interface that abstracts backend-specific implementations.

#### Scenario: Client initialization with authentication

- **WHEN** user creates SheetsClient with ServiceAccountAuth
- **THEN** system initializes client with authenticated credentials

#### Scenario: Client initialization with backend selection

- **WHEN** user creates SheetsClient with backend parameter (sdk, gspread, or cli)
- **THEN** system uses specified backend for all operations

#### Scenario: Default backend selection

- **WHEN** user creates SheetsClient without specifying backend
- **THEN** system defaults to 'sdk' (googleapiclient) backend

### Requirement: Read spreadsheet data

The system SHALL support reading data from spreadsheet ranges using A1 notation.

#### Scenario: Read single cell

- **WHEN** user calls client.read(spreadsheet_id, range='Sheet1!A1')
- **THEN** system returns value from cell A1 as 2D list with one row and one column

#### Scenario: Read range of cells

- **WHEN** user calls client.read(spreadsheet_id, range='Sheet1!A1:D10')
- **THEN** system returns 2D list of values with up to 10 rows and 4 columns

#### Scenario: Read entire sheet

- **WHEN** user calls client.read(spreadsheet_id, range='Sheet1')
- **THEN** system returns all data from Sheet1 as 2D list

#### Scenario: Empty range

- **WHEN** user reads a range that contains no data
- **THEN** system returns empty list []

#### Scenario: Invalid spreadsheet ID

- **WHEN** user reads with non-existent spreadsheet_id
- **THEN** system raises appropriate error (HttpError 404 or equivalent)

### Requirement: Write spreadsheet data

The system SHALL support writing data to spreadsheet ranges.

#### Scenario: Write single cell

- **WHEN** user calls client.write(spreadsheet_id, range='Sheet1!A1', values=[['Hello']])
- **THEN** system writes 'Hello' to cell A1 and returns updated cell count

#### Scenario: Write range of cells

- **WHEN** user calls client.write(spreadsheet_id, range='Sheet1!A1:B2', values=[['A', 'B'], ['C', 'D']])
- **THEN** system writes 2x2 grid to specified range

#### Scenario: Write with RAW value input option

- **WHEN** user calls client.write() with value_input_option='RAW'
- **THEN** system writes values exactly as provided without parsing

#### Scenario: Write with USER_ENTERED value input option

- **WHEN** user calls client.write() with value_input_option='USER_ENTERED'
- **THEN** system parses values (formulas, dates, numbers) as if user typed them

#### Scenario: Append to sheet

- **WHEN** user calls client.write() on range extending beyond current data
- **THEN** system expands sheet and writes data to specified cells

### Requirement: Batch read spreadsheet data

The system SHALL support reading data from multiple spreadsheet ranges in a single API call to reduce quota usage.

#### Scenario: Batch read multiple ranges

- **WHEN** user calls client.batch_read(spreadsheet_id, ranges=['Sheet1!A1:D10', 'Sheet2!A1:Z100'])
- **THEN** system returns dict mapping each range to its 2D list of values

#### Scenario: Batch read with major dimension

- **WHEN** user calls client.batch_read() with major_dimension='COLUMNS'
- **THEN** system returns data organized by columns instead of rows

#### Scenario: Batch read empty ranges

- **WHEN** user batch reads ranges that contain no data
- **THEN** system returns empty list [] for each empty range

#### Scenario: Batch read reduces API calls

- **WHEN** user reads 10 ranges via batch_read vs 10 individual read() calls
- **THEN** system makes 1 API call instead of 10 (90% reduction)

### Requirement: Batch write spreadsheet data

The system SHALL support writing data to multiple spreadsheet ranges in a single API call to reduce quota usage.

#### Scenario: Batch write multiple ranges

- **WHEN** user calls client.batch_write(spreadsheet_id, data=[{'range': 'Sheet1!A1', 'values': [['A']]}, {'range': 'Sheet2!A1', 'values': [['B']]}])
- **THEN** system writes all ranges in single API call and returns total updated cell count

#### Scenario: Batch write with RAW value input option

- **WHEN** user calls client.batch_write() with value_input_option='RAW'
- **THEN** system writes all values exactly as provided without parsing

#### Scenario: Batch write with USER_ENTERED value input option

- **WHEN** user calls client.batch_write() with value_input_option='USER_ENTERED'
- **THEN** system parses all values (formulas, dates, numbers) as if user typed them

#### Scenario: Batch write partial failure

- **WHEN** user batch writes to 5 ranges but 1 range has invalid data
- **THEN** system raises ValueError and no ranges are updated (atomic operation)

#### Scenario: Batch write reduces API calls

- **WHEN** user writes to 10 ranges via batch_write vs 10 individual write() calls
- **THEN** system makes 1 API call instead of 10 (90% reduction)

### Requirement: Batch clear spreadsheet data

The system SHALL support clearing data from multiple spreadsheet ranges in a single API call.

#### Scenario: Batch clear multiple ranges

- **WHEN** user calls client.batch_clear(spreadsheet_id, ranges=['Sheet1!A1:D10', 'Sheet2!A1:Z100'])
- **THEN** system clears content from all specified ranges in single API call

#### Scenario: Batch clear entire sheets

- **WHEN** user calls client.batch_clear(spreadsheet_id, ranges=['Sheet1', 'Sheet2'])
- **THEN** system clears all content from both sheets in single API call

#### Scenario: Batch clear preserves formatting

- **WHEN** user batch clears ranges with conditional formatting
- **THEN** system clears cell content but preserves formatting rules

### Requirement: Clear spreadsheet data

The system SHALL support clearing data from spreadsheet ranges.

#### Scenario: Clear single cell

- **WHEN** user calls client.clear(spreadsheet_id, range='Sheet1!A1')
- **THEN** system clears content from cell A1 while preserving formatting

#### Scenario: Clear range of cells

- **WHEN** user calls client.clear(spreadsheet_id, range='Sheet1!A1:D10')
- **THEN** system clears content from all cells in range

#### Scenario: Clear entire sheet

- **WHEN** user calls client.clear(spreadsheet_id, range='Sheet1')
- **THEN** system clears all content from Sheet1

### Requirement: Service caching

The system SHALL cache Google API service objects to avoid repeated initialization overhead.

#### Scenario: First API call

- **WHEN** client makes first API call (read/write/clear)
- **THEN** system initializes service object and caches it

#### Scenario: Subsequent API calls

- **WHEN** client makes additional API calls with same backend and credentials
- **THEN** system reuses cached service object

#### Scenario: Different backends

- **WHEN** multiple clients use different backends (sdk vs gspread)
- **THEN** system maintains separate cached service objects per backend

### Requirement: Error handling consistency

The system SHALL provide consistent error handling across all backends.

#### Scenario: Permission denied

- **WHEN** service account lacks permission to access spreadsheet
- **THEN** system raises PermissionError with spreadsheet ID in message

#### Scenario: Rate limit exceeded

- **WHEN** API rate limit is exceeded (500 requests per 100 seconds)
- **THEN** system raises RateLimitError with retry-after information and implements exponential backoff

#### Scenario: Network error

- **WHEN** network connection fails during API call
- **THEN** system raises NetworkError with original exception details

#### Scenario: Invalid range format

- **WHEN** user provides malformed A1 notation range
- **THEN** system raises ValueError with explanation of correct format

#### Scenario: Batch operation partial failure

- **WHEN** batch operation has one invalid range among valid ranges
- **THEN** system raises ValueError before making any API calls (fail-fast validation)

### Requirement: Quota awareness

The system SHALL track API call counts and warn when approaching Google Sheets API quota limits.

#### Scenario: Quota tracking

- **WHEN** client makes API calls
- **THEN** system tracks call count within 100-second window

#### Scenario: Quota warning

- **WHEN** client approaches 80% of quota (400 calls per 100 seconds)
- **THEN** system logs warning suggesting batch operations

#### Scenario: Quota reset

- **WHEN** 100-second window expires
- **THEN** system resets call counter

### Requirement: Backend-agnostic return types

The system SHALL return data in consistent format regardless of backend used.

#### Scenario: Read returns uniform structure

- **WHEN** user reads data with any backend (sdk, gspread, cli)
- **THEN** system always returns data as list[list[Any]]

#### Scenario: Write returns uniform response

- **WHEN** user writes data with any backend
- **THEN** system always returns integer count of updated cells

#### Scenario: Clear returns uniform response

- **WHEN** user clears data with any backend
- **THEN** system returns None or empty response consistently
