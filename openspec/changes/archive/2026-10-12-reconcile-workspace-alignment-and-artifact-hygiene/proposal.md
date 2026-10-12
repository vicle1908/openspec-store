# Proposal: Reconcile Workspace Alignment and Artifact Hygiene

## Why

Comprehensive workspace audits across repositories, agent skills, and specification directories revealed lingering temporary files, backup scrap, and unconfined test caches:
1. **Loose Backup Files**: 29 `*.bak`, `*.orig`, and `*~` backup files exist across repositories and skills (including `.agents/skills/graphify/SKILL.md.bak`, `platform/go-microservices/AGENTS.md.bak`, `tdt/realtime/.../*.bak`), creating noise and risking discovery confusion.
2. **Skill Hygiene & Non-Canonical Artifacts**: `.agents/skills/` contains backup files (`SKILL.md.bak`) that violate canonical skill discovery rules.
3. **Unconfined Test Caches & HTML Coverage**: Unmanaged `.pytest_cache`, `.ruff_cache`, and `htmlcov` folders exist in repo working trees outside virtual environments (`platform/openspec-store/.pytest_cache`, `study/ai-training-materials/.pytest_cache`, `tdt/tdt-sheets/htmlcov`).

Eliminating these scrap artifacts reinforces zero-scrap policies across repositories, purges dead files, and ensures 100% clean status across all 61 workspace checkouts.

## What Changes

1. **Purge Loose Backup & Temp Files**:
   - Recursively delete all `*.bak`, `*.orig`, and `*~` files across the workspace.
   - Clean `.agents/skills/graphify/SKILL.md.bak` to maintain pristine skill discovery.
2. **Purge Unconfined Test & Coverage Caches**:
   - Remove root/repo-level `.pytest_cache`, `.ruff_cache`, and `htmlcov` directories in `openspec-store`, `ai-training-materials`, `tdt-sheets`, and `vds-ai-memory`.
3. **Enforce Specification Contracts**:
   - Update `workspace-artifact-retention-policy` and `skill-index-hygiene` to strictly forbid backup scrap (`*.bak`, `*.orig`, `*~`) in skills and repositories.
4. **Skills Verification**:
   - Assert zero broken symlinks and 0 malformed entries via `sync-workspace-agent-skills.py --check`.

## Capabilities

### Modified Capabilities
- `workspace-artifact-retention-policy`: Mandates automated pruning of loose backup files (`*.bak`, `*.orig`, `*~`) and coverage scrap (`htmlcov/`).
- `skill-index-hygiene`: Mandates that skill directories SHALL NOT contain backup files or non-canonical file extensions.

## Impact
- **Affected Paths**: Workspace-wide repositories, `.agents/skills/`, `openspec-store`.
- **Zero Loss**: All primary sources and Git histories remain intact.
