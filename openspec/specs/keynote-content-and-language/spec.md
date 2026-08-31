## Purpose

Define the authoritative 17-slide narrative, Vietnamese language, factual framing, visual meaning, and roundtable content that the keynote must present without strengthening claims or leaving unresolved audience copy.

Stable identity policy: every requirement and scenario SHALL carry the explicit capability-qualified ID shown immediately below its heading. Headings are display text only; IDs SHALL NOT be derived implicitly from headings. IDs MUST be unique across all six specs, renaming a heading MUST preserve its existing ID, and any collision MUST fail central validation.

## Requirements

### Requirement: The keynote SHALL contain exactly 17 slides with one narrative job each
**Requirement ID:** `REQ-kcl-the-keynote-shall-contain-exactly-17-slides-with-one-narrative-job-each`

The audience deck SHALL contain exactly 17 uniquely ordered slides in three acts. Each slide SHALL have one dominant narrative job and one dominant visual job; no visual redesign may change the approved slide count, order, mandatory anchor, factual scope, or timing responsibility.

#### Scenario: Complete deck is inspected
**Scenario ID:** `SCN-kcl-the-keynote-shall-contain-exactly-17-slides-with-one-narrative-job-each-complete-deck-is-inspected`
- **WHEN** the audience slide sequence is enumerated
- **THEN** it SHALL contain slides 1 through 17 exactly once and SHALL preserve the approved three-act order

#### Scenario: A visual combines slide responsibilities
**Scenario ID:** `SCN-kcl-the-keynote-shall-contain-exactly-17-slides-with-one-narrative-job-each-a-visual-combines-slide-responsibilities`
- **WHEN** a proposed visual moves a mandatory claim or narrative job to another slide or requires an additional audience slide
- **THEN** the candidate MUST fail the content contract

### Requirement: Act 1 SHALL establish the macro picture with qualified claims
**Requirement ID:** `REQ-kcl-act-1-shall-establish-the-macro-picture-with-qualified-claims`

Slides 1–5 SHALL identify Lê Khánh Vinh as a Solutions Architect at Viettel and NTU alumnus 2006–2010, present the approved Vietnamese keynote title and two-question hook, and preserve the qualified PwC, Gartner, Nghị quyết 57, and Google/Access Partnership claims defined by the central proposal.

#### Scenario: Act 1 is stage-ready
**Scenario ID:** `SCN-kcl-act-1-shall-establish-the-macro-picture-with-qualified-claims-act-1-is-stage-ready`
- **WHEN** slides 1–5 are reviewed as audience content
- **THEN** each mandatory anchor SHALL be complete, Vietnamese, source-linked, and framed as projection, modeled potential, or policy target where applicable

#### Scenario: Forecast wording is strengthened
**Scenario ID:** `SCN-kcl-act-1-shall-establish-the-macro-picture-with-qualified-claims-forecast-wording-is-strengthened`
- **WHEN** an Act 1 projection or modeled potential is presented as an observed outcome, guaranteed result, or causal fact
- **THEN** the candidate MUST fail factual-language acceptance

### Requirement: Act 2 SHALL distinguish hype, evidence, and transferable experience
**Requirement ID:** `REQ-kcl-act-2-shall-distinguish-hype-evidence-and-transferable-experience`

Slides 6–14 SHALL present the iceberg as an explicitly illustrative and not-to-scale bridge, retain the scoped MIT NANDA and Gartner findings, separate the three transferable adoption layers, distinguish value conversion from advanced-technology adoption alone, and preserve the WEF workforce scope across all macro drivers.

#### Scenario: Three-layer journey is presented
**Scenario ID:** `SCN-kcl-act-2-shall-distinguish-hype-evidence-and-transferable-experience-three-layer-journey-is-presented`
- **WHEN** slides 9–12 are reviewed together
- **THEN** ChatGPT adoption/training, internal-LLM operational lessons, and multi-agent/Agentic AI discipline SHALL remain distinct, transferable narrative layers without requiring Viettel-scale infrastructure

#### Scenario: Value-producing group is described
**Scenario ID:** `SCN-kcl-act-2-shall-distinguish-hype-evidence-and-transferable-experience-value-producing-group-is-described`
- **WHEN** slide 13 explains what successful organizations do differently
- **THEN** it SHALL describe conversion of effort into P&L value and MUST NOT equate success solely with layer-3 or advanced-technology adoption

### Requirement: Slide 7 SHALL keep three factual contexts independent
**Requirement ID:** `REQ-kcl-slide-7-shall-keep-three-factual-contexts-independent`

Slide 7 SHALL present three independent contexts: the registered 95% finding about organizations in the analyzed population, the registered 5% finding about integrated AI pilots that generated substantial value, and the USD 30–40 billion figure only as separate directional investment context. The 95% and 5% figures have distinct populations and units and MUST NOT be encoded as complementary slices, a remainder, or one shared denominator. Text, layout, labels, connectors, proportions, animation, and narration MUST NOT connect the investment context to either percentage as its sample, denominator, or causal explanation.

#### Scenario: All slide 7 contexts are shown
**Scenario ID:** `SCN-kcl-slide-7-shall-keep-three-factual-contexts-independent-all-slide-7-contexts-are-shown`
- **WHEN** the 95% organization finding, 5% integrated-pilot finding, and USD 30–40 billion context appear together
- **THEN** each SHALL have its own claim identity, population or unit label, qualifier, and visual group, with no bar, pie, donut, track, connector, narration, animation, or proportional geometry implying a common denominator or causal relationship

#### Scenario: Populations or context are conflated
**Scenario ID:** `SCN-kcl-slide-7-shall-keep-three-factual-contexts-independent-populations-or-context-are-conflated`
- **WHEN** wording or visual encoding treats 95% and 5% as complementary parts, calls both figures organizations or both figures pilots, or links USD 30–40 billion to the analyzed percentage population
- **THEN** the candidate MUST fail content and provenance acceptance

### Requirement: Act 3 SHALL separate leadership, questions, and handoff
**Requirement ID:** `REQ-kcl-act-3-shall-separate-leadership-questions-and-handoff`

Slides 15–17 SHALL present three complete Vietnamese leadership mindsets, three concise statistically anchored audience prompts on slide 16, full moderator expansions only in notes or cue-sheet data, and a distinct complete 30-second NTU alumni handoff on slide 17 that does not repeat the questions.

#### Scenario: Roundtable prompts are displayed
**Scenario ID:** `SCN-kcl-act-3-shall-separate-leadership-questions-and-handoff-roundtable-prompts-are-displayed`
- **WHEN** slide 16 is shown at a qualified viewport
- **THEN** all three concise prompts SHALL be independently readable, non-overlapping, and anchored to the approved 95%, 39%, and **hơn 40%** contexts

#### Scenario: Handoff slide is reviewed
**Scenario ID:** `SCN-kcl-act-3-shall-separate-leadership-questions-and-handoff-handoff-slide-is-reviewed`
- **WHEN** slide 17 follows slide 16
- **THEN** it SHALL acknowledge the roundtable and NTU alumni bond without repeating the three questions or exposing unresolved panelist placeholders

### Requirement: Audience and operator language SHALL follow the Vietnamese policy
**Requirement ID:** `REQ-kcl-audience-and-operator-language-shall-follow-the-vietnamese-policy`

Audience copy, speaker notes, controls, warnings, source lines, README instructions, and cue sheets SHALL be Vietnamese except for approved technical terms and official source titles. LLM, Agentic AI, and other retained technical terms MUST receive a Vietnamese first-use explanation where required for audience comprehension.

#### Scenario: Language audit is run
**Scenario ID:** `SCN-kcl-audience-and-operator-language-shall-follow-the-vietnamese-policy-language-audit-is-run`
- **WHEN** all public and speaker-facing strings are reviewed
- **THEN** no unapproved English planning phrase, unresolved marker, conditional audience wording, `TBD`, `TODO`, or `placeholder` SHALL remain

#### Scenario: Technical term first appears
**Scenario ID:** `SCN-kcl-audience-and-operator-language-shall-follow-the-vietnamese-policy-technical-term-first-appears`
- **WHEN** a retained technical term first appears in audience content
- **THEN** the slide or immediately associated content SHALL provide the approved Vietnamese explanation without changing the claim's meaning

### Requirement: Visuals SHALL preserve factual and linguistic meaning
**Requirement ID:** `REQ-kcl-visuals-shall-preserve-factual-and-linguistic-meaning`

Every meaningful diagram, data visualization, illustration, or icon SHALL have concise Vietnamese labels or a text equivalent, SHALL preserve the registered factual qualifier, and MUST NOT encode a forecast, directional estimate, or metaphor as measured observed data. Decorative visuals SHALL carry no required meaning.

#### Scenario: Meaningful visual is reviewed
**Scenario ID:** `SCN-kcl-visuals-shall-preserve-factual-and-linguistic-meaning-meaningful-visual-is-reviewed`
- **WHEN** a visual carries information needed to understand a slide
- **THEN** its visible labels and accessible equivalent SHALL communicate the same Vietnamese meaning and factual scope

#### Scenario: Decorative visual is removed
**Scenario ID:** `SCN-kcl-visuals-shall-preserve-factual-and-linguistic-meaning-decorative-visual-is-removed`
- **WHEN** a decorative element is hidden or omitted
- **THEN** no required narrative, factual, or navigational meaning SHALL be lost

### Requirement: The 17-slide dominant visual matrix SHALL be authoritative
**Requirement ID:** `REQ-kcl-17-slide-dominant-visual-matrix`

Each slide SHALL implement exactly the following dominant visual job; these rows are normative contracts, not examples:

| Slide | Required dominant visual job |
|---:|---|
| 1 | Hero title with speaker card |
| 2 | Question cards with a value bridge |
| 3 | Hero metric with horizon and qualifier |
| 4 | Agentic-AI definition plus independent forecast cards |
| 5 | Policy/opportunity split with no causal connector |
| 6 | Explicitly illustrative, not-to-scale iceberg |
| 7 | Independent 95% organization and 5% integrated-pilot cards plus a separate investment/P&L context band |
| 8 | **Hơn 40%** banner plus three risk pillars |
| 9 | Three-layer overview |
| 10 | Adoption/problem split |
| 11 | Four-stage pipeline |
| 12 | Agent loop plus human-governance gate |
| 13 | 2×2 synthesis matrix |
| 14 | Signed workforce grid |
| 15 | Three leadership pillars |
| 16 | The exact three prompt cards required by the roundtable contract |
| 17 | Quiet handoff banner |

For every row, the central planning baseline and external evidence SHALL record the slide number, stable visual ID, dominant visual job and type, factual/metaphor/synthesis/decorative classification, encoded claim/source IDs, values/categories/populations/units where applicable, qualifier/scope, visible and DOM reading order, concise Vietnamese accessible description, safe-area obligation, reduced-motion/print state, and authorship or license basis.

#### Scenario: Complete visual matrix is reviewed
**Scenario ID:** `SCN-kcl-17-slide-dominant-visual-matrix-complete-matrix-reviewed`
- **WHEN** the 17 audience slides and their planning-baseline mappings are enumerated
- **THEN** every slide SHALL map exactly once to its required matrix row and all required visual-contract fields SHALL be present

#### Scenario: A dominant visual job is substituted
**Scenario ID:** `SCN-kcl-17-slide-dominant-visual-matrix-job-substituted`
- **WHEN** a slide omits, replaces, merges, or treats its matrix row as optional guidance
- **THEN** the candidate MUST fail central content acceptance even if its narrative text remains present
