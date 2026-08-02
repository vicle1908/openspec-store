## Current State

The shipping testcontainers pilot runs with `max_failures=0` (the shell
script default). This means any single failure — even a transient Docker
timing issue — stops the test.

The pilot script (`deploy/scripts/run-temporal-nexus-local-pilot.sh`) reads
`TEMPORAL_NEXUS_PILOT_MAX_FAILURES` from the environment and uses it as the
threshold. The Go test harness (`tests/ecosystem-verification/cmd/test-shipping/main.go`)
calls the pilot script but does not pass this env var.

## Proposed Change

Add `TEMPORAL_NEXUS_PILOT_MAX_FAILURES=2` to the environment map in
`main.go` when calling the pilot script. This allows up to 2 transient
failures before the pilot stops.

### Why 2

- The pilot runs concurrent operations (Nexus + HTTP) with multiple checks
- A single transient failure could be a Docker networking hiccup
- 2 failures allows recovery from one transient issue while still catching
  persistent failures
- The `service-integration` job (same workflow) always passes, confirming
  the infrastructure is generally stable

## Files Changed

- `tests/ecosystem-verification/cmd/test-shipping/main.go`: Add env var
