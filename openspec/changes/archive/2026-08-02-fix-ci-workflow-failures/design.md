## Issue 1: Attestation on private repos

`k8s-deploy.yaml` uses `actions/attest` (SLSA provenance) which requires
public repos. Added `if: github.repository_visibility == 'public'` to skip
silently on private repos.

## Issue 2: Missing catalog contracts

`services/catalog-service/contracts/` had zero tracked files. Dockerfile
`COPY` step failed in CI. Added placeholder `catalog/v1/README.md`.
