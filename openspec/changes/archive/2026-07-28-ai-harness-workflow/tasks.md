## 1. Decisions and Dependency Approval

- [x] 1.1 Confirm the final standalone repository and Python package names; record any rename from `ai-harness-skills/` in the README and package metadata
- [x] 1.2 Obtain team approval for all runtime, build, typing, linting, and test dependencies before adding them with `uv`
- [x] 1.3 Record the initial local gate actor policy and permitted approver configuration
- [x] 1.4 Record retention defaults for provider events, immutable artifact revisions, and completed runs
- [x] 1.5 Define the required provider capability baseline without using version strings as the sole compatibility check

## 2. Repository Bootstrap

- [x] 2.1 Create the standalone `ai-harness-skills/` repository and Python 3.14 package structure
- [x] 2.2 Create `.python-version`, `pyproject.toml`, and hatchling package configuration with the approved package name
- [x] 2.3 Add approved runtime and development dependencies with `uv add` and include the generated `uv.lock`
- [x] 2.4 Configure ruff linting and formatting for `src/` and `tests/`
- [x] 2.5 Configure strict mypy for `src/` and `tests/`
- [x] 2.6 Configure pytest, pytest-asyncio when required, coverage, and deterministic test markers
- [x] 2.7 Create the `harness` CLI entry point and verify `uv run harness --help`
- [x] 2.8 Create an initial README that states the standalone boundary, planning-only authority, and installation channels
- [x] 2.9 Verify `uv sync --frozen` succeeds from a clean checkout

## 3. Domain Models and Configuration

- [x] 3.1 Implement the exact 13-stage enum and authoritative stage sequence under `src/ai_harness/`
- [x] 3.2 Implement separate run status, stage status, wait reason, gate, clarification, revision, and verification-outcome types
- [x] 3.3 Implement `guided` and `headless` execution-mode types
- [x] 3.4 Implement `observed`, `proposed`, `assumption`, and `decision` claim types
- [x] 3.5 Implement provider capability, support-tier, stage-request, stage-result, usage, and diagnostic types
- [x] 3.6 Implement `TDT_HOME` resolution with `~` expansion and the `~/.tdt` fallback
- [x] 3.7 Implement typed configuration for providers, workspace roots, gates, retention, concurrency, timeouts, revisions, output limits, and budgets
- [x] 3.8 Reject missing, invalid, unbounded, secret-bearing, or path-escaping configuration before workflow startup
- [x] 3.9 Add unit tests for every enum, model, serialization format, configuration rule, and path-resolution case

## 4. Transactional SQLite Run Ledger

- [x] 4.1 Define the versioned SQLite schema for runs, stages, artifact revisions, gates, clarifications, provider sessions, events, and leases
- [x] 4.2 Implement first-use database initialization under `$TDT_HOME/ai-harness/state.sqlite`
- [x] 4.3 Implement schema-version inspection and fail-closed behavior for unsupported database versions
- [x] 4.4 Implement transactional run creation and stage-state transitions
- [x] 4.5 Implement append-only transition, validation, gate, clarification, recovery, and failure events
- [x] 4.6 Implement provider-session records with stage, attempt, provider, resume eligibility, and bounded metadata
- [x] 4.7 Implement digest-bound pending and historical gate records
- [x] 4.8 Implement clarification question and answer records with stable identifiers
- [x] 4.9 Implement per-run lease acquisition, renewal, release, and concurrent-advance rejection
- [x] 4.10 Implement stale-lease recovery with owner, expiry, and recovery-event validation
- [x] 4.11 Prevent credentials, full prompts, and unrestricted artifact bodies from entering routine ledger fields
- [x] 4.12 Add tests for transaction rollback, process restart, concurrent access, stale lease recovery, unsupported schema version, and database corruption

## 5. Workflow Engine

- [x] 5.1 Implement the sequential `intake -> context -> clarify -> spec -> impact -> design -> api_contract -> impl_plan -> coding_plan -> plan_review -> test_cases -> auto_test_plan -> verify` topology
- [x] 5.2 Implement dependency validation using named stage identifiers rather than ordinal numbers
- [x] 5.3 Implement CLI-owned transition checks so provider output cannot advance arbitrary state
- [x] 5.4 Implement guided-stage begin and complete operations using the common stage-request and stage-result contracts
- [x] 5.5 Implement headless-stage execution through the provider adapter interface
- [x] 5.6 Implement `resolved`, `needs_input`, and `blocked` clarification outcomes
- [x] 5.7 Implement answer submission bound to pending clarification question IDs
- [x] 5.8 Implement gates after `spec`, `design`, `impl_plan`, and `plan_review`
- [x] 5.9 Implement approval without rerunning the approved artifact-producing stage
- [x] 5.10 Implement rejection with reason and an allowed earlier backtrack target, plus digest-bound authorization for explicit trusted-actor backtrack
- [x] 5.11 Implement explicit `not_applicable` artifacts with rationale and evidence
- [x] 5.12 Implement resumable waiting run states separately from blocked/failed/completed run states and complete/partial/failed verification outcomes
- [x] 5.13 Add transition-table tests for every stage, dependency, gate, clarification, failure, and terminal outcome

## 6. Artifact Revisions, Evidence, and Traceability

- [x] 6.1 Define the common structured provider-result schema and all per-stage schema extensions
- [x] 6.2 Implement deterministic Markdown rendering from accepted structured stage results
- [x] 6.3 Persist immutable JSON and Markdown revisions under `$TDT_HOME/ai-harness/runs/<run-id>/artifacts/`
- [x] 6.4 Record provider identity, session, inputs, evidence, validations, JSON digest, and Markdown digest for each revision
- [x] 6.5 Atomically materialize the latest accepted revision at the current OpenSpec artifact path
- [x] 6.6 Detect current artifact modifications that lack a matching accepted ledger revision
- [x] 6.7 Implement revision supersession without deleting immutable history
- [x] 6.8 Remove invalidated current materializations only after verifying their immutable copies and digests
- [x] 6.9 Rerun a backtrack target as a new revision using a fresh provider session by default
- [x] 6.10 Implement stable evidence IDs with source type, repository, path or symbol, freshness, query, digest, and collection time
- [x] 6.11 Validate observed claims against accepted evidence IDs and digests
- [x] 6.12 Validate proposed claims against requirement or decision references without requiring current-source existence
- [x] 6.13 Surface unresolved assumptions for clarification or gate review
- [x] 6.14 Implement stable requirement, design, API, task, test-case, automated-test-plan, and verification IDs
- [x] 6.15 Implement upstream reference validation and terminal downstream traceability-matrix generation
- [x] 6.16 Compute requirement, acceptance-criterion, test-case, and automated-test-plan coverage percentages
- [x] 6.17 Add tests for fabricated evidence, stale evidence, proposed APIs, assumptions, broken references, direct artifact edits, supersession, and coverage calculation

## 7. OpenSpec Schema and Managed Initializer

- [x] 7.1 Create `openspec/schemas/harness-13/schema.yaml` with exactly 13 named artifacts and the approved sequential dependency graph
- [x] 7.2 Create the `intake`, `context`, `clarify`, `spec`, `impact`, `design`, `api_contract`, `impl_plan`, `coding_plan`, `plan_review`, `test_cases`, `auto_test_plan`, and `verify` templates
- [x] 7.3 Create inline schema stage instructions that describe required inputs, outputs, claim types, evidence, and stable IDs
- [x] 7.4 Configure OpenSpec apply readiness to require all 13 artifacts and explicitly hand off a planning-only package without implying implementation execution
- [x] 7.5 Validate the schema with `openspec schema validate harness-13`
- [x] 7.6 Implement project and symlink-aware OpenSpec root resolution
- [x] 7.7 Implement `harness init --dry-run` reporting destination, versions, ownership, and planned actions
- [x] 7.8 Add ownership and version markers to every initializer-managed schema and native-agent file
- [x] 7.9 Implement unmanaged-file conflict detection with no implicit overwrite
- [x] 7.10 Implement idempotent managed-file installation and compatible upgrade
- [x] 7.11 Implement rollback that removes only files with matching harness ownership metadata
- [x] 7.12 Verify initializer operations never add harness runtime fields to `.openspec.yaml`
- [x] 7.13 Add initializer tests for clean install, symlinked OpenSpec roots, repeat install, upgrade, conflict, partial failure, and rollback

## 8. Provider Adapter Infrastructure

- [x] 8.1 Define the provider adapter protocol for capability probing, invocation, cancellation, and result parsing
- [x] 8.2 Implement configured executable resolution through an allowlist without shell lookup ambiguity
- [x] 8.3 Implement subprocess argument arrays and prohibit `shell=True`
- [x] 8.4 Implement bounded prompt delivery through stdin or run-owned files without shell interpolation
- [x] 8.5 Implement explicit working-directory and additional-root containment checks
- [x] 8.6 Implement minimal environment inheritance, provider-auth passthrough policy, and secret redaction
- [x] 8.7 Implement timeouts, cancellation, output-size limits, and bounded stdout/stderr capture
- [x] 8.8 Implement request, token, and cost-limit enforcement where provider capabilities expose usage
- [x] 8.9 Implement provider event normalization with full prompts and protected artifact bodies excluded
- [x] 8.10 Create fake provider executables for success, invalid JSON, schema mismatch, timeout, cancellation, missing capability, stale session, and non-zero exit
- [x] 8.11 Add adapter conformance tests that assign `automated`, `guided`, `experimental`, or `unsupported` tiers

## 9. Claude Code Adapter

- [x] 9.1 Implement Claude Code executable and capability probing
- [x] 9.2 Implement non-interactive invocation with JSON Schema validation and parseable output
- [x] 9.3 Enforce planning-only Claude tools and permission mode
- [x] 9.4 Implement optional direct selection of a managed Claude agent without increasing stage authority
- [x] 9.5 Capture Claude session identity, usage, bounded diagnostics, and same-attempt resume capability
- [x] 9.6 Default backtracked or newly revised stages to fresh Claude sessions
- [x] 9.7 Add deterministic adapter tests for valid output, schema failure, permission failure, timeout, budget limit, session recovery, and non-zero exit
- [x] 9.8 Add an opt-in, read-only, finite-budget Claude smoke test

## 10. Codex Adapter

- [x] 10.1 Implement Codex executable and capability probing
- [x] 10.2 Implement `codex exec` invocation with explicit working directory and `--sandbox read-only`
- [x] 10.3 Apply the stage JSON Schema through `--output-schema`
- [x] 10.4 Parse Codex JSONL events and require a valid final structured result
- [x] 10.5 Capture Codex session identity, usage when available, bounded diagnostics, and same-attempt resume capability
- [x] 10.6 Ensure headless execution works without selecting a named custom Codex subagent
- [x] 10.7 Default backtracked or newly revised stages to fresh Codex sessions
- [x] 10.8 Add deterministic adapter tests for valid output, malformed event stream, missing final result, schema failure, timeout, session recovery, and non-zero exit
- [x] 10.9 Add an opt-in, read-only, finite-budget Codex smoke test

## 11. Feature-Based Skills and Optional Native Agents

### 11A. harness-workflow Skill (Main Orchestrator)

- [x] 11A.1 Create `skills/harness-workflow/SKILL.md` using portable Agent Skills metadata
- [x] 11A.2 Create `skills/harness-workflow/references/stages.md` with a non-authoritative map of all 13 stage purposes
- [x] 11A.3 Create `skills/harness-workflow/references/anti-hallucination.md` guide
- [x] 11A.4 Create `skills/harness-workflow/references/gotchas.md` with common mistakes
- [x] 11A.5 Create `skills/harness-workflow/references/commands.md` mapping start, status, next, stage begin/complete, answer, and report to CLI-owned operations
- [x] 11A.6 Add contract tests proving `harness-workflow` obtains and submits data only through the CLI and never mutates run state or current artifacts directly
- [x] 11A.7 Verify stage instructions, output schemas, and templates resolve from the CLI and OpenSpec schema without authoritative copies in the skill

### 11B. harness-gates Skill (Gate Management)

- [x] 11B.1 Create `skills/harness-gates/SKILL.md` for gate approval/rejection instructions
- [x] 11B.2 Create `skills/harness-gates/references/gate-policies.md` for gate configuration
- [x] 11B.3 Create `skills/harness-gates/references/approval-patterns.md` for artifact review
- [x] 11B.4 Add contract tests proving `harness-gates` invokes digest-bound CLI commands and performs no independent gate validation or mutation

### 11C. harness-traceability Skill (Traceability System)

- [x] 11C.1 Create `skills/harness-traceability/SKILL.md` for traceability instructions
- [x] 11C.2 Create `skills/harness-traceability/references/traceability-format.md` for link format
- [x] 11C.3 Create `skills/harness-traceability/references/traceability-matrix.md` for matrix examples
- [x] 11C.4 Add contract tests proving `harness-traceability` delegates link validation and matrix generation to the CLI

### 11D. Validation and Native Agents

- [x] 11D.1 Validate all 3 feature-based skills with `skills-ref`
- [x] 11D.2 Verify skills contain no Claude-only context, agent, argument, model, invocation fields
- [x] 11D.3 Create optional Claude `harness-researcher`, `harness-writer`, `harness-verifier` agent templates
- [x] 11D.4 Create optional Codex `harness-researcher`, `harness-writer`, `harness-verifier` agent templates
- [x] 11D.5 Generate native agent files through initializer-managed templates
- [x] 11D.6 Test `npx skills add` independently from CLI and initializer installation
- [x] 11D.7 Test guided stage begin/complete flows with deterministic Claude and Codex host fixtures; keep live-host checks opt-in

## 12. CLI, Gates, Doctor, Reporting, and Observability

- [x] 12.1 Implement `harness init` and managed rollback commands
- [x] 12.2 Implement `harness doctor` with OpenSpec, ledger, provider, skill, native-agent, conflict, and path checks
- [x] 12.3 Implement `harness start` with safe ticket input from file, stdin, or bounded literal argument
- [x] 12.4 Implement `harness run` and `harness next` for guided and headless execution
- [x] 12.5 Implement `harness status` with current stage, mode, provider, revisions, pending clarification or gate, warnings, and errors
- [x] 12.6 Implement `harness stage begin` and `harness stage complete` with JSON mode
- [x] 12.7 Implement `harness answer` bound to pending clarification IDs
- [x] 12.8 Implement digest-bound `harness approve` with trusted local actor resolution
- [x] 12.9 Implement `harness reject` with reason, allowed backtrack validation, and trusted local actor resolution
- [x] 12.10 Implement explicit trusted-actor `harness backtrack` with required reason, allowed-target validation, current-revision digest binding, and revision supersession
- [x] 12.11 Implement `harness report` with human-readable and machine-readable verification results
- [x] 12.12 Define stable exit codes for success, waiting states, invalid input, provider unavailable, provider failure, validation blocked, stale decision, not found, and internal failure
- [x] 12.13 Ensure JSON mode writes only schema-valid output to stdout and diagnostics to stderr
- [x] 12.14 Implement secret-safe structured events for run, stage, provider, gate, clarification, revision, validation, and failure operations
- [x] 12.15 Add CLI subprocess tests and golden files for human and JSON output

## 13. Security and Failure Verification

- [x] 13.1 Test ticket and prompt inputs containing quotes, substitutions, newlines, option-like prefixes, and shell metacharacters
- [x] 13.2 Test absolute, relative, traversal, symlink, and race-prone path escape attempts
- [x] 13.3 Test provider attempts to edit source or current artifacts outside the CLI acceptance path
- [x] 13.4 Test stale, replayed, expired, unauthorized, cross-run, cross-stage, cross-revision, and digest-mismatched gate decisions
- [x] 13.5 Test fabricated clarification answers and self-asserted actor identities
- [x] 13.6 Test concurrent advancement, duplicate completion, interrupted transactions, and stale lease recovery
- [x] 13.7 Test provider timeout, cancellation, oversized output, request limit, token limit, and cost limit behavior
- [x] 13.8 Test invalid provider capability claims and capability changes between doctor and execution
- [x] 13.9 Verify credentials, protected environment values, full prompts, and protected artifact bodies do not appear in routine SQLite fields, JSON output, stderr, or events
- [x] 13.10 Run dependency and security scanning approved for the new repository and document any accepted residual risk

## 14. End-to-End Acceptance

- [x] 14.1 Run the deterministic full 13-stage guided workflow fixture
- [x] 14.2 Run the deterministic full 13-stage headless workflow with fake providers
- [x] 14.3 Verify a `needs_input` clarification survives process restart and resumes only after recorded answers
- [x] 14.4 Verify all four gates pause, survive restart, reject invalid decisions, and resume without rerunning approved stages
- [x] 14.5 Verify rejection and backtrack preserve immutable history, supersede downstream revisions, reset current materializations, and create new revisions
- [x] 14.6 Verify `not_applicable` artifacts preserve dependency and traceability completeness
- [x] 14.7 Verify coverage reporting detects missing requirements, acceptance criteria, test cases, and automated-test mappings
- [x] 14.8 Run bounded Claude and Codex smoke workflows with read-only authority only when explicitly opted in and configured; otherwise record the documented skip
- [x] 14.9 Validate `harness-13`, the active OpenSpec change, and every portable skill
- [x] 14.10 Run `uv run ruff check .` and require a zero exit status
- [x] 14.11 Run `uv run ruff format --check .` and require a zero exit status
- [x] 14.12 Run strict mypy for `src/` and `tests/` and require a zero exit status
- [x] 14.13 Run the full pytest suite with coverage and require the approved coverage threshold
- [x] 14.14 Verify `uv sync --frozen` from a clean checkout
- [x] 14.15 Test initializer clean install, repeat install, compatible upgrade, unmanaged conflict, partial failure, and rollback in a temporary project

## 15. Focused Documentation and Internal Handoff

- [x] 15.1 Document CLI installation with `uv`, portable skill installation with `npx skills`, and explicit project initialization
- [x] 15.2 Create a getting-started tutorial for the first guided workflow
- [x] 15.3 Create a getting-started tutorial for the first Claude or Codex headless workflow
- [x] 15.4 Document clarification, approval, rejection, backtrack, revision, and restart procedures
- [x] 15.5 Document CLI commands, stable exit codes, JSON schemas, configuration, state, provider capabilities, and support tiers
- [x] 15.6 Document evidence classification, stable IDs, traceability coverage, and planning-verification semantics
- [x] 15.7 Document security boundaries, provider authentication ownership, path containment, budgets, retention, and secret handling
- [x] 15.8 Document architecture and the explicit comparison with `agent-harness`
- [x] 15.9 Document doctor diagnostics, provider failures, schema conflicts, ledger recovery, and rollback
- [x] 15.10 Create an internal local-development and acceptance runbook without public marketplace instructions
- [x] 15.11 Update the TDT ecosystem index to identify this repository as an alternative rather than a replacement
- [x] 15.12 Record final validation evidence and the commands/output required for `/opsx:verify`

## 16. Verification Remediation

- [x] 16.1 Persist the bounded ticket in a protected run-owned input file and expose it only through the current stage request without storing the body in routine SQLite metadata
- [x] 16.2 Compose a canonical bounded provider prompt containing run/stage identity, ticket input where applicable, accepted evidence, upstream artifacts, clarification answers, limits, and result instructions
- [x] 16.3 Wire production evidence, upstream-artifact, and clarification-answer resolvers into `build_runtime` and add real-composition guided/headless tests
- [x] 16.4 Generate terminal traceability links and coverage from accepted immutable revisions in the CLI rather than trusting provider-supplied coverage
- [x] 16.5 Expose mode, provider, revisions, and the complete pending gate contract through `harness status`
- [x] 16.6 Correct portable workflow and gate skill commands and execute their documented CLI shapes in contract tests
- [x] 16.7 Coordinate rejection and administrative backtracking with verified artifact materialization reset and crash-safe recovery behavior
- [x] 16.8 Reject unknown and shared-state configuration, honor configured default mode, and test the standalone fail-closed boundary
- [x] 16.9 Convert unexpected CLI exceptions to stable internal-failure output and enrich stage/provider events with required bounded fields
- [x] 16.10 Make doctor skill discovery host-aware and base support tiers on actual installed skills
- [x] 16.11 Add regression tests for ticket propagation, real provider prompt context, authoritative coverage, restart-safe gates, backtracking, configuration, diagnostics, and skill command accuracy
- [x] 16.12 Re-run frozen sync, lint, format, strict typing, coverage, dependency audit, OpenSpec/schema/skill validation, and GitNexus scope verification (unborn-repository compare limitation recorded)

## 17. Post-verification defect remediation

- [x] 17.1 Make expired gates recoverable without leaving runs permanently waiting; add regression coverage
- [x] 17.2 Reject non-finite configuration limits and provider usage values before budget enforcement
- [x] 17.3 Enforce run-wide request/revision limits and honor configured provider arguments and model aliases
- [x] 17.4 Bound provider output capture, restrict provider authentication environments, and reject protected values in accepted output
- [x] 17.5 Classify malformed CLI JSON as invalid input and close evidence path races during source reads
- [x] 17.6 Replace the stale validation report with current evidence and document resolution of the repository-baseline limitation
- [x] 17.7 Re-run all verification, initialize GitNexus and Graphify, install the Graphify hooks, and commit with the OpenSpec reference
