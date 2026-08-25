## 1. Fail-Closed Langfuse Contracts

- [ ] 1.1 Require `service_healthy` Redis ordering for Langfuse web/worker and add the pinned worker's bounded queue-aware readiness healthcheck; verify Langfuse and full Compose renders assert the endpoint, budgets, and dependency conditions.
- [ ] 1.2 Reject non-false file and ambient `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` values before Docker mutation; verify focused preflight tests cover the default, file override, and ambient override without exposing values.
- [ ] 1.3 Require `/api/public/otel/v1/traces` with `x-langfuse-ingestion-version: "4"` and no legacy route; verify both Langfuse-capable Collector configurations validate under the pinned Collector image and focused tests assert the exact route/header.

## 2. Documentation and Evidence

- [ ] 2.1 Update the operator template and runbook with the false BullMQ bypass value, strict worker readiness endpoint, healthy Redis ordering, v4 ingestion route, and explicit non-goals; verify documentation contains no credential value or unsupported timeout variable.
- [ ] 2.2 Update the acceptance lifecycle guidance and durable current deployment evidence additively, preserving historical manifests; verify the evidence records exact source identity, affected-service recreation, queue readiness, event receipt, restart counts, and unresolved warnings.

## 3. Static and Runtime Verification

- [ ] 3.1 Run focused Compose, gateway, and deployment-preflight tests plus Ruff, targeted mypy, four daemon-free profile renders, Graphify update, staged GitNexus review, and diff checks; record pre-existing or unrelated diagnostics separately from change-owned failures.
- [ ] 3.2 Recreate only `langfuse-redis`, `langfuse-worker`, and `otel-gateway` from the verified commit using the protected operator env; verify Redis healthy, worker queue readiness HTTP 200 with consumption enabled and not stuck, gateway readiness, zero affected-service restarts, and preserved databases/volumes.
- [ ] 3.3 Emit a unique trace through the gateway and verify exactly one Langfuse event in both `default.events_core` and `default.events_full`, matching Collector acceptance/export counters, and continued LGTM/MLflow fan-out.
- [ ] 3.4 Observe a finite post-recreation compatibility window of at least ten minutes and verify worker/web logs contain no Redis-version, command, BullMQ, socket-timeout, or restart failure; retain the warning and block readiness if the cadence recurs.

## 4. OpenSpec Review

- [ ] 4.1 Validate `harden-langfuse-worker-readiness` strictly and map every requirement/scenario to source, test, documentation, and runtime evidence in a verification report.
- [ ] 4.2 Reconcile the authoritative OpenSpec runtime report with the verified final verdict, stage only change-owned store paths, run staged review/diff checks, and commit the store without touching unrelated active changes or worktrees.
