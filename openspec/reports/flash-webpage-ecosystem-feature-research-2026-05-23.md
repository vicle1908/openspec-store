# Flash Webpage Ecosystem Feature Research — 2026-05-23

## Scope

Research current supported features for a future OpenSpec update covering a
flashy ecosystem webpage / presentation layer for the TDT workspace.

Sources reviewed:

- `docs/presentation.html`
- `~/.agents/skills/frontend-slides/SKILL.md`
- `~/.agents/skills/frontend-slides/STYLE_PRESETS.md`
- `README.md`
- `docs/CURRENT-FLOW.md`
- `jira-daily-reports/README.md`
- `jira-kanban-from-spreadsheet/README.md`
- `jira-epic-report/README.md`
- `tdt-core/README.md`
- `webhook-receiver/README.md`
- `browser-cli/README.md`
- `openspec/changes/jira-reports-consolidation/{spec,design,tasks}.md`
- `openspec/reports/jira-sprint-report-ecosystem-validation-2026-05-23.md`

---

## 1. Current implementation approaches

### 1.1 Existing user-facing artifact

Current artifact: `docs/presentation.html`

Observed implementation style:

- Single self-contained HTML file
- Inline CSS only
- No application build step
- Long-scroll sectioned landing page, not slide-controller UX
- Heavy use of cards, metric rows, tables, architecture boxes
- Responsive CSS breakpoint present (`max-width: 768px`)
- Google Fonts runtime dependency (`Inter`, `JetBrains Mono`)
- Dark gradient visual system
- Static hand-authored content

### 1.2 Skill-driven target format

`frontend-slides` requires a different contract than the current deck:

- zero-dependency single HTML file by default
- every slide must fit one viewport
- no internal scrolling
- keyboard, wheel, and touch navigation
- reveal-on-enter animations
- reduced-motion support
- progressive disclosure instead of dense wall-of-text

Style presets available from the skill:

- Bold Signal
- Electric Studio
- Creative Voltage
- Dark Botanical
- Notebook Tabs
- Pastel Geometry
- Split Pastel
- Vintage Editorial
- Neon Cyber
- Terminal Green
- Swiss Modern
- Paper & Ink

Best fit for this ecosystem: `Neon Cyber`, `Terminal Green`, or `Electric Studio`.

---

## 2. Supported ecosystem features worth showing

### 2.1 Shared infrastructure

#### `tdt-core`
Supported:

- environment loading from `~/.tdt/.env`
- Jira client factory via `atlassian-python-api`
- GitLab client factory via `python-gitlab`
- shared domain models
- common auth/bootstrap layer for the ecosystem

#### `jira-skill`
Supported:

- JQL query builder
- board management
- sprint operations
- issue CRUD / bulk ops
- GitLab integration
- typed configs + resilience patterns

### 2.2 Jira automation surface

#### `jira-kanban-from-spreadsheet`
Supported live flow:

- parse sprint planning spreadsheet
- validate rows into typed models
- generate dynamic cross-project JQL from issue keys
- update existing filter by ID (`15113`)
- verify board/filter alignment (`1067`)
- template support
- JSON output
- `--post-sync-reports` chaining
- live filter/board sync automation

#### `jira-daily-reports`
Supported command surface:

Reporting commands:

- `standup`
- `missing-info`
- `blocked`
- `velocity`
- `platform`
- `priority`
- `sprint-health`
- `code-review`
- `wip`
- `sprint-sheet`
- `dashboard`
- `cycle-time`
- `wip-age`

Operational commands:

- `run-all`
- `schedule`
- `remind`

Notable supported output modes:

- terminal
- markdown
- JSON
- Google Sheet
- native Jira dashboard

Special validated sprint-sheet features:

- estimation enrichment
- start date enrichment
- end date enrichment
- logwork enrichment
- missing vs unavailable semantics
- sprint-level summary / narrative
- graceful fallback on non-sprint boards

### 2.3 Epic analytics

#### `jira-epic-report`
Supported:

- epic generation
- list epics
- dashboard mode
- insights mode
- risk analysis
- resource tracking
- timeline analysis
- sprint alignment
- multi-format export (markdown / JSON / HTML / PDF)
- per-epic navigation pages

### 2.4 GitLab / review automation

#### `webhook-receiver`
Supported:

- GitLab MR webhook intake
- multi-CLI ensemble review pipeline
- worktree-based isolation
- parallel CLI execution
- dedup + confidence scoring
- coverage scanner
- health checks
- launchd runtime deployment
- production FastAPI service on port 8080

### 2.5 Browser + document handling

#### `browser-cli`
Supported:

- authenticated browser downloads
- CDP attach mode
- storage-state mode
- profile capture mode
- PDF/DOCX → markdown extraction

### 2.6 Operations / support tooling

Supported tooling shown in docs:

- `acli` for Jira/Confluence terminal ops
- `gws` for Google Sheets / Drive ops
- GitNexus for code intelligence / impact analysis
- Graphify for knowledge graph exploration
- Qi hybrid search for semantic search
- `glab` for GitLab CLI workflows

---

## 3. Feature maturity / status map

### Live / production-grade

- `webhook-receiver`
- `jira-kanban-from-spreadsheet`
- `jira-daily-reports`
- `tdt-core`
- `browser-cli`

### Stable / high-confidence

- `jira-epic-report`
- `jira-skill`

### Early / planned

- `ops-automation-suite`
- `jira-intelligent-reminders` real-time guard phase
- `jira-realtime-transition-guard`
- `microsoft-teams-integration`

### Historical / reference

- archived bash/acli daily-report skill
- old board/report docs preserved in archive only

---

## 4. What the flash webpage should support

### Mandatory content blocks

1. Hero / promise statement
2. Ecosystem architecture overview
3. Shared core / foundation section
4. Jira automation suite section
5. GitLab automation section
6. Analytics / reporting section
7. Supporting toolchain section
8. Status / maturity matrix
9. ROI / impact section

### Mandatory presentation behaviors

- self-contained HTML
- viewport-safe slide sizing
- no internal scrollbars
- keyboard / wheel / touch nav
- progress indicator
- reduced-motion support
- reveal animations
- responsive behavior on mobile + tablet

### Strongly recommended visual components

- stat chips / KPI blocks
- feature cards
- pipeline diagrams
- comparison tables
- metric bars
- architecture callout boxes
- one compact summary table per ecosystem family

---

## 5. Consistency notes / gaps

### Gaps in current `docs/presentation.html`

- no JS slide controller
- no reveal-on-enter logic
- no keyboard / touch nav
- no `prefers-reduced-motion` handling
- not viewport-strict (`min-height` sections, but not full slide system)
- too many dense sections for a true flash deck

### Consistency issues already visible

- root README still looks partially stale vs current Python ecosystem docs
- active source-of-truth is now spread across repo READMEs + `AGENTS.md` + `docs/CURRENT-FLOW.md` + OpenSpec reports
- `jira-daily-reports` is now Python-first and should not be described as bash-first in new spec text

---

## 6. Recommended OpenSpec spec direction

For the upcoming flash webpage spec, define it as:

> a zero-dependency, single-file, slide-based ecosystem showcase that presents the TDT Python/Jira/GitLab toolchain with live capability status, feature cards, and short narrative summaries.

### Suggested feature taxonomy for the spec

- Foundation
- Jira automation
- Reporting / analytics
- GitLab review automation
- Browser/document ops
- Shared toolchain
- Live status / maturity
- Impact / ROI

### Suggested wording rules

- describe features as `supported`, `live`, `stable`, `planned`, or `archived`
- label fallback behavior explicitly when a capability is partial
- distinguish implemented behavior from aspirational roadmap items
- avoid claiming native Jira sprint-report APIs that do not exist as a first-class REST surface

---

## 7. Bottom line

Current ecosystem supports a strong flash-webpage story already. The right spec should not invent new platform features; it should **curate and present** existing capabilities clearly, with maturity labels and a clean slide system.
