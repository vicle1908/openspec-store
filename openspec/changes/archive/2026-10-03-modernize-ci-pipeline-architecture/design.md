# Design: Modernize CI Pipeline Architecture & Registry Resilience

## Architecture Overview
This change addresses operational friction in monorepo PR and E2E verification pipelines by introducing:
1. Resilient registry manifest inspection with bounded exponential backoff retries and image target deduplication in `scripts/verify-images.sh`.
2. Mechanical documentation coverage parity synchronization (`scripts/sync-coverage-docs.py` / `make sync-coverage-docs`) reading machine-readable test summaries.
3. Pre-push developer verification runbooks.

---

## Detailed Component Design

### 1. Resilient Registry Verification (`scripts/verify-images.sh`)
- **Exponential Backoff**: Wrap `fetch_manifest_via_http` in a loop of 3 attempts with progressive sleep (2s, 4s) when `curl` fails or returns empty/error responses.
- **Image Deduplication**: In `scripts/verify-images.sh`, sanitize the `IMAGES` array using an associative array / deduplication filter before iterating:
  ```bash
  declare -A seen_images
  UNIQUE_IMAGES=()
  for img in "${IMAGES[@]}"; do
    if [[ -z "${seen_images[$img]:-}" ]]; then
      seen_images["$img"]=1
      UNIQUE_IMAGES+=("$img")
    fi
  done
  ```
  This eliminates redundant queries for identical tags (such as `redis:8.8.1-alpine3.23` shared by `REDIS_VERSION` and `REDIS_CLI_VERSION`).

### 2. Automated Coverage Documentation Synchronization (`scripts/sync-coverage-docs.py`)
- **Artifact Intake**: Reads verified JSON summary files from:
  `services/<service>/artifacts/verification/coverage/summary.json`
- **Percentage Formatting**: Formats statement coverage percentages with one decimal place (`{val:.1f}%`).
- **Markdown Target**: Matches the Markdown table in `docs/local-service-verification.md`:
  `| <service> | ... | <percentage>% | ... |`
  and replaces the documented figures in-place.
- **Make Target**: Integrates `make sync-coverage-docs` into the root `Makefile` so developers and agents can synchronize documentation with a single command before committing.

### 3. Integration with `tools/doccheck`
- `tools/doccheck` continues to validate that documented coverage matches `summary.json` within $\pm 0.5\%$.
- `make sync-coverage-docs` guarantees 0.0% delta, completely eliminating documentation drift failures in CI.
