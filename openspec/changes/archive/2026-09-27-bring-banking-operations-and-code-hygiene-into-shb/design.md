# Design: Bring Banking Operations, Digital Rails, and Code Hygiene into SHB

## Context

The Saigon - Hanoi Bank (`shb`) ecosystem consists of 12 decoupled repositories under `~/Developer/shb/` standardized on Python `>=3.14` and `uv`. Following the initial foundation bootstrap, a deep audit of peer ecosystems (`vds` and `tdt`) identified five mission-critical functional areas requiring integration into SHB:
1. **Digital Payment Rails & VietQR Engine**: Generation and EMVCo parsing of standard VietQR (NAPAS247) payment payloads.
2. **Utility Biller Presentment & Payment Hub**: Public utility bill presentment (EVN electricity, water, telecom, internet) and automated payment pipelines.
3. **Advanced Banking Operations & Sanction Screening**: Statement inquiry with pagination, interbank beneficiary verification, fund transfer initiation with maker-checker dual-control approval gates, and AML sanction screening.
4. **Transaction Reliability, Cryptography & Reconciliation**: Payload signing (HMAC/RSA), distributed idempotency deduplication, two-phase commit saga rollback state, and End-of-Day (EOD) transaction reconciliation (`shb-recon`).
5. **Code Hygiene & Contract Synchronization**: Automated banking security/PAN scanner (`shb-compliance-scan`) and multi-repo documentation synchronizer (`shb-docs-sync`).

## Goals / Non-Goals

**Goals:**
- **`shb-agent-core`**:
  - Implement VietQR tools (`generate_vietqr`, `parse_vietqr`) adhering to EMVCo and NAPAS247 standards.
  - Implement Biller Hub tools (`query_bill`, `pay_bill`) supporting electricity, water, and telecom services.
  - Implement Banking Operations tools (`get_transaction_history`, `verify_beneficiary_account`, `initiate_fund_transfer` with dual control, `screen_beneficiary`).
  - Implement `AuditLoggingMiddleware` enforcing PCI-DSS and SBV compliance by masking PANs/account numbers.
- **`shb-core`**:
  - Implement cryptographic utilities (`shb_core.security.crypto`): HMAC-SHA256 and RSA-SHA256 payload signing and verification.
  - Implement distributed idempotency manager (`shb_core.idempotency`) with memory/Redis deduplication caches.
- **`shb-mcp-servers`**:
  - Expose VietQR, Biller, Banking Operations, and Sanction Screening over MCP stdio and SSE transports.
- **`shb-tools`**:
  - Implement `shb-recon` CLI and engine for daily transaction settlement matching.
  - Implement `shb-compliance-scan` CLI for secret detection, PAN masking, clean-break syntax, and type check health.
  - Implement `shb-docs-sync` CLI for multi-repo documentation and schema alignment.
- **Testing**:
  - Maintain 100% test pass rate with hermetic offline evaluation using `TestModel`.

**Non-Goals:**
- Ingesting legacy Java microservices or Gradle builds from `vds`.
- Ingesting brokerage trading logic or mobile Swift/Kotlin code from `tdt`.
- Connecting to live banking networks or live mainframe endpoints during tests.

## Technical Decisions

### Decision 1: VietQR & EMVCo Engine (`shb-agent-core`)

- **Standard**: VietQR specification based on EMVCo QR Code Specification for Payment Systems (Consumer-Presented / Merchant-Presented Mode).
- **Contracts**:
  - `GenerateVietQRQuery`: `account_number: str`, `bank_bin: str` (e.g., `970415`), `amount: float | None = None`, `purpose: str | None = None`, `bill_number: str | None = None`, `is_dynamic: bool = False`.
  - `GenerateVietQRResponse`: `qr_payload: str`, `qr_data_url: str`, `crc_checksum: str`.
  - `ParseVietQRQuery`: `qr_payload: str`.
  - `ParseVietQRResponse`: `bank_bin: str`, `account_number: str`, `amount: float | None`, `purpose: str | None`, `is_valid_crc: bool`, `merchant_name: str | None`.

### Decision 2: Utility Biller Presentment & Payment Hub (`shb-agent-core`)

- **Contracts**:
  - `QueryBillQuery`: `biller_code: str` (e.g. `EVN_HANOI`, `VIETTEL_POSTPAID`, `SAWACO_WATER`), `customer_ref: str`.
  - `QueryBillResponse`: `biller_code: str`, `customer_ref: str`, `customer_name: str`, `period: str`, `amount_due: float`, `status: str` (`UNPAID`, `PAID`, `OVERDUE`).
  - `PayBillQuery`: `source_account: str`, `biller_code: str`, `customer_ref: str`, `amount: float`, `idempotency_key: str`.
  - `PayBillResponse`: `payment_reference: str`, `status: str` (`SUCCESS`, `PENDING`), `receipt_number: str`, `timestamp_utc: datetime`.

### Decision 3: Advanced Banking Operations & Sanction Screening (`shb-agent-core`)

- **Contracts**:
  - `get_transaction_history`: Date filtering, pagination (`limit`, `offset`), running ledger balance.
  - `verify_beneficiary_account`: NAPAS247 routing validation and customer name confirmation.
  - `initiate_fund_transfer`: Enforces idempotency keys; triggers `PENDING_APPROVAL` with `requires_maker_checker=True` for transfers exceeding `50,000,000 VND` without a supervisor token.
  - `screen_beneficiary`: Validates beneficiary account and name against AML watchlists and PEP (Politically Exposed Persons) registers, returning `CLEARED` or `FLAGGED_FOR_MANUAL_REVIEW`.

### Decision 4: Cryptography & Distributed Idempotency (`shb-core`)

- **`shb_core.security.crypto`**:
  - `sign_payload(payload: dict, secret_key: str, algorithm: str = "HMAC-SHA256") -> str`
  - `verify_signature(payload: dict, signature: str, secret_key: str, algorithm: str = "HMAC-SHA256") -> bool`
  - `mask_pan(pan: str) -> str`: Retains first 4 and last 2 digits (`1029****56`).
- **`shb_core.idempotency`**:
  - `IdempotencyManager`: Checks and locks request UUIDs. Prevents concurrent duplicate debit calls on retries.

### Decision 5: End-of-Day Transaction Reconciliation Worker (`shb-tools`)

- CLI: `shb-recon`
- Module: `src/shb_tools/recon/`
- Compares internal transaction ledger against clearing settlement statements (NAPAS/interbank):
  - Flags matching discrepancies (amount mismatch, fee discrepancy).
  - Detects orphan internal transactions (debited but not settled).
  - Generates structured Markdown and JSON reconciliation audit reports.

### Decision 6: Compliance Scanner & Multi-Repo Docs Synchronizer (`shb-tools`)

- **`shb-compliance-scan`**:
  - `SEC-001`: Secret leakage audit outside quarantined paths.
  - `PCI-001`: Unmasked PAN and CVV audit.
  - `SYN-001`: Clean-break syntax and deprecation audit.
  - `TYP-001`: Mypy strict and Ruff checks across all 12 repos.
- **`shb-docs-sync`**:
  - Checks parity between centralized OpenSpec store and individual repository README files and `SPEC_INDEX.md`.

## Risks / Trade-offs

- **[Risk] Sensitive Data in Audit Logs**:
  - *Mitigation*: The `AuditLogger` applies recursive PAN/account masking before serializing log payloads.
- **[Risk] Idempotency Token Collisions in Fund Transfers**:
  - *Mitigation*: The tool contract enforces UUIDv4 / min-length 16 characters for `idempotency_key` and caches seen keys in memory/Redis.
- **[Risk] False Positives in Compliance Scanner**:
  - *Mitigation*: The scanner skips test mock fixtures and test entity definitions containing known synthetic values.
