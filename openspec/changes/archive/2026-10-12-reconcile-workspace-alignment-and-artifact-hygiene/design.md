# Design

## Context

Following workspace topology consolidation, an exhaustive cross-repository scan discovered residual development artifacts:
- 29 loose backup/temporary files (`*.bak`, `*.orig`, `*~`) spread across repository trees (including `.agents/skills/graphify/SKILL.md.bak`, `platform/go-microservices/AGENTS.md.bak`, `tdt/realtime/.../*.bak`).
- Non-canonical backup files inside `.agents/skills/` violating single-source-of-truth skill discovery rules.
- 69 unconfined cache and coverage directories (`.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `htmlcov`) lingering at repository roots outside isolated virtual environments.

## Goals / Non-Goals

**Goals:**
- Purge all `*.bak`, `*.orig`, and `*~` backup files across repositories and skill roots.
- Purge `.agents/skills/graphify/SKILL.md.bak` to ensure all 96 skills adhere strictly to standard directory layouts.
- Remove loose `htmlcov/` coverage artifacts and root test caches in `openspec-store`, `ai-training-materials`, and `tdt-sheets`.
- Strictly validate and archive OpenSpec change `reconcile-workspace-alignment-and-artifact-hygiene`.
- Commit store changes on `main` in `openspec-store`.
- Persist memory to AgentMemory and Notion via `ntn` CLI.

**Non-Goals:**
- Deleting virtual environment caches inside `.venv/` or dependency caches in `node_modules/`.
- Modifying production Go or Python source code.

## Decisions

- **Decision 1: Immediate removal of backup scrap**: `*.bak` and `*.orig` files are unreferenced remnants of manual edits and automated script migrations. Deleting them is safe and eliminates repository noise.
- **Decision 2: Remove loose htmlcov and root test caches**: Caches outside `.venv` represent unmanaged ephemeral test runs. Purging them restores pristine working trees.

## Risks / Trade-offs

- **Risk**: Deleting an actively referenced backup file.
  - **Mitigation**: Pre-flight audit confirmed zero imports or references to `*.bak` files in codebase contracts.
