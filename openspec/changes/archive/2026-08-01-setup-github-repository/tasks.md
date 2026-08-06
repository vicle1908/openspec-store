# Tasks: Setup GitHub Repository

## Section 1: Git Configuration

- [x] 1.1 Configure git remote to point to GitHub repository.
  - **Verification**: `git remote -v` shows origin pointing to `vicle1908/go-microservices`

- [x] 1.2 Fix git user configuration with real identity.
  - **Verification**: `git config user.name` returns "Vinh Le"

## Section 2: Repository Files

- [x] 2.1 Add MIT LICENSE file to repository root.
  - **Verification**: `ls LICENSE` exists and contains MIT license text

- [x] 2.2 Add `.github/CODEOWNERS` file with `* @vicle1908`.
  - **Verification**: `cat .github/CODEOWNERS` shows `* @vicle1908`

## Section 3: Branch Protection

- [x] 3.1 Enable branch protection on `main` via GitHub API.
  - **Verification**: `gh api repos/vicle1908/go-microservices/branches/main/protection` returns 200

## Section 4: GitHub Secrets

- [x] 4.1 Add GHCR token secret for image builds.
  - **Verification**: `gh secret list` shows GHCR_TOKEN

## Section 5: Sync Local to GitHub

- [x] 5.1 Commit all local changes (LICENSE, CODEOWNERS, git config).
  - **Verification**: `git status` shows clean working tree

- [x] 5.2 Force-push local to GitHub to sync 20+ commits.
  - **Verification**: `gh api repos/vicle1908/go-microservices/commits?per_page=1` shows latest local commit

## Section 6: Verify CI

- [x] 6.1 Trigger verify workflow and check it passes.
  - **Verification**: `gh run list --workflow=verify.yml --limit=1 --json conclusion` returns "success"

- [x] 6.2 Trigger deployment-validation workflow and check it passes.
  - **Verification**: `gh run list --workflow=deployment-validation.yml --limit=1 --json conclusion` returns "success"
