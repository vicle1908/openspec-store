# Proposal: consolidate-python-runtime-layout

## Problem
The workspace has accumulated Python virtual environments across multiple locations:
- `.venv` directories in individual repos
- `.tdt/venvs/` for shared environments
- `.tdt/deployments/*/app/.venv` for deployed services

This makes it difficult to understand what's installed where, identify redundant environments, and plan disk cleanup.

## Solution
Conduct a comprehensive read-only audit of all Python virtual environments. Classify each environment by purpose (live, developer-owned, duplicate, unknown) and create a consolidation plan for review.

## Scope
- Inventory all `.venv` directories across the workspace
- Inventory `.tdt/venvs/` environments
- Inventory deployment venvs
- Map venvs to LaunchAgents
- Produce size report
- Create classification and consolidation plan

## Non-Goals
- No actual deletion or modification of environments
- No changes to running services
- No configuration changes
