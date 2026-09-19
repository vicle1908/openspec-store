## Why

Under controlled METR benchmark conditions, one study reported slower completion for its evaluated developers and tasks when using unverified AI code generation; applicability to this enterprise program is unknown. This initiative addresses the audit tax with deterministic verification, grounded context, and explicit evidence rather than assuming a universal productivity effect.

This initiative establishes a company-wide, production-grounded enterprise AI training curriculum. By anchoring directly to existing workspace infrastructure (`mcp-router`, `GitNexus`, `Graphify`, `AgentMemory`, `LLM Wiki`, `OpenSpec`, and `OmniRoute`), the program aligns Dev, BA, and QA roles around machine-readable specifications, isolated multi-worktree orchestration, and verifiable execution loops.

## What Changes

This change establishes the formal enterprise specification, architectural design, and implementation rollout plan for the company-wide AI training series:
- **Universal Common Core (Tier 0):** Mandates four foundational modules (C01–C04) covering LLM cognitive limits, structured JSON/YAML generation, MCP tool topology, and enterprise AI security (OWASP Top 10 for LLMs).
- Enhanced knowledge-infrastructure sections within Common Core C03 covering LLM Wiki curation, AgentMemory lifecycle, and index freshness verification.
- **Computer-Use & Device Control Integration:** Embeds autonomous browser agent engineering (Browser Use, Playwright MCP), cross-platform device-control instruction (agent-device), and device-control safety across seven existing modules (C04, D02, D06, B02, B06, Q02, and Q05). The safety model names three independent boundaries: **execution isolation**, **model-data exposure**, and **authorization to act**. Local/profile isolation does not prevent screenshots from being sent to hosted models; screenshot suppression and sensitive-data placeholders are separate controls, and consequential-action approval remains required independently of isolation. DOM/AX, vision, and hybrid modalities may be taught as lecture/demo comparisons; mobile execution is formative in Q02, while Q05 assesses only one browser exploration path, without adding standalone sessions or changing the eight-assessed-module, 40-lab-point model per role.
- **Role-Specialized Engineering Tracks (Tiers 1–3):** Implements three parallel role tracks (18 modules total) for Developers (D01–D06), Business Analysts (B01–B06), and QA Engineers (Q01–Q06).
- **Advanced Developer Sections:** Enhances advanced Developer modules D05 and D06 with dedicated curriculum and lab sections on autonomous agent runtime engineering (LangGraph + Pydantic AI) and harness engineering, preserving the 24-session course baseline without introducing separate standalone sessions.
- **Cross-Functional Capstone Triads (Tier 4):** Introduces two synchronized capstone simulations (X01 Micro-Feature Delivery and X02 AI Incident Root Cause Analysis) executing realistic collaboration across 4-member cross-functional Triads (one Business Analyst, two Developers, and one QA Engineer).
- **Deterministic Sandbox Verification:** Enforces automated test gates (`make verify-pr`, `uv run pytest`, `vitest`, `openspec validate`) exiting with code `0` as the sole criteria for lab credit.
- **16:9 Dark-Stage Presentation Standards:** Enforces keynote slide deck specifications using high-contrast `#0d1038` background, WCAG AA compliance, HUD progress telemetry, and zero-external-dependency self-contained HTML/SVG delivery.
- **Dedicated Training Materials Repository (`ai-training-materials`):** Establishes a dedicated version-controlled Git repository at `~/Developer/ai-training-materials` consolidating all instructional slide decks, master syllabi, lab exercise sandboxes, devcontainer configurations, and facilitator runbooks under release-tagged semantic versioning (`v1.0.0` per cohort baseline).
- **Weekend-First Cohort Operations & Dedicated Lab Facilities:** Establishes weekend-first intensive scheduling (Saturday modules for Cohorts A & B, Sunday Capstone and Open Lab) using a reference facility architecture (dual 85" 4K displays, isolated 10GbE networking, and on-premise Ollama/OmniRoute edge compute documented in presentation and facilitator materials). Infrastructure follows a dual-profile policy: a local zero-egress facility profile is canonical for live cohort delivery, and an approved cloud-backed preparation/development profile is permitted only for deterministic artifact generation and pre-seeding local mirrors — never for direct learner runtime.
- **100-Point Competency Rubric & CEIP Certification:** Formalizes an objective 100-point grading matrix (40 pts lab gates across each learner's 8 assessed practical modules: Common Core C01–C04, the learner's track-specific advanced pair D05/D06, B05/B06, or Q05/Q06, and shared capstones X01/X02; 40 pts capstone delivery; 20 pts security/hygiene) and establishes the Certified Enterprise AI Practitioner (CEIP) and AI Champion credentials.

### Explicit Non-Goals
- **No Production Code Alterations:** This proposal does not modify application code, runtime endpoints, or business logic in `go-microservices`, `mcp-router`, or `agent-core`.
- **No Replacement of Human Oversight:** AI tools are specified strictly as augmentative pairing and verification engines; human code review and architectural ownership remain mandatory.
- **Approved Cloud Prep Profile (Non-Learner):** An approved cloud-backed preparation profile may be used exclusively for deterministic artifact generation (slide compilation, PDF export, seed-manifest resolution) and pre-seeding local mirrors. This profile is never exposed to learner runtime, never attached to lab devcontainers, and never routes learner prompts or agent actions. All cloud usage must be logged, scoped, and approved by the Lead Enterprise Architect.
- **Physical Hardware Deployment Excluded from Materials Repository:** Physical hardware provisioning (on-premise compute racks, 10GbE network switches, dual 4K monitors, Cat 6A cabling, mechanical keyboards, and TA Command Station physical hardware) is strictly excluded from the deployment deliverables and acceptance gates of `ai-training-materials`. Physical infrastructure is documented exclusively as illustrative reference architecture within presentation slide decks and facilitator guides, not as deployable software infrastructure.

## Capabilities

### New Capabilities
- `enterprise-ai-training`: Formal specification governing the enterprise AI curriculum architecture, role tracks, capstone triad delivery, deterministic sandbox verification, presentation standards, weekend cohort operations, the dedicated training materials repository, and CEIP certification.

### Modified Capabilities
<!-- None: Greenfield training specification; no existing requirements modified. -->

## Impact

### Affected Ownership Boundaries
- **Lead Enterprise Architect:** Owns technical alignment, multi-agent orchestration patterns (Orca, OMP, Claude Code), and integration with workspace knowledge systems (`GitNexus`, `Graphify`, `LLM Wiki`).
- **Head of Quality Assurance:** Owns automated test gate criteria, CI evaluation pipelines, adversarial red-teaming standards, and lab grading verification.
- **Lead Business Analyst / Product Operations Lead:** Owns Gherkin/EARS specification standards, OpenSpec requirement quality, backlog dependency auditing workflows, and BA track governance.

### System & Infrastructure Impact
- **Compute & Facility Reference Architecture:** Presentation materials and slide decks include reference architecture diagrams illustrating an on-premise edge compute topology (Ollama and OmniRoute gateway); physical hardware procurement, cabling, and rack installation are external facility concerns and not deployment deliverables of the training materials repository.
- **Workspace Repositories:** Sandboxed lab branches across `go-microservices`, `realtime/frontend`, `agent-core`, and `openspec-store`.
- **Dedicated Materials Repository:** `~/Developer/ai-training-materials/` hosting all instructional slide decks, lab templates and exercise sandboxes, devcontainer configurations, the master syllabus, and evaluation benchmarks, release-tagged (`v1.0.0`) and synchronized with the `openspec-store` governance plane.
- **Dual-Profile Infrastructure Policy:** The program maintains two explicitly separated infrastructure profiles. The **Local Zero-Egress Facility Profile** is the sole canonical runtime for live cohort labs, exercises, and assessments; it operates fully offline on the 10GbE subnet with no non-loopback egress. The **Approved Cloud-Backed Preparation Profile** is restricted to pre-cohort deterministic artifact generation, seed-manifest resolution, and mirror pre-seeding; it never routes learner prompts, never attaches to lab devcontainers, and never serves live exercises. Cloud profile usage is logged, time-bounded, and approved per session by the Lead Enterprise Architect.
- **Personnel Enablement:** 100+ engineers, product managers, and QA specialists trained across 4 sequential cohorts.
