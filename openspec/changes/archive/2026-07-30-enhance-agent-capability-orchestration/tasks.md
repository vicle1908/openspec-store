## 1. Baseline and preservation evidence

- [x] 1.1 Capture HEAD, relevant dirty-state fingerprints, outer/nested Git
  roots, current tool versions, index metadata, MCP registrations, skill
  manifests, hooks, and pre-existing untracked paths in redacted baseline
  evidence.
- [x] 1.2 Add a fixture proving baseline capture preserves the three existing
  unrelated OpenSpec change directories and nested-repository dirty state.
- [x] 1.3 Record current approved/installed/latest observations for GitNexus,
  Graphify, OpenSpec, agentmemory, and the skills CLI without changing pins.
- [x] 1.4 Snapshot hashes for Agentmemory hooks, hand-authored guidance, native
  GitNexus/Graphify skills, OpenSpec-generated surfaces, and rollback-owned
  configuration.

## 2. Health schema and bounded runner

- [x] 2.1 Add the `microservices.agent-capability-health/v1` JSON Schema with
  run/source identity, profile, probe requirement class, attempts, duration,
  status, bounded error, evidence reference, overall readiness, and remediation.
- [x] 2.2 Add schema fixtures for `ready`, `ready-with-warnings`,
  `not-ready`, invalid status, missing source identity, and incomplete probe
  output.
- [x] 2.3 Implement atomic run-directory finalization and a latest-evidence
  pointer that updates only after terminal probes and schema validation pass.
- [x] 2.4 Add tests for interrupted runs, evidence-write failure, source-state
  changes during execution, and preservation of the prior successful report.
- [x] 2.5 Implement quick, exploration, and implementation profile policy with
  explicit required/optional probe IDs and deterministic exit status.
- [x] 2.6 Add outer process-group deadlines around every CLI/MCP/REST probe and
  tests proving a hung child and its descendants are terminated without
  blocking independent probes.
- [x] 2.7 Add bounded retry classification and tests proving transient read-only
  probes retry deterministically while unknown partial mutations never retry
  automatically.
- [x] 2.8 Extend centralized redaction and fixtures for tokens, passwords,
  private keys, authenticated URLs, complete environments, and credential-like
  memory content.
- [x] 2.9 Add `knowledge-health` Make/CLI entry points for each profile and
  document which profiles are read-only versus locally mutating.

## 3. Agentmemory recovery and verification

- [x] 3.1 Update diagnostics to report repository policy version,
  installed/version-documented tool mode, loopback health, and optional
  LLM/Ollama state independently.
- [x] 3.2 Start agentmemory through the supported host workflow and verify zero
  red doctor rows before any healthy memory claim.
- [x] 3.3 Discover the selected `AGENTMEMORY_TOOLS` mode and compare live MCP
  discovery with the reviewed version's full or core expected surface.
- [x] 3.4 Implement a unique disposable memory probe that saves, retrieves,
  governance-deletes, and verifies deletion/audit evidence without exposing
  content.
- [x] 3.5 Add fixtures for server-down wiring, full/core tool modes, partial
  tool discovery, duplicate-free repeated verification, cleanup failure, and
  optional summarizer unavailability.
- [x] 3.6 Document the `0.9.27` policy versus `0.9.28` installed/latest
  compatibility result and create a separate follow-up change if an upgrade is
  approved.

## 4. FileProvider and knowledge-index safety

- [x] 4.1 Build a disposable FileProvider/stale-read fixture that exercises
  bounded metadata reads, single-writer ownership, reader exclusion, timeout,
  and last-good-output restoration.
- [x] 4.2 Verify current GitNexus and Graphify documentation/CLI support for
  alternate state or output paths and record unsupported flags explicitly.
- [x] 4.3 Implement the selected in-place or local-mirror strategy without
  symlinking or deleting unreadable index state as an implicit repair.
- [x] 4.4 Add GitNexus probes for registry discovery, repository context,
  query, impact, structural checks, PDG, indexed commit, and dirty-state
  freshness under bounded deadlines.
- [x] 4.5 Add GitNexus fixtures for missing index, stale source identity,
  unavailable LadybugDB, concurrent rebuild, timeout, healthy outer root, and
  healthy nested root.
- [x] 4.6 Add Graphify probes for MCP discovery, graph statistics, scoped query,
  manifest/root parity, and structural diagnostics covering dangling, missing,
  collapsed, and self-loop edges.
- [x] 4.7 Add Graphify incremental fixtures proving changed-source replacement,
  deleted-source pruning, direction preservation, root-relative paths,
  unexpected-shrink refusal, and last-good-graph preservation.
- [x] 4.8 Restore and verify outer and nested GitNexus/Graphify state only after
  the compatibility gate passes, retaining independent evidence per root.
- [x] 4.9 Record Graphify `0.9.26` versus `0.9.30` compatibility results and
  create a separate upgrade change if the reviewed pin should move.

## 5. Orchestration skill and identity model

- [x] 5.1 Add the hand-authored orchestration skill to the canonical
  `.agents/skills` surface with Explore, Prepare, Verify, and Handoff phases.
- [x] 5.2 Encode the authority/fallback table for OpenSpec, GitNexus, Graphify,
  agentmemory, `rg`, direct source inspection, and focused tests.
- [x] 5.3 Add cross-tool evidence fields for root, repository, OpenSpec change,
  capability, source location, symbol/concept ID, confidence/evidence type, and
  memory reference.
- [x] 5.4 Add tests proving memory and inferred Graphify evidence cannot
  override current OpenSpec requirements or direct source-code observations.
- [x] 5.5 Add managed-surface policy showing, for every selected client, whether
  the orchestration skill uses a shared copy, native adapter, or explicit
  unsupported result.
- [x] 5.6 Verify duplicate-free setup, discovery/invocation, native-skill
  preservation, immutable-source policy, and no network installation from
  agent/Git hooks across outer and nested roots.
- [x] 5.7 Add root-aware GitNexus group/contract-link and Graphify projection
  evidence without merging independent source-of-truth indexes.

## 6. Workflow integration, rollback, and documentation

- [x] 6.1 Add quick-profile status that performs no index refresh, memory write,
  network ingestion, or generated-surface mutation.
- [x] 6.2 Add exploration-profile live read-only probes and verify missing tools
  fall back to bounded repository search with explicit missing-evidence output.
- [x] 6.3 Add advisory Prepare-phase GitNexus impact evidence and require manual
  dependency review when the impact probe is unavailable.
- [x] 6.4 Add Verify-phase focused checks, explicit index verification/refresh,
  strict OpenSpec and skill validation, and final source-identity recheck.
- [x] 6.5 Add Handoff output covering completed/skipped phases, evidence
  references, unresolved risks, exact source identity, and readiness state.
- [x] 6.6 Keep Git hooks non-interactive and code-only; add fixtures proving a
  missing knowledge service does not block commit and no network/LLM work runs
  in the Git process.
- [x] 6.7 Implement pointer-only orchestration rollback for owned latest-evidence
  pointers while preserving historical evidence and keeping managed-skill and
  native-tool uninstall workflows separate.
- [x] 6.8 Rehearse rollback twice and verify hashes and contents of memories,
  indexes, Agentmemory hooks, native/generated skills, guidance, credentials,
  application files, and unrelated dirty changes remain preserved.
- [x] 6.9 Update knowledge-graph, agentmemory, agent-skills, and OpenSpec
  runbooks with profiles, status semantics, recovery order, FileProvider
  decision, evidence retention, version boundaries, and rollback.
- [x] 6.10 Document that first-rollout evidence remains repository-local and
  direct `mcp-router` consumption requires a separate nested-repository change.
- [x] 6.11 Reconcile the accepted knowledge-graph ADR, runbooks, orchestration
  skill, and rollback fixtures with the pointer-only orchestration boundary and
  separately reviewed managed-skill/native-tool workflows.

## 7. Execution-readiness acceptance

- [x] 7.1 Run focused health-schema, knowledge-tool, agentmemory, agent-skill,
  instruction-governance, timeout, redaction, and rollback fixture suites.
- [x] 7.2 Run `make agent-skills-verify`, `make validate-agent-guidance`,
  `make openspec-surfaces-verify`, and the repository tooling verification gate
  required by the changed scripts and policies.
- [x] 7.3 Run change-specific and repository-wide
  `openspec validate --strict --all --no-interactive` validation and resolve
  every proposal/spec/design/task coherence failure.
- [x] 7.4 Run quick and exploration health profiles twice to prove stable,
  duplicate-free, bounded results.
- [x] 7.5 Run the implementation profile against the exact final source
  identity and retain a schema-valid `ready` manifest with every required probe
  healthy.
- [x] 7.6 Review the final diff and retained evidence to confirm no service,
  deployment, container, nested-repository implementation, unreviewed package
  upgrade, or unrelated worktree change entered scope.
- [x] 7.7 Add a required machine-readable implementation scope audit that
  classifies change-owned and unrelated dirty paths, rejects prohibited owned
  prefixes, remains read-only, and retains exact-source evidence.
- [x] 7.8 Restore the approved OpenSpec `1.7.0` executable, rerun focused and
  strict verification, and retain a new implementation-profile `ready` manifest
  for the final exact source identity.
