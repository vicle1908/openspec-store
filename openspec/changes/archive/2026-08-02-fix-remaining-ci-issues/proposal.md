## Why

After fixing attestation and catalog contracts, `lgtm-e2e` still failed
due to Docker build/pull race condition and missing env-file interpolation.

## What Changes

- Separate `docker compose build` from `docker compose up` in lgtm-e2e.yml
- Add disk cleanup step to free runner space
- Include `--env-file deploy/tools.env` for variable interpolation
- Fix health check port (13133 HTTP, not 4317 gRPC)
- Replace `make test-e2e` with direct compose smoke run
- Add `--profile smoke` to build step for smoke container

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. CI tooling only.

## Impact

- **Repository surfaces:** `.github/workflows/lgtm-e2e.yml`.
- **Rollout:** Commit and verify LGTM E2E passes on next PR.
