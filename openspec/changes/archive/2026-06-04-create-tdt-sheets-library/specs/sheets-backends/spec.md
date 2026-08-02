## ADDED Requirements

### Requirement: Backend abstraction protocol

The system SHALL define a Protocol or Abstract Base Class that all backend implementations must follow.

#### Scenario: Protocol definition

- **WHEN** developer examines the backend interface
- **THEN** system provides clear Protocol with read(), write(), clear(), batch_read(), batch_write(), and batch_clear() method signatures

#### Scenario: Type checking compatibility

- **WHEN** developer uses type checkers (mypy, pyright)
- **THEN** system validates backend implementations comply with Protocol

#### Scenario: Backend swapping

- **WHEN** user switches from one backend to another
- **THEN** system maintains identical behavior for equivalent operations

### Requirement: GoogleAPI SDK backend

The system SHALL provide a backend using google-api-python-client (googleapiclient).

#### Scenario: SDK backend initialization

- **WHEN** user selects 'sdk' backend
- **THEN** system uses googleapiclient.discovery.build() to create Sheets v4 service

#### Scenario: SDK read operation

- **WHEN** SDK backend executes read()
- **THEN** system calls service.spreadsheets().values().get() and returns values array

#### Scenario: SDK write operation

- **WHEN** SDK backend executes write()
- **THEN** system calls service.spreadsheets().values().update() with proper body

#### Scenario: SDK clear operation

- **WHEN** SDK backend executes clear()
- **THEN** system calls service.spreadsheets().values().clear()

#### Scenario: SDK batch read operation

- **WHEN** SDK backend executes batch_read()
- **THEN** system calls service.spreadsheets().values().batchGet() with multiple ranges

#### Scenario: SDK batch write operation

- **WHEN** SDK backend executes batch_write()
- **THEN** system calls service.spreadsheets().values().batchUpdate() with multiple data ranges

#### Scenario: SDK batch clear operation

- **WHEN** SDK backend executes batch_clear()
- **THEN** system calls service.spreadsheets().values().batchClear() with multiple ranges

#### Scenario: SDK error handling

- **WHEN** SDK backend encounters HttpError
- **THEN** system translates to appropriate exception type (PermissionError, NetworkError, etc.)

### Requirement: gspread library backend (REMOVED)

The gspread library backend is **not included** in tdt-sheets. gspread is unmaintained (GitHub notice: "unable to maintain Gspread"), uses API v3 (slower writes), and has no native batch operations. All ecosystem projects are migrating to the SDK backend.

#### Scenario: gspread removal justification

- **WHEN** developer reviews backend options
- **THEN** system documents that gspread was removed due to unmaintained status, API v3 limitations, and slow write performance
- **AND** recommends SDK backend as replacement

#### Scenario: jira-kanban migration from gspread

- **WHEN** jira-kanban-from-spreadsheet migrates to tdt-sheets
- **THEN** system replaces gspread backend with SDK backend
- **AND** adds write capability (previously read-only with gspread)

### Requirement: gws CLI subprocess backend

The system SHALL provide a backend using gws CLI via subprocess execution.

#### Scenario: CLI backend initialization

- **WHEN** user selects 'cli' backend
- **THEN** system verifies gws binary is on PATH

#### Scenario: CLI read operation

- **WHEN** CLI backend executes read()
- **THEN** system runs 'gws sheets +read --spreadsheet ID --range RANGE --format json' and parses output

#### Scenario: CLI write operation

- **WHEN** CLI backend executes write()
- **THEN** system runs 'gws sheets values update' with JSON body via stdin

#### Scenario: CLI clear operation

- **WHEN** CLI backend executes clear()
- **THEN** system runs 'gws sheets values clear' command

#### Scenario: CLI batch read operation

- **WHEN** CLI backend executes batch_read()
- **THEN** system runs multiple 'gws sheets +read' commands sequentially (no native batch in gws)

#### Scenario: CLI batch write operation

- **WHEN** CLI backend executes batch_write()
- **THEN** system runs multiple 'gws sheets values update' commands sequentially

#### Scenario: CLI batch clear operation

- **WHEN** CLI backend executes batch_clear()
- **THEN** system runs multiple 'gws sheets values clear' commands sequentially

#### Scenario: gws not installed

- **WHEN** user selects 'cli' backend but gws binary not found
- **THEN** system raises RuntimeError with installation instructions

#### Scenario: CLI subprocess timeout

- **WHEN** gws CLI command exceeds timeout (default 30s)
- **THEN** system terminates process and raises TimeoutError

#### Scenario: CLI OAuth authentication

- **WHEN** user has gws CLI configured with OAuth (not service account)
- **THEN** system uses existing gws authentication instead of service account

### Requirement: Backend performance characteristics

The system SHALL document performance characteristics of each backend.

#### Scenario: SDK backend performance

- **WHEN** developer reviews documentation
- **THEN** system documents SDK as fastest for direct API calls with lowest overhead

#### Scenario: gspread backend performance (REMOVED)

- **WHEN** developer reviews documentation
- **THEN** system documents that gspread was removed due to unmaintained status and API v3 limitations
- **AND** recommends SDK backend for all new development

#### Scenario: CLI backend performance

- **WHEN** developer reviews documentation
- **THEN** system documents CLI with subprocess overhead, useful for OAuth workflows

### Requirement: Backend dependency isolation

The system SHALL make backend dependencies optional except for the SDK backend.

#### Scenario: Core installation

- **WHEN** user installs tdt-sheets with pip install tdt-sheets
- **THEN** system installs only google-auth and google-api-python-client (SDK backend)

#### Scenario: No optional extras needed

- **WHEN** user installs tdt-sheets with pip install tdt-sheets
- **THEN** system installs only google-auth and google-api-python-client (SDK backend)
- **AND** no optional extras are needed (gspread removed, CLI is external binary)

### Requirement: Backend feature parity

The system SHALL ensure all backends support the same core operations (read, write, clear, batch_read, batch_write, batch_clear).

#### Scenario: Read parity

- **WHEN** same read() call executed on different backends
- **THEN** all backends return identical data structure

#### Scenario: Write parity

- **WHEN** same write() call executed on different backends
- **THEN** all backends produce identical spreadsheet state

#### Scenario: Clear parity

- **WHEN** same clear() call executed on different backends
- **THEN** all backends clear identical ranges

#### Scenario: Batch read parity

- **WHEN** same batch_read() call executed on different backends
- **THEN** all backends return identical dict of range -> values

#### Scenario: Batch write parity

- **WHEN** same batch_write() call executed on different backends
- **THEN** all backends produce identical spreadsheet state

#### Scenario: Advanced features unavailable on some backends

- **WHEN** advanced feature (e.g., formatting) not supported by CLI backend
- **THEN** system documents feature as SDK only and raises NotImplementedError on CLI

### Requirement: Batch operation optimization

The system SHALL optimize batch operations to minimize API calls and respect quota limits.

#### Scenario: SDK batch operation efficiency

- **WHEN** SDK backend executes batch_read() with 10 ranges
- **THEN** system makes 1 API call (batchGet) instead of 10 individual calls

#### Scenario: SDK batch write efficiency

- **WHEN** SDK backend executes batch_write() with 10 ranges
- **THEN** system makes 1 API call (batchUpdate) instead of 10 individual calls

#### Scenario: CLI batch operation fallback

- **WHEN** CLI backend executes batch operations
- **THEN** system makes N sequential subprocess calls (no native batch support)
- **AND** logs warning that CLI backend has higher API call count

#### Scenario: SDK batch operation efficiency

- **WHEN** SDK backend executes batch_read() with 10 ranges
- **THEN** system makes 1 API call (batchGet) instead of 10 individual calls

#### Scenario: SDK batch write efficiency

- **WHEN** SDK backend executes batch_write() with 10 ranges
- **THEN** system makes 1 API call (batchUpdate) instead of 10 individual calls

#### Scenario: CLI batch operation fallback

- **WHEN** CLI backend executes batch operations
- **THEN** system makes N sequential subprocess calls (no native batch support)
- **AND** logs warning that CLI backend has higher API call count
