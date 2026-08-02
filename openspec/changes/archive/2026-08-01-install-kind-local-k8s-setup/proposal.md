## Why

The `complete-cloud-deployment-and-cicd-readiness` change requires local
Kubernetes validation via kind (task 2.2). Currently kind is not installed
on this workstation, which blocks:

1. `make validate-deployment` — creates a disposable kind cluster to validate
   K8s overlays, run server-side dry-run, and produce deployment evidence
2. `make kind-up / kind-smoke / kind-down` — full in-cluster acceptance testing
3. The doc check "local acceptance evidence" gate — requires a passed
   deployment-validation manifest from kind

Without kind, 73/85 validator checks pass (preflight, repository, kubernetes
static analysis) but the 9 cluster-dependent checks fail, producing a
manifest with status="running" instead of "passed". This blocks the evidence
chain and prevents the cloud deployment change from proceeding.

## What Changes

- Install kind v0.31.0 (pinned in `deploy/kind/tool-versions.env`)
- Install kubeconform v0.7.0 for K8s schema validation
- Verify kind cluster creation, deployment of K8s overlays, and cleanup
- Run `make validate-deployment` to produce a passing deployment-validation
  manifest with correct worktree digest
- Verify doc check passes with the new evidence
- Unblock the `complete-cloud-deployment-and-cicd-readiness` change

## Non-Goals

- Building multi-architecture images (task 2.1 of cloud deployment change)
- CI/CD pipeline setup (Section 3 of cloud deployment change)
- Staging/production reconciliation (Section 4 of cloud deployment change)
