# Tasks

## 1. Specification & Review
- [x] 1.1 Complete proposal.md outlining data root hygiene and duplicate skills removal
- [x] 1.2 Author delta specification for workspace-artifact-retention-policy
- [x] 1.3 Draft design.md documenting goals, non-goals, and zero-loss decisions
- [x] 1.4 Validate OpenSpec change strictly via openspec validate
- [x] 1.5 Conduct Orca multi-agent review via configured worker agent

## 2. Targeted Application
- [x] 2.1 Purge duplicate data/skills/ tree (61 skills confirmed redundant with .agents/skills/)
- [x] 2.2 Purge obsolete reproduction directories (data/harness-prod-repro-qb71_yqg, data/harness-prod-repro-to792iqu)
- [x] 2.3 Archive/purge stale review patch and task markdown in data/
- [x] 2.4 Verify database state stores (state_store.db, stream_store, quarantine) remain completely intact

## 3. Verification & Validation
- [x] 3.1 Verify skills synchronization via sync-workspace-agent-skills.py --check
- [x] 3.2 Validate change strictly via openspec validate --strict --store openspec-store
- [x] 3.3 Verify store health via openspec store doctor

## 4. Archival & Knowledge Persistence
- [x] 4.1 Archive change via openspec archive --store openspec-store --yes
- [x] 4.2 Sync main specification workspace-artifact-retention-policy
- [x] 4.3 Commit store changes in platform/openspec-store on main
- [x] 4.4 Persist architecture insights into AgentMemory
- [x] 4.5 Publish consolidation report to Notion via ntn CLI
