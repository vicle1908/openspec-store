## Current State

### Action Version Chaos
```
checkout:    v4 (5), v6 (8 SHA-pinned), v7 (3)
setup-go:    v5 (2), v6 (1 SHA-pinned), v7 (3)
cache:       v4 (2), v6 (1)
upload-artifact: v4 (2+2 SHA-pinned), v7 (3)
download-artifact: v4 (0), v5 (2 SHA-pinned)
setup-buildx: v3 (1), v4 (1)
```

The "v6/v7" references are SHA-pinned references that happen to be the latest
commits. The actual stable versions are:
- checkout: v4
- setup-go: v5
- cache: v4
- upload-artifact: v4
- download-artifact: v4
- setup-buildx: v3

### Skill Restore Problem
```yaml
- name: Restore clean-checkout verification inputs
  run: |
    mkdir -p .agents/skills
    jq -r '.mirroredSkills[]' verification/documentation-currency.json | while read -r skill; do
      cp -R ".codex/skills/$skill" ".agents/skills/$skill"
    done
```

This assumes `.fable-5kills/` exists in the repo, but `.codex/` is gitignored.
On CI, the checkout won't have these files.

### No Linting
No actionlint or yamllint in CI. Workflow YAML issues are only caught at runtime.

## Proposed Change

### 1. Standardize Action Versions

Create a `.github/actions-versions.yaml` reference (or just use consistent
versions in all workflows):

| Action | Standard Version | SHA Pin |
|--------|-----------------|---------|
| actions/checkout | v4 | d23441a48e516b6c34aea4fa41551a30e30af803 |
| actions/setup-go | v5 | 924ae3a1cded613372ab5595356fb5720e22ba16 |
| actions/cache | v4 | 5a3ec84eff668545956fd18022155c47e93e2684 |
| actions/upload-artifact | v4 | ea165f8d65b6e75b540449e92b4886f43607fa02 |
| actions/download-artifact | v4 | fa0a91b85d4f404e444e00e005971372dc801d16 |
| docker/setup-buildx-action | v3 | 8d2750c68a42422c14e847fe6c8ac0403b4cbd6f |
| docker/setup-qemu-action | v3 | c7c53464625b32c7a7e944ae62b3e17d2b600130 |
| docker/build-push-action | v6 | 10e90e3645eae34f1e60eeb005ba3a3d33f178e8 |
| docker/login-action | v3 | c94ce9fb468520275223c153574b00df6fe4bcc9 |

### 2. Fix Skill Restore

Option A: Commit skills to repo (remove from .gitignore)
Option B: Use a restore script that works without .codex/
Option C: Generate skills during CI from source of truth

Best: Option A — commit the skills since they're needed for doccheck validation.

### 3. Add Actionlint

Add a lint job that runs actionlint on all workflow files before other jobs.

## Files Changed

- `.github/workflows/*.yml`: Standardize action versions
- `.github/workflows/verify.yml`: Fix skill restore
- `.github/workflows/verify.yml`: Add actionlint step
