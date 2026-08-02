# Security Tooling Specification

**Status:** Draft  
**Date:** 2026-05-24  
**Version:** 1.0

---

## ADDED Requirements

### Requirement: Workspace security tooling is enforced by hooks
The workspace SHALL standardize secret scanning, shell linting, shell formatting, Actions linting, and pre-commit enforcement so security and quality checks run automatically before changes land.

#### Scenario: Pre-commit runs on a Python repo
- **WHEN** a developer commits changes in a Python workspace repository
- **THEN** the configured pre-commit hooks run automatically and block the commit on security or formatting failures

#### Scenario: Secret scanning detects sensitive data
- **WHEN** a repository contains a hardcoded secret
- **THEN** gitleaks reports the finding and the scan fails

#### Scenario: Shell scripts are formatted consistently
- **WHEN** a shell script is checked by the workspace lint flow
- **THEN** shfmt and shellcheck validate the file using the shared formatting and linting rules

## 1. Overview

Security tooling layer provides secret scanning, shell linting, and pre-commit hook enforcement to prevent credential leaks and ensure code quality across all projects.

---

## 2. Requirements

### REQ-1: Secret Scanning

**Tool:** gitleaks  
**Purpose:** Detect hardcoded secrets in git repositories  
**Configuration:** `.gitleaks.toml` at workspace root

**Acceptance Criteria:**
- [ ] gitleaks installed via Homebrew
- [ ] Configuration file created with allowlist for false positives
- [ ] Pre-commit hook configured
- [ ] Scan completes without errors on existing codebase

**Verification:**
```bash
gitleaks detect --no-banner --report-path /tmp/gitleaks-report.json
```

---

### REQ-2: Shell Linting

**Tool:** shellcheck  
**Purpose:** Detect bugs and anti-patterns in bash scripts  
**Configuration:** Default settings (no config file needed)

**Acceptance Criteria:**
- [ ] shellcheck installed via Homebrew
- [ ] Pre-commit hook configured
- [ ] All existing bash scripts pass linting (or are allowlisted)

**Verification:**
```bash
find . -name "*.sh" -type f -exec shellcheck {} \;
```

---

### REQ-3: Shell Formatting

**Tool:** shfmt  
**Purpose:** Consistent bash script formatting  
**Configuration:** 2-space indentation, no tabs

**Acceptance Criteria:**
- [ ] shfmt installed via Homebrew
- [ ] Pre-commit hook configured with `-w -i 2` arguments
- [ ] All existing bash scripts formatted correctly

**Verification:**
```bash
find . -name "*.sh" -type f -exec shfmt -w -i 2 {} \;
```

---

### REQ-4: GitHub Actions Linting

**Tool:** actionlint  
**Purpose:** Validate GitHub Actions workflow files  
**Configuration:** Default settings

**Acceptance Criteria:**
- [ ] actionlint installed via Homebrew
- [ ] Pre-commit hook configured
- [ ] All existing workflow files pass validation

**Verification:**
```bash
find . -path "*/.github/workflows/*.yml" -exec actionlint {} \;
```

---

### REQ-5: Pre-commit Framework

**Tool:** pre-commit  
**Purpose:** Git hook management for consistent code quality  
**Configuration:** `.pre-commit-config.yaml` in each project

**Acceptance Criteria:**
- [ ] pre-commit installed via Homebrew
- [ ] Configuration file created with all security hooks
- [ ] Hooks installed in all Python projects (8 projects)
- [ ] Test run completes successfully

**Verification:**
```bash
pre-commit run --all-files --show-diff-on-failure
```

---

### REQ-6: Container Security Scanning

**Tool:** trivy  
**Purpose:** Scan container images and configs for vulnerabilities  
**Configuration:** `.trivy.yaml` (optional)

**Acceptance Criteria:**
- [ ] trivy installed via Homebrew
- [ ] Can scan Dockerfiles in workspace
- [ ] Pre-commit hook configured (optional)

**Verification:**
```bash
find . -name "Dockerfile" -exec trivy config {} \;
```

---

## 3. Integration

### Hook Execution Order

1. shfmt (fastest)
2. shellcheck (fast)
3. actionlint (medium)
4. gitleaks (medium)
5. trivy (medium, optional)

### Configuration Files

```
tdt/
├── .gitleaks.toml
├── .trivy.yaml (optional)
├── .pre-commit-config.yaml (in each project)
└── openspec/changes/dev-tooling-audit-and-enhancement/specs/security-tooling/spec.md
```

---

## 4. Success Metrics

- Zero secrets committed to repositories
- All bash scripts pass shellcheck
- All GitHub Actions workflows pass actionlint
- Pre-commit hooks run automatically on every commit
- No false positives from gitleaks (allowlist maintained)
