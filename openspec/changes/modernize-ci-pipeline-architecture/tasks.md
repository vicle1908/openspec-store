# Tasks: Modernize CI Pipeline Architecture & Registry Resilience

## 1. Registry Manifest Resilience (`scripts/verify-images.sh`)

- [ ] 1.1 Add 3-attempt exponential backoff retry loop in `fetch_manifest_via_http` inside `scripts/verify-images.sh` to absorb transient Docker Hub connection drops and 429 rate-limiting
- [ ] 1.2 Deduplicate image targets in `IMAGES` array in `scripts/verify-images.sh` before inspection so identical tags are not queried multiple times
- [ ] 1.3 Verify `scripts/verify-images.sh --verbose` passes locally with exit code 0

## 2. Automated Coverage Documentation Synchronization (`scripts/sync-coverage-docs.py`)

- [ ] 2.1 Implement `scripts/sync-coverage-docs.py` to parse `services/*/artifacts/verification/coverage/summary.json` and update `docs/local-service-verification.md` in-place
- [ ] 2.2 Wire `sync-coverage-docs` target into root `Makefile`
- [ ] 2.3 Run `make sync-coverage-docs` and verify `make validate-documentation` passes with zero delta

## 3. Pre-Push Validation Guidelines & Documentation

- [ ] 3.1 Document deterministic pre-push verification protocol in `docs/runbooks/ci-cd-operations.md`
- [ ] 3.2 Verify `make validate-agent-guidance` passes (50/50 checks, word counts $\le 550$)
- [ ] 3.3 Verify git diff hygiene (`git diff --check`)

## 4. OpenSpec Lifecycle & Delivery

- [ ] 4.1 Validate OpenSpec change strictly: `openspec validate modernize-ci-pipeline-architecture --strict --store openspec-store`
- [ ] 4.2 Commit and push changes in `openspec-store` and `go-microservices`
- [ ] 4.3 Open PR, verify CI pipeline passes, and merge to `main`
