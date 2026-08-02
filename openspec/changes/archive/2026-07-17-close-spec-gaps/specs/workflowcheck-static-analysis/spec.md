# workflowcheck-static-analysis Specification

## Purpose

Static analysis tool to detect non-deterministic patterns in Temporal workflow code, ensuring workflows can safely replay.

## Requirements

### Requirement: Non-deterministic pattern detection

The workflowcheck tool SHALL detect the following patterns in workflow code:

| Pattern | Example | Severity |
|---------|---------|----------|
| Wall-clock time | `time.Now()`, `time.Sleep()` | Error |
| Randomness | `math/rand.*` | Error |
| Goroutines | `go func()` | Error |
| Channel operations | `<-ch`, `ch<-` | Warning |
| Mutex/sync | `sync.Mutex` | Warning |

#### Scenario: time.Now detected

- **WHEN** workflow code calls `time.Now()`
- **THEN** workflowcheck reports an error with file, line, column

#### Scenario: goroutine detected

- **WHEN** workflow code contains `go func()`
- **THEN** workflowcheck reports an error

### Requirement: Allowlist support

The tool SHALL support an allowlist in `platform/workflows/.workflowcheck.yaml` that permits specific function calls.

#### Scenario: Allowlisted function permitted

- **WHEN** a function is listed in the allowlist
- **THEN** no issue is reported for calls to that function

### Requirement: Output formats

The tool SHALL support JSON and text output formats.

#### Scenario: JSON output format

- **WHEN** `--format=json` is passed
- **THEN** output is machine-parseable JSON

### Requirement: CI integration

The tool SHALL be executable as a standalone binary and integratable into CI pipelines.

#### Scenario: Exit code reflects issues

- **WHEN** issues are found
- **THEN** exit code is non-zero
- **WHEN** no issues are found
- **THEN** exit code is 0
