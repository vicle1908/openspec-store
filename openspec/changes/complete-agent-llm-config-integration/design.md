## Context

See `proposal.md` for the motivation and scope of this corrective change. The correction crosses configuration resolution, compatibility projection, protected credential access, model construction, docs-sync workflow lifecycle, harness production composition, and native-CLI consumer boundaries. The five delta specs in this change are authoritative for the changed behavior; the archived predecessors remain immutable historical provenance.

The authoritative configuration and canonical CLI-selection boundary belongs to `tdt-core`. `agent-core` and `agent-docs-sync` consume caller-resolved configuration snapshots, `agent-harness` consumes the configured effective model through production composition, and `ai-harness-skills` and `ai-review` adapt canonical CLI selections to provider-native process invocations. Native executable capabilities and authentication mechanics remain adapter-owned. No consumer may create an independent precedence chain or infer provider identity merely because it exposes a compatibility API, command-specific configuration object, executable name, model string, endpoint, or protocol.

The participating repositories may contain unrelated product edits, generated Graphify state, index output, test mechanisms, or incomplete candidate work. A branch name, historical test count, structurally valid OpenSpec change, or clean process exit is therefore insufficient proof of integration. Implementation intake must preserve unrelated state, establish one writer per repository, and bind every accepted result to exact committed identities, resolved dependency provenance, and an explicit disposition of all relevant uncommitted product, test, acceptance-script, and generated paths.

OpenSpec resolves this store-hosted change with a repository-local action context whose allowed edit root is `openspec-store`. That boundary is controlling: the shared change coordinates cross-repository planning and evidence, but it does not grant implementation authority in another Git repository. Source changes therefore execute only as separately authorized, one-repository work packets in dedicated worktrees. Repository writers treat the store artifacts as read-only and return credential-safe handoffs; the sole store writer owns the shared task and evidence ledger.

Concurrent credential-loading, shell-activation, provider-launcher, and native-runtime work remains externally owned. This correction neither edits those paths nor claims their completion. It consumes only recaptured, presence-only prerequisite state when live acceptance is authorized. Changes in those external prerequisites invalidate affected evidence rather than being silently absorbed into this change.

The principal transaction boundaries are:

- A configuration-resolution transaction begins when `tdt-core` atomically captures every relevant non-secret input and redacted credential-binding condition for one request. It ends when one immutable typed profile, source identity, and any compatibility projection derived from that same capture are returned or the complete request fails without a partial result.
- A protected-credential transaction begins with an explicit canonical provider ID and a typed or raw-key credential reference. It may access an environment value only after exactly one provider-bound metadata relationship is found and the requested provider, reference, and metadata all agree. The transaction ends at the provider-owned process boundary without making the protected value serializable.
- An agent-construction transaction begins only after its caller supplies either an explicit Pydantic AI `Model` or a model identifier plus one caller-resolved immutable snapshot. Construction never resolves a missing snapshot. A separate operation or composition boundary may resolve once before invoking construction.
- A docs-sync operation begins by capturing one canonical profile, one effective runtime-control projection, and one stable public provenance projection. In-process retries reuse that capture. Resume is a new lifecycle boundary that must restore and validate the retained non-secret operation identity before model construction, persistence, approval advancement, or write-capable construction.
- A native-CLI selection transaction ends in exactly one of three typed states: a valid selection preserving both identities, genuine absence of an applicable mapping after successful canonical resolution, or a canonical source/resolution/projection error that prevents local fallback and process launch.
- A live-acceptance transaction begins only after its exact consumer, dependency, source, launcher, shell, provider, credential-availability, dirty-state, and authorization prerequisites have been captured. It ends with separately recorded reachability, nested consumer outcome, nonce or artifact, and target-preservation evidence.

## Goals / Non-Goals

**Goals:**

- Establish one atomic, immutable, source-identifiable configuration capture as the only canonical model/provider input for a logical operation.
- Ensure compatibility projections derive from the same capture and preserve complete primary/fallback validation, provenance, overlay policy, and source identity.
- Keep protected values out of fingerprints, profiles, compatibility mappings, workflow state, diagnostics, exceptions, reports, and retained evidence.
- Make cache reuse depend on every non-secret input that can change the effective result, including registered environment state and redacted credential availability/provider binding.
- Isolate simultaneous configuration resolutions and model constructions from mutable files, environment changes, override objects, loader identity changes, and other requests.
- Require one explicit canonical provider ID and exactly one matching provider-bound credential metadata relationship at every public protected-credential resolve or reveal boundary.
- Make `agent-core` construction deterministic from caller-owned inputs, reject a model identifier without a snapshot before discovery, and preserve an unconditional zero-read path for an explicit `Model`.
- Give docs-sync one canonical profile, effective runtime-control projection, stable redacted provenance mapping, retry snapshot, and resume identity across its complete operation lifecycle.
- Preserve the existing harness containment-before-write contract while propagating the configured effective model into production services.
- Preserve both requested CLI adapter identity and canonical provider ID across selection, projection, diagnostics, credentials, and evidence.
- Distinguish genuine canonical mapping absence from unreadable sources or invalid canonical intent.
- Produce exactly two required, independently attributable live consumer rows with exact dependency and prerequisite identity.
- Keep planning validation, deterministic implementation verification, live acceptance, spec synchronization, and archive readiness as distinct lifecycle gates.
- Preserve the store edit boundary, predecessor archives, unrelated state, and one-writer-per-repository ownership.

**Non-Goals:**

- Define a new secret store or migrate, copy, rotate, compare, print, delete, overwrite, or serialize credential values.
- Remove the environment-key registry; it continues to own legacy aliases and CLI capability metadata, while new-schema `auth_env` remains provider-local.
- Normalize native CLI configuration files, authentication stores, or provider-specific invocation grammars.
- Give `agent-core`, docs-sync, the harness, or CLI consumers ownership of canonical configuration precedence.
- Allow a constructor to discover configuration because its caller omitted the required snapshot.
- Allow repository-domain docs-sync configuration to select LLM models, fallbacks, providers, or model behavior.
- Introduce a process-global mutable current profile, model, provider, or operation context.
- Expand the minimum live matrix beyond one `ai-harness-skills` row and one `ai-review` row without an explicit later scope revision.
- Integrate unrelated credential-loading, shell, native-runtime, scheduler, adapter, skills, memory, hooks, or domain-workflow work.
- Treat OpenSpec validity, task syntax, candidate tests, process reachability, exit zero, or the presence of an acceptance script as implementation acceptance.
- Expand OpenSpec `actionContext.allowedEditRoots`, treat a personal workset as write authority, or let implementation-repository writers edit the shared store ledger.

## Decisions

### 1. Separate store-owned coordination from repository-local execution

The shared change remains the single cross-repository statement of intent, contract deltas, task plan, and acceptance evidence. Its update/apply workflow may mutate only explicitly authorized artifacts inside `openspec-store`; it must stop before any source-repository mutation unless separate repository-scoped implementation authority is granted.

Implementation executes through one repository-local work packet at a time. Each packet names exactly one Git root, dedicated worktree, sole writer, allowed product and test paths, starting SHA, accepted candidate source, applicable requirement/scenario subset, current repository instructions, required impact analysis, focused and full gates, Graphify update policy, change-scope inspection, commit shape, rollback point, and credential restrictions.

A repository writer treats the store artifacts as read-only and returns a credential-safe handoff containing the committed SHA, dependency identities, complete dirty-state disposition, diff summary, exact commands and exits, pass/skip/fail counts, impact and change-scope evidence, rollback result, and blockers. Only the sole store writer may retain that handoff under the absolute evidence root or mark shared tasks complete.

Alternatives considered:

- Add source-repository paths to store metadata and assume that expands write authority. Rejected because repository-local action context and Git ownership remain controlling.
- Use one store apply session as a writer across every repository. Rejected because it collapses independent Git ownership and makes evidence attribution ambiguous.
- Copy the complete change into each implementation repository. Rejected because duplicated planning artifacts would drift and undermine the store as the single source of truth.
- Let repository writers update `tasks.md` directly. Rejected because concurrent ledger writers would destroy one-writer attribution.

### 2. Establish an immutable planning and evidence identity before implementation

After all revised planning artifacts are individually approved and focused validation passes, the sole store writer may create a planning-baseline commit only through a separately authorized store operation. Before doing so, the writer inventories all store dirt, stages only the corrective change subtree, inspects the cached name and content diff, and proves unrelated active changes, archives, canonical specs, generated files, and untracked paths are excluded.

The full store SHA and corrective-change tree identity become prerequisites for every repository packet and retained evidence row. Later evidence updates, canonical-spec synchronization, and archive movement use separately reviewable lifecycle commits. A full-store failure from unrelated concurrent work remains an explicit external blocker; it is neither repaired through this change nor relabeled as a pass.

Alternatives considered:

- Leave the approved plan uncommitted while collecting implementation evidence. Rejected because evidence would not be bound to an immutable planning identity.
- Stage all current store dirt merely to obtain a clean tree. Rejected because those paths have separate owners and may contain concurrent work.
- Treat a focused change validation as proof that the whole store is ready. Rejected because focused validity and store-wide health answer different questions.

### 3. Assign each capability and existing-contract correction to one implementation owner

Ownership is divided as follows:

| Capability or contract | Primary implementation owner | Required downstream verification |
| --- | --- | --- |
| `agent-config-resolution` | `tdt-core` | `agent-core`, docs-sync, harness, and native-CLI compatibility consumers |
| `provider-model-profile-resolution` | `tdt-core` | every protected-credential caller, export, and example |
| `agent-core-model-resolution` | `agent-core` | SDK, CLI, base-agent, fallback-chain, and runtime helper construction paths |
| `agent-docs-sync` | `agent-docs-sync` | CLI, discovery, validation, generation, retry, resume, diagnostics, normalized result, and report paths |
| `cli-provider-profile-resolution` selection | `tdt-core` | both native-CLI consumer repositories |
| `cli-provider-profile-resolution` harness adapter | `ai-harness-skills` | true contained generation boundary |
| `cli-provider-profile-resolution` review adapter | `ai-review` | true reviewer construction and invocation boundary |
| Existing canonical harness runner contract | `agent-harness` | production composition and containment-before-write |

Each repository compares its product diff only with its owned requirements and explicitly named downstream constraints. The breaking provider-bound credential boundary requires a workspace-wide caller/export/example audit even though its implementation owner is `tdt-core`.

Alternatives considered:

- Ask `tdt-core` to satisfy all five delta specs in its own diff. Rejected because construction, workflow, and native-adapter behavior remains owned by their respective repositories.
- Treat the harness correction as a sixth delta capability. Rejected because effective-model propagation and containment-before-write are already governed by the canonical harness runner contract.
- Give two writers overlapping files in one repository. Rejected because shared ownership would make provenance and rollback unreliable.

### 4. Freeze repository and worktree identities before candidate intake

Before implementation begins in a repository, the integration owner records:

- current main SHA and branch/upstream state;
- candidate SHA or exact diff source and ancestry;
- worktree path and ownership;
- resolved local/editable dependency paths and origins;
- tracked and untracked product paths;
- test and acceptance-script paths;
- generated Graphify or index paths;
- current writer assignment; and
- unexplained or overlapping dirt.

Candidate changes are reviewed and integrated only in a dedicated worktree owned by one writer. Unexpected product paths, missing/prunable worktrees, dependency drift, or overlapping ownership stop intake until disposition is explicit. Historical references do not authorize recreating, pruning, resetting, cleaning, checking out, or otherwise changing worktree state.

Generated graph/index state is inventoried separately from product and test changes but remains preserved. A filtered status or clean source subset is never represented as a clean whole worktree.

Alternatives considered:

- Apply known dirty diffs directly to main worktrees. Rejected because it mixes ownership and obscures provenance.
- Accept a candidate solely because its earlier tests passed. Rejected because code, dependencies, environment, or target main may have changed after capture.
- Remove generated or untracked files before comparing candidates. Rejected because cleanup would destroy evidence or another workflow’s state.

### 5. Represent `tdt-core` resolution as one atomic captured-input transaction

`tdt-core` introduces one internal immutable captured-input representation for each public resolution request. Capture occurs once at the outer resolver boundary and includes:

- canonical agent identity;
- effective `TDT_HOME` or selected root;
- selected environment profile;
- selected global and agent YAML identities;
- selected dotenv and environment-loader identities;
- non-secret content or state fingerprints for relevant sources;
- allowed overlay-key policy;
- a detached immutable copy of explicit source and run overrides;
- the values and presence state of relevant registered non-secret environment inputs;
- redacted protected-credential availability state;
- canonical provider-binding metadata needed to validate the selected route; and
- any other registered non-secret input that can alter parsing, precedence, validation, or projection.

Mutable caller mappings are copied and detached during capture. Files, environment variables, loader state, and mutable override objects are not reread during that request. Unregistered environment changes are outside the resolver’s effective identity and do not alter the returned profile or cache identity.

Source parsing, precedence, typed provider/model validation, fallback validation, model behavior resolution, provenance construction, credential-availability projection, and compatibility projection all operate on the captured representation. A compatibility mapping is therefore a projection of the completed typed result or the same internal capture, never a second loader.

Every declared primary and fallback is parsed with the canonical grammar and resolved against the same provider/model catalog. A malformed, unknown, ambiguous, or mismatched primary or fallback rejects the complete request before any partial mapping, lower-priority substitute, or unchecked value is returned.

Non-secret source fingerprints describe only non-secret source identity and contents. Protected credential values cannot appear in or contribute to a fingerprint. Redacted availability and provider-binding conditions may participate in cache identity as typed booleans or non-secret metadata, but never as secret-derived hashes or values.

Where caching remains, its identity includes every captured field capable of changing the effective result: agent, root, profile, source paths and identities, non-secret fingerprints, environment-loader identity, overlay policy, detached explicit overrides, relevant registered environment state, and redacted credential availability/provider binding. Cache reuse is rejected after any such effective-identity change. Simultaneous requests use their own captures and cannot contaminate one another through mutable process-global state.

The transaction is snapshot-consistent rather than globally locked. If a relevant source changes after capture, the in-flight operation retains its original profile and fingerprints; a subsequent resolution captures and reports the new identity.

Alternatives considered:

- Preserve a parallel compatibility precedence implementation. Rejected because typed and compatibility results could diverge.
- Lazily reread files or environment state for each requested field. Rejected because one operation could combine values from different source states.
- Retain caller-owned mutable override mappings by reference. Rejected because post-call mutation would change an in-flight result.
- Hash protected values to detect credential changes. Rejected because secret-derived fingerprints expand the protected-data surface and violate the contract.
- Hold a filesystem-wide lock for an entire operation. Rejected because immutable capture provides operation isolation without long-lived cross-process locking.
- Use an incomplete cache key and clear it opportunistically. Rejected because correctness must follow effective identity rather than cleanup timing.

### 6. Enforce exact canonical provider binding before protected-value lookup

Every public protected-credential resolve or reveal API requires an explicit, non-empty canonical provider ID. Canonical provider ID is a distinct typed identity from CLI adapter identity, protocol, endpoint, model identifier, executable, and credential availability.

The access sequence is fail closed:

1. Require and normalize the requested canonical provider ID without accessing protected material.
2. Normalize the typed credential reference or raw environment-key reference.
3. Find the provider-bound credential metadata relationship for that reference.
4. Require exactly one matching metadata relationship.
5. Verify that the requested provider, typed reference if present, matched metadata, and selected canonical route agree.
6. Only after all binding checks succeed, perform the environment lookup or protected reveal.
7. Keep the protected value process-local and pass it only to the provider-owned invocation boundary.

A raw environment-key reference cannot bypass provider binding; it must first resolve to exactly one matching provider-owned metadata relationship. Missing, duplicate, ambiguous, unbound, mismatched, or cross-provider relationships fail before environment access. The availability of another provider’s credential never authorizes substitution.

Credential availability may appear only as redacted metadata. Protected values remain excluded from typed profiles, compatibility mappings, cache fingerprints, provenance, diagnostics, exceptions, workflow state, reports, command captures, evidence, and serialization.

The environment-key registry remains authoritative for legacy aliases and CLI capability metadata. New-schema `auth_env` remains attached to its canonical provider and does not become a globally interchangeable credential name.

Alternatives considered:

- Infer provider identity from CLI name, model, endpoint, or protocol. Rejected because compatible aliases and protocols are not a secure credential binding.
- Keep the provider argument optional for compatibility. Rejected because an optional security context recreates the ambiguous reveal path being corrected.
- Look up a raw environment key before binding it. Rejected because value availability must not influence authorization.
- Search all available provider credentials until one works. Rejected because cross-provider substitution violates least authority and makes evidence misleading.
- Include protected values or secret-derived hashes in diagnostics. Rejected because binding can be established using typed non-secret metadata.

### 7. Make `agent-core` construction a configuration-input-only boundary

Every public `agent-core` construction path accepts one of two input forms:

- an already constructed Pydantic AI `Model`; or
- a model identifier plus one caller-resolved immutable configuration snapshot or immutable construction input derived from it.

A model identifier without a caller snapshot is invalid. The construction boundary raises a consistent typed error before reading TDT configuration, dotenv files, process environment, provider credentials, fallback catalogs, model registries, or any other discovery source.

A separate caller-owned operation or composition boundary may resolve configuration once and then invoke construction with the captured snapshot. That operation boundary is not part of the constructor and cannot make an omitted constructor snapshot valid. SDK, CLI, base-agent, fallback-chain, and runtime-helper paths must all preserve this separation.

When the caller supplies an explicit `Model`, the explicit-model branch is selected before inspecting any selection or configuration fields. The instance passes through unchanged and remains authoritative even if other caller fields contain a conflicting model identifier, provider, fallback, or behavior. The explicit-model branch performs zero canonical or legacy configuration-source reads.

For snapshot-based construction, the same snapshot or immutable construction input flows through all nested builders. Nested constructors cannot replace its primary, fallback order, provider route, behavior, provenance, source fingerprints, or credential-binding state. Concurrent constructions retain their own snapshot identity and never use a process-global current profile.

Alternatives considered:

- Allow the constructor to resolve once when no snapshot is supplied. Rejected because the approved contract requires missing-snapshot failure and caller-owned precedence.
- Let each public entry point resolve independently. Rejected because SDK, CLI, base-agent, and runtime helpers could observe different source states.
- Resolve configuration unconditionally and overwrite it later with an explicit model. Rejected because that violates zero-read behavior and can fail or touch credential sources unnecessarily.
- Infer a snapshot from a model identifier alone. Rejected because a string does not carry precedence, provenance, fallback, provider-binding, or source identity.
- Introduce a mutable process-global current profile. Rejected because concurrent operations would interfere and provenance would no longer be caller-owned.

### 8. Give docs-sync one operation context across validation, retry, and resume

Each public docs-sync operation constructs one immutable operation context containing:

- one caller-owned canonical agent profile;
- one `DocsSyncConfig` containing only documented repository-domain configuration;
- one effective runtime-control projection, including timeout and iteration limits;
- one stable, serializable, redacted public provenance mapping;
- one non-secret configuration identity used for retry/resume validation; and
- the operation-specific approval and containment state.

Repository-domain configuration may override only supported docs-sync runtime controls. It cannot select an LLM model, fallback, provider, credential, or model behavior. The override is applied once while creating the operation context; the resulting effective timeout and iteration values are used consistently by discovery, validation, generation, nested execution, diagnostics, normalized results, and reports. The source canonical profile remains immutable.

Public provenance is normalized at the docs-sync boundary into a stable serializable mapping. Internal typed provenance objects may be richer, but they cannot leak implementation-specific object representations or protected values into public results, workflow state, or reports.

Docs-sync uses three lifecycle phases:

1. **Capture and validation:** parse supported repository-domain configuration, reject unknown or legacy sections, validate registered environment types, capture the canonical profile, compute effective runtime controls, normalize public provenance, and validate the complete primary/fallback/provider/credential relationship.
2. **Side-effect-capable execution:** only after phase 1 succeeds may docs-sync construct model chains, initialize persistence, create write-capable tools, advance approval state, or execute the workflow.
3. **Result normalization:** normalize the actual nested workflow result into public status and reports, preserving distinct process reachability, generation completion, provider error, approval state, compliance outcome, usage, runtime controls, model diagnostics, and provenance.

An in-process retry of the same operation reuses the captured operation context. It does not reread files, environment state, mutable overrides, loader identity, or canonical selection sources.

Durable workflow state retains only the non-secret operation identity and the public non-secret runtime/provenance projection required to validate resume. Credential values are never checkpointed. On resume, docs-sync restores the retained identity and recaptures or restores the permitted non-secret configuration inputs according to the workflow contract. It then requires exact identity agreement and valid current provider-binding/availability metadata before constructing a model or side-effect-capable dependency.

If the retained identity is absent, incomplete, cannot be restored, or disagrees with the recaptured effective identity, resume fails closed. It does so before model construction, persistence initialization, approval advancement, or write-capable tool construction. The caller must explicitly start a new operation to accept changed configuration; resume cannot silently adopt it.

Nested workflow reports are derived from the actual nested result. Missing nested data is not replaced with apparently successful zero-valued defaults. Exit status follows the normalized execution and compliance contract, not process completion alone.

Alternatives considered:

- Recompute configuration separately in discovery, validation, generation, and reporting. Rejected because one operation could present contradictory effective settings.
- Let retries reread current configuration. Rejected because a retry would no longer represent the same operation.
- Let resume silently accept current configuration after drift. Rejected because approval and write authority would transfer to an unreviewed operation identity.
- Persist credential values to make resume self-contained. Rejected because protected material must remain process-local and non-serializable.
- Build persistence and write-capable tools while validation continues lazily. Rejected because invalid configuration could cause observable side effects before failure.
- Allow repository-local LLM overrides for convenience. Rejected because they would create a competing precedence source.
- Normalize only the outer workflow result. Rejected because nested provider or generation failure could be hidden.

### 9. Keep the harness correction within the existing canonical runner design

`agent-harness` production composition passes the already resolved effective `config.model` into services that construct or invoke the agent. It does not add a harness-specific LLM precedence path or perform an independent canonical resolution.

Existing containment validation remains ordered before artifact-directory creation or any other write effect. Correcting model propagation cannot make an invalid target writable or move write-capable construction before containment checks.

This behavior remains governed by the existing canonical harness runner contract, so the change does not introduce a sixth delta capability. Verification nevertheless exercises the actual production composition path and the containment-before-write boundary, not only a configuration-object unit test.

Alternatives considered:

- Add a harness-only model setting. Rejected because it would duplicate the canonical model source.
- Make the harness resolve omitted configuration during production service construction. Rejected because construction remains caller-owned and input-only.
- Broaden this correction into a harness lifecycle redesign. Rejected because the owned gap is limited to effective-model propagation and preservation of containment.

### 10. Preserve CLI adapter identity and canonical provider ID as separate fields

Canonical selection and provider-native invocation use two explicit identities:

- `cli_adapter_id` identifies the requested CLI implementation and controls executable discovery, supported capabilities, argument filtering, and provider-native invocation behavior.
- `provider_id` identifies the canonical provider selected by the model catalog and controls provider-owned credential metadata and protected-credential authorization.

The selector and every provider-neutral projection preserve both fields. Neither field is inferred from protocol, endpoint, model, executable path, credential availability, or the other identity.

`tdt-core` returns one of three typed selection outcomes:

1. **Selected:** canonical resolution succeeded and produced one valid provider/model relationship. The result contains both identities, canonical alias, wire model, supported behavior fields, redacted source/provenance information, and provider-bound credential metadata.
2. **Mapping absent:** canonical resolution succeeded, the catalog is valid, and no provider declaration or default mapping targets the requested CLI identity, or the profile is valid and legacy-only. Only this state permits the consumer’s documented local fallback.
3. **Canonical error:** a source is unreadable, parsing or resolution fails, or canonical intent for that CLI exists but is missing, undefined, ambiguous, mismatched, unsupported, or otherwise invalid. This state prevents local fallback and process launch.

Unreadable canonical files and resolver/projection exceptions are never caught and converted into `{}`, `None`, mapping absence, or local fallback.

`ai-harness-skills` and `ai-review` translate only a `Selected` outcome into provider-native arguments. They validate executables and capabilities with `cli_adapter_id`, request protected credential material with `provider_id`, keep native authentication inside the adapter boundary, and never pass one provider another provider’s model or credential metadata.

Both consumers are integrated or revalidated only after the final accepted `tdt-core` identity is resolved in their actual environment. Importability alone is insufficient; dependency path, lock/editable declaration, import origin, and full dependency SHA must agree.

Alternatives considered:

- Use one generic provider string for both identities. Rejected because executable capability and credential ownership are different authorities.
- Infer canonical provider from the CLI executable. Rejected because one CLI may route multiple providers and names are not security bindings.
- Represent every selection failure as `None`. Rejected because consumers would mask corrupt canonical intent with local fallback.
- Treat an unreadable canonical source as an empty catalog. Rejected because an I/O or parse failure is not genuine mapping absence.
- Centralize every provider’s native command grammar in `tdt-core`. Rejected because provider-native capabilities and authentication remain adapter-owned.
- Reuse one generic argument set across CLIs. Rejected because supported native flags differ.

### 11. Bind deterministic and live evidence to complete effective identity

All retained evidence lives under:

`/Users/androidteam/Developer/openspec-store/openspec/changes/complete-agent-llm-config-integration/evidence/`

Only the sole store writer writes to that ledger from accepted repository handoffs. Relative evidence paths are not used across implementation worktrees.

Deterministic evidence records:

- planning store SHA and corrective-change tree identity;
- repository and worktree identity;
- exact consumer and upstream dependency SHAs;
- resolved dependency path, declaration or lock state, import origin, and full SHA;
- product, test, acceptance-script, and generated dirty-state disposition;
- exact command, working directory, exit code, and pass/skip/fail counts;
- disposable cache and `TDT_HOME` identity;
- prerequisite and environment-loader identity;
- rollback result; and
- any blocker or stale condition.

Live acceptance uses one durable matrix with exactly two required independent rows:

- one `ai-harness-skills` contained generation row; and
- one `ai-review` reviewer row.

Each row records:

- planning store SHA and change-tree identity;
- consumer repository, full SHA, worktree, and dirty disposition;
- resolved `tdt-core` dependency path, declaration/lock state, import origin, and full SHA;
- relevant product, test, launcher, and acceptance-script identities;
- requested CLI adapter identity and canonical provider ID;
- canonical source identities and non-secret fingerprints;
- environment-loader identity;
- presence-only credential availability and provider-binding state;
- shell, executable, provider, network, containment, and authorization prerequisites;
- one contained operation and redacted command shape;
- expected nonce or artifact and result-record path;
- process reachability and process exit;
- actual nested consumer result or report status;
- nonce/artifact observation;
- target-preservation result;
- duration; and
- row status: `unauthorized`, `blocked`, `failed`, `passed`, or `stale`.

Process reachability, model construction, and exit zero are recorded separately from nested success. A row passes only when the contained operation completes successfully, the nested consumer result confirms success, the expected nonce or artifact exists, and the target-preservation assertion succeeds. A reusable script is a mechanism, not evidence; its retained exact-identity result record is the evidence.

Missing live authorization or an unavailable required provider leaves the row `blocked`, never skipped or passed. A provider error, incomplete nested result, missing artifact, or containment failure leaves it `failed`. Final live acceptance requires both required rows to be independently `passed`. Other supported providers remain covered by deterministic tests unless a later explicit scope revision expands the live matrix.

Evidence becomes stale after drift in any of the following:

- proposal, delta spec, design, task, or evidence-schema identity;
- consumer SHA or relevant uncommitted product/test/script state;
- resolved dependency path, declaration, lock, origin, or SHA;
- canonical source identity or non-secret fingerprint;
- environment-loader behavior or registered effective environment state;
- CLI launcher or provider-adapter behavior;
- shell, executable, provider, network, or containment prerequisites;
- credential availability or provider-binding metadata; or
- any rollback or upstream integration change.

Only affected evidence is recaptured, but dependency-ordered invalidation propagates downstream. Historical results are never relabeled as current merely because the same command would probably pass.

Alternatives considered:

- Store only an aggregate green result. Rejected because it cannot establish which identity, dependency, command, or nested result was tested.
- Record only consumer SHA and omit the actual imported dependency. Rejected because editable dependencies can resolve to a different checkout than intended.
- Treat process reachability as end-to-end acceptance. Rejected because a reachable provider can still return a failed nested result or no artifact.
- Ignore test or acceptance-script dirt. Rejected because a changed mechanism can alter what was proved.
- Embed credential values to prove account identity. Rejected because authorization and availability are proven with redacted provider-bound metadata.
- Keep one combined row for both consumers. Rejected because independent consumer behavior, dependencies, artifacts, and prerequisites must remain attributable.

### 12. Integrate in dependency order and keep lifecycle gates separate

Integration proceeds in dependency order:

1. `tdt-core`;
2. `agent-core`;
3. `agent-docs-sync`;
4. `agent-harness`;
5. deterministic cross-repository verification;
6. `ai-harness-skills`;
7. `ai-review`;
8. exactly two authorized live consumer rows;
9. scenario-by-scenario implementation verification;
10. synchronization of the five authoritative delta specs; and
11. archive readiness review.

The native-CLI consumers are corrected or revalidated only against the final accepted `tdt-core` dependency identity. A failed or superseded upstream gate invalidates downstream evidence.

OpenSpec lifecycle gates remain distinct:

- focused strict validation proves this change is structurally valid;
- full-store strict validation proves current store-wide health or identifies external blockers;
- implementation verification proves current source behavior against all scenarios;
- live acceptance proves the two authorized true consumer operations;
- spec synchronization updates only the five paths reported by `artifactPaths.specs.existingOutputPaths`; and
- archive readiness requires post-sync validation, current identities, complete tasks, and non-stale evidence.

Neither predecessor archive is edited, recreated, synchronized from, or used as a mutable implementation source.

Alternatives considered:

- Validate all consumers concurrently against provisional `tdt-core` branches for final acceptance. Rejected because results would not be bound to the final dependency identity.
- Synchronize specs immediately after planning validation. Rejected because that would repeat the lifecycle error this change corrects.
- Infer synchronization targets from proposal, design, or tasks. Rejected because the authoritative inputs are the concrete delta paths reported by OpenSpec.
- Archive when all task syntax parses as complete. Rejected because task state and parser readiness do not prove implementation or live behavior.

## Risks / Trade-offs

- [Repository identity drifts during multi-repository acceptance] → Freeze exact SHAs, dependency origin, and dirty-state disposition at each gate; stop and recapture affected evidence after drift.
- [The store apply action is used as implementation authority] → Treat `allowedEditRoots` as controlling and require separately authorized one-repository packets.
- [The planning set changes without an immutable baseline] → Create a separately authorized, corrective-subtree-only planning commit before implementation evidence is accepted.
- [Concurrent store work fails full-store validation] → Attribute the failure to its owning change, preserve it untouched, and retain an external store blocker rather than converting the gate into a pass.
- [Several writers update the task or evidence ledger] → Keep one `openspec-store` writer; repository writers return handoffs only.
- [A relative evidence path writes into the wrong worktree] → Use the one absolute evidence root and reject misplaced ledger output.
- [External credential/shell/provider work changes live prerequisites] → Keep its paths externally owned and mark affected rows stale after prerequisite drift.
- [A candidate contains incomplete, composite, or unrelated work] → Review ancestry and path-level diff in a dedicated worktree and integrate only owned corrections.
- [Generated graph or index state obscures product dirt] → Inventory generated paths separately and preserve them; do not infer whole-tree cleanliness from filtered status.
- [A mutable override or environment change contaminates an in-flight resolution] → Detach overrides, capture registered environment inputs once, and prohibit rereads within the transaction.
- [Protected values leak through fingerprints or cache identity] → Fingerprint only non-secret inputs and represent credential availability/provider binding with redacted typed metadata.
- [An incomplete cache key reuses the wrong profile] → Include the complete effective non-secret identity and reject reuse after any relevant change.
- [A compatibility mapping reintroduces a second resolver] → Derive it from the typed capture and test parity, invalid primary/fallback, explicit path, source mutation, and concurrent isolation.
- [The mandatory provider ID breaks unknown callers] → Audit direct and transitive callers, exports, and examples before integration and migrate each explicitly.
- [A raw environment key bypasses binding] → Resolve exactly one provider-owned metadata relationship before environment lookup.
- [Agent construction silently resolves an omitted snapshot] → Use a discriminated input boundary and fail before every discovery surface.
- [An explicit `Model` still triggers configuration reads] → Select that branch first and prove zero reads with static and runtime conformance tests.
- [Concurrent model construction uses mutable global state] → Pass immutable caller snapshots explicitly and prohibit a process-global current profile.
- [Docs-sync runtime controls diverge across nested paths] → Materialize one effective operation projection and pass it through discovery, validation, generation, reports, retry, and resume.
- [Docs-sync retry or resume adopts changed configuration] → Reuse the in-process capture for retry and require exact retained identity restoration on resume.
- [Invalid resume advances approval or creates side effects] → Validate restored identity before model, persistence, approval, or write-capable construction.
- [Typed provenance leaks unstable object representations] → Normalize one stable serializable redacted mapping at the public boundary.
- [CLI adapter and canonical provider identities collapse] → Preserve both typed fields and use each only for its owning capability or credential decision.
- [Unreadable canonical sources become local fallback] → Return a typed canonical error and prohibit catch-all conversion to absence.
- [A stale editable dependency is accepted] → Record declaration, path, origin, and full imported SHA for every consumer result.
- [A static diagnostic or process exit is mistaken for live success] → Require nested result inspection, nonce/artifact, and target-preservation evidence.
- [An acceptance script is treated as durable evidence] → Retain exact-identity result records separately and include script dirt in invalidation.
- [The live provider set remains implicit] → Materialize exactly two named rows before execution and block acceptance until both pass.
- [Toolchain, cache, network, or authorization failures are conflated with source failure] → Record prerequisites and exact exits separately without converting blocked or failed states into passes.
- [The change is synchronized or archived before implementation truth is established] → Keep validation, implementation, live, sync, and archive gates ordered and distinct.
- [Snapshot consistency hides a just-written source update from an in-flight operation] → Treat that as deliberate isolation; a new operation captures the new identity.
- [Single-writer, dependency-ordered integration takes longer] → Accept serialization at write and final-acceptance boundaries while permitting non-overlapping read-only research and test triage.

## Migration Plan

### Phase 0: Finish and validate the store-owned planning baseline

Individually approve and revise the proposal, five existing delta specs, design, and tasks. Run focused strict validation, full-store strict validation, parsed-delta inspection, task-count inspection, proposal/design/task whitespace checks, and `git diff --check`. Attribute unrelated full-store failures to their owning paths and do not edit those paths through this correction.

After separate authorization, the sole store writer inventories all store dirt, stages only this corrective change subtree, inspects the cached name and content diff, and creates the planning-baseline commit. Every repository packet records the resulting full store SHA and corrective-change tree identity.

### Phase 1: Freeze identities, ownership, dependencies, and authority

Capture current main and candidate identities, ancestry, worktree paths, branch/upstream state, product/test/generated dirt, dependency declarations and actual origins, and writer assignment for all six repositories. Confirm predecessor archives and unrelated store paths remain immutable and out of scope.

Create one repository packet per Git root with its owned scenarios and required policy gates. Stop when repository-scoped implementation authority is absent, worktree provenance is unresolved, ownership overlaps, dependencies resolve unexpectedly, or unexplained product paths exist.

### Phase 2: Integrate the canonical `tdt-core` correction

Through a separately authorized `tdt-core` packet:

- implement atomic captured resolution inputs;
- detach explicit overrides and capture registered environment state;
- make fingerprints secret-safe;
- complete cache identity and concurrency isolation;
- derive compatibility mappings from the same typed capture;
- validate all primary and fallback selections fail closed;
- preserve CLI and canonical provider identities separately;
- implement typed selected/absent/error CLI outcomes; and
- require exact provider-bound credential metadata before protected lookup.

Run current impact analysis before edits, audit every protected-credential caller/export/example, pause on repository-defined high-risk findings, run focused and full deterministic gates with isolated caches and a disposable non-secret `TDT_HOME`, refresh Graphify as required, inspect the complete diff, and run the repository change-scope gate before commit.

The accepted integrated `tdt-core` SHA becomes the only dependency identity eligible for downstream acceptance.

### Phase 3: Update direct Python consumers in dependency order

Execute three separately authorized repository packets:

- Update `agent-core` so constructors require an explicit `Model` or identifier-plus-snapshot, reject missing snapshots before discovery, preserve explicit-model zero-read behavior, and isolate concurrent construction.
- Update `agent-docs-sync` so one operation context carries canonical profile, runtime controls, public provenance, retry capture, and resume identity through every path, with invalid resume/configuration blocked before model, persistence, approval, or write-capable construction.
- Update `agent-harness` production composition to propagate the effective model while retaining containment-before-write.

Each packet resolves the accepted `tdt-core` identity, runs current impact analysis and repository-specific deterministic gates, updates Graphify as required, inspects all product/test/generated dirt, runs the repository change-scope gate, creates its own integration commit, and returns a credential-safe handoff.

### Phase 4: Run deterministic cross-repository verification

At exact accepted identities, run:

- focused contract tests;
- full repository test suites;
- required lint and type gates;
- static source-conformance checks;
- explicit-model zero-read probes;
- missing-snapshot pre-discovery probes;
- configuration capture/cache/concurrency probes;
- provider-binding security probes;
- docs-sync runtime/provenance/retry/resume/side-effect probes;
- harness production composition and containment probes;
- canonical absence versus canonical error probes;
- resolved-dependency identity checks; and
- commit-based rollback rehearsals.

Use isolated caches and disposable configuration roots where appropriate. Retain exact commands, working directories, exits, counts, prerequisites, and dirty dispositions.

### Phase 5: Correct or revalidate native CLI consumers

With the accepted `tdt-core` dependency actually resolved:

- execute a separately authorized `ai-harness-skills` packet at its true contained-generation adapter boundary; and
- execute a separately authorized `ai-review` packet at its true reviewer construction and invocation boundary.

Verify preservation of both identities, valid canonical projection, genuine-absence local fallback, canonical-source/error fail-closed behavior, provider-specific capability and argument handling, and provider-bound authentication ownership.

Record dependency declaration/lock, path, import origin, full `tdt-core` SHA, consumer SHA, product/test/script dirt, focused and full gate results, and rollback point. Any source or mechanism correction invalidates earlier evidence.

### Phase 6: Capture durable two-row live acceptance

Only after explicit live-provider authorization, materialize exactly:

- one `ai-harness-skills` contained generation row; and
- one `ai-review` reviewer row.

Perform presence-only prerequisite checks without exposing credentials. Bind each row to the current planning identity, consumer SHA, actual resolved `tdt-core` origin and SHA, dirty disposition, both provider identities, canonical source fingerprints, loader identity, launcher/script identity, shell/provider prerequisites, and credential-availability/provider-binding metadata.

Execute each row independently in an approved contained target. Record reachability, process exit, nested result, expected nonce or artifact, target preservation, duration, and redacted command shape. Mark unauthorized or unavailable rows `blocked`, unsuccessful rows `failed`, and drifted rows `stale`. Both rows must be `passed` before live acceptance is complete.

### Phase 7: Verify all 74 delta scenarios and the existing harness contract

Compare accepted source and current evidence with every scenario in:

- `agent-config-resolution`;
- `provider-model-profile-resolution`;
- `agent-core-model-resolution`;
- `agent-docs-sync`; and
- `cli-provider-profile-resolution`.

Separately verify the existing harness runner contract without introducing a sixth delta. A scenario supported only by historical counts, an uncommitted candidate, stale dependency resolution, task syntax, or structural OpenSpec validity remains failed or blocked.

Reconcile every checked task with its exact committed handoff, dependency identity, dirty inventory, commands, rollback result, and integration state.

### Phase 8: Synchronize and prepare archive readiness

Resolve synchronization inputs only from the five current `artifactPaths.specs.existingOutputPaths`. After implementation and both live rows are verified, use the normal spec-sync workflow as the sole store writer. Inspect the canonical spec diff for exact intended requirements and scenarios, unrelated paths, duplication, protected values, and predecessor archive changes.

Run focused and full-store strict validation after synchronization. Commit synchronization and evidence separately from the planning baseline through the reviewed store workflow.

Produce an archive-readiness handoff containing final store and repository SHAs, resolved dependency identities, dirty dispositions, rollback results, live row outcomes, validation totals, and external blockers. Do not archive until a later explicitly authorized archive workflow confirms that all identities and prerequisites remain current.

### Rollback

Each implementation repository records its pre-integration SHA and uses a normal repository-local revert or inverse integration commit in a dedicated worktree. Rollback never uses destructive reset, clean, checkout, or unrelated-state mutation.

An upstream rollback immediately invalidates downstream deterministic and live evidence. Downstream progression stops until dependencies are restored or affected gates are recaptured against the rolled-back identity.

Rollback does not migrate, copy, print, compare, rotate, delete, overwrite, or serialize credentials or alter the caller’s canonical `TDT_HOME`. Disposable verification roots are removed only as test fixtures after their non-secret contents and result records are accounted for.

If docs-sync configuration identity changes, an in-flight durable operation does not resume under the new identity; it fails closed and requires an explicitly initiated new operation. If canonical specs were already synchronized, lifecycle state must be reconciled through a reviewed corrective sync or revert rather than rewriting predecessor archives or concealing the code rollback.

OpenSpec synchronization or archive is never used to hide a failed implementation rollback. Canonical specs, active-change state, accepted repository identities, and retained evidence must continue to describe the implementation that is actually integrated.
