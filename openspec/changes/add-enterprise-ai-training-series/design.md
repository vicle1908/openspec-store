## Context

See `proposal.md` for business motivation and high-level scope.

The workspace architecture integrates several mature pillars:
- **`mcp-router`:** Centralized gateway aggregating 13 MCP servers and 142 tools across GitNexus, AgentMemory, Graphify, and LLM Wiki.
- **`GitNexus`:** Code intelligence engine providing AST call graphs, symbol references, and interprocedural taint/impact analysis across 20+ repos.
- **`Graphify`:** Architectural knowledge graph mapping directory dependencies and god-node clusters.
- **`AgentMemory`:** Cross-session memory plane capturing observations, architectural decision records (ADRs), and session handoffs.
- **`LLM Wiki`:** Curated markdown knowledge base at `~/Developer/wiki/` serving canonical engineering patterns.
- **`OpenSpec` (`openspec-store`):** Structured specification governance system enforcing strict proposal, spec, design, and task verification lifecycles.
- **`ntu-keynote`:** Established 16:9 dark-stage visual presentation standards (`#0d1038` background, high-contrast WCAG AA typography, self-contained SVG/HTML5 delivery).

While these capabilities exist in production, engineering teams have historically lacked a unified, role-tailored curriculum to operate them cohesively, resulting in fragmented tool adoption and unverified AI code generation.

## Goals / Non-Goals

**Goals:**
- Design a modular 4-Tier curriculum structure (Tier 0 Common Core, Tiers 1–3 Role Tracks, Tier 4 Capstone Triads) delivering 24 distinct 120-minute sessions.
- Formalize the 2026 architectural shift: transition from bloated monolithic MCP servers to lean on-demand Agent Skills backed by native CLI execution.
- Establish the Multi-CLI Matrix and hierarchical Director-Worker orchestration patterns using Orca worktrees and PTY controls.
- Specify the facility reference architecture and presentation materials illustrating the presentation rig and on-premise compute topology.
- Establish the 100-point objective competency evaluation framework and Certified Enterprise AI Practitioner (CEIP) certification.

**Non-Goals:**
- Modifying underlying backend production services or database schemas in `go-microservices`.
- Replacing existing CI/CD production deploy pipelines.
- Developing new proprietary LLM foundational models; training relies on established models served via OmniRoute and local Ollama.
- Physical hardware deployment: procurement, physical rack installation, 10GbE network switch configuration, monitor mounting, and workstation hardware are outside the deployment deliverables of `ai-training-materials`. These are included only as presentation materials and illustrative slide diagrams.

## Decisions

### Decision 1: 4-Tier Modular Curriculum Architecture
```
                               CURRICULUM TOPOLOGY
   ┌────────────────────────────────────────────────────────────────────────────┐
   │                       TIER 0: COMMON CORE (All Roles)                      │
   │      C01: LLM Foundations & Limits   │   C02: Schemas & Prompt Eng         │
   │      C03: Context Eng & MCP Gateway  │   C04: AI Security & OWASP          │
   └─────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 ▼                       ▼                       ▼
   ┌───────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐
   │         DEV TRACK         │ │         BA TRACK          │ │         QA TRACK          │
   │ D01: In-IDE AI Pairing    │ B01: AI Product Discovery │ Q01: AI Test Matrix Des.  │
   │ D02: CLI Coding Agents    │ B02: Gherkin / EARS AC    │ Q02: Playwright/Pytest    │
   │ D03: AGENTS.md & MCP      │ B03: Machine-Read Specs   │ Q03: Context Test Gaps    │
   │ D04: AST Refactoring      │ B04: Backlog Dep. Audits  │ Q04: LLM App Evals        │
   │ D05: Spec-Driven Dev      │ B05: Collaborative SDD    │ Q05: Autonomous Self-Heal │
   │ D06: Multi-Agent CI Evals │ B06: AI PRDs & Ethics     │ Q06: Red Team Fuzzing     │
   └───────────────────────────┘ └───────────────────────────┘ └───────────────────────────┘
                                         ▼
   ┌────────────────────────────────────────────────────────────────────────────┐
   │                   TIER 4: CROSS-FUNCTIONAL CAPSTONE TRIADS                 │
   │       X01: Triad Micro-Feature Delivery (BA -> Dev -> QA via SDD)          │
   │       X02: AI Incident Response, Chaos Debugging & Postmortem Defense      │
   └────────────────────────────────────────────────────────────────────────────┘
```
- **Rationale:** Separating foundations (Tier 0) from role depth (Tiers 1–3) guarantees all employees share a common security and vocabulary baseline before specializing. Culminating in cross-functional Triads of 4 members (one Business Analyst, two Developers, and one QA Engineer) aligns with the organizational cohort ratio (~14–16 Devs, 6–7 BAs, 5–6 QAs forming 5–6 triads) and mirrors real enterprise delivery.
- **Alternatives Considered:** Role-siloed training from Day 1. Rejected because siloed training perpetuates communication barriers between product specifications and test generation.

### Decision 2: The 2026 Architectural Shift — Lean Skills vs Large MCP Servers
- **Context:** Tool-schema overhead is architecture- and workload-dependent. The 10,000–25,000-token and 1.5–3.0-second figures are illustrative un-cached benchmark hypotheses, not universal measurements; caching, model, hardware, tool count, and prompt shape change results.
- **Decision:** Shift from monolithic MCP tool definitions to **Dynamic On-Demand Agent Skills (`SKILL.md`)** paired with fast local CLI binaries (`orca`, `openspec`, `tvly`, `bdata`).
  - Skills remain dormant until triggered by prompt intent or skill name; active-skill size is an illustrative target, to be measured locally.
  - Retain MCP strictly for stateful streaming, persistent socket connections, and centralized gateway mediation (`mcp-router`).
- **Trade-off:** Requires developers to understand CLI command arguments rather than relying entirely on LLM function-calling auto-discovery. Mitigated by explicit CLI profile guides in Module D02.


### Decision 3: Multi-CLI Matrix & Hierarchical Orca Orchestration
```
                         ORCA DIRECTOR-WORKER TOPOLOGY
   ┌────────────────────────────────────────────────────────────────────────────┐
   │                               DIRECTOR AGENT                               │
   │                            (Claude 3.7 / Opus)                             │
   │              - Task DAG Decomposition   - File Inspection                  │
   │              - OpenSpec Verification    - Conflict Arbitration             │
   └─────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
   ┌───────────────────────────┐                   ┌───────────────────────────┐
   │      WORKER AGENT A       │                   │      WORKER AGENT B       │
   │       (`fast` Tier)       │                   │       (`good` Tier)       │
   │ Worktree: `feat-codegen`  │                   │ Worktree: `ast-refactor`  │
   │ Boilerplate & Test Scaff. │                   │ Complex Logic & Migration │
   └───────────────────────────┘                   └───────────────────────────┘
```
- **Architecture:** The Multi-CLI ecosystem (`claude`, `codex`, `hermes`, `omp`, `kimi`, `goose`, `opencode`, `orca`, `openspec`, research CLIs) is orchestrated via Orca:
  - **Isolated Git Worktrees (`orca worktree add`):** Eliminates `index.lock` collisions and branch checkout contention during concurrent agent runs.
  - **Director-Worker Hierarchy:** Director agents (`good` tier, e.g. Claude 3.7 Sonnet / Opus) decompose work and verify results by reading files directly; worker agents are partitioned into `fast` tier (Haiku / Flash for boilerplate) and `good` tier (complex algorithms and AST refactoring).
  - **Terminal Synchronization:** Director monitors and steers workers via `orca terminal read`, `orca terminal send`, and `orca terminal wait`.

### Decision 4: Weekend-First Cohort Schedule & Facility Presentation Reference Architecture
- **Decision:** Schedule the 24 modules across weekend intensives (Saturday 255-minute windows for Cohort A 08:30–12:45 and Cohort B 13:45–18:00, preserving one-hour turnover/lunch and existing 120m+15m+120m arithmetic; Sunday Open Lab 09:00–12:00 and Capstone Triads 13:30–17:30).
- **Facility Presentation Reference Architecture:**
  Physical hardware specifications (dual 85" 4K displays, 28 student pods with dual 4K monitors and mechanical keyboards, 10GbE subnet, on-premise edge compute rack) are provided as presentation materials and illustrative reference architecture in lecture slide decks and facilitator guides, rather than deployable repository deliverables. The deployment deliverables of `ai-training-materials` are strictly software- and container-based (Docker Compose configs, devcontainers, slide decks, lab starter files, and deterministic verifiers). Physical procurement and facility installation remain external operational concerns.
### Decision 5: 100-Point Objective Competency Matrix & CEIP Certification
- **Evaluation Breakdown:**
  - **Lab Verification Gates (40 pts):** Exactly 8 assessed practical modules per learner tailored to their enrolled track, awarding 5 pts each (8 modules $\times$ 5 pts = 40 pts). The designated fixture-gate command MUST exit code `0`; this proves only that the designated fixture gate passed, not general LLM/agent quality or safety. Subjective grading is strictly prohibited.
    - **Developer Track:** Common Core (`C01–C04`) + Advanced Dev (`D05`, `D06`) + Capstones (`X01`, `X02`) = 8 assessed modules (40 pts).
    - **Business Analyst Track:** Common Core (`C01–C04`) + Advanced BA (`B05`, `B06`) + Capstones (`X01`, `X02`) = 8 assessed modules (40 pts).
    - **Quality Assurance Track:** Common Core (`C01–C04`) + Advanced QA (`Q05`, `Q06`) + Capstones (`X01`, `X02`) = 8 assessed modules (40 pts).
    - *Formative Scope:* Foundational role modules (`D01–D04`, `B01–B04`, `Q01–Q04`) and non-enrolled track modules are mandatory instructional and formative exercises required for course completion, but carry zero rubric points. Learners are never penalized for or required to attend modules outside their assigned track.
  - **Capstone Triad Performance (40 pts):** Evaluated in Session X01 for each 4-member triad (1 BA + 2 Devs + 1 QA: BA spec precision 10 pts, Dev implementation/coverage 15 pts, QA automated verification 10 pts, cycle time 5 pts).
  - **Governance & Security Hygiene (20 pts):** Zero committed secrets (verified via `gitleaks`), prompt instruction hygiene, and successful incident postmortem resolution in X02.
- **Certification:**
  - $\ge 80$ pts: Certified Enterprise AI Practitioner (CEIP).
  - $\ge 95$ pts: Enterprise AI Champion / Facilitator (certified to serve as subsequent cohort TA and department AI Reviewer).

### Decision 6: Dedicated Training Materials Repository Architecture
- **Context:** Training assets were previously scattered across workspace repositories and local directories, creating drift between slide decks, lab fixtures, and the governing specification, and preventing immutable cohort baselines.
- **Decision:** Consolidate all instructional assets into a dedicated version-controlled Git repository at `~/Developer/ai-training-materials`, giving every cohort an identical, hash-pinned materials snapshot.

**Repository layout:**
```
ai-training-materials/
├── .devcontainer/       # Pinned Docker devcontainer definitions (Go, Python, Node)
├── docs/                # Master syllabus, facilitator runbooks, assessment rubrics
├── slides/              # Standalone HTML5 16:9 presentations & WOFF2 fonts
├── labs/                # 24 modular sandbox exercise directories & test fixtures
│   ├── core/ (C01-C04)
│   ├── dev/ (D01-D06)
│   ├── ba/ (B01-B06)
│   ├── qa/ (Q01-Q06)
│   └── capstones/ (X01-X02)
├── scripts/             # Local verification scripts, chaos injection harnesses
└── README.md            # Quickstart, course map, and local environment preflight
```

- **Synchronization with `openspec-store`:** The living curriculum specification (requirements, scenarios, evaluation rubric) remains governed exclusively by `openspec-store` under this change; `ai-training-materials` consumes it as the downstream asset plane. Each release tag records the governing change hash so every slide, lab, and rubric in the materials snapshot is traceable to the exact specification revision it implements. The repository never edits `openspec/` artifacts directly.
- **Release Tagging:** Cohort baselines are cut as annotated semantic-version tags — `v1.0.0` for the initial cohort baseline, with minor bumps for curriculum revisions (`v1.1.0`) and patch bumps for errata such as slide typo or fixture corrections (`v1.0.1`). Facilitators clone by tag, guaranteeing 28 identical workstation baselines and an immutable evidence chain for certification audits.
- **Devcontainer Isolation:** Each lab stack (Go, Python, Node) ships a pinned devcontainer definition under `.devcontainer/` with digest-pinned base images and local mirror package caches. Students open labs in isolated containers, so workstation drift, host toolchain versions, and OS permission locks cannot leak into lab verification gates; the lab's exit-code-`0` gate always runs against the pinned toolchain.
- **Alternatives Considered:** Distributing materials via shared drives or cloud folders. Rejected because neither provides versioned history, immutable per-cohort baselines, deterministic reproducibility, or offline self-containment required by the 16:9 zero-dependency presentation standard.
### Decision 7: Advanced Developer Curriculum Embeddings (D05 Runtime & D06 Harness)
To provide deep autonomous runtime and execution harness engineering without expanding total course length beyond the 24-session baseline, these two advanced domains are embedded directly into existing Developer track modules D05 and D06:

#### Subsection 7.1: Autonomous Agent Runtime Engineering (Embedded in Module D05)
- **Scope & Boundary:** Embedded within Module D05 (Spec-Driven Development) to connect specification planning directly to typed autonomous runtime construction, without creating a separate session.
- **Workspace Pattern:** A typed Pydantic AI `Agent` uses `AgentRuntimeDeps`, output models, `@agent.tool` contracts, retries, validation, timeouts, and safe/idempotent tools; `ToolRegistry` supplies tools. `WorkflowBuilder`/`WorkflowEngine` composes LangGraph `StateGraph` nodes with `PostgresSaver`/`AsyncPostgresSaver`, `thread_id`, `interrupt()`/`Command` resume, `RetryPolicy`/`CachePolicy`, and `Send` fan-out. `skill_system` and telemetry/evaluation integrations provide controlled context and evidence.
- **Lab Sandbox (`labs/dev/D05`):** In 60 minutes learners build a typed triage/review agent and checkpointed fan-out graph with HITL approval, deterministic fixture gate, and trace/eval evidence.
- **Dependency & Version Policy:** Training follows workspace pins (`pydantic-ai>=2.31,<2.33`, `pydantic-ai-harness[dynamic-workflow]>=0.23,<0.24`, `langgraph>=1.2.9,<1.3`, `pydantic-evals>=2.18,<3`). Upstream releases (e.g. `pydantic-ai` 2.40.0 from https://ai.pydantic.dev, `langgraph` 1.2.11 from https://github.com/langchain-ai/langgraph) are research-only and unverified for workspace compatibility; training strictly uses workspace pinned versions.

#### Subsection 7.2: Harness Engineering & Reliable Agent Execution (Embedded in Module D06)
- **Scope & Boundary:** Embedded within Module D06 (Multi-Agent CI Evaluations) to focus on engineering the execution harness surrounding an agent—model/context assembly, tools, lifecycle hooks, permission policy, progressive-disclosure skills, sandbox/worktree isolation, deterministic gates, structured evidence, and telemetry—without duplicating multi-agent orchestration or adding a standalone session.
- **Workspace Pattern:** Grounded in `agent-core/_ai/hooks.py`, `skill_system`, `ToolRegistry` authority, observability, and OMP/Claude harness conventions.
- **Lab Sandbox (`labs/dev/D06`):** Learners implement pre-tool denial, post-tool audit, stop gate, one on-demand `SKILL.md`, isolated fixture/worktree execution, and pytest/ruff/OpenSpec exit-0 evidence; an intentional failure proves no commit.
- **Trade-off:** Additional control-plane code increases setup overhead, but ensures permissions, context assembly, and completion claims are inspectable and reproducible.

#### Subsection 7.3: Knowledge Infrastructure Governance (Embedded in Module C03)
- **Placement & Boundary:** Unlike the Developer-only embeddings in 7.1–7.2, this subsection belongs to Common Core C03 for Dev, BA, and QA. Integrate it into C03's existing 120-minute agenda and 60-minute lab; retain the 24-session baseline and 18 role-track modules. Extend the existing retrieval exercise with governance checkpoints rather than repeating GitNexus symbol/blast-radius queries, Graphify architecture queries, ADR retrieval, or context-bundle assembly.
- **LLM Wiki Curation:** Use an isolated copy of `~/Developer/wiki/`. Learners act as article authors: `wiki_search` discovers existing coverage, `wiki_read` checks sources and related pages, and `wiki_ingest` creates or updates the reviewed article. A designated domain owner reviews technical accuracy and provenance; the facilitator verifies the review evidence before acceptance. Apply `SCHEMA.md` frontmatter, related-link, word-limit, review-age, and stale-archive rules; run the workspace verifier `~/Developer/wiki/scripts/wiki-lint.py` against the sandbox copy. Human review and article provenance remain required even when lint passes.
- **AgentMemory Lifecycle:** Access the memory system through MCP tools and the `agentmemory-hooks`, `agentmemory-mcp-tools`, `recall`, and `forget` skills, not an assumed `agent-memory` repository. Recall before starting, inspect an automatically hook-captured observation, and deliberately save the new lesson with its session/source identifiers. Distinguish capture from consolidation or promotion into durable memory: facilitators preconfigure the supported promotion flow and learners verify retrieval from a subsequent session. Automatic capture does not imply opt-in compression or context injection is enabled. Mark superseded ADRs deprecated with a replacement link; show the exact disposable fixture and obtain explicit confirmation before forgetting it, then verify recall excludes it while preserving non-sensitive audit evidence and the replacement.
- **Index Freshness & Provenance:** Teach the workspace `freshness-reporting-contract` using `~/Developer/scripts/knowledge-refresh/knowledge-status.sh` and `~/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh --check`. Record repository identity, HEAD, indexed revision, source paths, and the check result before and after rebuilding only the affected sandbox index. Freshness requires indexed revision equality with HEAD, not a recent timestamp or successful refresh exit; unequal revisions are stale, absent revision evidence is unknown, and a HEAD change during refresh requires another check. Keep operational states such as dirty, skipped, or locked separate from freshness and never relabel them as clean proof.
- **Graphify Update Flow:** Inspect the sandbox's post-commit/post-merge refresh hooks and the resulting `graphify-out/` provenance. Demonstrate the manual recovery command `graphify update .` from the sandbox repository when a hook is absent or skipped, then rerun the freshness checks and verify recorded revision equality. This teaches index maintenance, not another architecture-query exercise. Pre-stage stale-index and memory fixtures to keep all governance checkpoints inside C03; do not modify production wiki articles, indexes, or memories during training.

### Decision 8: Computer-Use, Browser Agents & Device Control
- **Context:** The current curriculum emphasizes text, AST, and scripted DOM workflows but lacks practical coverage of visual browser agents, computer-use, and mobile device control. Modern agentic engineering also requires agents to perceive and act through GUIs. The cited research and gap-analysis documents are historical pre-integration baselines; the governing decisions below are authoritative and incorporate their applicable findings without treating those reports as current implementation state.
- **Decision:** Embed device-control across seven existing modules (C04, D02, D06, B02, B06, Q02, and Q05) through subsections 7.4–7.8 below, not new sessions. Preserve the 24-session baseline, each module's existing timebox, and eight assessed modules per role at five points each (40 lab points). Rebalance existing exercises instead of introducing additional assessment modules.
- **Perception Modalities:** Teach DOM/accessibility-driven control through Playwright MCP and agent-device snapshots; screenshot-driven vision through Claude Computer Use's screenshot/action loop; and hybrid control using structured observations with visual fallback and Set-of-Marks overlays. Orca computer-use provides the workspace example of OS/window-level accessibility-tree inspection. Observations ground actions, and a fresh observation verifies each resulting state.
- **Browser Agent Stack:** Browser Use (Python, MIT; official docs: https://docs.browser-use.com/) supplies autonomous multi-step tasks through `Agent(task=..., llm=..., browser=...)`; Playwright MCP (official repository/docs: https://github.com/microsoft/playwright-mcp and https://playwright.dev/) exposes structured accessibility-driven browser tools with optional vision. Teach sensitive-data placeholders, explicit vision configuration, and CDP attachment for advanced debugging only against dedicated disposable browser profiles. Browser-origin allow-lists are not security boundaries and do not establish redirect containment.
- **Mobile/Device Stack:** agent-device (TypeScript/Node.js, MIT; canonical repository: https://github.com/callstack/agent-device; official docs: https://oss.callstack.com/agent-device/) supplies a unified CLI, MCP server, and Node.js API for iOS, Android, HarmonyOS, TV, web, macOS, and Linux, using accessibility snapshots with refs/selectors. Mobile execution is a formative Q02 exercise; Q05 does not assess mobile execution. Broader platform coverage and mobile comparison are lecture/demo or optional, unassessed material.
- **Safety Architecture — Three Separate Boundaries:** Execution isolation constrains where agent-executed processes may write and communicate: one disposable environment per learner, synthetic data, resettable application state, and enforced filesystem/egress restrictions at the OS/network boundary. No production profiles, credentials, or existing user browser sessions are attached. Data exposure to the model is controlled independently through screenshot suppression and sensitive-data placeholders; placeholders do not redact screenshots, and local/profile isolation does not prevent screenshots from reaching a hosted model. Authorization to act independently requires point-of-action confirmation for consequential submit/delete/purchase operations, even inside an isolated environment. A display mechanism is not an isolation boundary. See Claude computer-use safety guidance (https://docs.anthropic.com/en/docs/agents-and-tools/computer-use) and Chrome remote-debugging security guidance (https://developer.chrome.com/blog/remote-debugging-port).
- **Containment Preflight:** Before enabling tools, prove that forbidden egress, forbidden file writes, wrong-profile attachment, and actions with denied approval are blocked using synthetic targets. A failed or missing check prevents the exercise from starting. Tool-origin filters and model instructions do not replace OS/network enforcement. Visual indirect prompt injection is untrusted page/image data, never authority to act.
- **Trade-off:** Q05's flagship content grows substantially; complementary safety, coding-loop, registry, acceptance, and governance instruction resides in C04, D02, D06, B02, and B06 rather than being duplicated. Q02 supplies foundational runtime inspection so Q05 can focus its existing lab time on autonomous exploration and evidence.

### Decision 9: Dual-Profile Infrastructure Policy
- **Context:** The program requires deterministic artifact generation (slide compilation, PDF export, seed-manifest resolution) and mirror pre-seeding that may need cloud-backed tooling, but live cohort labs, exercises, and assessments must run fully offline on the local 10GbE facility network. These are conflicting constraints.
- **Decision:** Maintain two explicitly separated infrastructure profiles with hard boundaries:
  - **Local Zero-Egress Facility Profile (Canonical for Live Cohort):** All learner-facing labs, exercises, assessments, and agent runtime operations run exclusively on the local 10GbE subnet with on-premise Ollama and OmniRoute. No non-loopback egress is permitted. This profile is the sole runtime for live cohort delivery and the only environment where learner prompts, agent actions, and verification gates execute.
  - **Approved Cloud-Backed Preparation Profile (Non-Learner):** Permitted exclusively for deterministic artifact generation (slide deck compilation, PDF export, seed-manifest dependency resolution), pre-seeding local mirrors with resolved packages/images, and generating cohort baseline artifacts. This profile never routes learner prompts, never attaches to lab devcontainers, and never serves live exercises. Cloud profile usage must be logged, time-bounded, and approved per session by the Lead Enterprise Architect.
- **Security Constraints:**
  - The cloud prep profile MUST NOT be accessible from learner workstations during live cohorts.
  - The cloud prep profile MUST NOT be referenced in any lab exercise, verification gate, or student-facing script.
  - All cloud-backed artifact outputs MUST be verified for integrity (hash, manifest) before import into the local facility profile.
  - The local facility profile MUST pass a zero-egress gate (`scripts/verify-zero-egress-resolution.sh`) before any live cohort session begins.
- **Alternatives Considered:** Single-profile architecture with internet filtering. Rejected because firewall rules are insufficient to guarantee zero egress under concurrent student load, and filtered environments create unreliable verification gates.
  - **Risk:** Cloud prep profile drift into learner-accessible scope. *Mitigation:* Automated preflight check (`scripts/verify-cloud-profile-isolation.sh`) verifies the cloud profile is unreachable from learner subnets before every cohort session. Fail-closed: session cannot begin if isolation check fails.

- **Q05 runtime contract:** Browser Use materials and the Q05 verifier run in the Python materials repository (`~/Developer/ai-training-materials`, `uv run python ...`). The realtime frontend fixture remains a Node runtime target; it is not a dependency installation source or an alternative verifier runtime. Node/TypeScript tooling is used only where a task explicitly names the realtime frontend or agent-device.
- **Q05 official references:** Browser Use (https://docs.browser-use.com/), Playwright MCP (https://github.com/microsoft/playwright-mcp), and agent-device (repository: https://github.com/callstack/agent-device; docs: https://oss.callstack.com/agent-device/) are the governing current references; no unverified version claim is implied.

#### Subsection 7.5: Device Control Safety & Sandboxing (Embedded in Module C04)
- **Placement & Content:** Extend OWASP LLM08 Excessive Agency with disposable environments and enforced OS/network filesystem/egress restrictions, independent model-data exposure controls, consequential action gates, and visual indirect injection defense. Keep production profiles, credentials, and existing browser sessions out of the exercise.
- **Lab:** Run preflight negative probes for forbidden egress, file write, wrong-profile attachment, and denied action approval before enabling tools. Compare screenshot suppression with sensitive-data placeholders using synthetic values, then present invisible CSS text and image-payload injection fixtures. Record blocked actions and unchanged protected state; any failed containment check prevents exercise startup.

#### Subsection 7.6: Visual Browser Feedback in Developer Loops (Embedded in Modules D02 & D06)
- **D02:** Incorporate coding agents invoking browser tools during the Code phase to verify the actual UI: observe, propose an action, pass policy/approval checks, act, then obtain fresh visual or accessibility evidence. Contrast Playwright MCP with Claude Computer Use and Orca OS/window-level inspection; CDP attaches only to the approved disposable browser.
- **D06:** Extend the existing harness tool registry to govern browser/device adapters through pre-tool containment and authorization checks and post-tool evidence capture. Separate execution isolation, model-data exposure policy, and authorization to act; record tool denials without enabling an alternative tool path to bypass them. Reuse the existing harness lab rather than creating another runtime framework.

#### Subsection 7.7: Visual Acceptance Criteria & RPA Governance (Embedded in Modules B02 & B06)
- **B02:** Specify UI-agent behavioral criteria in Gherkin, including observable initial/final state, visual or accessibility evidence, forbidden redirects, hidden prompt injection, and safe stopping when approval is denied. Specify outcomes rather than brittle coordinates or assumed deterministic model decisions.
- **B06:** Extend governance for RPA/web agents with ownership of allowed application scope, data exposure, consequential action approvals, trace retention, and reset/recovery procedures. Distinguish deployment isolation from permission to disclose screenshots or perform transactions. Reuse synthetic local fixtures and the common containment policy instead of production sessions.

#### Subsection 7.8: Cross-Platform Device Inspection (Embedded in Module Q02)
- **Placement & Content:** Evolve static Playwright Page Object Model generation into runtime agent browser control through accessibility observations, and introduce agent-device CLI/MCP/API for mobile inspection. Retain existing test-generation foundations; this is a formative exercise, not an additional assessed module.
- **Lab:** In a preflight-approved environment, open a synthetic app on an iOS simulator or Android emulator, capture an accessibility snapshot, press a grounded ref, and obtain a fresh snapshot plus screenshot evidence. Reset state for repeatability and verify the expected before/after diff deterministically; agent action selection itself remains nondeterministic. Reuse the trace/evidence pattern in Q05's flagship exploration exercise.

## Risks / Trade-offs

- **Risk: Student Environment Drift:** Local laptops may exhibit varying Node/Python versions or OS permission locks.
  - *Mitigation:* The dedicated lab provides standardized student workstations with pre-provisioned Docker devcontainers and package caches on the local 10GbE network.
- **Risk: LLM Gateway Saturation:** 28 students simultaneously prompting frontier models during 60-minute coding sprints could trigger cloud API rate limits.
  - *Mitigation:* The local edge rack runs high-throughput Ollama embeddings and OmniRoute caching proxy, with fallback chains distributed across enterprise keys.
- **Risk: Audit Tax Relapse:** Learners may revert to unverified copy-pasting after completing the course.
  - *Mitigation:* Enterprise AI Champions serve as mandatory reviewers on pull requests touching production repos, enforcing `AGENTS.md` and OpenSpec compliance.
- **Risk: Cloud Prep Profile Leakage into Learner Scope:** A misconfigured bridge between the cloud prep profile and the local facility profile could expose learners to non-zero-egress network paths or unvetted cloud endpoints.
  - *Mitigation:* Network-level isolation between the cloud prep profile and the 10GbE learner subnet, automated preflight isolation verification (`scripts/verify-cloud-profile-isolation.sh`), and hard-fail session gating. Cloud profile credentials and endpoints are never stored in learner-accessible locations.
