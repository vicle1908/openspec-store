## Why

Local development and macOS arm64 kind deployment are now evidence-backed.
The `install-kind-local-k8s-setup` change installed kind v0.32.0, kubeconform
v0.8.0, updated all tool pins, and proved the full pipeline: create cluster,
build images, load into kind, render overlays, deploy, smoke test, and
retain evidence. Deployment validation passes (185 checks, 0 failures).
Doc check passes all 11 checks including local acceptance evidence.

This change documents the local K8s foundation and tracks the remaining
cloud-deployment tasks (CI, multi-arch build, Argo CD, promotion) that
require external infrastructure.

## What Changes

- Verify all staging and production K8s overlays exist and are complete
- Run full local kind acceptance pipeline on macOS arm64
- Retain kind cluster, rollout, event, and telemetry evidence
- Prove deployment validation and doc check pass with kind evidence
- Document remaining cloud tasks (CI, multi-arch, Argo CD, promotion)
  as blocked on external infrastructure

## Non-Goals

- Cloud CI/CD pipeline setup (requires GitHub Actions)
- Multi-architecture image publishing (requires Docker registry)
- Staging/production reconciliation (requires cloud cluster with Argo CD)
- Rollback rehearse (requires staging environment)
