# fix-ci-shipping-test-reliability

Allow transient failures in the shipping testcontainers pilot to prevent flaky
CI.

## Status

Completed and archived on 2026-08-02.

- Implementation: `go-microservices`
- Pull request: [vicle1908/go-microservices#12](https://github.com/vicle1908/go-microservices/pull/12)
- Merge commit: `383e67269073493479533f84b52ad758b8b5bff5`
- OpenSpec mode: tooling-only change (`skip_specs: true`)
- Verification: local build and tests passed; PR shipping CI and main-branch
  verification passed; store validation passed 349/349 on 2026-08-03
