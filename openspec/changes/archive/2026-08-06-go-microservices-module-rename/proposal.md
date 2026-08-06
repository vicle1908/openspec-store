# Proposal: go-microservices Module Rename & Assessment Infrastructure

## Why

The Go microservices monorepo at `~/Developer/go-microservices` had inconsistent naming:
- Directory name: `go-microservices`
- Git remote URL: `victory1908/microservices.git` (missing `go-` prefix)
- GitNexus indexed as: `microservices` (derived from remote URL)
- Go module paths: `github.com/victory1908/microservices` (inconsistent with directory)

This caused:
- Pre-commit hook failures ("Repository not found") when GitNexus CLI used basename
- Confusion between directory name and module path
- Inconsistent naming across K8s namespaces, ArgoCD projects, and deployment configs

Additionally, the repo lacked structured assessment documentation and continuous
health monitoring infrastructure.

## What Changes

### Module Rename (154 files)
- Git remote: `microservices.git` → `go-microservices.git`
- Go module paths: `victory1908/microservices` → `victory1908/go-microservices` (18 go.mod + 26 Go files)
- Scripts: Docker volumes, LaunchAgent labels, kind clusters, schema namespaces (17 files)
- Deploy: K8s namespaces, ArgoCD project/apps, CDC schemas, kind labels (30+ files)
- OpenSpec: Active specs updated, archived specs preserved as historical record
- Docs: AGENTS.md, README, ADRs, runbooks, assessment

### Assessment Infrastructure
- `docs/assessment/README.md` — schedule, methodology, knowledge-tool validation
- `docs/assessment/baseline-2026-08-05.md` — comprehensive baseline (validated by graphify, GitNexus, LLM Wiki)
- `Makefile`: `health-check` target (go vet + short tests), `assessment` target (metrics collection)

### GitNexus Fix
- Pre-commit hook: use `--repo "$root"` (path) instead of basename
- knowledge-tools.sh: remove hardcoded `microservices` override, use path
- AGENTS.md: document correct GitNexus name and path-based CLI usage
- Re-indexed GitNexus as `go-microservices` (18,519 nodes, 51,808 edges)

### LLM Wiki Update
- Updated `entities/go-microservices.md` with current stats and new GitHub URL
- Updated `concepts/go-microservices-platform.md` with correct service names
- Updated `concepts/go-platform-architecture.md` with coupling analysis

## Verification

- All Go builds pass (platform, order-service, ecosystem-verification)
- GitNexus lists `go-microservices` correctly
- Pre-commit hook works without "Repository not found" errors
- Zero remaining `victory1908/microservices` in active Go/shell/mod files
- Monthly assessment cron configured (1st of month, 9AM Vietnam time)
