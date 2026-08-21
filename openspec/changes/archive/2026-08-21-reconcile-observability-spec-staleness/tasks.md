# Tasks

## 1. Reconciliation

- [x] 1.1 Record current canonical spec and runtime evidence (both specs read, 157/157 tests passing)
- [x] 1.2 Author MLflow route-mode delta (REMOVED + ADDED + MODIFIED requirements)
- [x] 1.3 Author instrumentation-ownership delta (REMOVED + ADDED + MODIFIED requirements)
- [x] 1.4 Author design and confirm no source-code scope

## 2. Validation

- [x] 2.1 Run strict change validation (`openspec validate reconcile-observability-spec-staleness --strict --store openspec-store`)
- [x] 2.2 Inspect parsed deltas — confirm only mlflow-otel-integration and otel-auto-instrumentation affected, with correct REMOVED/ADDED/MODIFIED operations
- [x] 2.3 Confirm no unrelated files changed in scoped git status (only untracked reconciliation directory)
