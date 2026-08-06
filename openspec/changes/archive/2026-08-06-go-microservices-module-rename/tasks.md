# Tasks: go-microservices Module Rename & Assessment Infrastructure

## Task 1: Git Remote Rename ✅
- [x] Update git remote URL from `victory1908/microservices.git` to `victory1908/go-microservices.git`
- [x] Verify remote is accessible

## Task 2: Go Module Paths ✅
- [x] Update 5 test/script go.mod files (tests/platform, tests/cross-service-smoke, tests/ecosystem-verification, scripts/composeevidence, scripts/validation)
- [x] Update 8 service go.mod files (order, payment, inventory, notification, customer, catalog, reporting, shipping)
- [x] Update platform/go.mod
- [x] Update all Go source imports (26 files)
- [x] Update all go.sum files
- [x] Update remaining go.mod refs (ecosystem-verification require/replace in service modules)

## Task 3: Scripts Update ✅
- [x] Update knowledge-pre-commit.sh (path-based GitNexus CLI)
- [x] Update knowledge-tools.sh (remove hardcoded name, use path)
- [x] Update 17 shell scripts (Docker volumes, LaunchAgent labels, kind clusters, schemas)
- [x] Verify bash syntax: `bash -n scripts/knowledge-pre-commit.sh`

## Task 4: Deploy Configs ✅
- [x] Update K8s namespaces (microservices-staging → go-microservices-staging, microservices → go-microservices)
- [x] Update ArgoCD project/applications (project name, namespaces, labels)
- [x] Update CDC schemas (microservices.local-cdc → go-microservices.local-cdc)
- [x] Update kind cluster labels and names

## Task 5: OpenSpec Specs ✅
- [x] Update active specs (schema refs, namespace refs, descriptions)
- [x] Preserve archived specs as historical record

## Task 6: Documentation ✅
- [x] Update AGENTS.md (GitNexus name, path-based CLI usage)
- [x] Update README.md (GitHub URL)
- [x] Update ADRs, runbooks, assessment docs

## Task 7: Assessment Infrastructure ✅
- [x] Create docs/assessment/README.md (schedule, methodology)
- [x] Create docs/assessment/baseline-2026-08-05.md (comprehensive baseline)
- [x] Add make health-check target (go vet + short tests)
- [x] Add make assessment target (metrics collection)
- [x] Configure monthly cron job (1st of month, 9AM Vietnam time)

## Task 8: Knowledge Tools Validation ✅
- [x] Run graphify queries (god-nodes, architecture, service isolation)
- [x] Run GitNexus analysis (context, impact, detect_changes)
- [x] Update LLM Wiki pages (entity, concepts)
- [x] Validate assessment against all three knowledge modalities

## Task 9: GitNexus Re-index ✅
- [x] Remove old `microservices` index
- [x] Re-index as `go-microservices` (18,519 nodes, 51,808 edges)
- [x] Verify GitNexus lists correct name

## Task 10: Verification ✅
- [x] Go builds pass (platform, order-service, ecosystem-verification)
- [x] Pre-commit hook works (no "Repository not found" errors)
- [x] Zero remaining `victory1908/microservices` in active files
- [x] All changes committed across 3 commits
