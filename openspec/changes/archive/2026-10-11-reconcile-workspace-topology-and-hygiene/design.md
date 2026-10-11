# Design

## Context

The developer workspace at `~/Developer/` organizes codebases by first-class organization namespaces (`platform/`, `tdt/`, `shb/`, `vds/`, `ascend/`, `ghtk/`, `fpt/`), operational meta-roots (`docs/`, `scripts/`, `wiki/`, `data/`, `sensitive-quarantine/`), and auxiliary domain subtrees (`apps/`, `legacy/`, `study/`, `ai-tooling/`, `migration-archives/`, `infra/`).

Recent development and testing operations left ~88MB of test/lint caches (`.mypy_cache`, `.pytest_cache`, `.ruff_cache`), probe logs, and session dumps at workspace root. In addition, an npx skill install or sync operation deposited 44 duplicate skills into `skills/` and `agent/skills/` alongside an unconfined `skills-lock.json` at root. Finally, three unclassified project directories (`cursor-account-manager-build/`, `main-db-migrations/`, `ntu-keynote/`) reside at the root level rather than within their proper domain subtrees.

## Goals / Non-Goals

**Goals:**
- Eliminate root cache directories and scratch artifacts without affecting individual repository virtualenvs.
- De-duplicate and confine skills by removing root `skills/`, `agent/`, and root `skills-lock.json`, enforcing `.agents/skills/` as the single canonical skills tree.
- Classify and relocate unmanaged root checkouts (`cursor-account-manager-build/`, `main-db-migrations/`, `ntu-keynote/`) into their proper domain subtrees (`apps/`, `legacy/`, `study/`).
- Update `docs/WORKSPACE_TOPOLOGY.md` and `AGENTS.md` to ensure documentation matches physical reality.
- Maintain zero regressions across LaunchAgents, knowledge refresh inventories, and rclone bisync.

**Non-Goals:**
- Modifying or reorganizing any checked-out code inside active organization repositories (`platform/`, `tdt/`, `shb/`, etc.).
- Creating backward-compatibility symlinks at root (clean-break policy prohibits root symlinks).
- Mutating files or executing moves prior to user review and approval.

## Decisions

- **Decision 1: Direct removal of duplicate skills trees**: Set comparison confirms that 100% of skills in root `skills/` (44) and `agent/skills/` (44) exist in canonical `.agents/skills/` (98 skills). Removal introduces zero content loss.
- **Decision 2: Relocate main-db-migrations to legacy Kafka microservices**: `main-db-migrations` contains Spring Flyway migrations for `inventory-service` (port 8083), which was part of the 2025 Java Kafka microservices architecture. It will be relocated to `legacy/kafka-microservices/db-migrations/`.
- **Decision 3: Relocate cursor-account-manager-build to apps**: Contains `CursorAccountManager-macOS.app`. It will be moved to `apps/cursor-account-manager-build/`.
- **Decision 4: Relocate ntu-keynote to study**: `ntu-keynote` is a standalone presentation deck with its own git history and no active CI. It fits naturally under `study/ntu-keynote/`.

## Risks / Trade-offs

- **Risk**: Active scripts or LaunchAgents referencing old root paths.
  - **Mitigation**: Pre-flight audit confirms zero references to `cursor-account-manager-build`, `main-db-migrations`, or `ntu-keynote` in `docs/`, `scripts/`, or `~/Library/LaunchAgents/`.
- **Risk**: Skill synchronization regression.
  - **Mitigation**: Post-cleanup verification runs `sync-workspace-agent-skills.py --check` to assert that all 96 canonical direct roots and symlinks remain intact.
