# Migration and Verification Evidence: migrate-icloud-worktrees-safely

**Date:** 2026-09-21
**Status:** In Progress (Reopened: Two-Way Audit Uncovered 2,551 Unaccounted Files)

## 1. Two-Way Reconciliation Audit Findings

A comprehensive two-way filesystem walk comparing the iCloud source against the local destination and manifest revealed that **2,551 candidate files** were unaccounted for in `migration-manifest.json`:

- **Legitimate Source & Skill Dot-Directories**:
  - `vds-skills/.cursor/skills/` (29 agent skills)
  - `vds-scripts/.openspace/` (217 files including `openspace.db`, `SKILL.md`, `QUALITY.md`)
  - `vds-scripts/.github/` (9 workflow files)
  - `vds-scripts/.claude/` (7 skill/doc files)
  - `vds-scripts/.import_linter_cache` / `.code-review-graph` (metadata)
  These were skipped because `run_hydration_loop.py` used `not d.startswith(".")`, inadvertently skipping configuration and skill directories.

- **Loose Top-Level Files in `vds-scripts/` and Root**:
  - Direct files in `vds-scripts/` (`analyze_hexagonal.py`, `upgrade_major.py`, `vds-evolution-mono.sh`, `repo-manifest.yaml`, `audit-checklist.xlsx`, `pyproject 2.toml`, `AGENTS.md`, `CLAUDE.md`, etc.).
  These were missed because `run_hydration_loop.py` iterated only over discovered child package directories, skipping files residing directly at directory roots.

- **iCloud Collision Copies of Excluded Directories**:
  - Entries like `.venv 2`, `.venv 3`, `.pytest_cache 2`, `.hypothesis 2`, and `__pycache__ 2` across multiple worktrees (~2,200 files).
  - When macOS iCloud syncs while local builds or virtual environments are created, it produces numbered collision copies of excluded items. These are build/cache artifacts, not application source code, and must be treated under the excluded directory rule.

## 2. Recovery Plan & Governance Actions

1. **OpenSpec Governance**: Premature archive reverted; Tasks 3.3, 4.1, 4.3, and 5.1 reopened (`[ ]`).
2. **Tooling Fixes**:
   - Enhance exclusion regex to treat numbered collision copies of excluded directories (`.venv 2`, `__pycache__ 2`, etc.) as excluded.
   - Fix directory discovery to include legitimate hidden directories (`.cursor`, `.openspace`, `.github`, `.claude`) while preserving exclusions for `.git*`, `.venv*`, and cache directories.
   - Ensure loose files at `WHO-project/` and `vds-scripts/` roots are explicitly ingested.
3. **Targeted Hydration & Ingestion**: Trigger Cocoa hydration for missing source files and ingest into `migration-manifest.json`.
4. **Re-audit**: Execute two-way reconciliation audit until `unaccounted_missing == 0`.
