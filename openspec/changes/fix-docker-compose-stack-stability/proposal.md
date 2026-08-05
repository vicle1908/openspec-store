# Proposal: Fix Docker Compose Stack Stability

## Why

Real local-stack verification exposed two reproducible regressions in the Compose
runtime topology:

1. The catalog Redis overlay published host port `6379`, colliding with another
   Compose project using the same host.
2. Adding a hard `depends_on` edge from focused service overlays to
   `otel-collector` broke the shipping-focused Testcontainers stack because its
   allowlisted topology does not include the LGTM collector service.

The same verification also confirmed two items that must remain documented rather
than changed: `temporal-admin-tools` is an intentional one-shot initializer with
`restart: "no"`, and the GHCR 403 was selective/transient while the workflow's
effective job permission was already `packages: write`.

## Scope

- Remove fixed host publication from the catalog Redis service (keep the
  container-network address `redis:6379`).
- Keep focused Compose overlays independent of optional LGTM services.
- Preserve OTel exporter retry behavior for startup ordering instead of requiring
  an undeclared service in every focused topology.
- Add regression validation and operator documentation for the startup contract.
- Upgrade the local Kubernetes validation toolchain to the latest upstream
  releases verified on 2026-08-05.
- Make the focused Shipping concurrency probe deterministic so it reliably
  observes the required in-progress response before stub completion.
- Record the real GitHub CI evidence and the known GHCR limitation.

## Out of Scope

- Changing GHCR authentication permissions, which are already correct at the
  job level.
- Converting the Temporal schema initializer into a long-running service.
- Disabling OTel or changing application exporter configuration.

## Acceptance Criteria

- `docker compose config` validates base, application, LGTM, tools, full, and
  arm64 models.
- The catalog Redis service has no fixed host port 6379.
- The shipping-focused Testcontainers operation passes with its exact three-file
  topology.
- Full LGTM smoke verification passes on GitHub Actions.
- All required GitHub checks pass on the PR.
- Repository preflight passes with kind v0.32.0, kubectl/Kubernetes v1.36.3,
  kubeconform v0.8.0, External Secrets v2.8.0, and kind's newest published
  Kubernetes node image.
