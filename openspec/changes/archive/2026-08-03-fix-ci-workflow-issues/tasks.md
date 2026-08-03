## 1. Standardize action versions

- [x] 1.1 Update verify.yml — checkout@v4, setup-go@v5, cache@v4, upload-artifact@v4
- [x] 1.2 Update deployment-validation.yml — checkout@v4
- [x] 1.3 Update integration.yml — checkout@v4, setup-go@v5
- [x] 1.4 Update k8s-deploy.yaml — checkout@v4, setup-buildx@v3, setup-qemu@v3, docker actions
- [x] 1.5 Update lgtm-e2e.yml — checkout@v4, setup-go@v5, cache@v4, upload-artifact@v4, setup-buildx@v3
- [x] 1.6 Update release-evidence.yml — checkout@v4, setup-go@v5, cache@v4, upload-artifact@v4, setup-node@v4
- [x] 1.7 Update gitops-reconcile.yml — checkout@v4, setup-go@v5, upload-artifact@v4
- [x] 1.8 Update gitops-rollback.yml — checkout@v4

## 2. Fix skill restore in verify.yml

- [x] 2.1 Commit .agents/skills/openspec-* to repo (remove from .gitignore)
- [x] 2.2 Remove the restore step from verify.yml (skills are now in repo)
- [x] 2.3 Update doccheck validator if needed

## 3. Add actionlint

- [x] 3.1 Add actionlint step to verify.yml (runs before other jobs)
- [x] 3.2 Fix any actionlint warnings

## 4. Validate

- [x] 4.1 Run actionlint locally
- [x] 4.2 Verify CI passes on PR
- [x] 4.3 Verify CI passes on main
