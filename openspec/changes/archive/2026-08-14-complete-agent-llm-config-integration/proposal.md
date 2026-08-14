## Why

The archived LLM-configuration changes synchronized a canonical contract before every required correction was integrated across its participating repositories. A focused corrective change is needed now to establish one atomic, fail-closed configuration and provider-identity contract—and to require current, dependency-bound consumer evidence—before the work can again be considered complete.

## What Changes

- Complete the canonical configuration boundary in `tdt-core` so each resolution request atomically captures agent identity, effective root and environment profile, selected YAML and dotenv identities, non-secret source fingerprints, overlay policy, detached explicit overrides, relevant registered non-secret environment values, and redacted credential-availability/provider-binding state.
- Require compatibility mappings to derive from that same immutable captured snapshot, validate every declared primary and fallback through the canonical typed catalog, and fail without returning a partial mapping, lower-priority substitute, or malformed or unregistered model value.
- Make cache reuse depend on the complete effective non-secret identity of a resolution request, keep secret values out of fingerprints and serializable results, and isolate simultaneous resolutions from changes to files, environment state, mutable override objects, or other concurrent requests.
- **BREAKING**: require one explicit, non-empty canonical provider ID and exactly one matching provider-bound credential metadata relationship at every public protected-credential resolve or reveal boundary. Missing, duplicate, ambiguous, unbound, raw-key-only, mismatched, or cross-provider relationships fail before environment lookup or credential return.
- Complete `agent-core` construction so callers provide either an explicit Pydantic AI `Model` or a model identifier together with one caller-resolved immutable configuration snapshot. Identifier-based construction without that snapshot fails before configuration, provider, credential, fallback, or model discovery; explicit-model construction performs zero configuration-source reads and remains authoritative over conflicting selection fields.
- Require simultaneous `agent-core` constructions to remain isolated to their respective caller-owned snapshots. Any compatibility resolution belongs to a separate operation or composition boundary that resolves once before invoking model construction, never to the constructor receiving an omitted snapshot.
- Complete `agent-docs-sync` so configuration, discovery, validation, generation, diagnostics, normalized results, and reports share one canonical profile and one effective set of timeout and iteration controls. Supported repository-domain runtime overrides remain consistent without modifying the source profile or authorizing repository-owned LLM selection fields.
- Require docs-sync public provenance to use a stable, serializable, redacted mapping; require retries within one operation to reuse the captured configuration; and require resumed work to restore and validate retained non-secret configuration identity or fail before model construction, persistence initialization, approval advancement, or write-capable tool construction. Credential values are never retained in workflow state.
- Complete `agent-harness` production composition by propagating the configured effective model while preserving the containment-before-write behavior required by the existing canonical runner contract.
- Keep requested CLI adapter identity distinct from canonical provider ID: CLI identity controls executable and capability validation, while canonical provider ID controls provider-owned credential metadata. Neither identity may be inferred from protocol, endpoint, model, executable, or credential availability.
- Permit consumer-local CLI fallback only after successful canonical resolution reports genuine absence of an applicable mapping. Unreadable canonical sources and resolution, validation, or projection failures remain failures and cannot be converted to an empty mapping, `None`, local fallback, or process launch.
- Revalidate the final integrated contract with exactly two required independent live consumer rows: one contained `ai-harness-skills` generation row and one `ai-review` reviewer row. Each row must bind the consumer SHA, resolved `tdt-core` SHA and dependency path/lock/origin, relevant dirty-state disposition, CLI and canonical provider identities, source fingerprints, shell/provider prerequisites, nested consumer result, nonce or artifact, and target-preservation result.
- Invalidate retained live evidence after drift in planning artifacts, consumer or dependency identity, product/test/acceptance scripts, canonical configuration sources, launcher behavior, environment loading, shell/provider prerequisites, or credential availability. Process reachability and exit status alone do not establish successful live acceptance.
- Require a store-owned, non-interactive preflight validator to recapture current planning, repository, dependency, source, mechanism, dirty-state, and presence-only prerequisite identities before retained deterministic or live evidence can complete a task, unblock a downstream packet, authorize a live launch, permit spec synchronization, or support archive readiness. Missing, unresolved, indeterminate, or drifted identity fails closed with a machine-readable nonzero result and dependency-ordered downstream invalidation.
- Treat `standardize-agent-llm-environment-resolution-v2` and `integrate-canonical-cli-projections-v1` as immutable historical provenance. This change corrects the resulting contract without recreating, rewriting, synchronizing from, or otherwise modifying either archived predecessor.
- Keep concurrent credential-loading, shell-activation, and native-provider launcher work under its existing external ownership. This change may consume presence-only readiness from that work as a recaptured acceptance prerequisite, but does not absorb, modify, or claim completion of it.

Explicit non-goals:

- Migrating, copying, rotating, comparing, printing, deleting, overwriting, or serializing credential values.
- Retiring the environment-key registry; it remains the authority for legacy aliases and CLI capability metadata while new-schema `auth_env` remains provider-local.
- Normalizing native CLI configuration files or authentication stores into one grammar.
- Giving model constructors ownership of configuration precedence or allowing them to discover a missing caller snapshot.
- Authorizing repository-domain configuration to select docs-sync LLM models, fallbacks, providers, or model behavior.
- Expanding the minimum live-provider matrix beyond the two named consumer rows without a later explicit scope revision.
- Continuous filesystem watching, TTL-based evidence expiration, background monitoring, provider execution, network dependency resolution, or automatic repository/worktree mutation. Validation is an explicit local preflight at acceptance and lifecycle gates.
- Changing `prime-agent`, Claude Code settings, provider-adapter infrastructure, scheduler, skills, memory, hooks, or unrelated domain workflow behavior.
- Absorbing concurrent credential-loading, fresh-shell, provider-launcher, or other native-runtime changes owned by separate work.
- Treating structural OpenSpec validation, task syntax, historical test counts, process exit zero, or an untracked acceptance script as implementation acceptance.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-config-resolution`: require one atomic, immutable resolution snapshot; detached overrides and registered environment capture; secret-safe fingerprints; complete cache identity; concurrent isolation; and canonical fail-closed validation of compatibility primary and fallback selections.
- `agent-core-model-resolution`: require every construction entry point to accept an explicit model or a model identifier plus caller-resolved snapshot, reject missing snapshots before discovery, preserve explicit-model zero-read behavior, and isolate concurrent constructions.
- `agent-docs-sync`: require one effective profile and runtime-control projection across every operation path, stable redacted public provenance, retry snapshot reuse, and fail-closed resume identity validation before persistence, approval advancement, or write-capable construction.
- `cli-provider-profile-resolution`: distinguish CLI adapter identity from canonical provider ID, distinguish genuine mapping absence from canonical-source or projection failure, require exactly two durable dependency-bound live consumer rows, and require an automated credential-safe preflight that rejects artifact, dependency, source, mechanism, prerequisite, or identity drift before evidence reuse or lifecycle advancement.
- `provider-model-profile-resolution`: require an explicit canonical provider ID and exactly one matching provider-bound credential metadata relationship before protected credential lookup, resolution, or reveal.

## Impact

- **Primary implementation ownership**: `tdt-core`, `agent-core`, `agent-docs-sync`, and `agent-harness`, integrated in dependency order with one writer per repository and dedicated, freshly verified worktrees.
- **Dependent verification ownership**: `ai-harness-skills` and `ai-review`, rerun only against the final resolved `tdt-core` dependency identity. Their native authentication, executable validation, and process-launch boundaries remain adapter-owned.
- **External prerequisite ownership**: concurrent credential-loading, shell-activation, and provider-launcher work remains outside this change. Its state is consumed only through credential-safe, presence-only prerequisite checks and must be recaptured before live acceptance.
- **Public APIs and behavior**: canonical resolution input and cache identity, typed and compatibility projections, protected credential resolve/reveal boundaries, agent construction inputs, docs-sync runtime/provenance/retry/resume behavior, harness production composition, and CLI selection and diagnostic projections.
- **Acceptance evidence**: deterministic repository gates, disposable-`TDT_HOME` precedence/security/rollback probes, exact integrated Git identities, resolved dependency provenance, dirty-state disposition, and two credential-safe live consumer records containing distinct reachability, nested-result, artifact, and target-preservation outcomes.
- **Planning and lifecycle**: the shared OpenSpec store retains exactly the five modified capabilities above. Both predecessor archives remain immutable. Synchronization and archival remain blocked until separately authorized implementation is verified against current evidence; OpenSpec planning validity alone is insufficient.
