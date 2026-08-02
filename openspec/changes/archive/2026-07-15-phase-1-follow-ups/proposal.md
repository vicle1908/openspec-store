## Why

The Order Service MVP change (`order-service-mvp`) shipped every in-scope task as
`[x]` and produced a green `make verify-pr` evidence run. Three normative
expectations were documented in the MVP as intentionally deferred follow-ups
because they only become meaningful once the MVP has at least one tagged
release: the optional Kafka broker-UI tooling profile (task 13.5), release-tier
evidence retention (task 17.4.3), and a rehearsed application rollback against
the first tagged image (task 17.11). The MVP design doc and traceability
manifest already treat these as required normative requirements; this change
turns them into executable gates so the first tagged release of the Order
Service can be cut against the same evidentiary discipline that protected the
PR gate.

## What Changes

- Pin a Kafka broker UI image and add `deploy/docker-compose.tools.yaml`
  exposing it under the existing `tools` Compose profile so local
  investigation can introspect topics, consumer groups, and schema state
  without touching the runtime stack.
- Extend `Makefile`'s `verify-images` target to cover the new broker-UI image
  with the same `linux/arm64` manifest check, so the pin is rejected if the
  chosen tag lacks a native arm64 build.
- Add a release-cadence GitHub Actions job (`release-evidence`) that runs
  `make verify-release`, uploads the per-SHA evidence directory with
  `retention-days: 365`, and fails on any reachable High/Critical vulnerability
  or stale exception.
- Author `docs/runbooks/rollback.md` describing the rehearsal procedure
  (start prior image + prior-schema database + prior event fixtures + in-flight
  Temporal histories, cut candidate forward, validate expanded schema, prove
  no business-effect loss). Add `make test-rollback-rehearsal` that exercises
  the script against a pinned prior-tag fixture.
- Extend `verification/traceability.yaml` so the three deferred verification
  IDs are mapped to concrete tests and are flagged `planned → implemented` as
  each task lands. The release-cadence job SHALL block on
  `verify-traceability` reporting zero unmapped scenarios that match
  `release-cadence` scope.

No backwards-incompatible contract, schema, or wire-format change is
introduced.

## Capabilities

### New Capabilities

- `release-cadence-pipeline`: a GitHub Actions workflow that runs the full
  release verification on tag pushes, publishes year-long evidence, and gates
  the tag on the rollback-rehearsal artifact. Owned by `platform-verification`.
- `rollback-rehearsal`: an executable rehearsal that proves a candidate build
  can be rolled back against the prior image, prior schema, prior fixtures,
  and prior Temporal histories without data loss. Owned by
  `platform-verification`.
- `compose-tools-profile`: a `deploy/docker-compose.tools.yaml` overlay that
  activates a Kafka broker UI (and any future optional tooling) behind the
  existing `tools` profile, with arm64 image validation. Owned by
  `platform-extensibility`.

### Modified Capabilities

- `platform-verification`: add a `Release evidence retention` requirement
  (`retention-days: 365`), a `Release gate requires rollback rehearsal`
  requirement (first-tag rehearsal is mandatory), and a `Release-cadence job
  executes verify-release` requirement. Implementation lands via delta specs.
- `platform-extensibility`: add a `Broker UI tools profile` requirement that
  pins the broker UI image, declares its `linux/arm64` manifest, scopes the
  profile to non-runtime inspection, and forbids it from influencing health
  or readiness. Implementation lands via delta specs.

## Impact

- New files:
  - `deploy/docker-compose.tools.yaml` (Compose tools overlay)
  - `.github/workflows/release-evidence.yml` (release-cadence CI job)
  - `docs/runbooks/rollback.md` (rollback runbook)
  - `scripts/rehearse-rollback.sh` (rehearsal driver)
  - `openspec/changes/phase-1-follow-ups/specs/{release-cadence-pipeline,rollback-rehearsal,compose-tools-profile}/spec.md`
  - `openspec/changes/phase-1-follow-ups/specs/{platform-verification,platform-extensibility}/spec.md` (delta specs)
- Modified files:
  - `Makefile` — extend `verify-images` to include the broker-UI image;
    add `test-rollback-rehearsal` target.
  - `verification/traceability.yaml` — register the three new verification IDs.
  - `verification/tools.env` — pin `KAFKA_UI_VERSION` once approved.
  - `deploy/docker-compose.yaml` — no change; the placeholder comment already
    declares the tools profile contract.
- New optional dependency: a Kafka broker-UI image (e.g., `provectuslabs/kafka-ui`
    or `apache/kafka-ui`); the exact tag is pinned only after
    `docker manifest inspect` confirms `linux/arm64`. Pinned in this change's
    `design.md`.
- CI surface: adds one workflow (`release-evidence.yml`) gated on tag pushes;
  leaves `pull-request` and `nightly` untouched. No PR-side latency change.
- Operations: the first tagged release (`v0.2.0` or later) MUST pass the new
  release-cadence job, including the rollback-rehearsal target, before the
  tag is considered shippable.