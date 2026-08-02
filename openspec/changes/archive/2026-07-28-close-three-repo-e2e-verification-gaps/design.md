## Context

The 2026-07-28 verification ran frozen installs, Ruff, formatting, strict mypy,
coverage-enabled full tests, CLI entrypoints, deterministic feature smoke
tests, targeted security scans, and strict OpenSpec validation across
`agent-core`, `agent-docs-sync`, and `agent-harness`.

The static and unit/integration surface is healthy (896 passed, one real
PostgreSQL test skipped), but feature-level evidence exposed four structural
gaps:

1. `agent-harness run` uses an in-memory saver when durability is disabled.
   Once it pauses at a gate and the process exits, a later CLI process creates
   a new runner and cannot recover the run.
2. Protected gates default to enabled while approvers default to empty. The
   graph correctly fails closed, but the error arrives late as a traceback and
   the quick-start path omits the required policy/persistence configuration.
3. Skill discovery parses every flat Markdown file and does not canonicalize
   aliased roots, producing 18 invalid-file and 125 shadow warnings during one
   doctor run.
4. Docs-sync discovery includes test sources by default and treats every source
   file as a potential one-file/one-document obligation. Audit conflates scan
   success with compliance, coverage is 63%, and tracked bytecode is rewritten
   by normal CLI imports. `agent-core` coverage is also below the shared 80%
   gate at 77%.

Existing contracts already require fail-closed gates, shared checkpoint
boundaries, canonical docs pipelines, and 80% coverage. This design closes the
observable implementation/evidence gaps without weakening authorization or
creating alternate workflow infrastructure.

## Goals / Non-Goals

**Goals:**

- Make the supported harness CLI lifecycle recoverable across processes.
- Preserve explicit approver authorization and native LangGraph interrupt
  identity.
- Produce concise, stable text and JSON CLI failures.
- Turn skill doctor output into actionable logical diagnostics.
- Make docs discovery/audit focus on supported production documentation
  surfaces and report compliance truthfully.
- Raise `agent-core` and `agent-docs-sync` to at least 80% coverage while
  retaining `agent-harness` at or above 80%.
- Prove the durable lifecycle using disposable real PostgreSQL and record a
  reproducible three-repository evidence manifest.
- Leave all three repositories free of tracked Python cache artifacts after
  verification.

**Non-Goals:**

- Auto-authorizing the current OS account or weakening gate validation.
- Supporting cross-process gates with an in-memory saver.
- Provisioning production databases, gateways, or secrets.
- Running write-capable LLM generation against production repositories.
- Replacing the shared `agent-core` checkpointer or consumer-owned LangGraph.
- Implementing the separate stale scheduler cleaner change.
- Documenting every test/private helper as a public docs-sync obligation.

## Decisions

### 1. Enforce protected-run prerequisites at the CLI boundary

Add one harness CLI preflight that loads configuration and validates:

- protected interrupt stages imply a non-empty `gate.approvers` list;
- protected CLI runs imply `persistence.durable=true`;
- durable mode implies a non-empty `persistence.postgres_url` loaded from the
  canonical `TDT_POSTGRES_URL` contract.

The preflight runs before `WorkflowRunner.run()` or graph construction and
returns stable domain error codes. `build_graph()` keeps its existing
fail-closed validation as defense in depth.

**Why:** This avoids changing the CRITICAL `build_graph` root for a UX/config
problem, while retaining its invariant for programmatic callers.

**Alternative considered:** Derive an approver automatically from the current
OS user. Rejected because it silently changes authorization policy.

**Alternative considered:** Persist non-durable runs to local files. Rejected
because it creates a second checkpoint model and weaker concurrency semantics.

### 2. Give every lifecycle command the same configuration resolver

Create a small CLI composition helper that accepts the optional `--config`
path, calls `HarnessConfig.load()`, performs command-appropriate preflight, and
constructs `WorkflowRunner`. Add the same configuration override to `status`,
`report`, `approve`, and `reject` while preserving canonical `$TDT_HOME`
defaults.

Runner operations continue opening the existing async Postgres checkpointer
for the operation lifetime and use `run_id` as the LangGraph `thread_id`.
Unknown checkpoints never create state. A configuration/backend mismatch is
reported using a stable error code when it can be distinguished safely; URLs
and credentials are never printed.

**Why:** A run created with an explicit config is otherwise unrecoverable from
the other CLI commands.

### 3. Centralize harness CLI error rendering

Map expected configuration, unknown-run, checkpoint-version, authorization,
expiry, and decision-mismatch exceptions to a small error model:

```text
code, message, remediation?, run_id?, stage?
```

Text mode prints one concise message; JSON mode prints exactly one JSON object.
Unexpected exceptions remain non-zero and are logged with correlation context,
but normal output stays machine-readable. `structlog` output for JSON commands
is sent to stderr or suppressed according to the existing quiet policy.

### 4. Use one canonical skill-candidate discovery algorithm

Share candidate enumeration semantics between `SkillLoader` and
`diagnose_profile`:

- always accept `<skill>/SKILL.md`;
- retain flat Markdown compatibility only for files that contain skill
  frontmatter or are explicitly named by an include filter;
- ignore catalog/reference Markdown without skill frontmatter;
- canonicalize candidates with `Path.resolve()` before parsing and shadow
  analysis;
- report aliases to the same canonical path once;
- report genuinely distinct same-name sources as one structured shadow issue;
- promote missing/invalid explicitly included skills to errors.

The loader's first-directory-wins behavior remains unchanged. Doctor JSON is
rendered after diagnostics complete so loader logs cannot be interleaved on
stdout.

**Alternative considered:** Remove flat Markdown support entirely. Rejected
because the canonical spec still promises backward compatibility.

### 5. Separate docs-sync scan scope, public obligations, execution, and compliance

Extend discovery/audit inputs with explicit inclusion controls while defaulting
to production source. Central path policy excludes `tests/`, `.venv/`, cache
directories, bytecode, coverage/build output, and generated metadata.

Scanning production source and deciding that a source needs dedicated public
documentation are separate operations. The actionable public surface consists
of package exports, configured console-script/CLI entrypoints, deployment and
configuration artifacts, and explicit docs mappings. Other production modules
remain visible in scan statistics and architecture evidence, but their missing
one-to-one document is informational unless a mapping or public export makes it
actionable. Expanded internal/test audits are explicit and report their
effective boundary.

Audit results expose:

- `execution_succeeded`;
- `documentation_compliant`;
- actionable/excluded gap counts;
- broken-link and Diataxis counts;
- the effective scan boundary.

Keep `validation_passed` for one compatibility window as a deprecated alias of
`documentation_compliant`, not scan execution. Add `audit --strict` to return
non-zero when actionable findings remain.

### 6. Close coverage through supported-path tests, not exclusions

Add tests around production behavior with the largest current gaps.

- `agent-core`: MCP/tool preparation, stream approvals, scheduler setup,
  tracing/checkpointer/memory boundaries, and CLI evaluation paths. Optional
  external systems use deterministic fakes except where a real backend is the
  feature under test.
- `agent-docs-sync`: discovery pipeline, canonical/full pipeline branches,
  strict audit semantics, state persistence, LLM gateway boundaries, and
  observability scorers/hooks.
- `agent-harness`: retain the current 84% baseline and add CLI process-error and
  durable lifecycle coverage.

Each repo adds `--cov-fail-under=80` to its CI-quality command and a check that
supported production modules do not remain at 0%. Coverage omissions are not
expanded to hide misses.

### 7. Test durability with disposable real PostgreSQL

Promote the existing opt-in `TDT_POSTGRES_TEST_URL` contract into a required CI
job. When an explicit `TDT_POSTGRES_TEST_URL` is present, use that operator- or
CI-supplied disposable backend. Otherwise, start
`PostgresContainer("postgres:18.4-trixie")`, matching the primary agent-core
Compose database, and obtain a psycopg 3-compatible DSN with
`get_connection_url(driver=None)`. Pass the same DSN to every child process as
both `TDT_POSTGRES_TEST_URL` and `TDT_POSTGRES_URL`.

`testcontainers[postgres]` is an agent-harness test-only dependency managed by
`uv`; it is not imported by production code. The container SHALL be owned by a
context-managed test fixture, use unique run/database/schema identities, and
be discarded rather than reused. `PostgresContainer` supplies the bounded
server-readiness wait; the fixture still invokes the shared checkpointer's
public async `setup()` contract before graph compilation. CI SHALL fail the
required PostgreSQL job when neither an explicit test DSN nor Docker-daemon
access is available, and SHALL never substitute an in-memory saver.

The real-backend lifecycle covers:

1. create an isolated database and call the public async saver `setup()` before
   graph compilation;
2. start in one operating-system process and pause at `spec`;
3. terminate that process;
4. recover status and the pending interrupt from a second process;
5. approve and advance without rerunning completed stages;
6. reject a later gate to an allowed target;
7. inspect report/history from another process;
8. reject unknown/cross-thread/replayed decisions without checkpoint mutation.

Database setup is test-only. Production migrations and deployment databases
are not touched. The existing user-owned initialization SQL and PostgreSQL test
files are inspected and preserved, then extended only where the isolated
fixture requires it.

### 8. Enforce clean generated-artifact boundaries

Remove tracked `.pyc`/`__pycache__` entries from `agent-docs-sync`, retain ignore
rules in all repositories, and add a CI assertion based on `git ls-files`.
Verification commands use isolated temporary workspaces and capture before/after
status so tool-generated files cannot be mistaken for implementation changes.

### 9. Record one evidence manifest without a new runtime service

Store the final verification manifest in this OpenSpec change. It records each
repo HEAD, tracked diff hash, untracked path inventory, frozen dependency
versions, commands/results, coverage, environment classification, PostgreSQL
fixture identity, and GitNexus `detect-changes` scope. A lightweight script MAY
orchestrate commands, but it does not become a deployed service.

GitNexus status SHALL be current for each repository before impact or
post-change detection is accepted as evidence. The finalized baseline is
`langgraph==1.2.9` and `langgraph-checkpoint-postgres==3.1.0`; later resolutions
must be recorded rather than silently treated as the same matrix row.

## Risks / Trade-offs

- **[CRITICAL graph regression]** Fresh GitNexus analysis shows `build_graph`
  affects nine processes. → Keep preflight outside the graph, freeze
  characterization tests, and run fresh-index GitNexus change detection before
  completion.
- **[HIGH CLI compatibility risk]** Adding shared config/error handling touches
  all lifecycle commands. → Preserve command names/options, add options
  additively, and test text plus JSON contracts.
- **[Existing non-durable CLI users now fail earlier]** Protected runs that
  previously reached a gate in memory will be rejected. → Provide actionable
  setup guidance; retain same-process behavior through the programmatic runner.
- **[Coverage work becomes assertion-free line execution]** Raising percentages
  can incentivize weak tests. → Require behavior/negative-path assertions and
  prioritize supported feature paths listed in the evidence matrix.
- **[Docs audit output compatibility]** Consumers may read
  `validation_passed`. → Retain a deprecated alias for one compatibility window
  and document the new fields.
- **[Skill aliases conceal distinct deployments]** Over-aggressive path
  canonicalization could merge files unintentionally. → De-duplicate only
  identical resolved paths; distinct canonical files remain shadow diagnostics.
- **[Real database and Docker flakiness]** Image startup or daemon access may
  fail in CI. → Pin the PostgreSQL image, prefer an explicit disposable DSN
  when supplied, rely on bounded Testcontainers readiness, use isolated names
  and context-managed cleanup, and fail the required gate rather than silently
  downgrading to in-memory.
- **[Dirty worktrees distort evidence]** Existing user changes are present in
  all three repos. → Record exact pre/post identities and never reset or absorb
  unrelated changes.

## Migration Plan

1. Capture current characterization fixtures for graph topology, gates, CLI
   outputs, skill loader precedence, docs audit reports, and coverage baselines.
2. Implement the low-risk docs-sync boundary/cache changes and agent-core
   diagnostic de-duplication; verify repository-local gates.
3. Add harness CLI preflight and shared configuration/error composition without
   changing `build_graph` semantics.
4. Add the Testcontainers test dependency, enable the disposable PostgreSQL
   lifecycle job with external-DSN override support, and prove cross-process
   gate recovery.
5. Raise and enforce coverage in `agent-core` and `agent-docs-sync`; preserve
   the `agent-harness` baseline.
6. Run the complete three-repository matrix and write the evidence manifest.
7. Deploy no daemon/service changes. Release consists of normal package/CLI and
   CI updates.

Rollback is per repository: revert the CLI composition/preflight layer while
leaving the existing graph fail-closed invariant intact; revert docs audit
fields while retaining compatibility aliases; revert diagnostic presentation
without changing loader precedence. Database fixtures are disposable and need
no production rollback.

## Open Questions

None blocking. PostgreSQL execution uses a pinned Testcontainers backend by
default while remaining provider-neutral through an explicit
`TDT_POSTGRES_TEST_URL` override. The deprecated `validation_passed` audit alias
is retained for exactly one compatibility release.
