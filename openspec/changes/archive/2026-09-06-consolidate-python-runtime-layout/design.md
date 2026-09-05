# Design: consolidate-python-runtime-layout

## Approach
Execute a series of read-only discovery commands to build a complete inventory of Python virtual environments. Each discovery step produces a JSON evidence file. Final steps classify environments and produce a human-readable consolidation plan.

## Data Sources
1. **Workspace scan**: `find /Users/androidteam/Developer -maxdepth 3 -name ".venv" -type d`
2. **TDT venvs**: `du -sh /Users/androidteam/.tdt/venvs/*`
3. **Deployment venvs**: `du -sh /Users/androidteam/.tdt/deployments/*/app/.venv`
4. **LaunchAgent mapping**: `grep -l "venv" ~/Library/LaunchAgents/com.tdt.*.plist`

## Evidence Files
All evidence written to `openspec/changes/consolidate-python-runtime-layout/evidence/`:

| File | Content |
|------|---------|
| `workspace-venvs.json` | All `.venv` dirs in workspace repos |
| `tdt-venvs.json` | `.tdt/venvs/` inventory |
| `deployment-venvs.json` | Deployment venv inventory |
| `launchagent-venvs.json` | LaunchAgent → venv mapping |
| `venv-sizes.json` | Comprehensive size report |
| `venv-inventory.json` | Classified inventory |
| `venv-consolidation-plan.md` | Human-readable consolidation plan |

## Classification Categories
- **live**: Actively used by a running service or LaunchAgent
- **developer-owned**: Local development environment created by `uv sync`
- **duplicate**: Redundant copy that could be consolidated
- **unknown**: Cannot determine purpose from available data

## Verification
After audit completion, review evidence files for completeness and accuracy. Consolidation plan is advisory only.
