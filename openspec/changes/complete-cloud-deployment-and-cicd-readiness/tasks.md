## 1. Non-local Kubernetes Manifests

> **Note:** Staging and production overlays already exist for all 8 services
> under `deploy/k8s/overlays/staging/` and `deploy/k8s/overlays/production/`.
> This section verifies completeness and alignment with runtime contract.

- [x] 1.1 Verify all eight staging overlays exist with kustomization.yaml, service-specific resources, and defaults overlay.
- [x] 1.2 Verify all eight production overlays exist with kustomization.yaml, service-specific resources, and defaults overlay.

## 2. Local Kind Acceptance

> **Note:** This section proves production-shaped K8s deployment on macOS arm64.
> Requires kind v0.32.0, kubeconform v0.8.0, kubectl v1.36.1 (installed 2026-08-01).

- [x] 2.1 Install kind v0.32.0, kubeconform v0.8.0, update tool pins to latest versions (kind node v1.36.1, External Secrets v2.8.0).
- [x] 2.2 Run `make kind-up` to create cluster, build images, load into kind, render overlays, deploy, and verify rollout.
- [x] 2.3 Run `make kind-smoke` for in-cluster cross-service acceptance testing.
- [x] 2.4 Run `make kind-diagnostics` to retain cluster, rollout, event, and telemetry evidence.
- [x] 2.5 Run `make kind-down` to clean up cluster.
- [x] 2.6 Verify deployment validation passes with kind: 185 checks, 0 failures, 50 skipped.
- [x] 2.7 Verify doc check passes all 11 checks including local acceptance evidence.

## 3. Multi-architecture Build (REQUIRES: Cloud CI)

> **Note:** Requires Docker registry and CI pipeline. Blocked until cloud
> infrastructure is available.

- [ ] 3.1 Build, scan, attest, and publish all eight services for linux/amd64 and linux/arm64, retaining service, source revision, repository, platforms, and immutable digest evidence.
- [ ] 3.2 Run complete clean Linux amd64 kind acceptance in CI alongside existing macOS arm64 evidence.

## 4. CI and Promotion Control (REQUIRES: GitHub Actions)

> **Note:** Requires CI platform. Blocked until Section 3 is complete.

- [ ] 4.1 Choose and document the least-privileged branch-protection-compatible promotion credential.
- [ ] 4.2 Make exhaustive deployment validation a required CI gate.
- [ ] 4.3 Run strict active-change validation on the release commit.

## 5. Environment Reconciliation (REQUIRES: Cloud Cluster + Argo CD)

> **Note:** Requires staging and production Kubernetes clusters. Blocked until
> cloud infrastructure is available.

- [ ] 5.1 Reconcile staging to the selected Git revision, verify Argo CD sync and health.
- [ ] 5.2 Promote staging-approved digests to production through reviewed Git state.

## 6. Failure Recovery (REQUIRES: Staging from Section 5)

> **Note:** Requires staging environment. Blocked until Section 5 is complete.

- [ ] 6.1 Implement deployment failure diagnostics and Git-revert rollback path.
- [ ] 6.2 Rehearse rollback in staging, verify convergence and smoke success.
