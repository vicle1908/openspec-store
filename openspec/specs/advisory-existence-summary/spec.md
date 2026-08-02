# advisory-existence-summary Specification

## Purpose
Define versioned structured claim subjects and bounded advisory diagnostics that
summarize exact evidence existence without weakening mandatory validation.
## Requirements
### Requirement: Claims may declare a versioned structured subject

Result schema `urn:tdt:ai-harness:stage-result:2` SHALL allow an additive optional claim subject with kind `symbol`, `file`, or `document`; canonical identifier; repository; optional source revision; and predicate `exists`. Legacy claim payloads without a subject SHALL remain valid. Claim prose SHALL NOT be parsed to derive identity.

#### Scenario: Structured symbol subject
- **WHEN** an observed claim supplies a valid symbol UID, repository, and `exists` predicate
- **THEN** result schema 2 accepts the subject and preserves existing claim fields

#### Scenario: Legacy claim
- **WHEN** an otherwise valid claim omits `subject`
- **THEN** result schema 2 accepts it and diagnostics classify the claim `not_applicable`

#### Scenario: Invalid subject
- **WHEN** a subject uses an unknown kind/predicate/field, unsafe path, empty identifier, or invalid repository/revision value
- **THEN** mandatory schema or semantic validation rejects the result before artifact acceptance

#### Scenario: Prose resembles a target
- **WHEN** claim text names a symbol or path without a structured subject
- **THEN** the harness does not infer a diagnostic target from the text

### Requirement: Result and diagnostic schemas resolve through immutable local registries

The harness SHALL retain the legacy stage-result schema and register `urn:tdt:ai-harness:stage-result:2` for optional subjects. `StageRequest` SHALL carry explicit immutable `result_schema_uri`; its value SHALL equal `output_schema.$id` and SHALL be included in protected-request persistence and its existing request digest. The prerequisite provider-attempt audit remains correlated through that digest; this later change SHALL NOT mutate or reinterpret its immutable terminal-event schema. Result validators SHALL be selected by `(result_schema_uri, StageId)` because each stage has stage-specific constraints. It SHALL register diagnostic schema `urn:tdt:ai-harness:claim-diagnostics:1`. Unknown schema URIs, mismatched URI/document IDs, or URI/stage combinations SHALL NOT be interpreted with a current model. The installed `harness-13` planning schema and verification-policy version SHALL remain version 2, including after a persisted request is reloaded on restart.

#### Scenario: New provider request
- **WHEN** a new stage request is constructed after this change
- **THEN** its supplied output schema declares `urn:tdt:ai-harness:stage-result:2`

#### Scenario: Legacy accepted result
- **WHEN** historical data was produced under the legacy result schema
- **THEN** it remains readable without forced schema-2 reinterpretation

#### Scenario: Unknown result or diagnostic schema
- **WHEN** a reader sees an unrecognized schema URI
- **THEN** it preserves the payload opaquely or returns an explicit unsupported-schema result

#### Scenario: Stage-specific result validator
- **WHEN** two stages use the same result-schema URI
- **THEN** the registry selects each validator using its requested `StageId`
- **AND** a result valid only for another stage is rejected

#### Scenario: Restart preserves request schema identity
- **WHEN** a persisted running-stage request is reloaded after restart
- **THEN** `schema_name`, `schema_version`, `verification_policy_version`, and `result_schema_uri` equal the saved values
- **AND** `result_schema_uri` still equals the persisted output schema `$id`
- **AND** missing identity/version fields are not silently replaced with dataclass defaults

#### Scenario: Narrow legacy protected-request mapping
- **WHEN** a pre-change protected request omits `result_schema_uri` but supplies all planning versions and its output-schema `$id` exactly equals the registered immutable legacy URI
- **THEN** the reader maps it to that legacy result-schema identity
- **AND** any other missing, unknown, or mismatched identity fails as unsupported

### Requirement: Advisory subjects resolve only through cited accepted evidence

For each structured observed claim that passes mandatory validation, diagnostics SHALL evaluate only records named by its `evidence_refs`. Matching SHALL require exact source-specific identity and the canonical run-local repository label (the final component of resolved `run.project_root`); when the subject specifies a source revision, evidence SHALL contain the same non-null revision. Same-basename evidence from another root SHALL still fail accepted-manifest/contained-path validation.

#### Scenario: Exact symbol match
- **WHEN** a symbol subject cites accepted `symbol` evidence with exact UID and repository and any specified revision matches
- **THEN** outcome is `verified`

#### Scenario: Exact file or document match
- **WHEN** a file/document subject cites accepted evidence of the matching source type and exact normalized contained path/repository/revision
- **THEN** outcome is `verified`

#### Scenario: Uncited similar evidence
- **WHEN** another manifest record resembles the subject but is not cited by the claim
- **THEN** it cannot verify the subject

#### Scenario: Subject revision omitted
- **WHEN** the subject has no source revision and cited evidence passed mandatory freshness/current-source validation
- **THEN** diagnostics impose no additional revision-equality constraint

#### Scenario: Specified revision mismatch
- **WHEN** the subject specifies a revision and cited evidence has a different or missing revision
- **THEN** outcome is `untrusted` with reason `revision_mismatch`

### Requirement: Accepted-revision diagnostics use reachable closed outcomes

Every accepted claim SHALL receive an in-memory outcome of `verified`, `not_found`, `untrusted`, or `not_applicable`. Mandatory rejection cases SHALL NOT be converted into accepted advisory outcomes. Evaluation SHALL be independent of cited-evidence order: any exact trusted match yields `verified`; otherwise an exact subject identifier in the applicable `symbol` or normalized `path` field with a source-type or specified-revision mismatch yields `untrusted`; only the absence of an exact-identifier candidate yields `not_found`. Repository mismatch remains a mandatory validation rejection and SHALL NOT appear as an accepted advisory reason. When multiple advisory mismatches exist, reason precedence SHALL be `source_type_mismatch`, then `revision_mismatch`.

#### Scenario: Verified structured observation
- **WHEN** a structured observed subject has an exact cited accepted match
- **THEN** outcome is `verified`

#### Scenario: No cited identity match
- **WHEN** cited accepted records exist but none carries the exact structured-subject identifier in the applicable identity field
- **THEN** outcome is `not_found`
- **AND** absence is not described as contradiction

#### Scenario: Incompatible accepted identity
- **WHEN** no exact trusted match exists and cited accepted evidence carries the exact subject identifier but has incompatible source type or specified revision
- **THEN** outcome is `untrusted` with a bounded reason code

#### Scenario: Repository mismatch remains mandatory
- **WHEN** a subject or cited record names a repository other than the canonical run-local repository
- **THEN** mandatory validation rejects before accepted-revision diagnostics

#### Scenario: Mixed cited evidence
- **WHEN** cited records include both an exact trusted match and one or more incompatible exact-identifier candidates in any order
- **THEN** outcome is `verified`
- **AND** reordering the cited records does not change the outcome

#### Scenario: Non-observed or legacy claim
- **WHEN** a claim is non-observed or omits a structured subject
- **THEN** outcome is `not_applicable`

#### Scenario: Mandatory stale or malformed failure
- **WHEN** evidence is stale/digest-invalid, a subject is malformed, evidence is fabricated, or human authority is used to prove current code
- **THEN** mandatory validation rejects before acceptance
- **AND** no accepted-revision advisory outcome is emitted for that submission

### Requirement: Subject adoption and verification coverage remain separate

The aggregate SHALL report observed and structured-observed totals, per-outcome counts, subject adoption, and verification coverage. It SHALL NOT report a composite confidence threshold.

#### Scenario: Adoption and verification are partial
- **WHEN** four observed claims exist, two have subjects, and one subject verifies
- **THEN** `subject_adoption=0.5` and `verification_coverage=0.5`
- **AND** per-outcome counts remain visible

#### Scenario: No observed claims
- **WHEN** a result has no observed claims
- **THEN** subject adoption and verification coverage are `None`
- **AND** aggregate status is `not_applicable`

#### Scenario: Legacy observed claims only
- **WHEN** observed claims exist but none has a subject
- **THEN** subject adoption is `0.0`, verification coverage is `None`, and aggregate status is `not_applicable`

#### Scenario: All structured observations verify
- **WHEN** every observed claim has a structured subject and every subject verifies
- **THEN** both metrics are `1.0` without converting advisory results into mandatory confidence

### Requirement: Advisory diagnostics cannot weaken mandatory validation

Schema, evidence, claim-policy, artifact-integrity, and traceability validation SHALL remain authoritative. Diagnostics SHALL run only after mandatory checks pass and SHALL NOT convert a rejection to acceptance or suppress a blocker.

#### Scenario: Fabricated evidence ID
- **WHEN** a claim cites an ID absent from accepted evidence
- **THEN** mandatory validation rejects before diagnostics

#### Scenario: Proposed claim
- **WHEN** a proposed claim contains a subject-like object
- **THEN** existing requirement/decision-reference policy remains authoritative
- **AND** diagnostic outcome is `not_applicable`

#### Scenario: Advisory mismatch after mandatory success
- **WHEN** mandatory validation passes but cited evidence does not exactly support a structured subject
- **THEN** the revision may be accepted with `not_found` or `untrusted` visibly recorded

### Requirement: One bounded diagnostic event commits with every accepted revision

Every accepted revision SHALL atomically include one compact `event_type="validation"`, `action="structured_claim_diagnostics"` event using schema `urn:tdt:ai-harness:claim-diagnostics:1`. Complete aggregate counts, subject adoption, and verification coverage SHALL cover all accepted claims. The persisted per-claim projection SHALL sort eligible entries by UTF-8 `claim_id` bytes, consider at most the first 32, and remove entries from the end until the payload satisfies existing depth/item/string and 16,384-byte limits. The event SHALL include revision ID, result schema URI, validator/policy versions, persisted stable claim IDs, compact subjects, cited evidence references/digests, outcomes/reason codes, `total_diagnostic_entries`, `persisted_diagnostic_entries`, `omitted_diagnostic_entries`, and `diagnostics_truncated`. It SHALL exclude full claim prose and evidence content.

#### Scenario: Structured accepted revision
- **WHEN** mandatory validation and bounded diagnostic serialization pass
- **THEN** revision metadata, diagnostic event, transition, and gate/next state commit in one transaction

#### Scenario: Legacy accepted revision
- **WHEN** a result has no structured observed subject
- **THEN** one `not_applicable` diagnostic summary still commits with the revision

#### Scenario: Diagnostic serialization fails
- **WHEN** diagnostic metadata violates its schema or ledger security/bounds
- **THEN** no revision or transition commits
- **AND** unaccepted-artifact cleanup plus the correlated post-invocation rejection path returns a headless stage to pending while preserving its terminal attempt and consumed budget

#### Scenario: Deterministic bounded projection
- **WHEN** an accepted result has more than 32 diagnostic entries or its first 32 entries exceed ledger bounds
- **THEN** aggregate counts cover the complete accepted result
- **AND** per-claim entries use the deterministic ordering and tail-removal rule
- **AND** omission counters exactly equal the difference between total and persisted entries

#### Scenario: Exact boundary fits
- **WHEN** the deterministic projection encodes to exactly the allowed byte/item/depth/string boundaries
- **THEN** it is accepted without unnecessary omission

#### Scenario: Append-only history
- **WHEN** a diagnostic event commits
- **THEN** existing event triggers reject normal application update/delete
