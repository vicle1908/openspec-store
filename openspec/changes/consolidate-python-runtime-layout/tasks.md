## 1. Inventory
- [ ] 1.1 Inventory repo-local `~/Developer/*/.venv`, `~/.tdt/venvs/*`, and `~/.tdt/deployments/*/app/.venv` paths with `du -sh`, `stat`, and absolute paths; write `evidence/venv-inventory.json`.
- [ ] 1.2 Map each environment to its `pyproject.toml`, `uv.lock`, LaunchAgent plist under `~/Library/LaunchAgents/`, container, or no owner; verify no credentials are recorded.
## 2. Evaluate
- [ ] 2.1 Classify environments as live, developer-owned, duplicate, or unknown using process/plist references; verify unknowns remain protected.
- [ ] 2.2 Write `evidence/venv-consolidation-plan.md` with exact deletion prerequisites, affected service, rollback path, and owner approval required for each candidate.
## 3. Finalize
- [ ] 3.1 Validate, archive, and commit evidence without deleting any venv.
