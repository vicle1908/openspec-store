# Design: TDT_HOME Source Conformance Governance

## Context

The provider-foundation change establishes `tdt-core` as the owner of call-time `TDT_HOME` resolution, bounded path helpers, packaged contract data, and redacted diagnostics. It deliberately does not claim facts about downstream source trees or deployments. The next boundary is therefore governance: every participating repository must declare its identity and ownership, and a reproducible audit must distinguish provider-compliant source from explicitly approved legacy construction.

The ecosystem currently contains 15 consumer repositories. Their source layouts, launch mechanisms, deployment owners, and remaining legacy `~/.tdt` sites are repository-owned facts. Encoding those facts only in a central `tdt-core` registry would make the provider guess about downstream state; leaving them undocumented would make cross-repository readiness unverifiable. This change joins the two views without collapsing their ownership boundaries:

- the packaged `tdt-core` participant registry identifies the expected consumer set and contract version;
- each consumer repository supplies a versioned `.tdt/governance-manifest.json` at its root;
- the `tdt-core` CLI validates manifests and performs parser-based source audits;
- exact legacy sites may be accepted only through repository-owned, time-bounded exception records; and
- aggregate readiness is computed from evidence tied to specific repository revisions.

This is a control-plane change. It records and audits source/deployment facts but does not modify live `TDT_HOME` data or deploy a new provider artifact to consumers.

## Goals / Non-Goals

### Goals

- Add a schema-valid `.tdt/governance-manifest.json` to each of the 15 registered consumer repositories.
- Bind every manifest to one unique participant identity in the packaged `tdt-core` registry so omissions, duplicates, and unregistered consumers fail visibly.
- Record stable repository ownership and, where applicable, deployment owner, launch mechanism, deployment-definition paths, and reader/writer principal identifiers without storing credentials or machine-local secrets.
- Add `tdt-core` CLI tooling that audits source using syntax trees rather than substring matching and reports stable rule IDs, source locations, and machine-readable evidence.
- Detect direct and equivalent constructions of the legacy home path, including aliased imports and common `pathlib`, `os.path`, expansion, join, and concatenation forms.
- Treat parse failures, unsupported executable source, incomplete audit scope, and unknown ownership as non-conforming rather than silently clean.
- Permit an existing legacy source site only when an exact, approved, repository-owned exception is present, unexpired, and bound to the finding it suppresses.
- Produce per-repository and ecosystem-level results that distinguish clean conformance, approved legacy debt, and failure.
- Make audit evidence reproducible by binding it to the provider/rules version, manifest digest, repository revision, and scanned-file inventory.

### Non-Goals

- Rewriting consumer path usage to provider helpers. Those edits belong to provider-gated adoption changes owned by each consumer repository.
- Changing consumer dependency floors, package metadata, application configuration schemas, or launch definitions merely to make an audit pass.
- Releasing or deploying `tdt-core`, restarting services, changing launchd/Compose configuration, or performing provider-first rollout.
- Reading, repairing, migrating, or otherwise mutating the live `~/.tdt` tree.
- Implementing migration plans, journals, recovery, rollback execution, or operator cutover.
- Treating a manifest declaration as proof of current live process state or filesystem access. Live attestations belong to the synthetic migration and rollout changes.
- Using broad path, directory, repository, or rule wildcards to waive legacy findings.
- Using grep success, absence of a literal string, or an unparsed file as verified source conformance.
- Automatically approving exceptions or allowing the `tdt-core` repository to invent consumer ownership facts.

## Decisions

### Decision 1: Join a central participant registry with repository-owned manifests

The installed `tdt-core` package remains the authority for the expected participant IDs, supported manifest schema versions, audit-rule bundle, and repository-role invariants. Each consumer repository remains the authority for its own source roots, repository owner, deployment classification, deployment owners, and legacy exceptions.

A manifest is accepted only when all of the following hold:

- it is located exactly at `.tdt/governance-manifest.json` relative to the repository root;
- its schema version and contract identity are supported by the installed audit tool;
- its repository ID matches exactly one participant in the packaged registry;
- its declared role and required source surfaces satisfy that participant's registry constraints;
- ownership and deployment fields required for that role are complete; and
- all paths are normalized repository-relative paths that cannot escape the checkout.

The logical manifest sections are:

- **contract identity** — schema version and audit-contract version;
- **repository identity** — participant ID, role, and stable owning team/service identifier;
- **audit scope** — production source roots and declarative deployment-definition paths;
- **deployment ownership** — either an explicit non-deployable/library classification or one or more named deployments with owner and launch facts; and
- **exceptions** — zero or more exact legacy-site records.

The JSON schema is packaged with `tdt-core` and validated before semantic checks run. Arbitrary source exclusions are not permitted. Generated, vendored, cache, and fixture exclusions come from the versioned central rule bundle; a repository cannot obtain a green result by declaring its production directory excluded.

**Alternative rejected:** maintain all 15 consumer facts in one provider-owned file. That would turn stale provider guesses into apparent downstream truth and require a provider release for routine ownership changes.

**Alternative rejected:** let every repository define its own rules. That would make cross-repository results incomparable and allow a consumer to weaken the audit locally.

### Decision 2: Use a parser-adapter audit engine with AST semantics

The CLI exposes the repository audit command as `tdt config source-audit <workspace-root>` under the provider's configuration/governance surface. The command accepts an explicit workspace root; it does not infer sibling checkouts or depend on the operator's current directory layout. The companion `tdt config create-manifest` command emits a value-free `.tdt/governance-manifest.json` scaffold to stdout by default, or to an explicitly requested path that does not already exist. It never writes a consumer repository implicitly and fails closed when the requested output path exists.

Python source is parsed with the standard-library AST. The Python adapter normalizes imports, aliases, calls, attributes, binary joins, f-strings, and simple local constant propagation sufficiently to recognize legacy path construction rather than just literal occurrence. Rules operate on normalized semantic forms and emit stable rule IDs. Initial rule families cover at least:

- `Path.home()` or equivalent home discovery followed by `.tdt` joining;
- `Path("~/.tdt")`, `expanduser("~/.tdt")`, and equivalent constructors;
- `os.path.join`/`joinpath`/`/`-operator construction of a home-relative `.tdt` path;
- direct absolute or user-home-derived legacy paths;
- local wrappers that re-create root/path behavior instead of calling the governed provider; and
- import-time snapshots of `TDT_HOME` or the default root where call-time provider resolution is required.

String mentions in documentation, comments, or test data are not findings merely because they contain `~/.tdt`; the expression must match a governed semantic rule. Conversely, a Python parse error or a suspicious expression the adapter cannot classify is reported as an audit error or unresolved finding, never as clean.

The audit core supports language/parser adapters. Declarative JSON, YAML, and TOML deployment files are inspected with their native parsers. Executable non-Python source cannot receive verified-green status from regex matching; it requires a structure-aware adapter or an explicit central declaration that the surface is not part of the participant's executable scope. An exception cannot waive an entire language or source root.

**Alternative rejected:** recursive grep for `~/.tdt`. It produces false positives in docs/tests and misses aliasing, concatenation, expansion, and wrapper functions.

**Alternative rejected:** importing consumer modules to observe values. Imports can execute code, require credentials or services, and still cannot establish source-wide absence.

### Decision 3: Make audit output stable, bounded, and reproducible

Each repository audit captures a single evidence envelope containing:

- repository participant ID and resolved repository root;
- repository revision and dirty-tree state;
- manifest digest and audit-scope digest;
- installed `tdt-core` version, registry identity, schema version, and rule-bundle digest;
- the sorted inventory/digest of scanned files;
- findings with rule ID, repository-relative path, symbol or structural location, and normalized finding fingerprint;
- exception disposition for each matched finding; and
- final status and exit classification.

Text output is optimized for developers, while JSON is the canonical interchange form for CI and aggregation. Absolute home paths, environment values, credentials, file contents unrelated to the finding, and live runtime data are omitted. Results are deterministic for the same checkout, manifest, and tool/rule versions.

A dirty tree is visible in the result. CI acceptance requires an immutable commit checkout; local dirty-tree runs are diagnostic only and cannot be promoted as ecosystem readiness evidence.

Statuses are:

- `PASS` — all in-scope source is parsed and no legacy finding exists;
- `PASS_WITH_EXCEPTIONS` — all in-scope source is parsed and every legacy finding is covered by a valid exact exception;
- `FAIL` — any unsuppressed finding, expired/invalid exception, scope gap, parse error, unsupported executable surface, identity mismatch, or ownership error exists.

`PASS_WITH_EXCEPTIONS` is intentionally not renamed to `PASS`: approved debt must stay visible until removed.

### Decision 4: Exceptions are exact, expiring policy records—not ignore patterns

Exceptions live in the owning repository's governance manifest so the debt changes in the same review and revision as the affected source. Each exception contains at least:

- a unique exception ID;
- audit rule ID;
- repository-relative source path;
- enclosing symbol or structural identity;
- normalized finding fingerprint;
- accountable owner;
- rationale and migration/blocker description;
- tracking issue/reference;
- approval authority and immutable approval reference;
- approval date; and
- expiry date.

An exception suppresses exactly one matching finding. Path globs, directory-wide exclusions, wildcard rule IDs, missing expiries, unknown owners, and fingerprints that no longer match fail validation. A source edit that changes the normalized legacy expression invalidates the old exception and requires fresh review. File line numbers are display evidence only because they are too unstable to define identity.

The central rule bundle defines maximum expiry and permitted approval-authority classes. Repository review policy supplies the human approval; the offline CLI validates the recorded fields and matching fingerprint but does not pretend it can reconstruct or authenticate a remote code-review event. CI must retain the immutable review reference with the result.

Exceptions authorize temporary source debt only. They do not prove provider use, live deployment safety, filesystem access, or migration readiness.

**Alternative rejected:** `# noqa`-style inline suppression. Inline comments are easy to copy, hard to inventory across repositories, and do not carry ownership, approval, or expiry.

### Decision 5: Deployment ownership is declared separately from source conformance

Every manifest declares one of two deployment classifications:

1. **non-deployable/library** — includes the repository owner and a reason that no deployment writer exists; or
2. **deployable** — contains one or more stable deployment IDs, each with an accountable owner, launch mechanism class, repository-relative definition paths, and declared reader/writer principal identifiers.

Principal identifiers are stable logical names, not passwords, tokens, local numeric UIDs, or secret environment values. A missing owner or an unexplained deployment definition is a manifest failure. A source-clean repository with incomplete deployment ownership therefore cannot be ecosystem-ready.

This declaration proves that the repository recorded an accountable owner at a particular revision. It does not prove which process is currently running, which artifact is deployed, or which principal can access live data. Those stronger claims require typed external attestations in successor changes.

### Decision 6: Ecosystem readiness is an all-participant aggregation

The CLI can validate one repository independently and can aggregate previously produced JSON envelopes against the packaged participant registry. Aggregation requires exactly one current envelope for each of the 15 expected participant IDs. Missing, duplicate, wrong-contract, stale-schema, dirty-tree, or mismatched-revision envelopes fail the aggregate.

The aggregate reports counts and identities for `PASS`, `PASS_WITH_EXCEPTIONS`, and `FAIL`, plus ownership and exception-expiry summaries. It never upgrades partial evidence to ecosystem readiness. Per-repository CI remains owned by each consumer; cross-repository orchestration may collect those immutable artifacts, but `tdt-core` does not discover arbitrary sibling directories or clone repositories.

The aggregate is eligible for downstream adoption planning only when all 15 repositories are either `PASS` or `PASS_WITH_EXCEPTIONS`, all manifests have complete ownership, and every exception is valid under the same rule bundle. Adoption and rollout changes may impose the stronger requirement that selected consumers reach `PASS` before deployment.

### Decision 7: Governance tooling is read-only with respect to consumers and runtime data

Manifest validation and source audit read repository files and write only explicitly requested report artifacts or standard output. They do not rewrite source, generate exceptions, modify manifests, inspect `~/.tdt`, contact live services, or verify credentials. Suggested remediation may name the governed provider helper or rule documentation, but applying that remediation remains a repository-owned change.

This preserves the transaction boundary between evidence production and implementation and makes the tooling safe to run in consumer CI without deployment access.

## Transaction Boundaries

The implementation and tests must preserve the following boundaries:

1. **Manifest load:** locate the exact root manifest, parse complete JSON, validate the packaged schema, then run registry and path semantics. No partially parsed manifest is published as usable evidence.
2. **Repository audit snapshot:** validate identity and scope, inventory tracked/in-scope files, parse all required files, evaluate all rules, then match exceptions. The final status is published only after the complete scope is evaluated; one parser or scope failure makes the result fail.
3. **Exception authorization:** normalize a finding, bind it to rule/path/symbol/fingerprint, validate owner/approval/expiry, and classify it. A near match never mutates or suppresses the original finding.
4. **Deployment declaration validation:** classify the repository as non-deployable or deployable, validate all required owners/principals/definition paths, and publish the ownership section as a whole. Partial deployment records are invalid rather than omitted.
5. **Evidence serialization:** construct the redacted deterministic envelope, calculate its digests, and write it atomically when an output file is requested. An interrupted write must not leave a report that appears complete.
6. **Ecosystem aggregation:** load the expected registry snapshot, verify all envelope identities/versions/revisions, then compute one aggregate result. Results from different rule bundles or incomplete participant sets are not merged into a readiness claim.
7. **Repository change transaction:** the manifest, any approved exception, and its corresponding review evidence land in the consumer repository together. Source remediation and exception removal land together so stale suppressions cannot remain after the finding disappears.

There is no transaction against a live deployment or `TDT_HOME` filesystem in this change.

## Evidence Classification

Evidence is classified by what it can actually prove:

| Classification | Meaning | Sufficient for |
|---|---|---|
| **Verified source conformance** | A complete AST/parser audit at an immutable repository revision produced `PASS` under the recorded schema and rule bundle. | Claiming the bounded scanned source contains no governed legacy construction. |
| **Approved legacy exception** | A specific finding is exactly matched by a valid, approved, unexpired repository record. | Allowing temporary `PASS_WITH_EXCEPTIONS` while preserving visible debt. It is not source conformance. |
| **Declared repository/deployment ownership** | A schema-valid manifest records accountable owners and deployment facts at a revision. | Governance routing and responsibility assignment. It is not live-state proof. |
| **Verified manifest/registry membership** | Manifest identity and role match exactly one packaged participant record. | Proving the expected repository supplied a compatible declaration. |
| **Externally attested runtime fact** | A separately signed or otherwise verifiable artifact proves deployed artifact, process principal, access, or runtime state. | Successor migration/rollout decisions only; not produced by this change. |
| **Informational observation** | Grep output, docs, local dirty-tree scans, inferred owners, or manual notes. | Discovery and remediation planning only. |
| **Unknown/invalid** | Missing, unparsable, unsupported, stale, conflicting, or unowned evidence. | Nothing; it fails the relevant repository and aggregate gate. |

Evidence is always scoped to its repository revision and tool/rule version. A clean audit cannot be carried forward across source changes without rerunning it. A manifest declaration must never be described as an external runtime attestation, and an approved exception must never be counted as verified conformance.

## Risks / Trade-offs

- **AST analysis can miss highly dynamic construction.** The audit reports unresolved/suspicious expressions and fails closed where the adapter cannot classify an in-scope expression. Focused fixtures cover aliases, wrappers, joins, f-strings, constants, and negative examples.
- **Language coverage may lag repository diversity.** Parser adapters are explicit capabilities. Unsupported executable surfaces cannot be certified by grep or waived wholesale; required adapters must be added before that participant can pass.
- **Strict scope validation can initially create many failures.** Begin with an inventory/report-only baseline, fix scope/schema defects, then enable the blocking gate. Acceptance still requires full scope; advisory mode is not readiness evidence.
- **Manifest facts can become stale.** Bind results to revisions, require ownership review for manifest changes, and rerun per-repository CI whenever the manifest, audited source, deployment definitions, registry, or rules change.
- **Exceptions can normalize permanent debt.** Require exact fingerprints, approval references, owners, issues, short expiries, aggregate visibility, and CI warnings before expiry. No automatic renewal is allowed.
- **Exact fingerprints may create review churn after harmless refactors.** The churn is intentional when the governed expression changes; symbol/path plus normalized AST minimizes invalidation from whitespace and line movement.
- **Repository-owned declarations can conflict with central registry metadata.** Treat identity/role conflicts as failures and resolve them through coordinated registry and manifest reviews rather than choosing one silently.
- **Deployment ownership may be mistaken for live proof.** Label it as declared evidence in every output and reserve live principal/artifact claims for successor attestations.
- **A `tdt-core` rule update can fail many repositories at once.** Version rules, retain digest-addressable result history, test rules against representative fixtures and the 15-repository baseline, and roll out rule changes through an explicit compatibility window.
- **Cross-repository aggregation can consume stale artifacts.** Require immutable revisions, matching contract/rule digests, and one envelope per participant; never infer readiness from the most recent available file alone.
- **Central exclusions can hide meaningful code if too broad.** Keep exclusions narrow, versioned, tested, and based on object class (generated/vendor/fixture), not consumer-provided arbitrary globs.

## Migration Plan

1. **Finalize the governance contract in `tdt-core`.** Package the manifest schema, participant registry identity, rule bundle, and parser-adapter interfaces. Add positive, negative, aliasing, parse-failure, scope, redaction, and deterministic-output tests.
2. **Inventory the participant set.** Resolve the exact 15 registry IDs and repository roles from packaged provider data. Record any repository or language that cannot yet be audited; do not invent a replacement ID or mark it clean.
3. **Run a non-blocking baseline audit.** Generate informational findings for each immutable checkout to identify manifest fields, parser coverage gaps, deployment definitions, owners, and legacy sites. Baseline output is discovery evidence only.
4. **Add repository manifests.** In each consumer repository, add `.tdt/governance-manifest.json` with the matching participant identity, source scope, repository owner, deployment classification, deployment owners/principals where applicable, and no secrets.
5. **Classify every legacy finding.** Provider-compliant sites need no record. A legacy site either receives an exact, approved, expiring exception with a migration issue or remains an unsuppressed failure. This change does not silently rewrite the site.
6. **Enable per-repository CI.** Pin a compatible `tdt-core` audit artifact, run the manifest/source audit on an immutable checkout, and retain the canonical JSON envelope. Fail on `FAIL`; surface `PASS_WITH_EXCEPTIONS` and upcoming expiries prominently.
7. **Aggregate all 15 envelopes.** Verify exact registry membership, revisions, rule/schema consistency, ownership completeness, and exception status. Publish the first ecosystem baseline with separate clean, excepted, and failed counts.
8. **Gate successor adoption work.** Use the baseline to open or refine one provider-gated adoption change per consumer. Remove an exception in the same repository change that replaces its legacy source site with provider APIs.
9. **Re-run strict OpenSpec and installed-tool verification.** Validate the change artifacts and prove the audit works from an installed `tdt-core` artifact without sibling-source imports or live credentials.

Rollback restores the previous `tdt-core` audit artifact and removes or disables the new CI gate. Repository manifests may remain as inert version-controlled declarations; rollback does not delete them automatically, rewrite consumer source, or touch live deployments and `~/.tdt`. Any exception accepted during an aborted rollout remains visible debt and must not be interpreted as provider conformance.

## Open Questions

1. Which stable identity namespace is authoritative for repository owners, deployment owners, and principals (for example, service-catalog IDs versus forge team IDs)?
2. Which reviewer groups are permitted to approve legacy exceptions, and what maximum initial/renewal expiry should the central policy enforce?
3. Do any of the 15 participants contain in-scope executable languages beyond the initial parser adapters, and which adapters must be blocking before the first aggregate baseline?
4. Which CI/orchestration system will collect the 15 immutable evidence envelopes, and what revision-set record will bind them into one ecosystem snapshot?
5. Which participant-registry changes require synchronized manifest updates, and how long—if at all—may old and new manifest schema/rule versions overlap?
6. Should `PASS_WITH_EXCEPTIONS` be sufficient only for this governance baseline, or must selected high-risk/deployed consumers reach `PASS` before provider rollout planning begins?
7. What immutable approval-reference forms can be validated in offline or restricted CI without requiring the audit command to contact the source-control forge?
