## Approach

### Tool Installation

1. Install kind via Homebrew: `brew install kind`
   - Pinned version: v0.31.0 (from `deploy/kind/tool-versions.env`)
   - Architecture: arm64 (Apple Silicon)
   - Size: ~10MB binary

2. Install kubeconform via Homebrew: `brew install kubeconform`
   - Pinned version: v0.7.0 (from `deploy/kind/tool-versions.env`)
   - Used by `validate-deployment` for K8s schema validation

3. Run `make install-kind-tools` to verify pins and install any
   additional tooling defined in `scripts/install-kind-tools.sh`

### Cluster Verification

1. Create a test kind cluster using the project's pinned node image:
   ```
   kind create cluster --name microservices-test \
     --image kindest/node:v1.35.0@sha256:452d... \
     --config deploy/kind/cluster.yaml
   ```

2. Verify cluster is healthy: `kubectl get nodes`

3. Clean up: `kind delete cluster --name microservices-test`

### Deployment Validation

1. Stop Docker Compose stack to free resources for kind
2. Run `make validate-deployment` which:
   - Runs preflight checks (17 checks)
   - Creates disposable kind cluster
   - Renders K8s overlays
   - Runs server-side dry-run
   - Validates schemas
   - Produces `artifacts/deployment-validation/<run-id>/manifest.json`
   - Destroys kind cluster
3. Verify manifest status=passed with correct worktreeDigest
4. Update `verification/documentation-currency.json` to point to new evidence
5. Restart Docker Compose stack

### Resource Requirements

- kind cluster: ~512MB RAM, 1 CPU (single control-plane node)
- Docker Desktop: 8 CPUs, 15.6 GiB available
- Sufficient for kind + Compose to coexist

## Risk

- kind creates a Docker container that competes with Compose for resources
- Solution: Stop Compose stack before running `validate-deployment`
- kind cluster is disposable (created, validated, destroyed in <5 minutes)
