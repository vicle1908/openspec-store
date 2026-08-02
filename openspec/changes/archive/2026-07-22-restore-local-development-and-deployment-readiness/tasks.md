## 1. Validation Baseline and Evidence

- [x] 1.1 Add a single deployment-validation entry point that records the source commit, unique run identifier, tool versions, commands, check results, and artifact paths in a machine-readable manifest.
- [x] 1.2 Add non-mutating preflight checks for supported Go, Docker, Docker Compose, kubectl, and kind versions, host architecture, required ports, minimum resources, and linux/amd64 plus linux/arm64 image availability.
- [x] 1.3 Add stale-state detection and isolation for Compose projects, kind clusters, containers, volumes, and images so a previous run cannot satisfy acceptance for the tested commit.
- [x] 1.4 Add bounded failure traps that collect Compose state, logs, health metadata, Kubernetes events, workload descriptions, image inventories, Argo CD status, and smoke reports before cleanup.
- [x] 1.5 Add a report-only CI job that runs the validator against the current repository and retains its failing baseline manifest and diagnostics.

## 2. Canonical Compose Runtime

- [x] 2.1 Refactor the root Makefile to define one pinned interpolation environment and canonical base, applications, LGTM, tools, and full Compose file sets used by validation, startup, shutdown, and CI.
- [x] 2.2 Make required Compose variables fail during model rendering, then add tests that reject empty image tags, undefined dependencies, and unresolved interpolation across every supported file set.
- [x] 2.3 Add all eight services and each required API, worker, orchestrator, consumer, migration, topic, connector, and infrastructure initializer to the canonical full-stack model.
- [x] 2.4 Make topic, connector, and migration initialization scripts executable and idempotent, and gate dependants with successful one-shot completion conditions.
- [x] 2.5 Add an idempotent Temporal namespace initializer that waits for frontend readiness, describes or creates each configured namespace, verifies the result, and blocks workers on failure.
- [x] 2.6 Add worker readiness that proves connection to the configured Temporal namespace and registration on every required task queue; retain polling failures in diagnostics.
- [x] 2.7 Update every OpenTelemetry Collector configuration to the schema accepted by the pinned image, expose a supported health endpoint, and validate each config with that exact image in CI.
- [x] 2.8 Add a one-shot smoke service on the Compose network that exercises the deployed order workflow across all eight service boundaries and writes a machine-readable report to a host artifact directory.
- [x] 2.9 Make smoke verification fail on any absent API, worker, data-plane dependency, workflow boundary, reporting outcome, or required trace, metric, or log signal.
- [x] 2.10 Implement canonical `dev-up`, routine `dev-down`, explicit destructive reset, and diagnostic commands with bounded waits and project-scoped cleanup.
- [x] 2.11 Prove clean full-stack startup and smoke success twice without duplicating namespaces, topics, connectors, migrations, or externally visible workflow effects, and retain both evidence manifests.

## 3. Local kind Lifecycle

- [x] 3.1 Pin the kind node image and supporting kubectl/schema-validation tool versions, and document the supported macOS arm64 and Linux amd64 setup.
- [x] 3.2 Add idempotent commands to create only the named kind cluster and optional local registry, record their initial inventory, and reject conflicting resources.
- [x] 3.3 Build uniquely tagged images for all eight services, verify their target architectures, and load them into kind or publish them to the documented local registry.
- [x] 3.4 Implement per-service local Kustomize overlays with resolved roles, ports, probes, service accounts, ConfigMaps, development Secrets, resources, selectors, and kind-compatible image pull policies.
- [x] 3.5 Add local aggregation and ordered application of prerequisites plus all eight service overlays, then wait a bounded time for workloads and Temporal workers to converge.
- [x] 3.6 Run the cross-service Kubernetes smoke and telemetry assertions against kind and retain the tested image identifiers, rendered manifests, rollout status, and smoke report.
- [x] 3.7 Add idempotent kind diagnostics and teardown that target only the configured cluster and registry and never delete unrelated local resources.

## 4. Deployable Staging and Production Manifests

- [x] 4.1 Refactor the Kubernetes base to use schema-valid stable resource names and remove free-form service, image, role, version, and resource placeholders.
- [x] 4.2 Implement per-service staging overlays for all eight services with complete workloads, immutable image digests, configuration, identities, resources, autoscaling, disruption budgets, and network policies.
- [x] 4.3 Implement per-service production overlays for all eight services with complete workloads, immutable image digests, configuration, identities, resources, autoscaling, disruption budgets, and network policies.
- [x] 4.4 Include ExternalSecret resources in every non-local service render, validate their target Secrets and ClusterSecretStore prerequisite, and remove committed reusable credential literals.
- [x] 4.5 Add recursive overlay discovery and forbidden-placeholder checks covering every local, staging, and production service directory.
- [x] 4.6 Add pinned Kubernetes schema and policy validation plus server-side dry-run for every rendered overlay, with tests for invalid quantities, APIs, selectors, and security settings.
- [x] 4.7 Add reference-integrity validation for service accounts, ConfigMaps, Secrets, ExternalSecrets, volumes, Services, HPAs, PDBs, selectors, and documented cluster prerequisites.
- [x] 4.8 Add policy tests that require unique local images, immutable non-local digests, compatible replica/HPA/PDB semantics, and no forbidden secret literal in tracked or rendered non-local configuration.
- [x] 4.9 Migrate every consumer to the per-service environment directories, remove the obsolete generic environment overlays, and verify no documentation or automation references them.

## 5. Argo CD Desired-State Ownership

- [x] 5.1 Decide and document the canonical repository URL, authoritative staging and production cluster-secret labels, target namespaces, and required AppProject plus External Secrets prerequisites.
- [x] 5.2 Rebuild local, staging, and production ApplicationSets with Go templates, `missingkey=error`, valid string-valued generator data, real per-service overlay paths, and explicit environment cluster selection.
- [x] 5.3 Add ApplicationSet generation tests proving exactly eight valid Applications per selected environment and failure on missing revision, path, image, cluster, or namespace values.
- [x] 5.4 Add AppProject and repository/destination constraints that permit the intended resources without granting unrelated repositories, clusters, namespaces, or cluster-scoped kinds.
- [x] 5.5 Add policy validation that rejects imperative mutation of Argo-managed service resources outside disposable validation clusters.
- [x] 5.6 Rehearse staging reconciliation to the selected Git revision, wait for all Applications to become Synced and Healthy, run environment smoke checks, and retain Argo CD resource evidence.

## 6. Immutable Build and Git Promotion

- [x] 6.1 Repair GitHub Actions permissions and registry configuration to authenticate to `ghcr.io` with least privilege, including `packages: write` only for publishing jobs.
- [x] 6.2 Replace the malformed service loop with a validated GitHub Actions matrix covering all eight services and fail the workflow when any required matrix job is absent.
- [x] 6.3 Build, scan, attest, and publish linux/amd64 plus linux/arm64 images, then record service, source commit, repository, platforms, and immutable digest in machine-readable artifacts.
- [x] 6.4 Prevent promotion when any required build, scan, attestation, publish, or digest-evidence job fails.
- [x] 6.5 Choose and document the least-privileged branch-protection-compatible promotion credential, then update environment digest fields on a promotion branch and open or refresh a reviewable pull request.
- [x] 6.6 Remove imperative application deployment from release workflows and make the merged Git promotion commit the only trigger for Argo-managed desired-state changes.
- [x] 6.7 Gate deployment completion on the promoted Applications becoming Synced and Healthy at the expected Git revision followed by successful environment smoke and telemetry verification.
- [x] 6.8 Implement failure diagnostics and an operator-approved Git-revert rollback path, then verify Argo CD returns affected Applications to the prior known-good digests.

## 7. Documentation and Evidence-Gated Status

- [x] 7.1 Audit current OpenSpec requirements and task checkboxes, downgrade unsupported implementation claims, and link every retained readiness claim to its acceptance command and evidence manifest.
- [x] 7.2 Update root and deployment documentation with canonical preflight, Compose, smoke, kind, validation, promotion, diagnostics, reset, and rollback commands plus their safety boundaries.
- [x] 7.3 Update Kubernetes and Argo CD documentation for per-service overlays, cluster labels, external-secret prerequisites, digest ownership, environment sequencing, and failure recovery.
- [x] 7.4 Label existing audit reports as dated snapshots and document how a changed runtime pin or deployment artifact requires a new validation manifest.
- [x] 7.5 Make deployment validation a required CI gate only after Compose, Collector, Kustomize, reference, secret, ApplicationSet, and OpenSpec checks all pass on a clean environment.

## 8. Acceptance and Rollout

- [x] 8.1 Run the complete Compose acceptance twice from a clean unique project and retain passing manifests proving all eight services, Temporal workers, reporting, and required telemetry.
- [x] 8.2 Run the complete kind acceptance from a clean named cluster on each supported architecture path and retain manifests, images, rollouts, diagnostics, and smoke evidence.
- [x] 8.3 Run strict OpenSpec validation and the exhaustive deployment validator on the release commit, and verify the result enumerates every Compose model, Collector config, service/environment overlay, ApplicationSet, and secret check.
- [x] 8.4 Promote the release through staging by Git digest change, verify Argo CD health and smoke evidence, and require explicit approval before applying the same reviewed digests to production.
- [x] 8.5 Rehearse Git-revert rollback in staging, verify convergence to the previous healthy digests, and record recovery timing and evidence before declaring the rollout mechanism ready.
