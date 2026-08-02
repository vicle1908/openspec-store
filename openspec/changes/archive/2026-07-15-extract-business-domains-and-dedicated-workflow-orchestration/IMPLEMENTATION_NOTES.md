# Implementation notes — extract-business-domains-and-dedicated-workflow-orchestration

> Captures the design adjustments made during implementation. The original
> proposal.md remains the source of truth for *what* was changed; this file
> captures *why* specific implementation choices differ from the proposal.

## Payment intent lifecycle (remote capture / remote refund)

The original proposal had the order-service continue to create the
`PaymentIntent` locally before the saga starts. With the new
payment-service owning the lifecycle, the saga was simplified:

- The `ProcessPayment` activity forwards `PaymentIntentID = ""` to the
  payment-service. The peer auto-creates a new intent using the
  idempotency key and returns the new ID in the response
  (`PaymentCaptureResponse.PaymentIntentID`).
- `ProcessPaymentResultV1` carries the new `PaymentIntentID` field so the
  workflow state can use it during compensation (refund).
- `RefundPaymentInputV1` gained a `PaymentIntentID` field and the
  `RefundPayment` adapter forwards it as the URL path
  `/api/v1/payments/{PaymentIntentID}/refund`.

The net effect is that **no order intent table is needed any more** on the
order-service; the saga flows are entirely remote-aware. (The local
`Order.PaymentIntentID` field is preserved for legacy API compatibility but
no longer written by the saga.)

## Capture URL fallback

The payment-service exposes two capture endpoints:

- `POST /api/v1/payments/{PaymentIntentID}/capture` — capture against a
  known intent (production).
- `POST /api/v1/payments/capture` — auto-create an intent + capture in one
  shot (saga path; idempotency-key driven).

The order-service client picks the second one when `PaymentIntentID == ""`.

## Remote adapter boundary

Rather than mutate the existing `temporal.InventoryActivities`,
`temporal.PaymentActivities`, `temporal.ShippingActivities` interfaces,
the remote activities live in `cmd/order-service/remote_activities.go`
and are wrapped by thin adapters in `remote_adapter.go`. This keeps the
existing local stub (`localFulfillmentActivities`) usable in tests and
during soft rollback — flipping to remote only requires a config change.

## Carrier stub

The shipping-service uses a `ShipmentProvider` interface with one
implementation today (`*carrier.StubAdapter`) that generates
deterministic tracking numbers (`STUB-<order-id>`). UPS/FedEx adapters
will plug in via the same interface.

## Worker placement

Workers are colocated with the service's API binary using Temporal
worker versioning (`worker_version_v1`) and shared task queues of the
form `<service>.worker.vN`. The base Compose file now has an overlay
per service that adds the worker container alongside the API container.

## What is **deferred**

The following tasks in `tasks.md` are explicitly flagged as **local-
toolchain-only** and were not executed in this automation environment:

| Task | Reason for deferral |
| --- | --- |
| `buf generate` for payment/inventory/shipping protobufs | Requires Buf CLI; hand-maintained stubs are committed with a `REGENERATE.md` per service. |
| Docker Compose bring-up | Requires local Docker daemon (`docker compose up`) on the operator machine. |
| Smoke tests | The test scaffolds are committed; running them requires the full bring-up. |
| Archive (`openspec archive`) | Operated by the spec owner once the verify checklist is signed off. |

See `tasks.md` for the exact per-task annotations.

## Post-implementation verification (commit-time)

After the implementation, the following compile-time errors were uncovered and
fixed before the change was considered ready to merge:

| Service | Error | Fix |
| --- | --- | --- |
| payment, inventory, shipping | `pgx.CommandTag` undefined | `CommandTag` lives in `github.com/jackc/pgx/v5/pgconn`. Updated `pgQuerier` interface and `pgxTx` wrapper. |
| payment, inventory, shipping | `workflow.RetryPolicy`, `workflow.Saga` undefined | Use `temporalsdk.RetryPolicy` from `go.temporal.io/sdk/temporal`. `workflow.Saga` is provided by `platform/temporal`; the file-level `var _ = workflow.Saga` assertion was removed because it does not compile against the stock SDK. |
| payment, inventory, shipping | `otelpgx.Exec/QueryRow/Query` undefined | Those helpers do not exist. The correct way to instrument pgx is `cfg.ConnConfig.Tracer = otelpgx.NewTracer()` at pool construction time (as done in notification/catalog/customer/reporting). The `instrumentedPool` wrapper and the otelpgx import were removed. |
| payment | `runWorker` declared twice | Renamed the inner implementation in `worker.go` to `runWorkerImpl`, matching the `runAPIImpl` / `runWorkerImpl` convention used by inventory/shipping. |
| payment | `runtime.SignalContext` undefined | Added the helper in `internal/runtime/config.go` (SIGINT/SIGTERM → context cancel). |
| payment | `workflow.Saga` referenced from orchestration | Removed the file-level sentinel; the saga helper is invoked via the platform module. |
| inventory, shipping | Unused `time` import | Removed. |
| order-service | `package smoke_test` in `cmd/order-service` (mixed with `package main` files) | Renamed to `package main`. |
| order-service | Missing `contracts/{payment|inventory|shipping}/v1/*.go` packages referenced by `internal/application/clients/*` | Recreated as hand-maintained mirrors (see `contracts/payment/v1/payment.go` etc.). |
| order-service | `ReleaseInventoryResultV1` missing `ReservationID` field | Added field with `json:"reservation_id"` tag. |
| order-service | Unused `os` import in `smoke_inventory_contract_test.go` | Removed. |

After these fixes:

- `go vet ./...` passes on `payment-service`, `inventory-service`, `shipping-service`, and `order-service`.
- `go build ./...` passes on all four services.
- `go test -run=^$ ./...` (test compilation) passes on all four services.
- The full `go test ./internal/...` run on `order-service` reports only four
  pre-existing failures in `internal/adapters/postgres` (confirmed by running
  them on a stashed-clean main). These pre-existing failures are unrelated
  to this change.
- `openspec validate extract-business-domains-and-dedicated-workflow-orchestration --type change --strict` reports the change as valid.
- `shellcheck -x -S warning` passes on all four `provision-topics.sh` scripts.
