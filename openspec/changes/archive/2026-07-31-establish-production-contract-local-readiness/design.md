## Context

See `proposal.md` for motivation. The existing readiness runner already owns an
isolated Compose project, validates model interpolation and Collector config,
waits for health and one-shot roles, executes cross-service and Shipping/Nexus
operations, reruns startup for idempotency, binds evidence to one run/project,
captures diagnostics, and performs scoped cleanup. That lifecycle is retained.

The existing smoke workload is broad but not causally complete. Its CDC stage
inserts synthetic outbox records directly, its fulfillment assertion observes
only the Order terminal state, its notification and Reporting assertions do not
bind exact event content and projected fields to the order, its Workflow
canaries generally assert only `COMPLETED`, and its telemetry checks can select
unrelated signals. These remain useful diagnostics but cannot be promoted into
production-contract operation evidence unchanged.

The current data plane instead embeds a shared PostgreSQL credential, uses
plaintext Kafka, attaches everything to one bridge network, and supplies no
Compose secrets or container hardening. Production overlays are also under
readiness repair and contain insecure OTLP, plaintext peer HTTP, incomplete
secret inputs, and a Shipping stub, so they cannot be copied as the local source
of truth.

This change begins only after
`standardize-service-runtime-security-contract` is implemented and verified.
It consumes that application contract and does not implement cloud resources.

## Goals / Non-Goals

**Goals:**

- Make one machine-readable runtime contract authoritative across Compose and
  local kind while allowing technology-specific rendering.
- Make secure production-contract startup the canonical developer topology and
  retain an explicit local-fast compatibility path.
- Reuse the proven operational-readiness lifecycle while adding security,
  provider, fault, recovery, redaction, and reduction evidence.
- Make the acceptance authority a causal set of real business operations with
  explicit durable-effect and compensation oracles.
- Keep the stack practical on supported arm64 workstations.

**Non-Goals:**

- Raw YAML equality between Compose and Kubernetes.
- Local proof of production replicas, load, failure domains, autoscaling,
  managed control planes, cloud identity, GitOps convergence, backup restore,
  or rollback.
- Staging or production mutation.

## Decisions

### 1. Runtime parity is a normalized contract, not manifest equality

Add a versioned repository inventory under `verification/` with one record per
service role and shared dependency. The validator renders the exact Compose
file set and local kind Kustomize inputs, normalizes each into the contract
model, and compares required invariants. It ignores renderer-specific fields
only when the contract classifies them as topology implementation or an allowed
local reduction.

The inventory owns:

- role/image-build/command/port/health identities;
- required and secret configuration classes, never secret values;
- workload identity and authorized dependency edges;
- PostgreSQL schemas and roles, Kafka topics/groups/principals, Temporal
  namespace/queues/endpoints, Redis ACL identities, and OTLP routes;
- provider mode, container security, network classes, resource envelope;
- allowed local reductions and required evidence classes.

The existing OpenSpec capabilities remain normative behavior; the inventory is
their executable deployment mapping. A validator checks that every inventory
entry maps to a capability/scenario and that no deployed role is unowned.

Alternative considered: compare current Compose directly to production YAML.
Rejected because topology and secret-provider syntax legitimately differ and
the current production overlays contain known insecure settings.

### 2. Compose uses a common structural base plus mutually exclusive profiles

Preserve the existing base and eight per-service overlay contract. Move
profile-specific plaintext credentials, host exposures, and stub selections out
of the common model. Add mutually exclusive production-contract and local-fast
overrides:

```text
base data plane + eight service overlays
                    |
          +---------+---------+
          |                   |
production-contract       local-fast
secure/default/evidence    explicit/non-evidence
```

The canonical `COMPOSE_FULL`, `dev-up`, `dev-smoke`, diagnostics, and readiness
paths select production-contract. `dev-fast-up`, `dev-fast-smoke`, and matching
down/diagnostic targets select local-fast. The profile identity is injected into
every role and evidence artifact. Validation rejects both profiles in one merge.

Alternative considered: leave `dev-up` insecure and add a separate readiness
command. Rejected because the user-facing canonical stack would continue to
exercise different protocols and defaults from readiness.

### 3. One run-scoped bootstrap owns PKI and secrets

Use a repository-owned Go bootstrap/validation tool rather than adding a new
runtime image. It creates a run-local root, server/client certificates with
canonical service/role identities, PostgreSQL and Kafka credentials, Redis ACL
secrets, and other required local credentials under a mode-0700 run directory.
Compose secret objects and local kind Secrets mount individual files; values are
never interpolated into YAML or command lines.

The tool writes a non-secret manifest of logical identities, certificate
fingerprints, validity windows, file hashes, ownership, and run/project identity.
It supports idempotent same-project rerun, rejects cross-run reuse, and deletes
private material during owned cleanup. It does not install trust into the host
keychain.

Alternative considered: committed self-signed certificates. Rejected because
they become reusable credentials and allow cross-run identity collision.

### 4. Dependency bootstrap is ordered and least privileged

Production-contract initialization order is:

1. run identity, PKI, and secret generation;
2. secured PostgreSQL/Kafka/Temporal/Redis/Collector listeners;
3. PostgreSQL role/schema grants, Kafka ACLs/topics, Temporal namespace and
   ClaimMapper/Authorizer policy, Redis ACLs, Collector trust policy;
4. service migrations, publications, and connectors using role identities;
5. application roles and provider sandbox;
6. health, parity, operation, negative, fault, and recovery gates.

One-shot containers use `service_completed_successfully`; long-running
dependencies use health-based conditions. Every initializer is idempotent and
has a least-privilege administrative identity distinct from service runtimes.
Failure blocks dependents and records redacted diagnostics.

### 5. Network segmentation is coarse reachability, not identity

Use internal Compose networks representing edge, services, data, messaging,
workflow, observability, and provider egress. Roles attach only to required
classes from the runtime inventory. Only declared developer entry points bind
loopback host ports; all dependency host ports move to local-fast or diagnostic
profiles. Application mTLS and dependency ACLs remain mandatory because bridge
network membership is not an authorization boundary.

Local kind uses NetworkPolicy with the same normalized allowed-edge intent. The
validator compares edges, not raw network names.

### 6. Service containers use the Kubernetes hardening contract

Compose application roles adopt the existing Kubernetes posture: non-root,
read-only root filesystem, no-new-privileges, dropped capabilities, bounded
tmpfs/volumes, and no unnecessary service-account or host access. Inventory and
Shipping canonical Dockerfiles gain the same role-aware healthcheck contract as
the other six services. Infrastructure images receive explicit exceptions only
for required writable paths or capabilities, with a validator fixture for every
exception.

No new external runtime image is selected by this design. The Shipping provider
sandbox is a role in the existing canonical Shipping image, and the PKI tool is
repository-built. Existing pins remain subject to `verify-images`; any later
image addition must be checked against current official documentation and
native linux/arm64 support before selection.

### 7. Shipping readiness uses a networked provider sandbox

Add a sandbox-server role that exposes the protocol subset required by the
Shipping external adapter: authenticated dispatch, lookup by stable provider
idempotency key, cancellation, deterministic latency/error controls, and an
operator-only effect counter. Shipping connects through its normal network
adapter; application code sees only the existing ShippingProvider port.

The sandbox supports controlled outcomes: success, rejection, delay before
effect, delay after effect, connection loss after effect, lookup recovery, and
duplicate request. Evidence proves logical effect counts without representing
the sandbox as a live carrier or cloud readiness.

Alternative considered: continue using the in-process stub. Rejected because it
bypasses transport security, timeout, authentication, and unknown network
outcomes.

### 8. Faults are bounded cohorts inside the owned project

Extend readiness with explicit fault cohorts rather than a general chaos tool.
The runner validates ownership before stopping/restarting containers or
replacing run-local credentials. Cohorts execute serially after baseline
operations and restore healthy state before the next cohort:

- wrong workload identity and wrong trust root for each dependency class;
- denied PostgreSQL cross-schema/DDL and Kafka topic/group operations;
- dependency restart during a retry-safe operation;
- credential/certificate replacement followed by affected-role restart;
- API, Worker, orchestrator, and consumer graceful termination;
- Kafka redelivery, Temporal replay, Nexus authorization denial;
- Shipping provider response loss after effect and lookup reconciliation.

Each cohort carries the original operation/event/offset/Workflow/provider
identity and asserts one logical effect. Fault injection is forbidden outside
the validated owned project or cluster.

### 9. Canonical readiness is operation-led and causally evidenced

Replace the independent smoke assertions with five coordinated operation
cohorts. Setup and commands use owning service APIs or authorized Nexus
operations; service-scoped SQL and Kafka consumers are read-only evidence
oracles after the operation. Direct outbox writes and direct Kafka injection are
retained only for focused connector and negative fixtures.

| Cohort | Trigger | Required durable proof |
| --- | --- | --- |
| Happy path | Customer, Catalog/Price, Inventory, then Order APIs | captured Payment; reserved and confirmed Inventory; dispatched Shipping sandbox effect; shipped Order; exact notification; correct Reporting projection |
| Compensation | deterministic Shipping failure after Payment and Inventory | Payment refund; Inventory release; compensated Order; compensation outbox/Kafka facts; zero Shipping logical effect |
| Idempotency | repeat API request, Workflow/Nexus operation, and admitted event delivery | one aggregate transition, outbox fact, provider effect, notification, and projection result |
| Authorization | repeat the purposeful operation with a wrong workload identity | denial before mutation, outbox, retry/DLQ, Workflow effect, or provider call |
| Recovery | restart a dependency, rotate a credential, or lose the provider response during work | bounded recovery or explicit recoverable state, preserved identity, and one logical effect |

Each cohort emits a causal ledger rather than a collection of pass booleans.
The ledger carries run/project/source/contract identity; request, correlation,
and idempotency IDs; customer/product/order/payment/reservation/shipment and
notification IDs; Temporal Workflow/run/activity identities; outbox event IDs;
Kafka topic/partition/offset; processed receipt and projection identity;
provider effect count; trace ID; and before/after durable states. A field may be
marked not applicable only by the cohort schema. A required but missing link is
a failure.

Notification verification matches the exact recipient plus order/event or
correlation identity and expected template outcome. Reporting verification
asserts projected fields and the exact processed receipt, not row existence.
Temporal canaries assert their resulting durable state, outbox fact, or provider
effect in addition to Workflow completion. Telemetry queries start from the
cohort trace or correlation ID and prove expected service participation.

Alternative considered: keep independent synthetic probes and add more health
checks. Rejected because they can all pass while the domain transaction,
delivery, compensation, or correlation chain is broken.

### 10. Evidence extends the existing exact-identity model

Version the acceptance schema to include runtime-contract version/digest,
security mode, non-secret identity fingerprints, declared reductions, parity
results, security positive/negative results, fault/recovery results, provider
effect counts, causal operation ledgers, redaction scan, and secret cleanup.
Every child artifact includes source revision, run ID, project/cluster, profile,
and contract digest.

The aggregate gate accepts only `local-production-contract`. Local-fast,
focused, service-integration, kind-only, stale, mismatched, or secret-bearing
artifacts remain supplemental or rejected as appropriate. Diagnostics identify
paths and categories but redact values.

### 11. Local reductions are a reviewed allowlist

The initial allowlist permits one application replica per role, one PostgreSQL
server, one Kafka broker with replication factor one, one Temporal server,
workstation-sized resources, local volumes, and the run-scoped local PKI/secret
provider. Targeted tests may scale selected consumers or Workers, but HA is not
claimed. Any new reduction requires a contract and spec update rather than an
unreviewed validator skip.

### 12. Resource budgets protect the developer experience

The production-contract profile reuses the existing bounded Compose parallelism
and resource envelopes. Security bootstrap is one-shot and the provider sandbox
is lightweight. Optional UI/LGTM tools remain opt-in where possible; required
Collector assertions stay in the readiness path. Preflight estimates memory,
disk, architecture, port, and certificate-time prerequisites before creating
state and reports when local-fast is the only practical developer option without
mislabeling it as readiness.

## Risks / Trade-offs

- **Secure default increases startup time and setup complexity** → use one-shot
  bootstrap, same-project idempotency, bounded waits, diagnostics, and explicit
  local-fast for constrained inner-loop work.
- **Runtime inventory becomes another source of drift** → require traceability
  to OpenSpec, compare both renderers, and fail when a deployed role is missing
  or extra.
- **Compose network segmentation gives false confidence** → keep mTLS and ACLs
  mandatory and describe networks only as reachability reduction.
- **Single-node dependencies hide quorum failure** → record reductions and keep
  quorum/zone/managed behavior in external cloud gates.
- **Fault injection destroys unrelated state** → require exact project/cluster
  ownership labels and refuse unowned targets before any mutation.
- **Independent checks create false causal confidence** → require one ledger per
  operation cohort and reject unlinked terminal states, messages, projections,
  provider counts, or telemetry samples.
- **Secret evidence leaks despite redaction** → scan every retained artifact,
  fail on secret patterns, and delete run-local private material even after test
  failure while preserving only redacted diagnostics.
- **Current cloud artifacts conflict with the contract** → treat them as deferred
  drift and update the cloud change only after local contract evidence passes.

## Migration Plan

1. Require the completed and verified service-runtime-security change.
2. Add the runtime inventory, schema, traceability, normalization, and validator
   with fixtures for current known drift.
3. Add run-scoped PKI/secrets and secure infrastructure bootstrap without
   changing canonical target aliases.
4. Add production-contract Compose and local kind inputs, network segmentation,
   hardening, healthcheck corrections, and secure initialization.
5. Add the networked Shipping sandbox and the operation-led happy-path,
   compensation, idempotency, and authorization cohorts with causal ledgers.
6. Add bounded fault, rotation, termination, replay, redaction, and recovery
   cohorts; make the aggregate gate pass repeatedly on a clean project and a
   same-project rerun.
7. Run deployment validation and retained readiness on supported arm64; verify
   the exact images and resource budget.
8. Switch `dev-up`, `dev-smoke`, diagnostics, and readiness to
   production-contract; publish separately named local-fast commands and update
   documentation.
9. Record the active cloud-readiness change as downstream of the runtime
   contract; do not mutate non-local resources here.

Rollback restores the prior Make target aliases or explicitly selects
local-fast, retains failure diagnostics, and removes only owned run secrets,
containers, networks, and volumes. It does not remove the secure profile,
runtime inventory, database role model, or application security support and
does not reverse domain data, schema migrations, events, or Workflow history.
