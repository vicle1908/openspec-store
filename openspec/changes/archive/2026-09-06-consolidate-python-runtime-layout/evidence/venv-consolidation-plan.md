# Python Virtual Environment Consolidation Plan

**Date**: 2026-09-05
**Type**: READ-ONLY AUDIT - No deletions performed
**Status**: Review only

---

## Summary

| Category | Count | Size |
|----------|-------|------|
| Live (LaunchAgent) | 2 | 1.1 GB |
| Developer-owned (.venv) | 10 | 3.6 GB |
| Duplicate (TDT legacy) | 4 | 1.9 GB |
| Unknown | 0 | 0 GB |
| **Total** | **16** | **6.6 GB** |

---

## Live Environments (KEEP)

These are actively used by LaunchAgents and must not be touched:

| Path | Service | Size |
|------|---------|------|
| `.tdt/deployments/ai-review/app/.venv` | ai-review | 876 MB |
| `.tdt/deployments/webhook-receiver/state/.venv` | webhook-receiver | 261 MB |

**Action**: No change required. These are referenced by `com.tdt.*.plist` LaunchAgents.

---

## Developer-Owned Environments (KEEP)

These are standard `uv sync` environments for each repo. Each repo has its own isolated `.venv` as expected.

| Repo | Size |
|------|------|
| agent-harness | 800 MB |
| agent-docs-sync | 791 MB |
| code-daily-scan | 834 MB |
| browser-cli | 321 MB |
| jira-kanban-from-spreadsheet | 267 MB |
| tdt-sheets | 256 MB |
| tdt-core | 192 MB |
| hermes-webui | 127 MB |
| ai-harness-skills | 114 MB |
| openspec-store | 33 MB |

**Action**: No change required. These are the canonical per-repo development environments.

---

## Duplicate / Legacy Environments (REVIEW)

These `.tdt/venvs/` directories may be redundant. Each needs manual verification before deletion.

### 1. `.tdt/venvs/ai-review` (841 MB)

- **Overlap**: Deployment venv at `.tdt/deployments/ai-review/app/.venv` (876 MB)
- **Assessment**: The deployment venv is actively used by `com.tdt.ai-review.plist`. The `.tdt/venvs/ai-review` may be an older copy that was superseded by the deployment venv.
- **Recommendation**: Verify if `.tdt/venvs/ai-review` is referenced anywhere. If not, it can be safely removed.

### 2. `.tdt/venvs/webhook-receiver` (330 MB)

- **Overlap**: Deployment venv at `.tdt/deployments/webhook-receiver/state/.venv` (261 MB)
- **Assessment**: The deployment venv is actively used by `com.tdt.webhook-receiver.plist`. The `.tdt/venvs/webhook-receiver` may be an older copy that was superseded by the deployment venv.
- **Recommendation**: Verify if `.tdt/venvs/webhook-receiver` is referenced anywhere. If not, it can be safely removed.

### 3. `.tdt/venvs/jira-daily-reports` (321 MB)

- **Overlap**: No workspace `.venv` found for `jira-daily-reports` repo
- **Assessment**: This TDT venv exists but the repo doesn't have a local `.venv`. May be orphaned if the repo has been migrated to use `uv sync` locally, or may still be needed for running the service.
- **Recommendation**: Check if the service is actively running. If the repo now uses `uv sync` for development, this TDT venv may be removable.

### 4. `.tdt/venvs/tdt-observability` (437 MB)

- **Overlap**: No workspace `.venv` found for `tdt-observability` repo
- **Assessment**: Same situation as jira-daily-reports. The TDT venv exists but no local `.venv` in the repo.
- **Recommendation**: Check if the service is actively running. If the repo now uses `uv sync` for development, this TDT venv may be removable.

---

## Potential Savings

If all 4 duplicate/legacy TDT venvs are confirmed unused and removed:

| Venv | Size |
|------|------|
| .tdt/venvs/ai-review | 841 MB |
| .tdt/venvs/tdt-observability | 437 MB |
| .tdt/venvs/webhook-receiver | 330 MB |
| .tdt/venvs/jira-daily-reports | 321 MB |
| **Total savings** | **1,929 MB (1.9 GB)** |

---

## Next Steps (Requires Manual Review)

1. **Verify TDT venv usage**: Check if any running processes reference `.tdt/venvs/*`
2. **Check deployment status**: Confirm which services are actively deployed via LaunchAgents
3. **Test removal**: Before deleting, temporarily rename a TDT venv to verify nothing breaks
4. **Update documentation**: If TDT venvs are removed, update workspace docs to reflect new layout

---

## Files Generated

| File | Content |
|------|---------|
| `workspace-venvs.json` | All `.venv` directories in workspace repos |
| `tdt-venvs.json` | `.tdt/venvs/` inventory |
| `deployment-venvs.json` | Deployment venv inventory |
| `launchagent-venvs.json` | LaunchAgent to venv mapping |
| `venv-sizes.json` | Comprehensive size report |
| `venv-inventory.json` | Classified inventory with categories |
| `venv-consolidation-plan.md` | This file |
