# Design: Fix Pre-existing Verification Issues

## Context

Live stack verification against the latest code revealed 5 pre-existing issues.
These are not regressions — they existed before the workspace migration but were
masked by test skips or compilation exclusions.

## Section 1: Customer Worker Workflow Implementations

### Current

`run.go` registers workflows with `RegisterWorkflowWithOptions(orchestration.CustomerPurgeWorkflow, ...)` where `CustomerPurgeWorkflow` is a `const string` ("customer.purge.v1"). The Temporal SDK expects a workflow function, not a string. This causes a panic on startup.

### Proposed

Create workflow functions in `internal/application/orchestration/purge_workflow.go` and `export_workflow.go`:

- `PurgeWorkflow(ctx workflow.Context, input PurgeWorkflowInput) error` — placeholder that logs and returns nil
- `GDPRExportWorkflow(ctx workflow.Context, input GDPRExportInput) error` — placeholder that logs and returns nil

Update `run.go` to register the function references instead of the string constants.

### Why

Placeholder workflows allow the worker to start without panic. Real implementation
logic (erasure, PII collection) will be added in a future change.

## Section 2: Inventory GenerateReservationID

### Current

`activities_test.go` calls `GenerateReservationID()` but the function doesn't exist.

### Proposed

Add to `internal/application/orchestration/activities.go`:

```go
func GenerateReservationID() string {
    return fmt.Sprintf("RES-%s", uuid.New().String()[:12])
}
```

### Why

The test expects a unique ID generator for reservation tracking.

## Section 3: Reporting Service Test Path Resolution

### Current

`reportingRepositoryRoot()` walks up from CWD looking for a directory named
`microservices`. The workspace is `~/Developer/go-microservices` which contains
"microservices" in the name, so the check `filepath.Base(dir) == "microservices"`
fails because `filepath.Base("~/Developer/go-microservices")` returns
`go-microservices`, not `microservices`.

### Proposed

Change the check to `strings.HasSuffix(filepath.Base(dir), "microservices")` or
`strings.Contains(filepath.Base(dir), "microservices")`.

### Why

The workspace directory name changed during migration from Google Drive.

## Section 4: Validation Script collectDiagnostics

### Current

`main.go` calls `r.collectDiagnostics("requested")` and `r.collectDiagnostics("validation-failed")` but the method doesn't exist on the `runner` struct.

### Proposed

Add a minimal implementation that creates a diagnostics directory and writes basic info:

```go
func (r *runner) collectDiagnostics(reason string) {
    dir := filepath.Join(r.root, "artifacts", "diagnostics", reason)
    os.MkdirAll(dir, 0o755)
    // Write basic diagnostics: git status, docker ps, etc.
}
```

### Why

The method was referenced in the code but never implemented during initial development.

## Section 5: Catalog Service Coverage

### Current

Coverage at 77.3% — below the 80% gate. Pre-existing gap.

### Proposed

Add unit tests for uncovered paths in `internal/runtime/` and `internal/adapters/redis/`.
Focus on config parsing and adapter initialization paths.

### Why

Coverage gate is part of the verification contract.
