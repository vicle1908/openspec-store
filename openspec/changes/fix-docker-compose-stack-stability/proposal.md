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
