# Tasks

## 1. Specification & Review
- [x] 1.1 Complete proposal.md outlining cross-surface drift and consistency remediation
- [x] 1.2 Author delta specifications for gdrive-ios-and-deployments and workspace-topology-and-hygiene
- [x] 1.3 Draft design.md documenting goals, decisions, and risk mitigations
- [x] 1.4 Validate OpenSpec change strictly via openspec validate

## 2. Agent Documentation Synchronization
- [x] 2.1 Audit AGENTS.md lines 178-189 for legacy path prefixes (protected instruction file remains governed)
- [x] 2.2 Verify CLAUDE.md byte-for-byte synchronization with AGENTS.md
- [x] 2.3 Document canonical organization mapping in OpenSpec proposal and topology guides

## 3. Workspace Hygiene & Scrap Purge
- [x] 3.1 Recursively locate and purge all 62 .DS_Store files across workspace top 3 levels
- [x] 3.2 Verify workspace root and subdirectories are clean of OS metadata scrap

## 4. Skills & Codebase Consistency Verification
- [x] 4.1 Run sync-workspace-agent-skills.py --check to verify all 96 canonical skills and symlinks
- [x] 4.2 Verify zero legacy references remain in knowledge refresh inventory and scripts

## 5. OpenSpec Archival & Knowledge Persistence
- [x] 5.1 Re-run strict validation on reconcile-workspace-consistency-across-surfaces
- [x] 5.2 Archive completed change and sync main specifications
- [x] 5.3 Commit store changes in platform/openspec-store
- [x] 5.4 Persist consistency architecture note into AgentMemory and publish to Notion via ntn CLI
