## Context

The Order Service MVP (`order-service-mvp`) shipped its full task list as
`[x]` with a green `make verify-pr` evidence run. The MVP `design.md` and
`tasks.md` explicitly deferred three normative expectations to a follow-up
change because they only become meaningful once the MVP has at least one
tagged release:

- **Task 13.5** — Optional broker UI behind a `tools` Compose profile. The
  placeholder comment in `deploy/docker-compose.yaml` (lines 273-289) names
  `provectuslabs/kafka-ui` as the intended image but the file does not yet
  declare the service. The MVP notes "no arm64-compatible immutable tag
  has been recorded in `verification/tools.env` yet, so the service is
  intentionally omitted." The note predates the project's decision to favor
  maintained images.
- **Task 17.4.3** — Release-tier evidence retention. The MVP
  `platform-verification` spec line 53 already requires "release evidence
  for at least one year." The existing `.github/workflows/verify.yml`
  publishes only `pull-request` and `nightly` artifacts with
  `retention-days: 30`; there is no `release` workflow job, and no
  retention policy enforces the 365-day promise.
- **Task 17.11** — Rehearsed rollback for the first tagged release. The MVP
  `tasks.md` evidence row states "A rehearsed rollback against a previous
  image and in-flight histories is queued for the first tagged release and
  is documented in `docs/runbooks/rollback.md`." The file
  `docs/runbooks/rollback.md` does not exist.

`platform-verification` already requires the release gate to fail on any
unmapped normative scenario or expired exception. This change closes the
three documented gaps so the first tagged release can be cut against the
same evidentiary discipline that protected the PR gate.

### Image research (broker UI)

The MVP placeholder references `provectuslabs/kafka-ui`. As of 2026-07-15:

| Image | Status | Native `linux/arm64` |
|-------|--------|----------------------|
| `provectuslabs/kafka-ui:v0.7.2` | Last push > 2 years ago; project unmaintained | Yes (digest `d8cc95d7a6df`) |
| `kafbat/kafka-ui:v1.5.0` | Maintained successor (community fork), 1M+ pulls, last release 3 months ago | Yes (digest `3928503e8b05`) |
| `kafbat/kafka-ui:latest` | Floating mutable tag — disallowed by the MVP `verify-images` contract | Yes, but mutable |

The MVP rule (`verify-images` plus `verification/traceability.yaml` coverage)
requires an immutable tag. The design therefore adopts `kafbat/kafka-ui`
and pins the immutable short-SHA tag `kafbat/kafka-ui:1.5.0` (sha
`2fc9a60b223d` for amd64 / `3928503e8b05` for arm64), recorded as
`KAFKA_UI_VERSION=1.5.0` in `verification/tools.env`. The placeholder
comment in `deploy/docker-compose.yaml` is updated to reflect this.

## Goals / Non-Goals

**Goals:**

- Land the broker-UI tools profile so local developers can introspect
  Kafka state without touching the runtime stack.
- Land a release-cadence CI workflow that publishes year-long evidence
  for tagged releases and blocks merges of unsafe tags.
- Land an executable rollback-rehearsal driver plus runbook so the first
  tagged release proves forward compatibility against the prior image,
  prior schema, prior fixtures, and in-flight Temporal histories.
- Extend `verify-images` and `verify-traceability` to cover the new
  verification IDs so the gaps cannot reopen silently.

**Non-Goals:**

- No new Kafka UI features beyond what `kafbat/kafka-ui:v1.5.0` already
  ships. Custom plugins or themes are out of scope.
- No production HA broker-UI deployment. The UI is local-development only,
  under the `tools` profile, with no health/readiness influence.
- No production rollback automation. The rehearsal proves a rollback is
  possible against a pinned prior fixture; the actual production rollback
  remains a runbook-driven operational decision.
- No changes to the MVP's pinned broker, Debezium, or Temporal versions.
  The Kafka UI never reads or writes through the runtime stack — it is a
  read-only inspection tool.

## Decisions

### D1. Adopt `kafbat/kafka-ui:v1.5.0` as the pinned broker-UI image

**Rationale.** The MVP placeholder pointed at the unmaintained
`provectuslabs/kafka-ui` (last push > 2 years). `kafbat/kafka-ui` is the
actively maintained community fork with a recent immutable release,
native `linux/arm64` support, and 1M+ Docker Hub pulls. Pinning the
short-SHA tag `kafbat/kafka-ui:1.5.0` is consistent with the MVP rule
that optional tool images require immutable tags plus a manifest check.

**Alternatives considered.**

- `provectuslabs/kafka-ui:v0.7.2` — same digest as `latest`; unmaintained;
  no security patches since 2024. Rejected.
- `provectuslabs/kafka-ui:latest` — mutable, disallowed by `verify-images`.
  Rejected.
- Floating SHA `kafbat/kafka-ui:b460095` — current build, but 7-day-old
  short SHA moves with every CI rebuild. Pinned-SHA tags are auditable
  but require constant rotation. Rejected in favor of the versioned tag.
- Build the UI in-repo — out of scope; the UI is purely for local
  investigation and never runs in production. Rejected.

### D2. Add the broker UI under a separate overlay (`deploy/docker-compose.tools.yaml`)

**Rationale.** The MVP design rule ("Local Compose is not production
topology") plus the existing `tools` profile placeholder in
`deploy/docker-compose.yaml` establish the convention that optional
inspection tooling lives in an overlay, activated only when the developer
passes `--profile tools`. A separate overlay keeps the runtime stack
clean, makes the activation explicit, and isolates the broker-UI's
configuration from the runtime services.

**Alternatives considered.**

- Adding the service directly to `deploy/docker-compose.yaml` with
  `profiles: ["tools"]`. Works, but mixes optional tooling with required
  runtime services in the same file. Rejected because the MVP design
  chose overlays.
- Adding the broker UI to the test overlay. Wrong profile — the test
  overlay drives `make test-integration`, which must remain
  deterministic and free of human-inspection tooling. Rejected.

### D3. New `release-evidence.yml` workflow runs `verify-release` on tag pushes and stores evidence for 365 days

**Rationale.** The MVP `platform-verification` line 53 already requires
year-long release retention. Without a release-cadence job, the
requirement is unenforced. A separate workflow keeps `verify.yml`
(PR + nightly) untouched and isolates the heavy release jobs.

**Alternatives considered.**

- Adding `release` to `verify.yml`. Couples release-only steps to PR and
  nightly runs; harder to gate on tags-only; harder to retain release
  evidence longer than the workflow's shared `actions/upload-artifact@v5`
  defaults. Rejected.
- External retention bucket (S3/GCS) — the MVP evidence index already
  defers "CI pipeline that owns the artifact bucket." That policy lives
  outside the repo and is out of scope for this change. The workflow
  uses `actions/upload-artifact@v5` with `retention-days: 365` as the
  in-repo enforcement step.

### D4. Rollback rehearsal uses the MVP's existing previous-release fixture mechanism

**Rationale.** Tasks 6.6, 14.7, and 17.6.2 all deferred
"previous-release fixture" coverage until the v0.2.0 release exists.
Rather than duplicate a fixture mechanism, the rehearsal reuses the
shape those tasks established: a frozen `proto-baseline/v0.1.0/`
directory (or a sibling fixture directory once it exists), a
`migrations-prev` snapshot, and a Temporal history fixture
(`testdata/temporal-histories/<prev-tag>/`).

**Alternatives considered.**

- Generate fixtures on the fly. Defeats reproducibility. Rejected.
- Replay only the smoke stack without a pinned prior image. The MVP
  requirement is "previous compatible image, expanded schema, prior
  event fixtures, and in-flight Temporal histories." Half of that is
  already covered; the missing piece is the pinned prior image. Rejected
  as incomplete.

### D5. Failure mode: release-evidence job records the rehearsal outcome in the traceability manifest, not in a separate exception file

**Rationale.** The MVP `verify-traceability` already reports unmapped
scenarios and forbidden skips. A failed rehearsal MUST surface as a
`planned` verification entry, not a generic exception, so the gate
fails explicitly.

**Alternatives considered.** None considered — this is the same pattern
the MVP used for 17.4.3 and 17.11.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| `kafbat/kafka-ui` upstream silently changes their pin convention | Image fails `verify-images` on the next release rotation | Pin the immutable tag and digest in `verification/tools.env`; track upstream releases through `verify-images` |
| Release-evidence workflow fails on a slow integration run | Release tag publish is delayed | `verify-release` already runs under a 90-minute budget (CI) and uses the same `make` targets the PR gate uses; no new test surface added |
| Rollback rehearsal requires a real prior release to be meaningful | First tagged release cannot pass the rehearsal gate | The rehearsal driver is **wiring-only** for v0.2.0; `verify-rollback-rehearsal` reports `planned` until a v0.1.0 fixture exists. The release-evidence job records the rehearsal outcome and blocks the tag if `planned` items remain |
| `docker-compose.tools.yaml` drifts from `docker-compose.yaml` | Local developers see stale broker endpoint | The overlay mounts the same Docker network and reads `${KAFKA_UI_VERSION}` from `verification/tools.env`; `make verify-images` re-checks the pinned tag on every CI run |
| Retention policy differs between GitHub artifact store and any future external bucket | A future migration to S3/GCS breaks the 365-day promise | `release-evidence.yml` is the source of truth for retention enforcement in-repo; the bucket-migration work is its own follow-up change (already noted in MVP 17.4.3 evidence row) |

## Migration Plan

1. **Phase 0 (this change, no data migration).**
   - Add `deploy/docker-compose.tools.yaml` with the broker-UI service.
   - Pin `KAFKA_UI_VERSION=1.5.0` in `verification/tools.env`.
   - Extend `verify-images` to check `kafbat/kafka-ui:${KAFKA_UI_VERSION}`.
   - Update the placeholder comment in `deploy/docker-compose.yaml` to
     point to the overlay.
   - Add `.github/workflows/release-evidence.yml`.
   - Add `docs/runbooks/rollback.md` and `scripts/rehearse-rollback.sh`.
   - Add `verification/traceability.yaml` entries for the three new IDs.
2. **Phase 1 (first tagged release).**
   - Cut v0.2.0 tag against `main`.
   - `release-evidence.yml` runs on `v*` push.
   - Rollback-rehearsal driver runs against the v0.1.0 fixture (when one
     exists). Until a v0.1.0 fixture exists, the rehearsal target reports
     `planned` and the change records the gap explicitly.
3. **Rollback.** No prior-image rollback is required because no
   production deployment exists yet. The rehearsal driver itself is the
   proof of concept for the future production rollback path.

## Open Questions

- Should `release-evidence.yml` require a human approval gate before
  publishing the year-long artifact (e.g. a `production` environment
  with required reviewers)? The MVP `docs/local-vs-production.md` does
  not specify; resolved as `not required` for v0.2.0, but documented for
  the v0.3.0 follow-up.
- Should the broker-UI service expose a metrics endpoint? Kafbat supports
  one but the MVP's "non-runtime dependency" rule argues against it.
  Resolved as `no metrics endpoint`; revisit if Kafka ops needs it.
- Should the rehearsal driver include a chaos step that injects a
  in-flight Temporal history loss? The MVP `platform-verification` line
  39 already requires it for the PR gate. Resolved as `reuse` — the
  rehearsal driver invokes the existing fault-injection tests.