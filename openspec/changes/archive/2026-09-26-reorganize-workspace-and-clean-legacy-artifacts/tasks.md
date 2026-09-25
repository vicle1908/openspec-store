# Tasks: Reorganize Workspace Domains and Clean Legacy Artifacts

## 1. Pre-flight Baseline and Safety Verification

- [x] 1.1 Snapshot current `~/Developer/` directory tree and disk usage to evidence file, verifying no uncommitted changes in active core repos (`git status` across active repos).
- [x] 1.2 Verify zero active dependencies on candidate paths in `~/.zshrc`, LaunchAgents, and `scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` via grep check.

## 2. Purge Ephemeral Caches and Dead Scraps

- [x] 2.1 Remove root-level Python/linter caches (`.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.infinity_cache/`) and verify removal with `ls -d`.
- [x] 2.2 Remove empty and obsolete test scratch directories (`.knowledge-refresh-test-s1lr2rxj/`, `.phase6-field-audit/`, `.workspace-lifecycle-dryrun-2026-09/`, `vds/`, `.tmp/`, `tmp/`, `tdt-v2-accept/`, `recovery-pilot/`) and verify removal with `test ! -d`.
- [x] 2.3 Remove unreferenced backups and dead logs (`mcp-router-backup-20260722/`, `claude-icloud-backup/`, `.claude.json.backup`, `.claude-server-commander*`, `.codex_cursor`) and verify removal with `test ! -e`.
- [x] 2.4 Prune dead internal virtualenv in `mcp-servers/Code-Index-MCP/venv/` and obsolete worktrees in `vds-content-migration/WHO-project/worktrees/`, verifying disk space reclaimed (~2.2 GB).

## 3. Establish Domain Subtree Hierarchy

- [x] 3.1 Create target domain directories (`legacy/ghtk/`, `apps/camunda/`, `study/`, `ai-tooling/rules/`, `migration-archives/`, `docs/contracts/`) and verify directory structure with `test -d`.

## 4. Atomic Project and Asset Relocations

- [x] 4.1 Relocate GHTK legacy projects (`ghtk-android-drawables/`, `ghtk-catalog-v2/`, `ghtk-detekt/`, `ghtk-project-assets/`, `ghtk-scripts/`, `ghtk-training-cicd/`) to `legacy/ghtk/` and verify presence with `ls legacy/ghtk`.
- [x] 4.2 Move and rename `microservices/` to `legacy/kafka-microservices/` and move `ascend-configs/` to `legacy/ascend-configs/`, verifying Git commit history is preserved with `git log -1`.
- [x] 4.3 Relocate Camunda and lending mini-app assets (`camunda7/`, `camunda-loan-approval/`, `lending-miniapp-docs/`) to `apps/camunda/` and verify presence with `ls apps/camunda`.
- [x] 4.4 Relocate standalone application tools (`airbridge/`, `invest-bots/`, `githubusers/`, `viettel-excel-updater/`, `tmz-case-challenge/`) to `apps/` and verify presence with `ls apps`.
- [x] 4.5 Relocate reference and study materials (`study-examples/`, `ai-training-materials/`) to `study/` and verify presence with `ls study`.
- [x] 4.6 Relocate agent tools and rules (`mcp-servers/`, `mcp-suite/`, `wiki-mcp-server/`, `claudia/`, `workspace-python-template/`, `ai-rules/`, `cursor-rules/`) to `ai-tooling/` and verify presence with `ls ai-tooling`.
- [x] 4.7 Relocate historical migration tools and receipts (`vds-content-migration/`, `content-migration-manifests/`, `icloud-migration-tools/`) to `migration-archives/` and verify presence with `ls migration-archives`.

## 5. Relocate Loose Root Configuration and Doc Files

- [x] 5.1 Move `qi_config.yaml` to `qi-bridge/qi_config.yaml`, update hardcoded paths to local paths, and verify syntax with `python3 -c "import yaml; yaml.safe_load(open('qi-bridge/qi_config.yaml'))"`.
- [x] 5.2 Move `skills-lock.json` to `.agents/skills-lock.json` and verify JSON syntax with `python3 -m json.tool`.
- [x] 5.3 Move `.worktree-execution-contracts-*.md` to `docs/contracts/` and verify presence with `ls docs/contracts`.

## 6. Workspace Documentation and Verification

- [x] 6.1 Update `~/Developer/AGENTS.md` and `CLAUDE.md` to document the new domain directory hierarchy and verify links with markdown check.
- [x] 6.2 Verify the 20 approved repositories in `scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` remain undisturbed and valid.
- [x] 6.3 Run `openspec validate reorganize-workspace-and-clean-legacy-artifacts --strict --store openspec-store` and verify 100% strict compliance.
