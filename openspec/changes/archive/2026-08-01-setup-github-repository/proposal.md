# Setup GitHub Repository

## Why

The microservices repository exists on GitHub (`vicle1908/microservices`) but lacks essential configuration for proper development workflow:

1. **No git remote configured locally** — workspace was migrated from Google Drive to `~/Developer/go-microservices` without re-configuring the remote
2. **No branch protection** — no required reviews, status checks, or merge controls
3. **No secrets configured** — CI workflows fail because GHCR token and other secrets are missing
4. **No CODEOWNERS** — no automated review assignments
5. **No LICENSE file** — legal uncertainty for contributors
6. **Git user is placeholder** — "Phase 2 Implementation" instead of real identity
7. **GitHub has stale `openspec/` directory** — we migrated to store-based approach
8. **Image build workflow fails** — missing GHCR authentication

## What Changes

- Configure git remote to point to GitHub
- Fix git user configuration
- Add LICENSE file (MIT)
- Add CODEOWNERS file
- Configure branch protection rules
- Add GitHub secrets (GHCR token)
- Remove stale `openspec/` directory from GitHub
- Fix image build workflow
- Sync local changes to GitHub

## Goals

- Enable CI/CD pipeline to run on all PRs and pushes
- Enable image builds to GHCR
- Enable branch protection with required reviews
- Establish proper code ownership
- Sync local workspace (20+ commits ahead) to GitHub

## Non-Goals

- Full cloud deployment (blocked on infrastructure)
- Kubernetes cluster setup on cloud
- Argo CD configuration

## Affected Boundaries

- `.github/` — workflows, CODEOWNERS
- `.gitignore` — may need updates
- Git configuration — remote, user
- GitHub repository settings — branch protection, secrets

## Compatibility

All changes are additive or configuration. No service code changes.
