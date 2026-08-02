## Root cause

Services without `build:` sections tried to pull images from GHCR before
migrate services finished building locally. Docker race condition.

## Fix

1. Disk cleanup: remove unused runner software (android, dotnet, ghc)
2. Separate build from up: `docker compose build --parallel` then `up --no-build`
3. Include `--env-file deploy/tools.env` for all compose commands
4. Fix health check: HTTP 13133, not gRPC 4317
5. Replace `make test-e2e` with direct compose smoke run
6. Add `--profile smoke` to build step
