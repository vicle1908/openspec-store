## 1. Tool Installation

- [x] 1.1 Install kind via Homebrew: `brew install kind`
- [x] 1.2 Install kubeconform via Homebrew: `brew install kubeconform`
- [x] 1.3 Run `make install-kind-tools` to verify pins
- [x] 1.4 Verify kind version matches `deploy/kind/tool-versions.env` pin
- [x] 1.5 Verify kubeconform version matches pin

## 2. Cluster Verification

- [x] 2.1 Create test kind cluster with project's pinned node image
- [x] 2.2 Verify cluster is healthy: `kubectl get nodes` shows Ready
- [x] 2.3 Verify kubectl context is set correctly
- [x] 2.4 Clean up test cluster: `kind delete cluster --name microservices-test`

## 3. Deployment Validation

- [x] 3.1 Stop Docker Compose stack to free resources
- [x] 3.2 Run `make validate-deployment` with full validation
- [x] 3.3 Verify manifest status=passed with correct worktreeDigest
- [x] 3.4 Update `verification/documentation-currency.json` to new evidence
- [x] 3.5 Verify doc check passes with `--skip-local-evidence` removed

## 4. Smoke Test

- [x] 4.1 Restart Docker Compose stack
- [x] 4.2 Run `make kind-up` to create production-shaped local cluster
- [x] 4.3 Run `make kind-smoke` for in-cluster acceptance
- [x] 4.4 Run `make kind-diagnostics` to retain evidence
- [x] 4.5 Run `make kind-down` to clean up

## 5. Verification

- [x] 5.1 Run full validation suite (all 7 gates)
- [x] 5.2 Verify doc check passes all 11 checks including evidence
- [x] 5.3 Commit all changes
