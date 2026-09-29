# shb-mcp-servers Specification Delta

## Purpose
Specifies additions to the `shb-mcp-servers` package for exposing digital payment rails (VietQR), utility biller payment hubs, advanced banking operations, AML sanction screening, and reconciliation status over Model Context Protocol (MCP) JSON-RPC 2.0 stdio and SSE transports.

## ADDED Requirements

### Requirement: Expanded Banking and Digital Payment Tool Exposure via Model Context Protocol
The `shb-mcp-servers` package SHALL expose advanced banking operations (`get_transaction_history`, `verify_beneficiary_account`, `initiate_fund_transfer`), VietQR digital payment tools (`generate_vietqr`, `parse_vietqr`), and AML sanction screening (`screen_beneficiary`) through the Model Context Protocol tool catalog, providing complete input and output JSON Schema reflection.

#### Scenario: VietQR discovery and execution via MCP
- **WHEN** an MCP client issues `tools/call` for `generate_vietqr` or `parse_vietqr`
- **THEN** the MCP server executes the underlying generator/parser and returns the EMVCo-compliant QR payload, CRC16 verification, and beneficiary bank routing

#### Scenario: Transaction statement discovery and execution via MCP
- **WHEN** an MCP client issues `tools/list`
- **THEN** the server returns `get_transaction_history` with parameter schemas for account number, date range, pagination limits, and channel filtering
- **AND** executing `tools/call` for `get_transaction_history` returns structured JSON transaction records

#### Scenario: Beneficiary verification and sanction screening via MCP
- **WHEN** an MCP client issues `tools/call` for `verify_beneficiary_account` or `screen_beneficiary`
- **THEN** the server routes the query through NAPAS247 validation and AML watchlist checks, returning customer identity and clearance flags

#### Scenario: Fund transfer initiation with dual-control status via MCP
- **WHEN** an MCP client issues `tools/call` for `initiate_fund_transfer`
- **THEN** the server enforces idempotency keys and reports maker-checker approval state (`COMPLETED` or `PENDING_APPROVAL`) per compliance rules

### Requirement: Utility Biller and Reconciliation Tool Exposure
The `shb-mcp-servers` package SHALL expose public utility bill inquiry (`query_bill`), utility bill payment (`pay_bill`), and settlement reconciliation status query tools to connected AI coding agents.

#### Scenario: Utility bill inquiry and payment via MCP
- **WHEN** an MCP agent issues `tools/call` for `query_bill` or `pay_bill`
- **THEN** the server connects to the utility biller adapter, validates customer reference numbers, and returns bill status or payment receipts
