## MODIFIED Requirements

### Requirement: Go 1.26.5 toolchain pinned per module

Every service `go.mod` SHALL pin the toolchain as `go 1.27.1`. The platform's CI SHALL verify a `go build ./...` and `go test ./...` pass before any PR merges. The platform's `Makefile` template includes a target `verify-go-version` that fails if the toolchain is anything other than `1.27.1+`.

#### Scenario: A new service module is bootstrapped on Go 1.26
- **WHEN** a developer runs `go mod init` against a fresh `services/customer-service/`
- **THEN** `go.mod` directive is aligned to `go 1.27.1`; the platform's `bootstrap.sh` ensures compatibility with `1.27.1+`

#### Scenario: A PR fails CI if the toolchain is not 1.26.5
- **WHEN** a service's `go.mod` specifies a Go toolchain older than `1.27.1`
- **THEN** the `verify-go-version` CI check fails with a clear message
