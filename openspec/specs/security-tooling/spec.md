# Security Tooling Specification

**Status:** Draft
**Date:** 2026-05-24
**Version:** 1.0

---

## Purpose

Security tooling layer provides secret scanning, shell linting, and pre-commit hook enforcement to prevent credential leaks and ensure code quality across all projects.

---

## Requirements

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

### Requirement: Secret scanning with gitleaks

The workspace SHALL use gitleaks for detecting hardcoded secrets in git repositories.

#### Scenario: gitleaks is configured
- **WHEN** a developer clones the workspace
- **THEN** `.gitleaks.toml` exists at workspace root with allowlist for false positives

#### Scenario: Secret scan runs on commit
- **WHEN** a developer commits changes
- **THEN** gitleaks scans for secrets and blocks commit if found

### Requirement: Shell linting with shellcheck

The workspace SHALL use shellcheck for detecting bugs and anti-patterns in bash scripts.

#### Scenario: shellcheck is available
- **WHEN** a developer runs shellcheck on a bash script
- **THEN** it detects bugs and anti-patterns

#### Scenario: Shell linting runs on commit
- **WHEN** a developer commits shell script changes
- **THEN** shellcheck validates the scripts

### Requirement: Shell formatting with shfmt

The workspace SHALL use shfmt for consistent bash script formatting.

#### Scenario: shfmt is configured
- **WHEN** a developer runs shfmt on a bash script
- **THEN** it formats the script with 2-space indentation

#### Scenario: Shell formatting runs on commit
- **WHEN** a developer commits shell script changes
- **THEN** shfmt formats the scripts automatically

### Requirement: GitHub Actions linting with actionlint

The workspace SHALL use actionlint for validating GitHub Actions workflow files.

#### Scenario: actionlint is available
- **WHEN** a developer runs actionlint on workflow files
- **THEN** it validates the workflow syntax

#### Scenario: Actions linting runs on commit
- **WHEN** a developer commits workflow file changes
- **THEN** actionlint validates the workflows

### Requirement: Pre-commit framework enforcement

The workspace SHALL use pre-commit for git hook management across all projects.

#### Scenario: Pre-commit is configured
- **WHEN** a developer clones a Python project
- **THEN** `.pre-commit-config.yaml` exists with all security hooks

#### Scenario: Hooks run automatically
- **WHEN** a developer commits changes
- **THEN** pre-commit hooks run and block commit on failures

### Requirement: Container security scanning with trivy

The workspace SHALL use trivy for scanning container images and configs for vulnerabilities.

#### Scenario: trivy is available
- **WHEN** a developer runs trivy on a Dockerfile
- **THEN** it scans for vulnerabilities

---

## Integration

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
```

---

## Success Metrics

- Zero secrets committed to repositories
- All bash scripts pass shellcheck
- All GitHub Actions workflows pass actionlint
- Pre-commit hooks run automatically on every commit
- No false positives from gitleaks (allowlist maintained)
