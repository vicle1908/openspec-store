## Context

All service unit suites pass without special tags, and deployment validation is
green, but the repository code gate remains red. Current aggregate statement
coverage is order 57.2%, notification 25.9%, customer 27.9%, catalog 21.3%,
reporting 21.6%, payment 18.3%, inventory 40.2%, and shipping 37.7%.
Inventory and shipping advertise required fuzz targets without implementations.
Order, customer, and reporting generated-contract checks use a pinned remote Buf
plugin whose anonymous BSR quota currently prevents reproducible local runs.

## Goals / Non-Goals

**Goals:**

- Make every service's default local `verify-pr` pass at the real threshold.
- Measure a numeric aggregate once and retain package detail without masking
  test failures as zero coverage or parsing command output as a percentage.
- Add meaningful boundary fuzzing with deterministic regression corpora.
- Make contract lint/build/generation checks pinned, reproducible, and
  fail-closed while distinguishing source incompatibility from remote quota.
- Keep architecture and live-stack tests correctly isolated under trimpath and
  build tags.

**Non-Goals:**

- Hosted CI schedules, cloud deployment, production promotion, or runtime
  feature work.
- Lowering the existing coverage target or marking missing suites as skipped.
- Changing protobuf wire contracts merely to simplify generation.

## Decisions

1. Keep 80% aggregate coverage as the immediate local gate and report the finer
   package/layer targets alongside it. Raising coverage proceeds from domain and
   application behavior outward to adapters/runtime; generated files and
   migrations are excluded only through one documented policy.

2. Use table-driven unit tests for deterministic logic, in-process HTTP tests
   for handlers, explicit fakes for ports, and container-tagged tests only for
   real infrastructure. Tests MUST NOT contact local services in the default
   unit command.

3. Inventory and shipping receive native Go fuzz targets with committed seed
   corpora and separate bounded regression/short-fuzz commands. A missing fuzz
   suite remains a gate failure.

4. Contract verification separates `buf lint` and `buf build` from generated
   output comparison. Remote plugins remain pinned; local bootstrap SHALL
   support authenticated BSR access or an officially supported cached/local
   plugin path. A quota failure is reported as external tooling failure, never
   contract success.

5. Every Makefile target propagates the real exit code and emits concise,
   machine-readable evidence. Threshold overrides are diagnostic-only and MUST
   NOT alter the default gate.

## Risks / Trade-offs

- [Coverage-driven tests assert implementation details] → Prefer externally
  observable behavior, domain invariants, and port contracts.
- [Parallel tests expose shared-state flakes] → Run shuffled and race variants;
  remove ordering assumptions rather than pinning test order.
- [Generated code changes across plugin versions] → Pin plugin versions and
  compare generated output from a clean deterministic invocation.
- [Remote Buf service remains unavailable] → Preserve lint/build where possible
  and report generation as blocked; never silently bypass it.

## Migration Plan

Close one service at a time, retaining its baseline and final coverage report.
Add fuzz suites before enabling their targets, then standardize contract
tooling. Finish with all service gates, root `make verify-pr`, strict OpenSpec
validation, and local deployment validation. Rollback affects only tests and
developer tooling.

## Resolved Questions

- Use Buf's officially supported local-plugin path with repository-local,
  version-pinned `buf` and `protoc-gen-go` executables. This removes remote
  registry quota and authentication from normal generation without committing
  credentials. Remote-tool failures remain classified and fail closed.
