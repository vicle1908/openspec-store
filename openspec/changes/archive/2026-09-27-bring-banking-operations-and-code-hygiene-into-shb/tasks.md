# Tasks: Bring Banking Operations, Digital Rails, and Code Hygiene into SHB

## Phase 1: Cryptography & Distributed Idempotency (`shb-core`)

- [x] 1.1 Implement cryptographic payload signing (`sign_payload`), signature verification (`verify_signature`), and account PAN masking (`mask_pan`) in `src/shb_core/security/crypto.py`.
- [x] 1.2 Implement distributed idempotency manager (`IdempotencyManager`) in `src/shb_core/idempotency.py` with memory/Redis deduplication cache and TTL expiration.
- [x] 1.3 Add unit tests in `shb-core/tests/test_crypto.py` and `shb-core/tests/test_idempotency.py` asserting signature verification and duplicate request rejection.

## Phase 2: Banking Domain Tools, VietQR & Biller Hub (`shb-agent-core`)

- [x] 2.1 Author typed Pydantic models for `TransactionHistoryQuery` / `Response` and `BeneficiaryVerificationQuery` / `Response` in `src/shb_agent/tools/banking.py`.
- [x] 2.2 Author typed Pydantic models for `FundTransferInitiationQuery` / `Response` supporting idempotency tokens and maker-checker approval gates (threshold > 50,000,000 VND).
- [x] 2.3 Author typed Pydantic models for VietQR generation (`GenerateVietQRQuery` / `Response`) and EMVCo parsing (`ParseVietQRQuery` / `Response`) in `src/shb_agent/tools/vietqr.py`.
- [x] 2.4 Author typed Pydantic models for Biller Hub (`QueryBillQuery` / `Response`, `PayBillQuery` / `Response`) in `src/shb_agent/tools/biller.py`.
- [x] 2.5 Author typed Pydantic models for Sanction Screening (`SanctionScreeningQuery` / `Response`) in `src/shb_agent/tools/compliance.py`.
- [x] 2.6 Implement `AuditLoggingMiddleware` in `src/shb_agent/tools/audit.py` with automatic PAN masking and structured JSON audit logging per PCI-DSS and SBV standards.
- [x] 2.7 Register all new tools in `shb_agent.tools.banking.banking_tools` and add comprehensive hermetic unit tests in `tests/`.

## Phase 3: Model Context Protocol Tool Exposure (`shb-mcp-servers`)

- [x] 3.1 Register VietQR, Biller, Statement, Beneficiary, Transfer, and Sanction screening tools in `shb_mcp.tools`.
- [x] 3.2 Wire tool definitions and JSON Schema reflection into the MCP server handlers in `src/shb_mcp/server.py`.
- [x] 3.3 Add unit tests in `shb-mcp-servers/tests/test_tools.py` asserting JSON-RPC 2.0 tool execution and parameter schema correctness.

## Phase 4: EOD Transaction Reconciliation Engine (`shb-tools`)

- [x] 4.1 Implement reconciliation engine in `src/shb_tools/recon/` matching internal transaction ledger against clearing settlement statements.
- [x] 4.2 Implement `shb-recon` CLI command in `src/shb_tools/cli.py` (`run`, `status`, `diff`, `export`) and register entrypoint in `pyproject.toml`.
- [x] 4.3 Add unit tests in `shb-tools/tests/test_recon.py` verifying discrepancy detection and report generation.

## Phase 5: Automated Compliance Scanner & Multi-Repo Docs Sync (`shb-tools`)

- [x] 5.1 Implement compliance scanning engine in `shb-tools/src/shb_tools/scanner/`:
  - Rule `SEC-001`: Detect accidental `.env` keys, RSA/SSH keys, and hardcoded secrets.
  - Rule `PCI-001`: Detect unmasked PANs (credit card numbers / account numbers) in non-fixture files.
  - Rule `SYN-001`: Detect deprecated Python 3.12/3.13 typing and standard library constructs.
  - Rule `TYP-001`: Execute and verify strict `mypy` and `pytest` statuses.
- [x] 5.2 Implement `shb-compliance-scan` CLI command in `src/shb_tools/cli.py` and register entrypoint in `pyproject.toml`.
- [x] 5.3 Implement documentation and schema synchronizer in `src/shb_tools/docs_sync/` and CLI command `shb-docs-sync`.
- [x] 5.4 Add unit tests in `shb-tools/tests/test_compliance_scanner.py` and `shb-tools/tests/test_docs_sync.py`.

## Phase 6: Verification & OpenSpec Strict Validation

- [x] 6.1 Execute `uv run pytest` across `shb-core`, `shb-agent-core`, `shb-mcp-servers`, and `shb-tools` asserting 100% test passing.
- [x] 6.2 Execute `uv run ruff check` and `uv run mypy` across modified repositories with zero violations.
- [x] 6.3 Validate the change strictly via `openspec validate bring-banking-operations-and-code-hygiene-into-shb --strict --store openspec-store`.
