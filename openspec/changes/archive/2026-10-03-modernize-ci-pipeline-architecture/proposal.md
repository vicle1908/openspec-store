# Proposal: Modernize CI Pipeline Architecture & Registry Resilience

## Why
Analysis of recent pull request runs (PR #41 and PR #42) revealed multiple points of operational friction in the monorepo's CI/CD pipeline:
1. **Unauthenticated Registry Flakiness**: In `lgtm-e2e`, `scripts/verify-images.sh` failed when Docker Hub transiently rate-limited unauthenticated manifest requests for `redis:8.8.1-alpine3.23`. Because the script had no retry loop and checked duplicate image tags (both `REDIS_VERSION` and `REDIS_CLI_VERSION` resolve to the same tag), a single dropped HTTP packet caused the entire 60-minute pipeline to fail.
2. **Manual Documentation Coverage Synchronization**: `tools/doccheck` strictly enforces that statement coverage figures in `docs/local-service-verification.md` match actual test summaries within $\pm 0.5\%$. When unit tests are added or updated to clear the $\ge 80.0\%$ threshold, developers currently have to manually calculate and update the markdown table rows by hand, frequently causing CI failures due to decimal rounding or forgotten service updates.

Modernizing these workflows with automated synchronization and network resilience eliminates pipeline flakiness and accelerates delivery.

## What Changes
- **Resilient Registry Manifest Verification (`scripts/verify-images.sh`)**:
  - Add bounded exponential backoff retry logic (3 attempts with 2s/4s backoff) to `fetch_manifest_via_http` in `scripts/verify-images.sh`.
  - Deduplicate image targets in `IMAGES` array so identical tags (such as `redis:8.8.1-alpine3.23`) are inspected only once per run.
- **Automated Documentation Coverage Parity Tool (`scripts/sync-coverage-docs.py`)**:
  - Implement an automated Python script that reads verified test coverage from `services/*/artifacts/verification/coverage/summary.json` and updates `docs/local-service-verification.md` in place.
  - Wire a new root Make target `make sync-coverage-docs` to allow one-command documentation synchronization.
- **Pre-Push Validation Runbook Integration**:
  - Document pre-push verification checklists in `docs/runbooks/ci-cd-operations.md`.

## Capabilities

### Modified Capabilities
- `platform-verification`: Hardened container manifest verification against registry rate-limiting and added automated coverage documentation synchronization.

## Impact
- **Services Affected**: All 8 microservices (`catalog`, `customer`, `inventory`, `notification`, `order`, `payment`, `reporting`, `shipping`), shared scripts, and documentation.
- **Breaking Changes**: Zero. Public APIs, runtime behavior, and coverage policy gates ($\ge 80.0\%$) remain unchanged.
