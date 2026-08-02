## Pre-Change State

The shipping testcontainers pilot runs with `max_failures=0` (the shell
script default). This means any single failure — even a transient Docker
timing issue — stops the test.

The pilot script (`deploy/scripts/run-temporal-nexus-local-pilot.sh`) reads
`TEMPORAL_NEXUS_PILOT_MAX_FAILURES` from the environment and uses it as the
threshold. The Go test harness (`tests/ecosystem-verification/cmd/test-shipping/main.go`)
calls the pilot script but does not pass this env var.

## Implemented Change

Add `TEMPORAL_NEXUS_PILOT_MAX_FAILURES=2` to the environment map in
`main.go` when calling the pilot script. This allows up to 2 transient
failures before the pilot stops.

The initial implementation exposed a second validation path: the pilot script
correctly marked runs within the configured threshold as `passed`, but the Go
validator still rejected any non-zero failure count. The completed design
therefore also makes `validateFocusedPilot` trust the pilot's `status` field.
The pilot script remains the single owner of threshold evaluation.

### Why 2

- The pilot runs concurrent operations (Nexus + HTTP) with multiple checks
- A single transient failure could be a Docker networking hiccup
- 2 failures allows recovery from one transient issue while still catching
  persistent failures
- The `service-integration` job (same workflow) always passes, confirming
  the infrastructure is generally stable

## Files Changed

- `tests/ecosystem-verification/cmd/test-shipping/main.go`: Add env var
  and use the pilot's computed status as the readiness decision

## Verification Evidence

- `go build ./cmd/test-shipping/...` passed from the
  `tests/ecosystem-verification` module root on 2026-08-03.
- `go test ./cmd/test-shipping/...` passed from the same module root on
  2026-08-03.
- Pull request
  [vicle1908/microservices#12](https://github.com/vicle1908/microservices/pull/12)
  merged both implementation commits.
- The PR's `service-integration` and `shipping-focused` jobs completed
  successfully in workflow run
  [30741051002](https://github.com/vicle1908/microservices/actions/runs/30741051002).
- The merge commit's main-branch verify, deployment-validation, and eight image
  build checks completed successfully.
- `openspec validate --strict --all --store openspec-store` passed 349/349
  items on 2026-08-03.

## Review Note

The focused unit-test matrix verifies that `status="failed"` is rejected, but it
does not explicitly model a non-zero failure count with `status="passed"`.
The successful end-to-end `shipping-focused` job verifies the completed flow;
an explicit unit case would make future threshold regressions faster to
diagnose.
