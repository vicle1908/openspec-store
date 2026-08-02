## Context

The canonical local topology runs Temporal Server 1.31.2 and Go SDK 1.46.0,
bootstraps the `default` namespace with 72-hour retention, and observes
versioned workflow and activity pollers on nine task queues. The retained
readiness evidence proves namespace, polling, Worker Deployment, Build ID, and
routing convergence.

That evidence does not inspect registered Workflow or Activity types and does
not execute each advertised Workflow. Source inspection found four distinct
correctness classes:

1. Order, notification, customer, and reporting have real Workflow
   registrations and concrete Activity dependencies.
2. Payment, inventory, and shipping register zero-value Activity bundles even
   though the Activity methods require command handlers and persistence
   dependencies; they also omit event-recording Activities invoked by their
   Workflows.
3. Catalog creates a versioned worker but registers no Workflow or Activity,
   has no starter, and implements price rollback as an ordinary Go function
   using `context.Context` and `time.Now`.
4. Compatibility tests named as replay tests normally execute the Workflow
   again in a fresh test environment; none uses Temporal `WorkflowReplayer`
   with a retained Event History.
5. Payment, inventory, and shipping Workflow code invokes bare Activity names
   such as `CapturePaymentActivity`, while the workers register canonical
   dotted `.v1` names. The same Workflows call `time.Now` directly.
6. The repository `tools/workflowaudit` command currently returns success after
   discovering zero Workflow packages. A cold upstream `workflowcheck` run
   reports the payment, inventory, and shipping time calls as nondeterministic.
7. Workers use custom names without consistently enabling
   `DisableRegistrationAliasing`, and most Workflow registrations inherit a
   default versioning behavior rather than declaring it per type.

The official Temporal guidance used for this design requires every worker
polling a task queue to register the Workflow and Activity types it can receive,
uses `WorkflowReplayer` for compatibility against Event Histories, requires at
least `StartToCloseTimeout` or `ScheduleToCloseTimeout` for every Activity, and
recommends heartbeats for long-running Activities. Worker Versioning supports
both `AUTO_UPGRADE` and `PINNED`; this change preserves existing routing
semantics and makes the choice explicit per Workflow.

The outer repository has an existing, separate
`complete-cloud-deployment-and-cicd-readiness` change. This design must not
absorb or block on that work.

## Goals / Non-Goals

**Goals:**

- Make every Workflow advertised by the local specifications executable with
  real dependencies and a complete registration set.
- Distinguish namespace/poller/routing readiness from Workflow execution
  acceptance in commands and retained evidence.
- Establish clean-slate Temporal Event Histories as deterministic regression
  fixtures for the new Workflow code; prior histories are out of scope.
- Apply one validated SDK Activity policy across services while allowing
  operation-specific timeouts and retry error classifications.
- Make heartbeat configuration correspond to actual progress reporting.
- Make the local workflow-termination operator command truthful and testable.
- Run deterministic Workflow analysis for every service that owns Workflow
  code.
- Converge worker lifecycle and fatal-error propagation on the repository's
  non-blocking Start/Stop runtime contract.

**Non-Goals:**

- Cloud, staging, or production Temporal topology, authentication, namespaces,
  persistence, high availability, autoscaling, rollout control, or GitOps.
- CI/CD image publication or promotion.
- Public REST, Protobuf, or Kafka contract changes.
- Database ownership changes or cross-service table access.
- Preserving prior local executions, histories, aliases, or payload versions.
- A compatibility migration or dual-registration period.

## Decisions

### Decision 1: Preserve the advertised Workflow inventory and make it real

The implementation SHALL retain the Workflow inventory already declared by
`per-service-temporal-registration`:

| Service | Queue | Workflow set |
|---|---|---|
| order | `order-fulfillment.v1` | order fulfillment |
| payment | `payment.capture.v1` | capture and refund |
| inventory | `inventory.reservation.v1` | reserve, release, and confirm |
| shipping | `shipping.dispatch.v1` | dispatch and cancel |
| notification | `notification.dispatch.v1` | notification fulfillment |
| customer | `customer.purge.v1`, `customer.gdpr.v1` | purge and GDPR export |
| reporting | `reporting.admin.v1` | daily revenue rollup |
| catalog | `catalog.admin.v1` | price rollback |

Payment, inventory, and shipping workers will construct Activities through
their existing `NewActivities` constructors using the same application
handlers and unit-of-work adapters as their API roles. Every Activity referenced
by Workflow code, including event-recording Activities, will be registered
under its stable name.

Catalog price rollback will become a real Temporal Workflow using
`workflow.Context`, `workflow.Now`, and `workflow.ExecuteActivity`. A discovery
Activity will call the existing `queries.Service.GetPriceHistory` boundary in
stable pages of at most 100. The existing repository cursor implementation,
which currently ignores its cursor argument, will be corrected to use an opaque
keyset cursor containing the rollback request-time cutoff and last
`(effective_at, price_id)` tuple. Queries will use
`created_at <= request_cutoff` and deterministic
`effective_at DESC, price_id DESC` ordering, so reissued prices created during
the Workflow cannot enter or shift the frozen source set.

One retry-safe reissue Activity per selected snapshot will invoke the existing
`SetPriceHandler` with the historical amount, currency, tax class, effective
window, and a stable key derived from Workflow ID plus source Snapshot ID. The
handler remains the only writer and atomically creates the new immutable
snapshot plus outbox event. No new application port is required.

Progress will be represented in Workflow state by the opaque page cursor and
issued count; stable per-snapshot idempotency handles an Activity retry without
carrying an ever-growing completed-ID list.
The Workflow will Continue-As-New after a bounded page count while carrying
that progress, preventing unbounded Event History growth for large products. No
Activity may access another service's schema or bypass the transactional
outbox. A local starter will use the existing queue and
`PriceRollbackWorkflow.v1` type name.

Alternative considered: remove payment, inventory, shipping, and catalog
workers because the order saga already calls their HTTP APIs. Rejected because
the accepted ADRs and canonical specs explicitly advertise these service-owned
Workflows; removing them is a larger architecture change than completing them.

### Decision 1A: Canonical names and current contracts fail closed

The new implementation will use the already-declared canonical dotted `.v1`
Activity constants at every `ExecuteActivity` call. Each worker will set
`DisableRegistrationAliasing: true`, leave duplicate-registration checking
enabled, and register every Workflow with its stable string name and explicit
Auto Upgrade behavior.

Bare Activity names and compatibility wrappers will not be registered. Any
execution that requests an old or unknown name fails closed because the local
cutover starts from a clean namespace and disposable project. The canonical
inventory contains only current names and has no legacy entries.

Every advertised Workflow and Activity input/output will carry the current
contract version. Unsupported or older versions fail before any external side
effect with a non-retryable typed error. Mutating Activities derive their
idempotency key from stable Workflow/run-independent operation identity rather
than a new random value on retry.

### Decision 2: Split Temporal readiness into infrastructure and execution

`dev-up` will continue to require namespace bootstrap plus valid workflow and
activity pollers, deployment metadata, and current routing. This remains
`temporal-worker-readiness.json`.

`dev-smoke` will additionally invoke a dedicated local Temporal canary harness
that starts every advertised Workflow directly with isolated fixture
identifiers and asserts its expected terminal state. The harness will use the
same canonical inventory as architecture checks and will write a separate
versioned `temporal-workflow-execution.json` containing, per Workflow:

- service, namespace, task queue, Workflow type, Workflow ID, and run ID;
- expected and observed terminal state;
- attempt/result summary with secrets and payload data redacted;
- start and finish timestamps; and
- pass/fail diagnostic.

The aggregate Compose evidence manifest will hash and reference both files.
Poller readiness SHALL NOT be labeled as Workflow registration or execution
success.

Alternative considered: infer registrations through `DescribeTaskQueue`.
Rejected because poller metadata does not prove that the worker registered the
advertised types or that its Activity object has usable dependencies.

### Decision 3: Generate and replay current-code Event Histories

Each Workflow owner will generate representative JSON Event Histories under
`test/replay/fixtures/temporal/<workflow-type>/`. Tests will use
`worker.NewWorkflowReplayer`, register the stable Workflow type, and replay the
fixture produced by the current implementation. Replay verifies deterministic
command sequences for the current code; it is not a backward-compatibility
test.

Fixtures will cover the required current-code paths available for each
Workflow: success and, where applicable, retry, timer, cancellation,
compensation, and Continue-As-New. A dedicated, non-default fixture-generation
command may export histories from an isolated clean local project. Normal tests
MUST never regenerate fixtures. Fixture changes require a deterministic-behavior
review note, not a compatibility approval.

Fixture executions will use synthetic non-sensitive inputs from the start.
Exported Event History JSON will not be edited to redact encoded payloads,
because post-export mutation can change the replay command stream. Fixture
metadata and evidence may redact payload summaries while retaining the original
synthetic history bytes. Tests will use
`ReplayWorkflowHistoryFromJSONFile` or `client.HistoryFromJSON` plus
`ReplayWorkflowHistory`.

The implementation does not support histories created by the previous
direct-`time.Now` or bare-name code. Before starting the new workers, the local
Temporal namespace and disposable Compose project MUST be clean; stale local
executions and histories are removed through the documented project-scoped
reset. No old history is exported, retained, migrated, or replayed.

Alternative considered: keep `testsuite.TestWorkflowEnvironment` reruns only.
Rejected because reruns do not compare new Workflow commands with an existing
Event History and therefore cannot establish backward replay compatibility.

### Decision 4: Make versioning explicit for new executions only

Every `RegisterWorkflowWithOptions` call will specify
`VersioningBehaviorAutoUpgrade` for the new clean-slate local deployment. This
is a routing default for new executions, not a promise to execute old code or
drain old histories. The cutover preflight fails if any prior local execution
remains.

Long-running customer and catalog Workflows are not required to support an
older build in this local-only change. Any future cloud rollout policy remains
in the separate cloud change.

Alternative considered: retain old workers or pin old executions during the
cutover. Rejected because the requested architecture is a complete move to the
new code without a compatibility period.

### Decision 5: Convert validated platform Activity policy into SDK options

`platform/temporal` will expose a typed conversion from validated platform
options to SDK `workflow.ActivityOptions`. The conversion will set:

- `StartToCloseTimeout` for every Activity;
- a bounded `ScheduleToCloseTimeout`;
- `ScheduleToStartTimeout` only when the Activity has a documented queue-delay
  requirement;
- an explicit Retry Policy with a positive, bounded `MaximumAttempts` of at
  least three; and
- `HeartbeatTimeout` only for an Activity that records progress.

This intentionally corrects the current OpenSpec rule that requires
Schedule-To-Start on every Activity. Temporal treats it as optional; making it
universal can turn capacity delay into failure without improving execution
failure detection.

Order's longer remote-call timeouts remain unchanged unless current-code replay
and focused behavior tests prove a safe change. Reporting gains an
overall bound and explicit retry policy. Notification maps its already
validated retry count into the SDK policy.

### Decision 6: Heartbeats represent ongoing progress

Activities with a Heartbeat Timeout MUST call `activity.RecordHeartbeat` at
progress boundaries or periodically below the timeout. Short atomic database or
HTTP Activities that cannot expose progress will omit Heartbeat Timeout and use
Start-To-Close plus Schedule-To-Close bounds instead.

Cancellation tests will prove that long-running Activities notice canceled
contexts and do not continue an external side effect after Temporal has
abandoned the attempt.

### Decision 7: Use non-blocking Start/Stop and surface fatal errors

All worker roles will use non-blocking `Start`, wait under the role runtime, and
call `Stop` within the configured shutdown budget. The reusable wrapper will
surface SDK fatal polling errors to the owning process and mark readiness false.
SDK worker options will set a bounded `WorkerStopTimeout`,
`DisableRegistrationAliasing: true`, and an `OnFatalError` callback connected
to the role's fatal-error channel.

Payment, inventory, shipping, and catalog will migrate away from top-level
`Run(stopper)` so implementation matches the canonical runtime contract.
Notification's existing fail-closed readiness/fatal channel is the reference
behavior. The implementation may share an adapter without importing service
business types into `platform`.

Alternative considered: update the runtime spec to permit both lifecycle
styles. Rejected because one Start/Stop contract simplifies readiness,
fatal-error propagation, and bounded shutdown across eight services.

### Decision 8: Implement termination behind an injectable client

`platform/temporal` will define the smallest interface needed for
`TerminateWorkflow`. The CLI will construct the SDK client from local address
and namespace flags, call termination with Workflow ID, optional run ID, and a
required or defaulted reason, then close the client. SDK status codes will map
Not Found to `ErrWorkflowNotFound`; string matching is forbidden.

Unit tests use a fake client. Local integration starts a blocking fixture
Workflow, invokes the command, and verifies the terminal Event History contains
the operator reason. Namespace deletion remains prohibited.

### Decision 9: Determinism checking is a root local gate

A root Temporal verification target will invoke the checker against every
actual Workflow source directory and load the canonical allowlist. Service
`verify-pr` targets that own Workflows will call the same target or an equivalent
module-scoped entry point. Architecture tests will fail when a new Workflow
owner is missing from the inventory.

The repository auditor will use module-aware package loading, report discovered
Workflow packages and functions, and fail when the inventory expects any
Workflow but discovery returns zero. Regression fixtures will intentionally
contain `time.Now` and prove both the repository auditor and upstream
`workflowcheck` fail. Cached analyzer success is not accepted as proof unless
the gate's own negative control also fails as expected.

### Decision 10: Evidence and status claims change only after execution passes

Main OpenSpec `LOCAL IMPLEMENTED` or `LOCAL VERIFIED` annotations will be
changed to `PARTIAL` while implementation is in progress. They return to
implemented only after:

- all focused unit and deterministic-replay tests pass;
- true history replay passes;
- Compose validation passes;
- every execution canary passes in a clean local topology; and
- the exact-source deployment validation manifest is retained.

Cloud and CI/CD status is unchanged.

### Decision 11: Service architecture gates reuse canonical Temporal verification

Every service that owns an inventoried Workflow will expose
`TestWorkerVersioningIsConfigured` and `TestDeterministicWorkflowCode` in its
own architecture suite. The tests will not use superficial import-presence or
string scans. Worker verification will call the service-filtered canonical
inventory validator, and determinism verification will additionally run the
upstream Temporal workflow checker against that service's actual Workflow
source directory. Because every service `verify-pr` already runs its
architecture suite, this makes the per-service gate equivalent to the relevant
portion of the root Temporal gate.

Hexagonal checks will continue to inspect the transitive closure when proving
domain purity and in-repository layer direction. Application checks for
third-party infrastructure frameworks will inspect direct imports of every
application package. This distinction is required because the explicitly
admitted Temporal Workflow APIs have their own transitive Fx, Zap, and OTel
dependencies; those packages are not imported by application source. Temporal
SDK and platform Temporal APIs remain admitted only within owned
`application/orchestration` code, while direct imports of service adapters,
Fx, Zap, OTel, pgx, Kafka, or Redis remain forbidden.

Alternative considered: preserve the existing transitive third-party scan and
allowlist the current SDK dependency graph. Rejected because the allowlist
would encode incidental Temporal SDK internals, change on dependency upgrades,
and still misidentify indirect packages as application source imports.

## Risks / Trade-offs

- **[Existing local histories remain after cutover]** → fail preflight and
  require the documented disposable-project reset before workers start.
- **[Synthetic history is modified during redaction]** → create fixtures with
  non-sensitive inputs and keep exported history bytes immutable; redact only
  derived summaries and metadata.
- **[Execution canaries mutate domain data]** → Use isolated fixture IDs,
  service-owned APIs/Activities, idempotency keys, and disposable local
  projects; never write another service's schema directly.
- **[Catalog implementation exposes underspecified business behavior]** →
  constrain the Activity to existing catalog commands and update the accepted
  catalog ADR if its stated multi-step rollback cannot be represented by
  existing application ports.
- **[Catalog writes shift the price-history pages being scanned]** → freeze the
  source set at the requested-at cutoff and use an opaque deterministic keyset
  cursor; add tests proving newly reissued rows never appear in later pages.
- **[Shared Activity defaults hide operation-specific needs]** → validate
  invariants centrally while leaving durations and non-retryable error types
  explicit at each Workflow call site.
- **[Heartbeat goroutines leak or race shutdown]** → prefer progress heartbeats
  inside the Activity's natural loop; when periodic reporting is necessary,
  bind it to the Activity context and test cancellation.
- **[Local smoke duration increases]** → keep fixtures minimal, execute
  independent Workflow canaries concurrently where data ownership permits, and
  retain per-Workflow timing evidence.
- **[Worker Start succeeds before pollers register]** → keep bounded
  `DescribeTaskQueue` convergence and fatal-error observation after `Start`.

## Clean-slate Cutover Plan

1. Mark affected main-spec status annotations partial and add traceability IDs.
2. Add the project-scoped clean-namespace reset/preflight and prove stale local
   executions block startup.
3. Fix determinism and inventory discovery gates and prove their negative
   controls fail.
4. Add shared Activity conversion, lifecycle/fatal-error support, current
   contract validation, and termination client abstraction.
5. Repair payment, inventory, and shipping dependencies, canonical names,
   deterministic time, and registrations without compatibility aliases.
6. Implement the multi-step catalog Workflow, Activities, registration, and
   starter through catalog-owned ports.
7. Make versioning behavior explicit for new executions and correct Activity
   heartbeat/retry policy service by service.
8. Generate current-code synthetic histories from a clean local stack and add
   `WorkflowReplayer` deterministic regression tests.
9. Add direct execution canaries and the versioned execution-evidence document.
10. Run focused service/platform gates, `make verify-pr`, clean local Compose
    acceptance, and `make validate-deployment`; retain exact-source evidence.
11. Sync the delta specs and restore implemented status only for passing local
    behavior.
12. Replace stale Temporal architecture deferrals, make every service gate run
    canonical worker and determinism checks, and reconcile direct-import
    hexagonal semantics before archive.

Rollback means reverting the uncommitted code and recreating the disposable
local project. It does not restore legacy workers, aliases, payload decoders,
or histories.

## Deferred Fixture Extensions

The required success, retry, timer, cancellation, compensation, and
Continue-As-New fixture coverage is sufficient to begin implementation.
Additional failure-path histories may be added after the first executable
matrix establishes baseline histories; they do not block this change and do
not expand its runtime scope.
