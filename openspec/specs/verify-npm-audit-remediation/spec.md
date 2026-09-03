# verify-npm-audit-remediation Specification

## Purpose
TBD - created by archiving change verify-npm-audit-remediation. Update Purpose after archive.

## Requirements

### Requirement: Audit Remediation Verification Gates
The verification pass SHALL re-execute, in fresh processes against the current working tree, every audit/build/test claim made by the 2026-09-03 remediation session across mcp-router, goose-docs (oidc-proxy, documentation, services/ask-ai-bot, ui), prime-agent, and realtime/frontend, and SHALL record verifiable evidence satisfying each gate's declared release condition (fresh command execution with exit code and observed output, or explicit reclassification as unpatched-upstream residual with no-fix marker cited).

#### Scenario: audit counts match remediation outcomes
- **WHEN** the package-manager audit command for a repository is re-executed
- **THEN** the reported vulnerability count equals the remediation session's recorded outcome for that repository, or any delta is explained in evidence as a newly published advisory rather than a remediation regression

#### Scenario: unpatched residuals are identified, not just counted
- **WHEN** an audit reports remaining vulnerabilities in mcp-router, goose-docs/ui, or goose-docs/documentation
- **THEN** evidence identifies each remaining advisory by package, version, and no-fix marker (patched_versions `<0.0.0` or equivalent), confirming no patched version exists at verification time

#### Scenario: builds and focused tests pass on changed surfaces
- **WHEN** the verification commands for each repository are executed (CLI build, Electron typecheck, oidc-proxy test suite, docs build, bot build, focused tools-manager test, frontend build, jspdf smoke)
- **THEN** each command exits successfully, or a failure is either fixed within remediation scope or shown to be pre-existing and unrelated to the dependency changes, with the distinction recorded in evidence

#### Scenario: pnpm-managed repo stays pnpm-only
- **WHEN** mcp-router is verified
- **THEN** no package-lock.json exists anywhere in the repository, all mutations were made via pnpm, and the webpack-dev-server override resolves to the patched 5.2.6 line (engines node >=18.12.0) rather than 6.0.0

#### Scenario: bugs found during verification are fixed
- **WHEN** a verification command fails where the remediation session recorded a pass, or a defect is found in migration-touched code
- **THEN** the bug is fixed within the remediation's scope, the failing command is re-run and passes, and the fix is recorded in evidence with file paths

#### Scenario: evidence is literal-safe
- **WHEN** evidence records package names, versions, or model identifiers
- **THEN** literals are programmatically derived from lockfiles, manifests, or command output read back from disk, not hand-typed from memory
