## Why

Two CI workflows fail systematically on every run.

## What Changes

- Skip SLSA attestation on private repos (`k8s-deploy.yaml`)
- Add catalog contracts placeholder (`catalog/v1/README.md`)
- Archive OpenSpec change (skip_specs: true)

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. CI/tooling only.

## Impact

- **Repository surfaces:** `.github/workflows/k8s-deploy.yaml`,
  `services/catalog-service/contracts/`.
- **Rollout:** Commit and verify CI passes on next PR/push.
