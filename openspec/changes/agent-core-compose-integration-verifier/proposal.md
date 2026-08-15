# Proposal: Portable agent-core Compose integration verifier

## Why

The Go workspace needs a repeatable local integration entry point that can build the verifier from the repository's `platform/` module, start only the required Compose dependencies, wait for real health state, and clean up only resources created by the run. The current repository has platform health primitives and service-specific checks, but no portable verifier for the local data-plane stack.

## What Changes

- Add a small `platform/cmd/agent-core` binary with `version` and `health` commands.
- Make health evaluation fail closed for missing, malformed, stopped, or unhealthy Compose containers and support both object and array JSON output from Compose.
- Add `scripts/agent-core-integration-test.sh` with repository-relative Compose defaults, an explicit prebuilt-binary override, bounded polling, and trap-based cleanup.
- Add a no-Docker regression script that exercises portability, override ownership, cleanup scope, strict mode, and exit-code propagation.
- Document the verifier and its required environment variables in `scripts/README.md`.

This change is intentionally scoped to local integration verification. It does not replace the canonical `platform/health` runtime registry or change service health endpoints.
