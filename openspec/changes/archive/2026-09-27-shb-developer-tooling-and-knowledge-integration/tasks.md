# Tasks: SHB Developer Tooling and Knowledge Infrastructure Integration

## 1. Toolchain Upgrade and Feature Enablement

- [x] 1.1 Upgrade Notion CLI (`ntn`) to v0.23.10 and verify via `ntn doctor` passing 7/7 checks
- [x] 1.2 Upgrade Graphify to v0.9.69 with full optional extras (`graphifyy[all,postgres]`) and verify via `graphify --version`
- [x] 1.3 Refresh Graphify agent skills across all 10 agent platforms and verify skill installations
- [x] 1.4 Verify GitNexus v1.6.12 runtime and capabilities via `gitnexus doctor`
- [x] 1.5 Configure AgentMemory B+ feature flags in `~/.agentmemory/.env` and verify via `agentmemory doctor` passing 9/9 diagnostics

## 2. In-Repository Configuration and Git Hygiene

- [x] 2.1 Provision standardized `.gitnexusrc` embedding configuration in all 12 SHB repositories and verify file presence
- [x] 2.2 Update `.gitignore` in all 12 SHB repositories to quarantine `.gitnexus/` and ignore snapshot trees `graphify-out/20*/`
- [x] 2.3 Install Graphify Git merge drivers and post-commit hooks via `graphify hook install` in all 12 SHB repositories and verify hook presence

## 3. Knowledge Indexing and Cross-Repository Graph Registration

- [x] 3.1 Generate initial AST knowledge graphs via `graphify update .` in all 12 SHB repositories and verify `graphify-out/graph.json` creation
- [x] 3.2 Register all 12 SHB repositories into the global graph `~/.graphify/global-graph.json` via `graphify global add` and verify via `graphify global list`
- [x] 3.3 Execute semantic code indexing via `gitnexus analyze` across all 12 SHB repositories and verify `gitnexus status` reports up-to-date

## 4. Verification and Specification Alignment

- [x] 4.1 Validate knowledge refresh script inventory compliance via `knowledge-status.sh`
- [x] 4.2 Verify all repository commits and clean working tree state across `~/Developer/shb/*` via `git status`
- [x] 4.3 Validate the OpenSpec change strictly against store rules via `openspec validate --strict --store openspec-store`
