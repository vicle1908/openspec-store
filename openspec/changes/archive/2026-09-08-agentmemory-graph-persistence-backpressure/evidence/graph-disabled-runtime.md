# Evidence: graph-disabled config-only mitigation

Runtime: `@agentmemory/agentmemory@0.9.29`

Configuration:

```text
GRAPH_EXTRACTION_ENABLED=false
CONSOLIDATION_ENABLED=true
embeddings enabled
observation capture enabled
session-end processing enabled
```

Verified:

- `GET /agentmemory/health` returned HTTP 200
- `GET /agentmemory/config/flags` returned `GRAPH_EXTRACTION_ENABLED=false`
- Synthetic observation returned HTTP 201
- Synthetic session-end returned HTTP 200 with `success=true`
- Rollback to prior `.env` restored health/session behavior, then mitigation reapplied successfully

No source modification, no unofficial package, no graph reset, no state database migration.

Deferred until official release supports bounded graph scheduling:

- graph batch/queue/concurrency/backpressure
- graph extraction re-enable with idempotent recovery
- disposable provider/state-store fixture implementation if unsupported by official release
