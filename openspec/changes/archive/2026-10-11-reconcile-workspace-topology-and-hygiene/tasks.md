# Tasks

## 1. Specification & Review
- [x] 1.1 Complete proposal.md outlining workspace hygiene drift and consolidation plan
- [x] 1.2 Author delta specification for workspace-topology-and-hygiene
- [x] 1.3 Draft design.md documenting goals, non-goals, and architectural decisions
- [x] 1.4 Validate OpenSpec change strictly via openspec validate

## 2. Root Hygiene Purge
- [x] 2.1 Purge root test and lint caches (.mypy_cache/, .pytest_cache/, .ruff_cache/)
- [x] 2.2 Purge root test logs and session html exports
- [x] 2.3 Purge internal repo scrap caches (ntu-keynote/.pytest_cache, wiki/.pytest_cache)

## 3. Skills Confinement
- [x] 3.1 Merge root skills-lock.json registry into .agents/skills-lock.json
- [x] 3.2 Remove duplicate skills/ and agent/ directories at workspace root
- [x] 3.3 Remove unconfined root skills-lock.json
- [x] 3.4 Verify canonical skill synchronization via sync-workspace-agent-skills.py --check

## 4. Auxiliary Domain Reclassification
- [x] 4.1 Relocate main-db-migrations/ to legacy/kafka-microservices/db-migrations/
- [x] 4.2 Relocate cursor-account-manager-build/ to apps/cursor-account-manager-build/
- [x] 4.3 Relocate ntu-keynote/ to study/ntu-keynote/

## 5. Documentation & Verification
- [x] 5.1 Update docs/WORKSPACE_TOPOLOGY.md and AGENTS.md
- [x] 5.2 Verify LaunchAgents, rclone filters, and knowledge refresh inventory
- [x] 5.3 Run strict OpenSpec validation across change and store
