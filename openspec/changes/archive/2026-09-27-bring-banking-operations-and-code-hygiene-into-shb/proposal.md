# Proposal: Bring Banking Operations, Digital Rails, and Code Hygiene into SHB

## Why

Following the initial bootstrap and modernization of the 12 Saigon - Hanoi Bank (SHB) repositories, core execution runtimes (`shb-agent-core`), planning harnesses (`shb-agent-harness`), review engines (`shb-ai-review`), browser automation (`shb-browser-cli`), and the 30-skill catalog (`shb-agent-skills`) were established.

However, an exhaustive capability audit across peer ecosystems (`vds` and `tdt`) reveals critical banking digital rails, transaction reliability primitives, cryptographic security standards, and operational utilities that remain missing in `shb`:

1. **Digital Payment Rails & Utility Biller Hub (`vds` → `shb-agent-core`, `shb-mcp-servers`)**:
   - **VietQR / EMVCo Engine**: Full NAPAS247 standard QR payload generation and parsing with CRC16 validation, merchant account identification, dynamic amount embedding, and bill references.
   - **Utility Biller Presentment & Payment Hub**: Adapter interfaces for public utilities (electricity EVN, water, telecommunications, internet) supporting customer bill lookup, outstanding balance presentment, and bill payment execution.

2. **Advanced Core Banking Operations & Compliance Screening (`shb-agent-core`, `shb-mcp-servers`)**:
   - **Transaction Statement & History Inquiry** (`get_transaction_history`) with Pydantic pagination and date/channel filtering.
   - **Interbank Beneficiary Verification** (`verify_beneficiary_account`) supporting NAPAS247 BIN routing and beneficiary name confirmation.
   - **Fund Transfer Execution with Maker-Checker / Dual-Control Gate** (`initiate_fund_transfer`) requiring cryptographic idempotency tokens and multi-party authorization gates for transactions exceeding compliance thresholds.
   - **Anti-Money Laundering (AML) & Sanction Screening** (`screen_beneficiary`) checking beneficiary accounts and recipient names against SBV watchlists and high-risk sanctions prior to transfer dispatch.
   - **PCI-DSS and SBV Regulatory Audit Logging Middleware** capturing actor identity, masked account PANs, tool parameters, execution latency, and digital signatures on every tool invocation.

3. **Transaction Reliability, Cryptography & Reconciliation (`tdt` → `shb-core`, `shb-tools`)**:
   - **Cryptographic Payload Signing & Verification**: HMAC-SHA256 and RSA-SHA256 request payload signing and verification for banking gateway calls in `shb-core`.
   - **Distributed Idempotency Key Manager**: Deduplication filter in `shb-core` preventing double debits on agent retries or network timeouts using unique UUID idempotency keys.
   - **Compensating Transaction Saga Primitives**: Two-phase commit / compensating rollback state recording ensuring failed transfers trigger automatic reconciliation records.
   - **End-of-Day (EOD) Transaction Reconciliation Worker**: CLI-driven reconciliation engine (`shb-recon`) in `shb-tools` matching internal ledgers against NAPAS/clearing settlement files, detecting orphan records, and generating mismatch reports.

4. **Automated Banking Code Hygiene & Compliance Scanner (`tdt/code-daily-scan` → `shb-tools`)**:
   - Platform-agnostic scanner (`shb-compliance-scan`) auditing all 12 SHB repositories for:
     * Unmasked Primary Account Numbers (PANs), cardholder data, or PII per PCI-DSS.
     * Accidental secret or environment credential leakage (`~/.shb/.env`).
     * Python 3.14 strict typing compliance (`mypy --strict`) and zero deprecated typing constructs.
     * Structured JSON and Markdown audit report generation.

5. **Multi-Repository Documentation & Contract Synchronization (`tdt/agent-docs-sync` → `shb-tools`)**:
   - Automated dispatcher (`shb-docs-sync`) in `shb-tools` ensuring `SPEC_INDEX.md`, README files, OpenAPI endpoints, and `resources/harness-13` validation schemas remain synchronized across all 12 repositories.

## What Changes

- **`shb-core`**:
  - Implement `shb_core.security.crypto`: HMAC-SHA256 and RSA-SHA256 payload signing, signature verification, and secret envelope encryption.
  - Implement `shb_core.idempotency`: Distributed idempotency key filter and memory/Redis deduplication cache.
  - Expose cryptographic and idempotency helpers in `shb-core` public exports.

- **`shb-agent-core`**:
  - Implement typed Pydantic models and tools for VietQR (`generate_vietqr`, `parse_vietqr`).
  - Implement typed Pydantic models and tools for Biller Hub (`query_bill`, `pay_bill`).
  - Implement typed Pydantic models and tools for Banking (`get_transaction_history`, `verify_beneficiary_account`, `initiate_fund_transfer` with dual control, `screen_beneficiary`).
  - Implement `AuditLoggingMiddleware` in `shb_agent.tools.audit` enforcing PCI-DSS and SBV audit trails with masked account numbers.
  - Register all tools in `shb_agent.tools.banking.banking_tools`.
  - Add comprehensive hermetic tests in `tests/test_banking_tools.py`, `tests/test_vietqr.py`, and `tests/test_biller.py`.

- **`shb-mcp-servers`**:
  - Expose VietQR, Biller, Statement, Beneficiary, Transfer, and Sanction screening tools over JSON-RPC stdio and SSE MCP transports.
  - Wire tool definitions and JSON Schema reflection into MCP server handlers.

- **`shb-tools`**:
  - Implement `shb-recon` CLI and module (`src/shb_tools/recon/`): daily settlement and transaction reconciliation engine matching ledger data against clearing statements.
  - Implement `shb-compliance-scan` CLI and module (`src/shb_tools/scanner/`): scans all 12 SHB repositories for unmasked PANs, leaked credentials, AST deprecated syntax, and type check health.
  - Implement `shb-docs-sync` CLI and module (`src/shb_tools/docs_sync/`): synchronizes architecture contracts, README indices, and schema definitions across the ecosystem.
  - Update `pyproject.toml` with console script entrypoints for `shb-recon`, `shb-compliance-scan`, and `shb-docs-sync`.

## Non-Goals

- Ingesting, porting, or deploying Java Spring Boot/Gradle microservices (`vds/SAVING-project`, `EKYC-project`, `LEP-project`, `PAR-project`) — permanently out of scope.
- Ingesting mobile Swift/Kotlin components from `tdt/poems-mobile3-*`.
- Porting stock brokerage/trading logic from `tdt/agent-core`.
- Live connection to production core banking networks during automated testing (all tools run with hermetic offline mock providers and `TestModel`).

## Capabilities

### New Capabilities
- None (extends existing capabilities).

### Modified Capabilities
- `shb-core-foundation`: Adds cryptographic payload signing utilities and distributed idempotency management.
- `shb-agent-runtime`: Adds VietQR engine, Biller payment hub, advanced banking operations, sanction screening, and PCI-DSS/SBV audit logging middleware.
- `shb-mcp-servers`: Extends MCP tool catalog with VietQR, utility biller, and advanced banking tools.
- `shb-ecosystem-tooling`: Adds EOD transaction reconciliation, automated compliance scanning, and multi-repo documentation synchronization into `shb-tools`.

## Impact

- **Security & Regulatory Compliance**: Meets SBV Circular 09/2020 and PCI-DSS requirements for financial transaction auditing, payload integrity, and secret leakage prevention.
- **Digital Banking Capabilities**: Delivers full VietQR, bill presentment, interbank transfer, and reconciliation capabilities.
- **Agent Autonomy**: Enables autonomous coding and review agents to perform realistic banking workflows with strong type safety, cryptographic verification, and approval gates.
- **Repository Health**: Automated daily scans and syncs prevent regressions and maintain contract alignment across the 12 SHB repositories.
