# Design: Comprehensive Local GitHub Actions Validation CLI, Pre-Push Enforcement, and Agent Skill

## Overview
This design establishes an automated, local validation suite for GitHub Actions workflows in `go-microservices` and packages the operational protocol into a reusable workspace Agent Skill (`github-actions-validation`).

By unifying syntax checking, AST expression analysis, action commit SHA pinning, retention baseline verification, PR concurrency rules, trigger lifecycle rules, and security scans into a single command (`make validate-workflows` / `scripts/validate-workflows.py`), any workflow defect is caught in < 2 seconds on the developer workstation prior to `git push`.

---

## Architecture of `scripts/validate-workflows.py`

### 1. File Discovery
Discovers all tracked workflow files:
- Repository root workflows: `.github/workflows/*.yml`, `.github/workflows/*.yaml`
- Sub-service workflows: `services/*/.github/workflows/*.yml`

### 2. Validation Checks Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                scripts/validate-workflows.py                │
├─────────────────────────────────────────────────────────────┤
│ Check 1: YAML Structural & Duplicate Key Parsing            │
│          - Loads each file via yaml.SafeLoader              │
│          - Validates map structure and non-empty jobs       │
├─────────────────────────────────────────────────────────────┤
│ Check 2: actionlint AST & Shellcheck Linting                │
│          - Invokes `actionlint` (with embedded shellcheck)  │
│          - Checks expression contexts, inputs, and shell    │
├─────────────────────────────────────────────────────────────┤
│ Check 3: Action SHA Pinning via tools/actionpin             │
│          - Invokes `tools/actionpin/actionpin.py`           │
│          - Validates 40-char commit SHAs in lockfile        │
├─────────────────────────────────────────────────────────────┤
│ Check 4: Artifact Retention Baseline Compliance             │
│          - Invokes `scripts/verify-retention.py`            │
│          - Compares retention values against origin/main    │
├─────────────────────────────────────────────────────────────┤
│ Check 5: PR-Scoped Concurrency Invariants                   │
│          - Validates group: ${{ github.workflow }}-...      │
│          - Enforces cancel-in-progress: pull_request        │
├─────────────────────────────────────────────────────────────┤
│ Check 6: Explicit PR Trigger Lifecycle                     │
│          - Enforces branches: [main]                        │
│          - Enforces types: [opened, synchronize, reopened]  │
├─────────────────────────────────────────────────────────────┤
│ Check 7: Branch Protection Check Context Invariants         │
│          - In verify.yml: job 'verify-pr' must have name    │
│            'PR gate (verify-pr)'                            │
├─────────────────────────────────────────────────────────────┤
│ Check 8: Security Audit via zizmor (offline mode)           │
│          - If zizmor is installed or accessible via uvx,    │
│            runs security audit across workflow files        │
└─────────────────────────────────────────────────────────────┘
```

### 3. Integration with Root `Makefile` & `make pre-push`
Add dedicated target:
```makefile
.PHONY: validate-workflows
validate-workflows:
	@python3 scripts/validate-workflows.py
```
And wire into `pre-push`:
```makefile
.PHONY: pre-push
pre-push:
	git diff --check
	$(MAKE) validate-agent-guidance
	$(MAKE) validate-workflows
	python3 scripts/sync-coverage-docs.py --check
	$(MAKE) validate-documentation
```

---

## Agent Skill Specification (`github-actions-validation`)

Location: `.agents/skills/github-actions-validation/SKILL.md`

### Contents
- Frontmatter with name, description, tags.
- 5-stage pre-flight validation workflow.
- Common failure modes and authoritative solutions:
  - Docker Hub manifest 429 errors -> backoff retries.
  - Setup-go tar cache collisions -> setup-go v5 native cache.
  - Newman CI host execution -> loopback `127.0.0.1:<PORT>` vs container network.
  - `pgxpool` unit test eager connection -> `MinConns = 0`.
  - Retention array matching -> matching occurrence order.
  - Branch protection context invariants -> `PR gate (verify-pr)`.
