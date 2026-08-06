# Design: Setup GitHub Repository

## Context

The microservices repository exists on GitHub (`vicle1908/go-microservices`) but lacks essential configuration. The local repo has 20+ commits ahead of GitHub after workspace migration. The existing CI/CD workflows are sophisticated but need proper GitHub configuration to function.

## Section 1: Git Configuration

### Current

- Remote: NOT configured locally
- User: "Phase 2 Implementation" (placeholder)
- Email: phase2-bot@microservices.local

### Proposed

```bash
git remote add origin https://github.com/vicle1908/go-go-microservices.git
git config user.name "Vinh Le"
git config user.email "victory1908@gmail.com"
```

### Why

Proper attribution for commits. Remote enables push/pull operations.

## Section 2: Repository Files

### Current

- No LICENSE file
- No CODEOWNERS file

### Proposed

- Add MIT LICENSE file
- Add `.github/CODEOWNERS` with `* @vicle1908`

### Why

MIT is permissive and matches the project's open nature. CODEOWNERS enables automatic review assignments per [GitHub docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).

## Section 3: Branch Protection

### Current

No branch protection rules.

### Proposed

Enable branch protection on `main` via GitHub API:
- Require pull request reviews (1 reviewer)
- Require status checks to pass (`verify`, `deployment-validation`)
- Require branches to be up to date
- Dismiss stale reviews
- Require code owner reviews

### Why

Prevents direct pushes to main, ensures CI passes before merge. Per [GitHub docs](https://docs.github.com/en/rest/branches/branch-protection).

## Section 4: GitHub Secrets

### Current

No secrets configured.

### Proposed

Add secrets via `gh secret set`:
- `GHCR_TOKEN` — personal access token with `write:packages` scope for GHCR authentication
- `DOCKER_USERNAME` — Docker Hub username (if needed for base images)
- `DOCKER_PASSWORD` — Docker Hub password (if needed)

### Why

Image build workflow needs GHCR authentication to push images. Per [GitHub docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).

## Section 5: Sync Local to GitHub

### Current

Local has 20+ commits ahead of GitHub (workspace migration, OpenSpec store, Redis improvements, etc.).

### Proposed

Force-push local to GitHub:
```bash
git push --force-with-lease origin main
```

### Why

Local has all the workspace migration fixes, OpenSpec store setup, and recent improvements. GitHub is stale (last push July 29).

## Section 6: Clean Stale Files

### Current

GitHub has `openspec/` directory (in-repo approach).

### Proposed

Remove `openspec/` from GitHub (we use store-based approach now at `~/Developer/openspec-store/`).

### Why

OpenSpec lives at workspace level, not in the repo. The in-repo directory is stale.
