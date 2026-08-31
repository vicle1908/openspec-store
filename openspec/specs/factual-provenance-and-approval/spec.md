## Purpose

Define source fidelity, visual provenance, exact-copy company approval, neutral-default selection, and evidence invalidation rules for an auditable keynote release.

Stable identity policy: every requirement and scenario SHALL carry the explicit capability-qualified ID shown immediately below its heading. Headings are display text only; IDs SHALL NOT be derived implicitly from headings. IDs MUST be unique across all six specs, renaming a heading MUST preserve its existing ID, and any collision MUST fail central validation.

## Requirements

### Requirement: Every factual claim SHALL resolve to a registered source and qualifier
**Requirement ID:** `REQ-fpa-every-factual-claim-shall-resolve-to-a-registered-source-and-qualifier`

Every audience or notes claim SHALL resolve bidirectionally to a stable source identifier recording the organization, title, publication and access dates, URL or lawful local reference, exact approved wording, slide mapping, scope, and qualifier. Unused registered claims MUST NOT be represented as active release claims.

#### Scenario: Released claim is traced
**Scenario ID:** `SCN-fpa-every-factual-claim-shall-resolve-to-a-registered-source-and-qualifier-released-claim-is-traced`
- **WHEN** an audience statistic or factual statement is selected in the release candidate
- **THEN** it SHALL map to exactly one active registered source entry whose wording, scope, and qualifier match the candidate

#### Scenario: Registered claim is orphaned or unqualified
**Scenario ID:** `SCN-fpa-every-factual-claim-shall-resolve-to-a-registered-source-and-qualifier-registered-claim-is-orphaned-or-unqualified`
- **WHEN** a release claim lacks a source mapping or its source entry omits the required forecast, model, sample, horizon, policy-scope, or directional qualifier
- **THEN** the candidate MUST fail provenance acceptance

### Requirement: Specific factual scopes SHALL remain explicit
**Requirement ID:** `REQ-fpa-specific-factual-scopes-shall-remain-explicit`

PwC, Gartner, Google/Access Partnership, McKinsey, and WEF values SHALL remain projections, modeled potential, or estimates as registered; the MIT NANDA 95% finding SHALL remain scoped to organizations in its analyzed population and the 5% finding SHALL remain scoped to integrated AI pilots that generated substantial value; those percentage claims SHALL retain distinct populations and units and MUST NOT be treated as complements; the USD 30–40 billion figure SHALL remain separate directional investment context; Gartner SHALL remain **hơn 40%**, not an exact 40%; WEF workforce figures SHALL remain projections across all macro drivers; and Nghị quyết 57 SHALL remain scoped to the top-three ASEAN target for AI research and development.

#### Scenario: Claim wording is reviewed
**Scenario ID:** `SCN-fpa-specific-factual-scopes-shall-remain-explicit-claim-wording-is-reviewed`
- **WHEN** released wording is compared with its registered source entry
- **THEN** the wording SHALL preserve the source's population, denominator, horizon, uncertainty, policy scope, and non-causal meaning

#### Scenario: Scope is broadened
**Scenario ID:** `SCN-fpa-specific-factual-scopes-shall-remain-explicit-scope-is-broadened`
- **WHEN** wording generalizes a scoped finding to all AI projects, all investment, all jobs, or a guaranteed national outcome
- **THEN** the candidate MUST fail factual acceptance

### Requirement: Meaningful visuals SHALL have provenance and encoding fidelity
**Requirement ID:** `REQ-fpa-meaningful-visuals-shall-have-provenance-and-encoding-fidelity`

Every meaningful visual SHALL record its slide, purpose, authorship or license basis, source identifiers, encoded values, qualifier, and accessible equivalent. Visual lengths, areas, positions, signs, proportions, labels, and connectors MUST match the registered meaning; illustrative metaphors SHALL be identified as illustrative and not to scale.

#### Scenario: Data visual is inspected
**Scenario ID:** `SCN-fpa-meaningful-visuals-shall-have-provenance-and-encoding-fidelity-data-visual-is-inspected`
- **WHEN** a chart, diagram, or numeric illustration is used to communicate factual meaning
- **THEN** its provenance record and visible encoding SHALL agree with the registered source values and qualifier

#### Scenario: Visual asset has no lawful basis
**Scenario ID:** `SCN-fpa-meaningful-visuals-shall-have-provenance-and-encoding-fidelity-visual-asset-has-no-lawful-basis`
- **WHEN** a meaningful visual lacks project authorship or a recorded permissible license basis
- **THEN** it MUST NOT be accepted into the release candidate

### Requirement: Neutral company-safe copy SHALL be the default
**Requirement ID:** `REQ-fpa-neutral-company-safe-copy-shall-be-the-default`

The selected release copy SHALL default to the complete neutral variant. Viettel or other company identity, infrastructure, operations, customer context, or metrics SHALL be selected only when a named approval record covers the exact released wording and slides, records decision scope and timestamp, and matches the wording's SHA-256.

#### Scenario: Exact-copy approval matches
**Scenario ID:** `SCN-fpa-neutral-company-safe-copy-shall-be-the-default-exact-copy-approval-matches`
- **WHEN** a positive approval names the selected wording, covered slides, scope, approver, timestamp, and matching SHA-256
- **THEN** only the covered approved wording MAY replace its neutral counterpart

#### Scenario: Approval is absent, rejected, stale, partial, or mismatched
**Scenario ID:** `SCN-fpa-neutral-company-safe-copy-shall-be-the-default-approval-is-absent-rejected-stale-partial-or-mismatched`
- **WHEN** no positive exact-copy decision covers the selected wording and slides
- **THEN** the release candidate MUST select neutral copy and MUST contain no dormant gated claim in the public package

### Requirement: Evidence invalidation SHALL use Tier 1 and Tier 2
**Requirement ID:** `REQ-fpa-evidence-invalidation-shall-use-tier-1-and-tier-2`

Evidence invalidation SHALL distinguish **Tier 1 — public-candidate change** from **Tier 2 — private-record-only change**.

1. Tier 1 SHALL apply to a change to any public venue-package byte, selected audience or notes wording, visual encoding, runtime behavior, or PDF input and SHALL invalidate every content-dependent artifact, including browser, accessibility, viewport, screenshot, PDF, public-package checksum, manifest, and copied-folder rehearsal evidence.
2. Tier 2 SHALL apply only to a private-record-only change that leaves all public package bytes and the selected copy unchanged. Rendering and interaction evidence MAY be retained only when its recorded public hashes still match. The changed private record and every manifest, traceability, approval, freshness, or checksum field that depends on it MUST be regenerated or reconciled before release.

#### Scenario: Public candidate bytes change
**Scenario ID:** `SCN-fpa-evidence-invalidation-shall-use-tier-1-and-tier-2-public-candidate-bytes-change`
- **WHEN** `index.html`, `README.md`, the PDF, logo, or a public font changes
- **THEN** all content-dependent evidence SHALL become stale until rerun or regenerated against one exact candidate

#### Scenario: Private metadata changes without public-byte change
**Scenario ID:** `SCN-fpa-evidence-invalidation-shall-use-tier-1-and-tier-2-private-metadata-changes-without-public-byte-change`
- **WHEN** a source-access date, evidence annotation, or other private record changes while selected copy and every public package hash remain identical
- **THEN** matching rendering evidence MAY remain valid, but affected private traceability, freshness, manifest, approval, and checksum assertions MUST be refreshed before acceptance

#### Scenario: Private change alters selected meaning
**Scenario ID:** `SCN-fpa-evidence-invalidation-shall-use-tier-1-and-tier-2-private-change-alters-selected-meaning`
- **WHEN** a private approval, source, or selection change changes the selected public wording or visual meaning
- **THEN** the change SHALL be classified as Tier 1 and the full public-candidate invalidation requirements MUST apply

### Requirement: Release identity SHALL avoid self-reference
**Requirement ID:** `REQ-fpa-release-identity-shall-avoid-self-reference`

The private release record SHALL bind one evidence-base commit, non-self checksums, the exact public package digest, selected copy, source and approval records, evidence status, and the fixed intended annotated ref `refs/tags/ntu-ai-keynote-v1.0.0`. It MUST NOT embed the SHA of the commit containing that manifest. After external release, acceptance SHALL verify that the exact ref resolves to an annotated tag object and SHALL derive the authoritative final commit by peeling `refs/tags/ntu-ai-keynote-v1.0.0^{commit}`.

#### Scenario: Release manifest is finalized
**Scenario ID:** `SCN-fpa-release-identity-shall-avoid-self-reference-release-manifest-is-finalized`
- **WHEN** all release gates have passed and the manifest is committed
- **THEN** the manifest SHALL identify its evidence base, public digest, and fixed intended ref without claiming its own containing commit SHA

#### Scenario: Tag identity is verified
**Scenario ID:** `SCN-fpa-release-identity-shall-avoid-self-reference-tag-identity-is-verified`
- **WHEN** the fixed annotated ref is inspected after the external release commit
- **THEN** `refs/tags/ntu-ai-keynote-v1.0.0` SHALL resolve to an annotated tag object whose peeled commit contains the committed release candidate and exact public package digest

### Requirement: Central acceptance SHALL consume external evidence without mutating its root
**Requirement ID:** `REQ-fpa-central-acceptance-shall-consume-external-evidence-without-mutating-its-root`

External implementation and evidence MAY be submitted to the central change as read-only, hash-bound acceptance evidence. Central planning or task execution SHALL evaluate that evidence against these requirements and MUST NOT write to, reconcile, or regenerate files in the external implementation repository. External or historical local OpenSpec artifacts MAY be consulted only as read-only migration or evidence inputs; no local OpenSpec `status`, `validate`, `apply`, `archive`, task completion, or same-named lifecycle SHALL contribute independent authority or central acceptance state.

#### Scenario: Central acceptance reviews external evidence
**Scenario ID:** `SCN-fpa-central-acceptance-shall-consume-external-evidence-without-mutating-its-root-central-acceptance-reviews-external-evidence`
- **WHEN** an external evidence bundle is presented for a central gate
- **THEN** the central workflow SHALL verify identifiers, hashes, scope, freshness, and results without modifying the evidence source

#### Scenario: Evidence is missing or stale
**Scenario ID:** `SCN-fpa-central-acceptance-shall-consume-external-evidence-without-mutating-its-root-evidence-is-missing-or-stale`
- **WHEN** required external evidence does not satisfy a central acceptance contract
- **THEN** the central gate SHALL remain incomplete and SHALL return the deficiency to the external implementation owner rather than attempting a local repair
