# platform-go-runtime Specification Delta

## MODIFIED Requirements

### Requirement: Goroutine leak profile enabled in staging canary

The platform SHALL expose the Go 1.27 generally available goroutine leak profile at `/debug/pprof/goroutineleak` in staging and production canary deployments without setting the retired `GOEXPERIMENT=goroutineleakprofile` build flag. The platform's alert SHALL fire when the scraped leak count exceeds a service-specific threshold (default: 10 leaks over 24 hours).

#### Scenario: Canary exposes goroutine leak profile
- **WHEN** a service compiled with Go `1.27.2` runs in the staging or production canary deployment
- **THEN** no `GOEXPERIMENT=goroutineleakprofile` variable SHALL be set
- **AND** the leak profile endpoint SHALL be reachable at `/debug/pprof/goroutineleak` and Prometheus metrics SHALL expose the leak count

## ADDED Requirements

### Requirement: Module go 1.27.2 directive and v2 tool block alignment across go-microservices

`platform/go-microservices/platform/go.mod` and all `services/*/go.mod` files SHALL declare `go 1.27.2` (matching `.go-version`) and pin `github.com/golangci/golangci-lint/v2/cmd/golangci-lint` and `github.com/bufbuild/buf/cmd/buf` (`v1.71.0` module tool / `1.74.0` host CLI) in their `tool (...)` directive.

#### Scenario: All go.mod files match .go-version 1.27.2 and v2 tool paths
- **WHEN** `platform/go.mod` and `services/*/go.mod` in `platform/go-microservices` are inspected
- **THEN** every `go.mod` file SHALL specify `go 1.27.2`
- **AND** the `tool (...)` block SHALL reference `github.com/golangci/golangci-lint/v2/cmd/golangci-lint` rather than the v1 module path
