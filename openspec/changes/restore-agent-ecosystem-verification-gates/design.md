## Context

See `proposal.md` for motivation and scope. The current evidence is bound to
three independent Git roots:

- `agent-core` at `52419d9d77358212770f783d0749b3c9c3538d32`:
  679 passed, 14 failed, and one prerequisite skip; Ruff and strict source
  mypy pass. Nine failures construct credential-requiring providers and five
  perform uncontrolled DNS resolution before mocked HTTP transport.
- `agent-docs-sync` at `1bcb7c7654ac744d60595f41f38abbc235b3767d`:
  205 passed and one prerequisite skip; Ruff and strict source mypy pass, but
  `mypy src tests --strict` reports one untyped pytest fixture boundary.
- `agent-harness` at `ce33bb50d7f8b1e9658397a0802717a591a6133e`:
  323 passed and six prerequisite skips; Ruff passes, but `mypy src tests
  --strict` reports nine errors in four test files.

All three default worktrees contain pre-existing dirty `graphify-out/` files;
`agent-docs-sync` also contains an untracked generic `doc-sync/SKILL.md`
scaffold. Those paths are not owned by this change. The tracked canonical
docs-sync skill remains `.agents/skills/doc-sync/SKILL.md`.

Archived corrective evidence already defines the required zero-failure,
strict-typing, coverage, prerequisite, and source-identity contracts. The
active `android-scanner` profile is effective host configuration used by
`code-daily-scan`; archived July 28 evidence recorded missing named includes
and explicitly prohibited silently rewriting developer configuration. The
August 9 coding-agent skill-distribution change owns Claude/Codex/shared agent
skill discovery, not this application runtime profile.

## Goals / Non-Goals

**Goals:**

- Restore a reproducible, credential-less and network-restricted unit-test
  baseline for agent-core while retaining production security checks.
- Make both consumer repositories' source-plus-test strict typing commands
  truthful and green.
- Re-certify all three repositories from exact, stable source identities and
  refresh only evidence that is derived from those commands.
- Keep each repository's source edit, verification, commit, and rollback
  independently attributable while producing one joint readiness verdict.
- Preserve all unrelated dirty state and fail closed when source identity moves
  during verification.

**Non-Goals:**

- Reconfigure the host, repair `code-daily-scan`, invent application skills,
  or merge coding-agent and application-runtime skill ownership.
- Change public behavior, external dependencies, deployment state, or
  repository policy unrelated to a reproduced failing gate.
- Clean or regenerate Graphify/GitNexus data as a side effect of test repair.
- Convert unavailable external prerequisites into skips that satisfy a required
  readiness gate.

## Decisions

### 1. Use one corrective readiness change with separate repository transactions

The readiness claim covers the compatible set, but implementation SHALL use a
dedicated worktree and one writer for each Git repository. Every repository is
reviewed, tested, and committed independently; the integration owner records
the three resulting commits in store evidence only after all source identities
are stable.

**Alternative considered:** Three unrelated OpenSpec changes. Rejected because
the stale archived claims and final readiness verdict are cross-repository, but
the design still preserves independent source transactions and rollback.

### 2. Reuse existing normative requirements and stop on contract drift

This change uses `skip_specs: true` because the intended result is conformance
to existing `agent-core-quality-gate`, `agent-framework-verification`,
`documentation-currency`, and
`agent-framework-documentation-evaluation` requirements. Apply work SHALL stop
before any public/runtime contract change and revise the proposal plus add a
delta spec when implementation-only repair proves insufficient.

**Alternative considered:** Add a new generic ecosystem-readiness capability.
Rejected because it would duplicate existing zero-test-failure, strict typing,
current evidence, and source-attribution requirements.

### 3. Make unit tests deterministic at external-construction boundaries

Agent-core provider-construction tests SHALL pass an explicit Pydantic AI test
model/provider or inject the provider factory at the boundary under test. They
MUST NOT depend on `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, host provider config,
or a reachable provider.

HTTP-tool tests SHALL preserve the production `_validate_destination` and
redirect-security path while supplying deterministic `socket.getaddrinfo`
results and mocked transport responses. Tests MUST continue to cover blocked
hostnames, private/reserved addresses, redirects, response-size bounds, and
DNS failure. Production DNS and SSRF behavior remains unchanged.

**Alternative considered:** Set fake global credentials and enable network for
the suite. Rejected because it hides construction coupling and cannot support
offline CI or secure local verification.

### 4. Correct consumer test typing without weakening production contracts

Tests SHALL prefer the supported string model identifier when exercising
`HarnessServices`. Explicit `TestModel` instances remain valid where the public
`StageCompositionContext` already declares `str | Model | None`. Missing
fixture/helper annotations SHALL be completed directly.

If impact analysis shows `HarnessServices.model` is intentionally a public
`Model`-accepting boundary whose annotation is stale, a type-only annotation
correction MAY be proposed, but apply work must first establish that runtime
behavior already supports it and that no spec/API compatibility change is
introduced. Otherwise production types are not widened.

The docs-sync failure is a missing annotation on a pytest fixture boundary in
`tests/test_state_lifecycle.py`; it SHALL be fixed directly with the existing
typed pytest interfaces and no production change.

**Alternative considered:** Add broad mypy suppressions or relax strict mode.
Rejected because that would violate the existing quality gate and conceal the
composition mismatch.

### 5. Regenerate evidence only after final source is frozen

Each repository SHALL record:

- HEAD, branch/worktree, sorted dirty path inventory, and a production-relevant
  content fingerprint before and after verification;
- locked dependency resolution and exact tool versions;
- formatting, Ruff, strict source-plus-test mypy, full tests, per-repository
  coverage, secret scan, and CLI subprocess commands with exit status;
- every skip or blocked prerequisite with the condition that caused it;
- test and import counts derived from the same final source state.

README, `AGENTS.md`, and `SPEC_INDEX.md` metrics are updated only from that
evidence. The corrective ledger points to archived claims and records current
replacement evidence without editing archived artifacts.

**Alternative considered:** Update static counts before implementation.
Rejected because any later source/test edit would make them stale again.

### 6. Preserve unowned working-tree and active-change state

The implementation scope audit SHALL classify every dirty path as owned or
external before edits. Existing `graphify-out/`, the untracked root docs-sync
scaffold, tracked report history, and other active OpenSpec changes are never
staged or removed by this change. Full-store validation failures with different
owners are reported separately from focused validation of this change.

### 7. Separate application profile health from three-repository code readiness

The final report SHALL preserve the `android-scanner` doctor result as an
external configuration/profile finding. It SHALL identify `code-daily-scan`
and host configuration as the affected ownership boundary and SHALL not claim
that the August 9 coding-agent skill migration caused or fixed the missing
application skills. A separate follow-up may be proposed after those skill
sources and the host-config owner are identified.

## Risks / Trade-offs

- **[Mocking hides production security behavior]** → Mock only provider/DNS
  inputs, retain production validation code, and keep explicit negative SSRF,
  redirect, and DNS-failure cases.
- **[Joint readiness conceals one failing repository]** → Emit independent
  per-repository results and reject the joint verdict when any required gate is
  failed, blocked, stale, or below threshold.
- **[Type repair changes public API unintentionally]** → Prefer fixture
  corrections; require impact review and proposal/spec revision before any
  actual contract change.
- **[Concurrent sessions overwrite store or source work]** → Use dedicated
  worktrees, one writer per repository, explicit ownership messages, and
  compare HEAD plus dirty fingerprints before and after every gate.
- **[Static metrics drift again]** → Generate them last from retained command
  output and include the source identity beside every readiness statement.
- **[External prerequisites remain unavailable]** → Leave the corresponding
  task unchecked and classify the joint result as not ready rather than
  weakening the gate.

## Migration Plan

1. Establish repository worktree ownership and capture pre-edit source
   identities and dirty inventories.
2. Repair agent-core tests using deterministic provider and DNS fixtures; run
   its complete required gates.
3. Repair consumer test typing without weakening strictness or public
   contracts; run the complete agent-harness and agent-docs-sync gates.
4. Classify external docs-sync scaffold state and identify only
   evidence-document updates owned by this change.
5. Freeze the three source commits, regenerate evidence and documentation, and
   rerun every gate against the final commits.
6. Validate this OpenSpec change strictly, run all-store validation with
   unrelated failures separately attributed, and perform an independent
   diff/scope review.
7. Integrate each repository only after its own review passes; then commit the
   store evidence and leave the change active for user review before apply or
   archive decisions.

Rollback is repository-local: revert evidence/docs first, then the matching
test-only commit. Do not revert existing SDK/runtime behavior, delete external
dirty paths, or modify host configuration. If a test isolation change weakens a
security assertion, revert it immediately and retain the failing gate as open.
