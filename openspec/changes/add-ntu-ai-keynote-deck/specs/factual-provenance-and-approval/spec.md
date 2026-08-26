## Purpose

Define source fidelity, visual provenance, exact-copy company approval, neutral-default selection, and evidence invalidation rules for an auditable keynote release.

## ADDED Requirements

### Requirement: Every factual claim SHALL resolve to a registered source and qualifier

Every audience or notes claim SHALL resolve bidirectionally to a stable source identifier recording the organization, title, publication and access dates, URL or lawful local reference, exact approved wording, slide mapping, scope, and qualifier. Unused registered claims MUST NOT be represented as active release claims.

#### Scenario: Released claim is traced
- **WHEN** an audience statistic or factual statement is selected in the release candidate
- **THEN** it SHALL map to exactly one active registered source entry whose wording, scope, and qualifier match the candidate

#### Scenario: Registered claim is orphaned or unqualified
- **WHEN** a release claim lacks a source mapping or its source entry omits the required forecast, model, sample, horizon, policy-scope, or directional qualifier
- **THEN** the candidate MUST fail provenance acceptance

### Requirement: Specific factual scopes SHALL remain explicit

PwC, Gartner, Google/Access Partnership, McKinsey, and WEF values SHALL remain projections, modeled potential, or estimates as registered; the MIT NANDA 95% finding SHALL remain scoped to analyzed GenAI pilots and measurable P&L at evaluation; the USD 30–40 billion figure SHALL remain a separate directional estimate; WEF workforce figures SHALL remain projections across all macro drivers; and Nghị quyết 57 SHALL remain scoped to the top-three ASEAN target for AI research and development.

#### Scenario: Claim wording is reviewed
- **WHEN** released wording is compared with its registered source entry
- **THEN** the wording SHALL preserve the source's population, denominator, horizon, uncertainty, policy scope, and non-causal meaning

#### Scenario: Scope is broadened
- **WHEN** wording generalizes a scoped finding to all AI projects, all investment, all jobs, or a guaranteed national outcome
- **THEN** the candidate MUST fail factual acceptance

### Requirement: Meaningful visuals SHALL have provenance and encoding fidelity

Every meaningful visual SHALL record its slide, purpose, authorship or license basis, source identifiers, encoded values, qualifier, and accessible equivalent. Visual lengths, areas, positions, signs, proportions, labels, and connectors MUST match the registered meaning; illustrative metaphors SHALL be identified as illustrative and not to scale.

#### Scenario: Data visual is inspected
- **WHEN** a chart, diagram, or numeric illustration is used to communicate factual meaning
- **THEN** its provenance record and visible encoding SHALL agree with the registered source values and qualifier

#### Scenario: Visual asset has no lawful basis
- **WHEN** a meaningful visual lacks project authorship or a recorded permissible license basis
- **THEN** it MUST NOT be accepted into the release candidate

### Requirement: Neutral company-safe copy SHALL be the default

The selected release copy SHALL default to the complete neutral variant. Viettel or other company identity, infrastructure, operations, customer context, or metrics SHALL be selected only when a named approval record covers the exact released wording and slides, records decision scope and timestamp, and matches the wording's SHA-256.

#### Scenario: Exact-copy approval matches
- **WHEN** a positive approval names the selected wording, covered slides, scope, approver, timestamp, and matching SHA-256
- **THEN** only the covered approved wording MAY replace its neutral counterpart

#### Scenario: Approval is absent, rejected, stale, partial, or mismatched
- **WHEN** no positive exact-copy decision covers the selected wording and slides
- **THEN** the release candidate MUST select neutral copy and MUST contain no dormant gated claim in the public package

### Requirement: Evidence invalidation SHALL use two tiers

Evidence invalidation SHALL distinguish public-byte changes from private-record-only changes.

1. A change to any public venue-package byte, selected audience or notes wording, visual encoding, runtime behavior, or PDF input SHALL invalidate every content-dependent artifact, including browser, accessibility, viewport, screenshot, PDF, public-package checksum, manifest, and copied-folder rehearsal evidence.
2. A private-record-only change that leaves all public package bytes and the selected copy unchanged SHALL preserve rendering and interaction evidence only when the retained evidence's recorded public hashes still match. The changed private record and every manifest, traceability, approval, freshness, or checksum field that depends on it MUST be regenerated or reconciled before release.

#### Scenario: Public candidate bytes change
- **WHEN** `index.html`, `README.md`, the PDF, logo, or a public font changes
- **THEN** all content-dependent evidence SHALL become stale until rerun or regenerated against one exact candidate

#### Scenario: Private metadata changes without public-byte change
- **WHEN** a source-access date, evidence annotation, or other private record changes while selected copy and every public package hash remain identical
- **THEN** matching rendering evidence MAY remain valid, but affected private traceability, freshness, manifest, approval, and checksum assertions MUST be refreshed before acceptance

#### Scenario: Private change alters selected meaning
- **WHEN** a private approval, source, or selection change changes the selected public wording or visual meaning
- **THEN** the change SHALL be treated as a public-candidate change and the full invalidation tier MUST apply

### Requirement: Release identity SHALL avoid self-reference

The private release record SHALL bind one evidence-base commit, non-self checksums, the exact public package digest, selected copy, source and approval records, evidence status, and intended annotated tag `ntu-ai-keynote-v1.0.0`. It MUST NOT embed the SHA of the commit containing that manifest; the authoritative final commit SHALL be resolved externally from the annotated tag.

#### Scenario: Release manifest is finalized
- **WHEN** all release gates have passed and the manifest is committed
- **THEN** the manifest SHALL identify its evidence base and public digest without claiming its own containing commit SHA

#### Scenario: Tag identity is verified
- **WHEN** the annotated release tag is inspected after the release commit
- **THEN** the authoritative commit SHALL be derived from the tag object and SHALL match the committed release candidate

### Requirement: Central acceptance SHALL consume external evidence without mutating its root

External implementation and evidence MAY be submitted to the central change as read-only, hash-bound acceptance evidence. Central planning or task execution SHALL evaluate that evidence against these requirements and MUST NOT write to, reconcile, or regenerate files in the external implementation repository.

#### Scenario: Central acceptance reviews external evidence
- **WHEN** an external evidence bundle is presented for a central gate
- **THEN** the central workflow SHALL verify identifiers, hashes, scope, freshness, and results without modifying the evidence source

#### Scenario: Evidence is missing or stale
- **WHEN** required external evidence does not satisfy a central acceptance contract
- **THEN** the central gate SHALL remain incomplete and SHALL return the deficiency to the external implementation owner rather than attempting a local repair
