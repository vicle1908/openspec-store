# Tasks

## 1. Specification & Review
- [x] 1.1 Complete proposal.md outlining workspace alignment and artifact hygiene
- [x] 1.2 Author delta specifications for skill-index-hygiene and workspace-artifact-retention-policy
- [x] 1.3 Draft design.md documenting goals, non-goals, and zero-loss decisions
- [x] 1.4 Validate OpenSpec change strictly via openspec validate
- [x] 1.5 Conduct Orca multi-agent review via configured worker agent

## 2. Targeted Application
- [x] 2.1 Purge loose backup files (*.bak, *.orig, *~) across repositories
- [x] 2.2 Purge .agents/skills/graphify/SKILL.md.bak to enforce pristine skill discovery
- [x] 2.3 Purge unconfined htmlcov and root test caches in openspec-store, ai-training-materials, and tdt-sheets

## 3. Verification & Validation
- [x] 3.1 Verify skills synchronization via sync-workspace-agent-skills.py --check
- [x] 3.2 Validate change strictly via openspec validate --strict --store openspec-store
- [x] 3.3 Verify store health via openspec store doctor

## 4. Archival & Knowledge Persistence
- [x] 4.1 Archive change via openspec archive --store openspec-store --yes
- [x] 4.2 Sync main specifications skill-index-hygiene and workspace-artifact-retention-policy
- [x] 4.3 Commit store changes in platform/openspec-store on main
- [x] 4.4 Persist architecture insights into AgentMemory
- [x] 4.5 Publish consolidation report to Notion via ntn CLI
