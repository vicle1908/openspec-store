## Approach

### Phase 1: Local Kind Acceptance (COMPLETE)

1. **Tool Installation** — kind v0.32.0, kubeconform v0.8.0 via Homebrew
2. **Cluster Lifecycle** — create, build, load, render, deploy, smoke, diagnostics, down
3. **Evidence** — deployment-validation manifest, doc check 11/11, operation readiness 29/29

### Phase 2: Overlay Verification (COMPLETE)

1. **Staging Overlays** — all 8 services exist under `deploy/k8s/overlays/staging/`
2. **Production Overlays** — all 8 services exist under `deploy/k8s/overlays/production/`
3. **Validation** — overlays pass recursive discovery, schema, policy, and reference checks

### Phase 3: Cloud CI/CD (BLOCKED — requires external infrastructure)

1. **Multi-arch Build** — build linux/amd64 + linux/arm64 images, publish to registry
2. **CI Gates** — GitHub Actions with deployment validation, image verification, OpenSpec checks
3. **Argo CD** — staging reconciliation, promotion, production deployment

### Phase 4: Staging/Production (BLOCKED — requires cloud clusters)

1. **Staging** — Argo CD reconciliation, smoke, telemetry verification
2. **Production** — promotion, deployment, rollback rehearse

## Risk

- kind cluster builds images for arm64 only (macOS host)
- Multi-arch builds require CI with cross-compilation or buildx
- Cloud deployment requires Docker registry, Kubernetes cluster, Argo CD
