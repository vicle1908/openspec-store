# shb-agent-runtime Specification Delta

## Purpose
Specifies additions to the `shb-agent-core` runtime for digital payment rails (VietQR), utility biller payment hubs, advanced banking operations, maker-checker dual-control approval gates, AML sanction screening, and regulatory audit logging middleware.

## ADDED Requirements

### Requirement: VietQR and EMVCo Digital Payment Rails
The `shb-agent-core` tool registry SHALL provide typed Pydantic tools for VietQR code generation (`generate_vietqr`) and EMVCo QR code payload parsing (`parse_vietqr`) conforming to NAPAS247 standards.

#### Scenario: Dynamic VietQR generation with embedded amount
- **WHEN** an agent invokes `generate_vietqr` with account number, bank BIN, amount, and payment reference
- **THEN** the tool returns a schema-validated `GenerateVietQRResponse` containing the standardized EMVCo payload string, CRC16 checksum, and QR data URL

#### Scenario: VietQR payload parsing and validation
- **WHEN** an agent invokes `parse_vietqr` with an EMVCo QR string
- **THEN** the tool parses merchant account information, beneficiary bank BIN, transaction amount, and verifies the CRC16 checksum

### Requirement: Utility Biller Presentment and Payment Hub
The `shb-agent-core` tool registry SHALL provide typed Pydantic tools for public utility bill inquiry (`query_bill`) and payment execution (`pay_bill`) across electricity, water, telecom, and internet categories.

#### Scenario: Utility bill inquiry
- **WHEN** an agent invokes `query_bill` with a biller code (e.g. `EVN_HANOI`, `SAWACO_WATER`) and customer reference
- **THEN** the tool queries bill presentment and returns the customer name, billing period, and outstanding amount due

#### Scenario: Utility bill payment execution
- **WHEN** an agent invokes `pay_bill` with source account, biller code, customer reference, amount, and an idempotency key
- **THEN** the tool debits the source account, settles the utility bill, and returns a verified payment reference and timestamp

### Requirement: Advanced Banking Domain Operations
The `shb-agent-core` tool registry SHALL provide typed Pydantic tools for transaction history statement inquiry (`get_transaction_history`), interbank beneficiary account verification (`verify_beneficiary_account`), and fund transfer initiation (`initiate_fund_transfer`).

#### Scenario: Transaction statement inquiry with pagination
- **WHEN** an agent invokes `get_transaction_history` with account number, date range, and pagination parameters (`limit`, `offset`)
- **THEN** the tool returns a schema-validated `TransactionHistoryResponse` containing a paginated list of transaction records and total count

#### Scenario: Interbank beneficiary account verification
- **WHEN** an agent invokes `verify_beneficiary_account` with a beneficiary bank code and account number
- **THEN** the tool validates the account format, checks bank routing against NAPAS247 network specifications, and returns the verified beneficiary customer name

#### Scenario: Fund transfer initiation with dual-control maker-checker
- **WHEN** an agent invokes `initiate_fund_transfer` for an amount exceeding 50,000,000 VND without a supervisor approval token
- **THEN** the tool marks the transaction as `PENDING_APPROVAL` with `requires_maker_checker=True`
- **AND** requires a valid `supervisor_approval_token` before finalizing execution

#### Scenario: Idempotency token enforcement
- **WHEN** an agent initiates a fund transfer with an idempotency key
- **THEN** the system validates that the key has minimum length 16 and prevents duplicate processing for identical idempotency tokens

### Requirement: AML and Sanction Screening
The `shb-agent-core` tool registry SHALL provide a typed tool (`screen_beneficiary`) to check beneficiary accounts and recipient names against State Bank of Vietnam (SBV) regulatory watchlists and high-risk sanctions prior to transaction execution.

#### Scenario: Beneficiary clearance screening
- **WHEN** an agent screens a beneficiary prior to transfer dispatch
- **THEN** the screening tool matches the entity against watchlist databases and returns clearance status `CLEARED` or `FLAGGED_FOR_MANUAL_REVIEW`

### Requirement: Regulatory Audit Logging Middleware
The `shb-agent-core` runtime SHALL intercept and log all domain banking and payment tool executions through an immutable audit logging middleware enforcing State Bank of Vietnam (SBV) and PCI-DSS compliance standards.

#### Scenario: Account and card number masking in audit logs
- **WHEN** any banking or payment tool executes
- **THEN** the audit logger records structured JSON containing timestamp UTC, actor ID, tool name, execution latency, and sanitized arguments where account numbers and PANs are masked (retaining only first 4 and last 2 digits)
