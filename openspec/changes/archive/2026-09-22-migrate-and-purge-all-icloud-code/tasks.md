# Tasks: Migrate and Purge All iCloud Code (Option 3 - Expanded)

## 1. Pre-flight Inventory & Capacity Gates

- [x] 1.1 Run APFS volume capacity check on `/Users/androidteam/Developer` (assert >30 GB free space available)
- [x] 1.2 Generate pre-flight manifests for Categories 1–4 recording candidate file paths, dataless flags, and exclusion classifications
- [x] 1.3 Verify target destinations exist or create required directories under `~/Developer/`

## 2. Category 1 Migration: Active & Uncommitted Code

- [x] 2.1 Trigger Cocoa hydration and migrate `project/microservices` (5,984 files, 1,417 dataless) to `~/Developer/microservices`
- [x] 2.2 Reconcile git status in `~/Developer/microservices` (assert 264 uncommitted files on `feature/temporal-workflow-orchestration` preserved)
- [x] 2.3 Trigger Cocoa hydration and migrate `viettel/Nangluc/excel-updater` (4,969 files) to `~/Developer/viettel-excel-updater`
- [x] 2.4 Initialize git baseline in `~/Developer/viettel-excel-updater` and commit untracked source files
- [x] 2.5 Trigger Cocoa hydration and migrate `timecompany/test/githubusers` (36 files, 36 dataless) to `~/Developer/githubusers`
- [x] 2.6 Migrate database migrations in `main/` to `~/Developer/main-db-migrations`

## 3. Category 2 Migration: Microservice Monorepos & Integration Projects

- [x] 3.1 Migrate `project/camunda7` (pruning `node_modules`) to `~/Developer/camunda7` (1,201 files verified)
- [x] 3.2 Migrate `project/camunda` (pruning `node_modules`) to `~/Developer/camunda-loan-approval` (212 eligible files)
- [x] 3.3 Migrate `project/airbridge` (pruning `node_modules`) to `~/Developer/airbridge` (86 eligible files)
- [x] 3.4 Migrate `project/tmz` (pruning `node_modules`) to `~/Developer/tmz-case-challenge` (50 eligible files)

## 4. Category 3 Migration: Utility Scripts, Devops & Study Code

- [x] 4.1 Migrate `ghtk/project/script/catalog-v2` to `~/Developer/ghtk-catalog-v2` (18 eligible files)
- [x] 4.2 Migrate `ghtk/training/cicd` to `~/Developer/ghtk-training-cicd` (3 eligible files)
- [x] 4.3 Trigger Cocoa hydration and migrate `books/.../Go by Example Source Code` to `~/Developer/study-examples/go-by-example` (463 Go files)
- [x] 4.4 Trigger Cocoa hydration and migrate `books/.../Learning-Spring-Boot-4-main` to `~/Developer/study-examples/spring-boot-4` (199 Java files)
- [x] 4.5 Migrate `invest/` to `~/Developer/invest-bots` (578 eligible files)

## 5. Category 4 Migration: MCP Servers & AI Projects

- [x] 5.1 Migrate `AI/mcp/server/` (pruning `node_modules` and `qdrant_storage/`) to `~/Developer/mcp-servers` (4,963 eligible files)
- [x] 5.2 Migrate `AI/claudia/` (pruning `node_modules`) to `~/Developer/claudia` (369 eligible files)

## 6. Category 5 Migration: Additional Utilities, Configs & Sensitive Credentials

- [x] 6.1 Trigger Cocoa hydration and migrate `ghtk/project/script/` (40 files) to `~/Developer/ghtk-scripts`
- [x] 6.2 Trigger Cocoa hydration and migrate `ghtk/detekt/` (3 files) to `~/Developer/ghtk-detekt`
- [x] 6.3 Migrate `ascend/` code and configs to `~/Developer/ascend-configs` and quarantine `.pem` certificates to `~/Developer/sensitive-quarantine/ascend/`
- [x] 6.4 Quarantine `github/github-recovery-codes.txt` to `~/Developer/sensitive-quarantine/github/`
- [x] 6.5 Migrate `.claude/` to `~/Developer/claude-icloud-backup`
- [x] 6.6 Quarantine `.vds/.env` to `~/Developer/sensitive-quarantine/vds/`

## 7. Quarantine Audit & Two-Way Reconciliation Gate

- [x] 7.1 Audit all quarantined files in `~/Developer/sensitive-quarantine/` (enforce `0700` dirs / `0600` files)
- [x] 7.2 Execute two-way reconciliation audit across all migrated projects (assert 0 unaccounted missing files and 0 size mismatches)
- [x] 7.3 Run `--verify-only` across all project manifests (assert 100% SHA-256 verification with 0 failures)

## 8. Controlled Deletion of Migrated Cloud Sources

- [x] 8.1 Execute fail-closed bounded deletion of `project/microservices` from iCloud
- [x] 8.2 Execute fail-closed bounded deletion of `project/camunda`, `airbridge`, `tmz` from iCloud
- [x] 8.3 Execute fail-closed bounded deletion of `viettel/Nangluc/excel-updater` from iCloud
- [x] 8.4 Execute fail-closed bounded deletion of `timecompany/test/githubusers` from iCloud
- [x] 8.5 Execute fail-closed bounded deletion of `ghtk/project/script/catalog-v2`, `ghtk/training/cicd`, and `invest/` from iCloud
- [x] 8.6 Execute fail-closed bounded deletion of migrated code directories in `books/` (assert non-code book documents remain intact)
- [x] 8.7 Execute fail-closed bounded deletion of `AI/mcp/server` and `AI/claudia` from iCloud
- [x] 8.8 Execute fail-closed bounded deletion of `main/` from iCloud
- [x] 8.9 Bottom-up prune empty parent directories under `project/`, `viettel/`, `timecompany/`, `ghtk/`, `invest/`, and `AI/`
- [x] 8.10 Execute fail-closed bounded deletion of `ghtk/project/script/` and `ghtk/detekt/` from iCloud
- [x] 8.11 Execute fail-closed bounded deletion of `ascend/` code and quarantined keys from iCloud
- [x] 8.12 Execute fail-closed bounded deletion of `github/github-recovery-codes.txt` from iCloud
- [x] 8.13 Execute fail-closed bounded deletion of `.claude/` from iCloud
- [x] 8.14 Execute fail-closed bounded deletion of `.vds/` from iCloud

## 9. Direct Purge of Root Debris

- [x] 9.1 Safely unlink loose Python packaging debris in iCloud root (`_internal/`, `base64/`, `filters/`, `formatters/`, `lexers/`, `strings/`, `styles/`, `time/`, `vecs/`, `v1/`, `INSTALLER`, `METADATA`, `RECORD`, `REQUESTED`, `WHEEL`)
- [x] 9.2 Safely unlink empty root directories (`experimental/`, `internal/`, `backups/`, `random/`)
- [x] 9.3 Verify personal directories (`SHB/`, `TDT/`, `candidate/`, `che/`, `family/`, `fcfc/`, etc.) remain completely untouched

## 10. Final Verification & Archival

- [x] 10.1 Run post-migration verification confirming all local destinations are intact and readable
- [x] 10.2 Record before/after disk usage and manifest statistics in change evidence
- [x] 10.3 Strictly validate and archive `migrate-and-purge-all-icloud-code` in `openspec-store`
