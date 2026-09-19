## Purpose

The Enterprise AI Training capability defines the governance, curriculum structure, verification gates, presentation standards, cohort operations, and competency certification for company-wide AI engineering enablement across Developer, Business Analyst, and Quality Assurance roles.

## ADDED Requirements

### Requirement: Universal Common Core Training Architecture
The curriculum SHALL mandate four foundational Common Core modules (C01 through C04) for all participating learners regardless of engineering role, establishing a shared baseline in cognitive limits, structured outputs, MCP connectivity, and AI security.

#### Scenario: Common Core module completion
- **GIVEN** an enrolled learner in any track (Dev, BA, or QA)
- **WHEN** attending Tier 0 training sessions
- **THEN** the learner SHALL complete Module C01 (Cognitive Limits & Workspace Tooling), Module C02 (Structured Prompts, JSON/YAML Schemas & System Instructions), Module C03 (Context Engineering & MCP Gateway Navigation), and Module C04 (AI Security, OWASP Top 10 for LLMs & Secret Hygiene)
- **AND** the learner MUST demonstrate zero secret leakage in test repositories prior to advancing to role-specialized tracks.

#### Scenario: Failed security verification in Common Core
- **GIVEN** a learner completing the Module C04 practical evaluation
- **WHEN** the learner commits a `.env` file, hardcoded API secret, or unauthorized credential token to version control
- **THEN** the automated scanning gate SHALL fail with a non-zero exit code
- **AND** the learner SHALL NOT receive credit for Tier 0 until the secret is revoked, removed from Git history, and re-verified.

### Requirement: Knowledge Infrastructure Governance
The curriculum SHALL embed knowledge-infrastructure governance within Common Core C03 for all roles, preserving the 24-session baseline and 18 role-track modules without creating a standalone module or repeating existing symbol-query, blast-radius, ADR-retrieval, or context-bundle instruction.

#### Scenario: Wiki curation and index freshness verification
- **GIVEN** a Developer learner in the C03 sandbox with a stale-index warning and a wiki article requiring review
- **WHEN** the learner reads the warning, uses `wiki_search` and `wiki_read` to inspect existing knowledge, curates the article through `wiki_ingest`, runs the freshness check, and rebuilds the affected index
- **THEN** the reviewed article SHALL pass `wiki-lint.py` verification and conform to `SCHEMA.md`: `title`, `tags`, `created`, `updated`, and `status` frontmatter; related-page links; fewer than 500 words; a review flag after more than 30 days without update; and archival of stale pages to `_archive/` after 90 days
- **AND** the learner MUST record author and reviewer approval plus source provenance, and prove the rebuilt index is clean by showing its indexed revision equals the unchanged repository HEAD; missing revision evidence or a newer HEAD SHALL NOT count as fresh.

#### Scenario: AgentMemory observation lifecycle
- **GIVEN** a Developer learner starting a C03 sandbox session with a prior observation and a deprecated ADR fixture
- **WHEN** the learner recalls the prior session before starting work, observes automatic hook capture, saves a new observation, verifies session-to-long-term promotion, and forgets the deprecated ADR after explicit confirmation of the selected fixture
- **THEN** the learner SHALL demonstrate that the promoted observation is retrievable from a subsequent session with its source-session provenance intact, rather than treating hook capture alone as proof of promotion
- **AND** the learner MUST verify that the forgotten ADR is no longer returned by recall while the replacement decision remains retrievable, preserving a non-sensitive deprecation and deletion audit record.

---

### Requirement: Role-Specialized Engineering Tracks
The program SHALL provide three distinct, role-specialized tracks comprising 18 modules total (6 Developer, 6 Business Analyst, and 6 Quality Assurance), tailoring Context Engineering and Spec-Driven Development to role practices.

#### Scenario: Developer track execution
- **GIVEN** an enrolled software engineer who has completed Tier 0
- **WHEN** proceeding through the Developer track (Modules D01 through D06)
- **THEN** the curriculum SHALL train and evaluate the engineer on In-IDE AI pairing (D01), CLI coding agents and Explore-Plan-Code workflows (D02), AGENTS.md boundaries and MCP tool integration (D03), AST-aware refactoring and type-system validation (D04), Spec-Driven Development and autonomous agent runtime engineering with OpenSpec, LangGraph, and Pydantic AI (D05), and multi-agent CI evaluations and harness engineering (D06).

#### Scenario: Business Analyst track execution
- **GIVEN** an enrolled business analyst or product manager who has completed Tier 0
- **WHEN** proceeding through the Business Analyst track (Modules B01 through B06)
- **THEN** the curriculum SHALL train and evaluate the learner on AI-assisted product discovery and user interview synthesis (B01), precision acceptance criteria using Gherkin and EARS (B02), machine-readable specifications and truth tables (B03), backlog semantic dependency audits (B04), collaborative OpenSpec specification authoring (B05), and AI product PRDs with bias/drift monitoring (B06).

#### Scenario: Quality Assurance track execution
- **GIVEN** an enrolled quality assurance engineer who has completed Tier 0
- **WHEN** proceeding through the Quality Assurance track (Modules Q01 through Q06)
- **THEN** the curriculum SHALL train and evaluate the engineer on AI-augmented combinatorial test matrix design (Q01), automated Playwright/Pytest test generation and formative mobile accessibility inspection (Q02), context-aware test gap analysis against AST call graphs (Q03), testing and evaluating LLM applications with DeepEval/RAGAS (Q04), autonomous self-healing test suites and one assessed browser exploration with external containment preflight, indirect-injection defense, structured trace, and independent final-state assertion (Q05), and adversarial red teaming and prompt injection defense (Q06).


### Requirement: Autonomous Agent Runtime Engineering Section
The curriculum SHALL provide a dedicated autonomous agent runtime engineering section within advanced Developer Module D05 on constructing typed autonomous runtimes with Pydantic AI and LangGraph, distinct from basic specification planning and multi-agent CI evaluations, without adding standalone course sessions.

#### Scenario: Successful runtime lab
- **GIVEN** a Developer learner implementing the runtime engineering section in the `agent-core` sandbox for Module D05
- **WHEN** the learner builds a typed triage/review `Agent` with `AgentRuntimeDeps`, output validation, `@agent.tool` contracts, and a `WorkflowBuilder` graph using checkpointing
- **THEN** the lab SHALL demonstrate fan-out analysis with `Send`, an approval `interrupt()` resumed by `Command` using a stable `thread_id`, and deterministic fixture verification with trace/eval evidence
- **AND** the runtime SHALL use safe, idempotent tools with bounded retries and timeouts.

#### Scenario: Runtime failure and resume edge case
- **GIVEN** a Module D05 runtime graph paused at a human approval interrupt or encountering invalid tool output
- **WHEN** the learner resumes with the same `thread_id` or submits the invalid result
- **THEN** the checkpointed graph SHALL resume without losing prior state, while typed validation SHALL reject the invalid result and the deterministic gate SHALL exit non-zero until corrected.

### Requirement: Harness Engineering Section
The curriculum SHALL provide a dedicated harness engineering section within advanced Developer Module D06 on engineering reliable execution harnesses around agents, including context assembly, tools, lifecycle hooks, permission policy, progressive-disclosure skills, isolation, deterministic gates, evidence, and telemetry, without adding standalone course sessions or duplicating business-agent construction.

#### Scenario: Successful harness lab
- **GIVEN** a learner wrapping an agent in the `agent-core` sandbox for Module D06
- **WHEN** the harness loads one on-demand `SKILL.md`, applies a pre-tool deny policy, records a post-tool audit, runs an isolated fixture/worktree, and evaluates a stop gate
- **THEN** pytest, ruff, and OpenSpec verification SHALL each exit `0`
- **AND** the canonical positive verifier SHALL be run from the materials repository as `cd ~/Developer/ai-training-materials && python labs/dev/D06/verify_harness.py`
- **AND** the harness SHALL emit structured evidence and telemetry without committing outside the isolated scope.

#### Scenario: Harness gate failure prevents commit
- **GIVEN** an intentional fixture failure or unauthorized tool request during Module D06 harness evaluation
- **WHEN** the stop gate evaluates the run
- **THEN** the harness SHALL deny the unsafe tool or stop before commit, record the failed gate and reason, and return a non-zero verification result
- **AND** the canonical negative verifier SHALL be run from the materials repository as `cd ~/Developer/ai-training-materials && python labs/dev/D06/verify_harness_failure.py`, exit non-zero, and leave no commit.


### Requirement: Autonomous Browser & Device Control
The curriculum SHALL embed autonomous browser and device-control engineering across seven existing modules (C04, D02, D06, B02, B06, Q02, and Q05), teaching DOM/accessibility-driven, screenshot-driven, and hybrid UI perception as lecture/demo comparisons, browser agent frameworks (Browser Use and Playwright MCP), and cross-platform device-control concepts (agent-device CLI/MCP/API) without creating standalone modules beyond the 24-session baseline. Mobile execution SHALL remain formative in Q02; Q05 SHALL assess one browser exploration path with external preflight, injection defense, trace evidence, and an independent final-state assertion. These embedded exercises SHALL preserve the existing assessment model of eight assessed modules per role at five points each, totaling 40 lab points.

#### Scenario: Browser agent completion
- **GIVEN** a learner with Browser Use or Playwright MCP configured in an approved disposable lab environment
- **WHEN** the agent executes a multi-step local form task by navigating, filling fields, and verifying state using accessibility snapshots
- **THEN** the agent SHALL complete the task and produce structured evidence of the actions and verified final state
- **AND** the learner MUST demonstrate that a redirect to a forbidden network destination is blocked at the enforced egress boundary; browser-origin allow-lists SHALL NOT count as a security boundary.

#### Scenario: Formative mobile device inspection
- **GIVEN** a learner in formative Q02 with agent-device and a resettable synthetic app fixture
- **WHEN** the learner captures an accessibility snapshot, presses a grounded ref, captures a fresh snapshot and screenshot, resets state, and compares the before/after diff
- **THEN** the learner SHALL produce deterministic fixture-state evidence; mobile execution SHALL carry no Q05 assessment points, and agent action selection SHALL NOT be treated as deterministic.
#### Scenario: Q05 assessed browser exploration
- **GIVEN** a learner with Browser Use or Playwright MCP in an approved disposable environment and a passing external containment preflight
- **WHEN** the learner explores the local fixture, encounters hidden prompt injection, records the denied action and structured trace, and checks the result independently
- **THEN** the learner SHALL provide an independent final-state assertion with unchanged protected state; mobile execution and modality comparisons SHALL remain formative or optional and unassessed in Q05.

### Requirement: Device Control Safety & Sandboxing
The curriculum SHALL teach device-control safety as a cross-cutting concern with three explicitly separate boundaries: execution isolation, data exposure to the model, and authorization to act. Execution isolation SHALL use one disposable environment per learner with synthetic data, resettable application state, and enforced filesystem/egress restrictions at the OS/network boundary; production profiles, production credentials, and existing user browser sessions MUST NOT be attached. Data exposure controls SHALL include screenshot suppression and sensitive-data placeholders, without treating placeholders as screenshot redaction; local/profile isolation alone MUST NOT be treated as preventing screenshots from reaching a hosted model. Consequential action gates SHALL require user confirmation for submit/delete/purchase actions, independently of environment isolation.

#### Scenario: Sandbox containment proof
- **GIVEN** a learner configuring a browser/device agent lab in a disposable environment with enforced filesystem/egress restrictions
- **WHEN** an external deterministic containment preflight tests a forbidden network destination, forbidden file write, wrong-profile attachment, and denied action approval using synthetic targets
- **THEN** all four prohibited operations MUST be blocked and their denials recorded before agent tools are enabled and the exercise starts
- **AND** a failed or missing containment check SHALL prevent tool mounting and the exercise from starting; learners SHALL NOT self-certify containment.

#### Scenario: Visual indirect injection defense
-**GIVEN** a learner with an active browser agent in the approved disposable environment
-**WHEN** the agent encounters a webpage containing hidden prompt injection in invisible CSS text or an image payload
-**THEN** the agent MUST treat the embedded instruction as untrusted data and MUST NOT execute the requested action
-**AND** the learner SHALL record the blocked action and verified unchanged protected state as evidence.
 
#### Scenario: Model-data and authorization safety evidence
 - **GIVEN** a safety fixture containing synthetic sensitive-looking values and a pending consequential transaction
 - **WHEN** the learner runs the designated safety verifier, changes the transaction recipient or value, and exercises screenshot suppression and placeholder handling
 - **THEN** the verifier SHALL prove that suppressed screenshots are not exposed, placeholders are not claimed to redact screenshots, no sensitive values appear in model or log evidence, and reapproval is required after the recipient or value changes
 - **AND** the learner SHALL retain only non-sensitive pass/fail evidence and the changed-transaction approval record.







---


### Requirement: Cross-Functional Capstone Triads
The curriculum SHALL culminate in Tier 4 collaborative Capstone Triads comprising one Business Analyst, two Developers, and one QA Engineer executing simulated production delivery and incident response.

#### Scenario: Capstone X01 micro-feature delivery sprint
- **GIVEN** a formed cross-functional Triad (one Business Analyst, two Developers, and one QA Engineer)
- **WHEN** executing Session X01 under an 80-minute timeboxed sprint
- **THEN** the BA SHALL author an OpenSpec specification containing zero ambiguous criteria and 100% Gherkin acceptance coverage
- **AND** the Developers SHALL implement the feature within isolated worktrees achieving passing compilation and $\ge 80\%$ test coverage
- **AND** the QA Engineer SHALL generate and execute automated boundary verification suites that pass cleanly in CI.

#### Scenario: Capstone X02 currency-precision incident
- **GIVEN** an active production-like `go-microservices` environment with an injected currency-ledger precision fault caused by floating-point arithmetic
- **WHEN** executing Session X02 incident response
- **THEN** the Triad SHALL collaboratively diagnose the incident using workspace telemetry and knowledge graphs
- **AND** the Triad SHALL deliver a regression test, permanent precision remedy, and formal postmortem, with `make verify-pr && test -f POSTMORTEM.md` as acceptance evidence.

---

### Requirement: Deterministic Lab Sandbox Verification
All practical lab assignments across Tiers 0 through 4 SHALL evaluate learner competency solely through deterministic, automated verification commands that must exit with return code `0`.

- **GIVEN** a learner completing a practical hands-on sandbox lab
- **WHEN** executing the designated verification command (`make verify-pr`, `uv run pytest`, `vitest run`, or `openspec validate`)
- **THEN** the command SHALL exit with code `0` for the designated fixture gate, which SHALL NOT be presented as proof of general LLM/agent quality or safety
- **AND** the verification harness SHALL record cryptographically verified test telemetry in the session artifact store.

#### Scenario: Unverified or subjective lab claims
- **GIVEN** a learner submitting lab results
- **WHEN** the designated verification command fails with non-zero exit code or is bypassed via manual subjective grading
- **THEN** the scoring engine SHALL award zero points for that lab module
- **AND** partial credit based on conversational claims or unchecked pull requests SHALL NOT be permitted.

---

### Requirement: 16:9 Dark-Stage Presentation Standards
All instructional slide decks, keynote presentations, and stage visual aids SHALL conform strictly to the enterprise 16:9 dark-stage presentation specification.

#### Scenario: Slide visual and contrast compliance
- **GIVEN** any slide deck authored for the training series
- **WHEN** rendered on lab displays or projected on stage
- **THEN** the presentation canvas SHALL maintain a 16:9 aspect ratio with a fixed 1280×720 stage and dynamic viewport scaling (`scale = min(innerWidth/1280, innerHeight/720)`)
- **AND** the background canvas SHALL use the dark-stage navy tone `#0d1038`
- **AND** all body text SHALL use high-contrast white `#f8fafc` or cyan `#38bdf8` meeting WCAG AA contrast ratios ($\ge 4.5:1$)
- **AND** typography SHALL enforce a minimum of 28pt for slide body text and 40pt for slide titles.

#### Scenario: Telemetry HUD and offline self-containment
- **GIVEN** an instructional deck presented in the training facility
- **WHEN** displayed to learners during a 120-minute session
- **THEN** the slide layout SHALL include an operational HUD displaying module progress, current phase (Concept, Demo, Lab, Debrief), and time remaining
- **AND** the presentation deck SHALL be fully self-contained HTML5/SVG with embedded WOFF2 fonts, requiring zero external CDN or cloud connectivity during stage execution.

---

### Requirement: Weekend-First Cohort Schedule & Facility Presentation Reference
The enterprise rollout SHALL operate on a Weekend-First schedule to eliminate weekday sprint friction and prevent network saturation. The curriculum presentation materials SHALL illustrate a reference facility architecture (front stage displays, student pods, isolated edge compute topology) for lecture and demonstration purposes, but physical hardware installation SHALL NOT be required as a software deployment deliverable of the training materials repository.

#### Scenario: Saturday intensive cohort scheduling
- **GIVEN** enrolled learners assigned to weekend cohorts
- **WHEN** attending Saturday intensive training
- **THEN** Cohort A SHALL attend morning sessions from 08:30 to 12:45 and Cohort B SHALL attend afternoon sessions from 13:45 to 18:00, each comprising two 120-minute modules with a 15-minute break (255 minutes total)
- **AND** the one-hour interval from 12:45 to 13:45 SHALL be reserved for turnover and lunch.

#### Scenario: Sunday capstone and office hours execution
- **GIVEN** learners completing Saturday modular training
- **WHEN** attending Sunday sessions
- **THEN** the facility SHALL host Open Lab and Facilitator Office Hours from 09:00 to 12:00 for 1-on-1 remediation and technical deep-dives
- **AND** the facility SHALL host X01 and X02 sequentially from 13:30 to 17:30, each receiving 120 minutes.

#### Scenario: Lab facility presentation reference architecture
- **GIVEN** lecture and presentation materials covering facility infrastructure
- **WHEN** slide decks and facilitator guides are rendered
- **THEN** they SHALL provide illustrative reference diagrams showing the recommended dual 4K front stage, student pod layout, and local zero-egress OmniRoute/Ollama edge compute topology
- **AND** physical hardware procurement and deployment SHALL NOT be a prerequisite or deliverable of the `ai-training-materials` software baseline.
---
### Requirement: Infrastructure Profile Governance
The program SHALL maintain two explicitly separated infrastructure profiles with hard security boundaries: a Local Zero-Egress Facility Profile canonical for all live cohort runtime, and an Approved Cloud-Backed Preparation Profile restricted exclusively to deterministic artifact generation and mirror pre-seeding. These profiles MUST NOT share network paths, credentials, learner workstations, or lab devcontainers during live cohort operations.

#### Scenario: Local facility profile zero-egress gate
- **GIVEN** a facilitator preparing for a live cohort session
- **WHEN** running the zero-egress preflight gate before cohort delivery begins
- **THEN** the gate script (`scripts/verify-zero-egress-resolution.sh`) MUST verify that no non-loopback egress route exists on the learner subnet
- **AND** the gate MUST verify that all AI traffic routes exclusively to on-premise Ollama (`ofable-5`) and local OmniRoute (`localhost:20128/v1`)
- **AND** a failed or missing zero-egress gate SHALL prevent the live cohort session from starting.

#### Scenario: Cloud prep profile isolation
- **GIVEN** a curriculum maintainer using the Approved Cloud-Backed Preparation Profile for deterministic artifact generation or mirror pre-seeding
- **WHEN** executing cloud-backed operations (slide compilation, seed-manifest resolution, mirror warm-up)
- **THEN** the cloud profile MUST NOT be accessible from any learner workstation or lab devcontainer during live cohorts
- **AND** the cloud profile MUST NOT be referenced in any lab exercise, verification gate, or student-facing script
- **AND** all cloud-backed artifact outputs MUST pass integrity verification (hash and manifest check) before import into the local facility profile
- **AND** cloud profile usage MUST be logged, time-bounded, and approved per session by the Lead Enterprise Architect.

#### Scenario: Dual-profile security constraint enforcement
- **GIVEN** a pre-cohort infrastructure readiness check
- **WHEN** verifying dual-profile isolation before any live cohort session
- **THEN** an automated isolation verification gate (`scripts/verify-cloud-profile-isolation.sh`) MUST confirm the cloud prep profile is unreachable from learner subnets
- **AND** a failed isolation check SHALL fail-closed: the live cohort session MUST NOT begin
- **AND** the isolation gate evidence MUST be recorded in the cohort readiness log.

### Requirement: 100-Point Competency Evaluation & CEIP Certification
Learner graduation and enterprise certification SHALL be governed by an objective 100-point competency rubric evaluating lab verification across exactly eight assessed practical modules per learner (Common Core C01 through C04, the learner's assigned track-specific advanced modules—Developer D05 and D06, Business Analyst B05 and B06, or Quality Assurance Q05 and Q06—and shared Capstones X01 and X02, awarding 5 points each for 40 points total), capstone triad delivery (40 points), and security hygiene (20 points); foundational role-track modules (D01 through D04, B01 through B04, and Q01 through Q04) and non-enrolled tracks SHALL serve as required formative exercises without point deductions, and learners SHALL NOT be required to attend or pass modules outside their assigned role track.

#### Scenario: CEIP certification award
- **GIVEN** an enrolled learner in any track (Developer, Business Analyst, or Quality Assurance) who has attended 100% of required Tier 0, assigned role-track, and Capstone sessions
- **WHEN** their cumulative evaluation score reaches or exceeds 80 points out of 100 across their eight role-specific assessed practical modules (C01–C04, their track's 05–06 pair, and X01–X02), capstone triad delivery, and security hygiene
- **THEN** the program SHALL award the Certified Enterprise AI Practitioner (CEIP) credential
- **AND** the learner SHALL be certified to use autonomous coding agent harnesses in production repositories.

#### Scenario: Role-track scoring equity across disciplines
- **GIVEN** three enrolled learners from the Developer, Business Analyst, and Quality Assurance tracks respectively
- **WHEN** each learner completes Common Core (C01–C04), their assigned role-track advanced modules (D05–D06 for Dev, B05–B06 for BA, Q05–Q06 for QA), and shared Capstones (X01–X02) with passing deterministic verification gates (exit code 0)
- **THEN** each learner SHALL receive the full 40 lab verification gate points (8 modules × 5 points) without attending or completing labs from other tracks
- **AND** all three roles SHALL have an identical opportunity to achieve the maximum 100-point competency score.

#### Scenario: Enterprise AI Champion recognition
- **GIVEN** a top-performing graduate achieving $\ge 95$ points out of 100
- **WHEN** demonstrating verified leadership and peer review excellence in Capstone Triads
- **THEN** the organization SHALL award the Enterprise AI Champion credential
- **AND** the graduate SHALL be certified to serve as Teaching Assistant (TA) for subsequent cohorts and Department AI Reviewer for production specifications and pull requests.
---

### Requirement: Dedicated Training Materials Repository
The enterprise enablement program SHALL maintain a dedicated version-controlled Git repository at `~/Developer/ai-training-materials` containing all instructional slide decks, master syllabi, student exercise sandboxes, devcontainer configurations, and facilitator runbooks.

#### Scenario: Repository structure and asset self-containment
- **GIVEN** a cloned checkout of `ai-training-materials` on a lab workstation or facilitator machine
- **WHEN** inspecting the repository layout and opening any slide deck, syllabus, or lab asset
- **THEN** the repository SHALL expose the canonical directory structure (`slides/`, `labs/`, `docs/`, `.devcontainer/`, `scripts/`) with every 24-session HTML5 deck and WOFF2 font asset stored in-tree
- **AND** every instructional asset SHALL render and execute with zero external CDN, cloud, or network dependency.

#### Scenario: Devcontainer and student sandbox reproducibility
- **GIVEN** a student workstation provisioning a lab environment from the repository
- **WHEN** building the pinned Docker devcontainer definition for the target stack (Go, Python, or Node)
- **THEN** the devcontainer SHALL build deterministically from image digest pins and restore package caches from the local 10GbE mirror registry
- **AND** the resulting sandbox SHALL pass the lab's automated verification gate (`uv run pytest`, `vitest run`, or `make verify-pr`) with exit code `0` before any student work begins.

#### Scenario: Release tagging and version synchronization
- **GIVEN** a cohort baseline or curriculum revision ready for rollout
- **WHEN** facilitators cut the materials release
- **THEN** the repository SHALL be tagged with a semantic version (`v1.0.0` for the initial cohort baseline) signed with an annotated Git tag
- **AND** the tag SHALL be synchronized with the governing `openspec-store` change evidence so each cohort trains against an immutable, hash-pinned materials snapshot.
