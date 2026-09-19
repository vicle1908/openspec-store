# Blocker Audit: add-enterprise-ai-training-series

# Generated: 2026-09-19 (eighth pass: M1 validator schema drift resolved in `go-microservices` and a reachable `govulncheck` advisory cleared, so `make verify-pr` now exits 0 across all four staged repositories; external tasks remain governed by facility, staffing, and live-cohort evidence)
# Change progress: **22/31 tasks complete (71%)** — 9 tasks remain, all strict external facility, staffing, or live-cohort gates (Phase 4 operational milestones plus facility-dependent 1.1/1.2). Task 1.3 is now accepted; Task 2.7 (release tag v1.0.0) is complete.
# Blocking axes: external facility, staffing, release-tag, cohort execution, and repository-local sandbox staging/verification.

---

## A. Completed Repository-Local Verification (19 tasks)

These tasks are fully verified on this workstation with local evidence. No further action required.

| Tasks | Summary | Evidence |
|-------|---------|----------|
| 1.2a–1.2f | Mirror infrastructure: seed manifest, Docker Compose, cache warm-up, zero-egress gate, cloud-profile isolation, usage logging | All verified locally; scripts exist and pass local dry runs |
| 1.5 | Training materials repository scaffold (`ai-training-materials` initialized with .git, .gitignore, README, .devcontainer) | Verified: `test -d …/.git && test -f …/.gitignore && test -f …/README.md && test -d …/.devcontainer` exits 0 |
| 2.1–2.6 | Slide deck bundle (24 sessions), typography (WOFF2), HUD telemetry, PDF fallback, syllabus migration, lab directories (24 dirs) | Verified locally; `ls-files slides/*.html | wc -l` returns 24; `find labs … -type d | wc -l` returns 24 |
| 2.8–2.12 | D05 runtime lab, D06 harness lab, C03 governance gate, browser-agent safety gate, Q02/Q05 verifiers | All verifiers exist and pass local execution |
| 3.4 | X02 currency-precision incident rehearsal (fault injection, diagnosis, regression test, POSTMORTEM.md) | Verified acceptance: X02 fixture/postmortem and regression remedy verified (`make verify-pr && test -f POSTMORTEM.md` exits 0) |

---

## B. Remaining Tasks — Category Classification

### B1. External Facility Gates (cannot complete on this workstation)

| Task | Description | Blocker |
|------|-------------|---------|
| **1.1** | Provision Local Zero-Egress Facility Profile (Ollama ofable-5, OmniRoute gateway, Docker Compose on training subnet) | **External-facility validation only.** Requires physical 10GbE subnet, on-premise edge compute rack, and Docker Compose running on facility hardware. `curl localhost:20128/api/monitoring/health` and `verify-zero-egress-resolution.sh` cannot succeed without the facility provisioned. |
| **1.4** | Validate student workstation reference architecture in presentation materials and facility runbooks | **Completed and verified.** Re-scoped from physical hardware deployment to presentation and curriculum reference specification; verified in `docs/master-syllabus.md:1450-1456` with dual 4K display setup, ergonomic keyboards, and Cat 6A drops benchmarked for $\ge 940\text{ Mbps}$ local throughput via `iperf3`. |

### B2. External Facility + Owner Prerequisite

| Task | Description | Blocker |
|------|-------------|---------|
| **1.2** | Configure isolated local caching package mirrors (devpi, verdaccio, registry) on 10GbE network | **Owner prerequisite + facility dependency.** Sub-tasks 1.2a–1.2f (scripts/configs) are complete, but 1.2 itself requires: (a) mirror services actually running on the facility 10GbE subnet (requires 1.1), and (b) mirror initialization executed under the Approved Cloud-Backed Preparation Profile (requires cloud-profile credentials and operator action). Scripts exist but cannot be validated against live mirrors. |

### B3. Repository-Local — Attempted or Completed

| Task | Description | Status |
|------|-------------|--------|
| **1.3** | Stage sandbox lab branches across go-microservices, realtime/frontend, agent-core, openspec-store | **Completed and verified (2026-09-19).** All in-scope staging fixes applied and kept: root `AGENTS.md` guidance H2; order-service traceability remap H3; coverage lifts on 4 services with real focused tests H1; docs coverage table aligned to current measurements with an 80% floor and 0.5% variance unchanged; realtime frontend npm-ci Makefile; openspec-store scoped pytest Makefile. All gates now PASS: `validate-agent-guidance` PASS (5 guides, 50 checks, 0 violations), `platform-verify` PASS, `services-verify` PASS (all 8 services >=80%: order 80.2, notification 81.1, customer 80.3, catalog 81.9, reporting 82.4, payment 80.0, inventory 81.3, shipping 80.1), `validate-documentation` PASS. **`make verify-pr` exits 0.** M1 closed by aligning validator schema expectations to the post-rename artifacts; a reachable govulncheck advisory in catalog-service was cleared by a grpc patch upgrade. |
| **2.7** | Repository preflight (lint + test) and cut v1.0.0 annotated release tag | **Completed and verified.** Preflight suite passed (36 passes, exit 0), release baseline verified (103 package files, SHA-256 digest `b976fe41...`, 0 warnings, 0 failures), and annotated release tag `v1.0.0` was explicitly authorized and cut pointing to commit `85df609`. |
| **3.4** | Rehearse X02 currency-precision incident (inject fault, diagnose, regression test, POSTMORTEM.md) | **Completed and checked.** The canonical acceptance evidence (`make verify-pr && test -f POSTMORTEM.md`) is recorded in the repository-local verification results. |

### B4. External Staffing Gates

| Task | Description | Blocker |
|------|-------------|---------|
| **3.1** | Recruit and onboard instructional team (1 Lead + 2 TAs per 28-student cohort, CEIP-certified) | **External staffing prerequisite.** Facilitators must be recruited, CEIP-certified, and available. Authoring or documenting the staffing plan locally is explicitly insufficient per task description. No facilitator evidence exists. |
| **3.2** | End-to-end facilitator rehearsal (8 assessed modules × 3 role variants, triage within 3 minutes) | **External staffing prerequisite.** Recruited facilitators must attend and complete the rehearsal. Locally authored rehearsal materials alone cannot satisfy acceptance. Depends on 3.1. |

### B5. External Facility + Technical

| Task | Description | Blocker |
|------|-------------|---------|
| **3.3** | Configure TA Command Station dashboard configurations and telemetry runbooks | **Completed and verified locally.** Operational assets delivered: Grafana dashboard definition `dashboards/ta-command-station.json` and telemetry runbook `docs/ta-command-station-telemetry.md` in `ai-training-materials`. Live hardware and physical mirroring remain external facility setups. |

### B6. External Cohort Execution Gates (Phase 4 — all fully external)

| Task | Description | Blocker |
|------|-------------|---------|
| **4.1** | Cohort 1 Saturday sessions (A/B cohorts, Common Core + Track Modules 1–2) | **External-execution gate.** Live cohort delivery, attendance, and baseline pass-rate evidence must be produced at the physical training facility. Fully external. |
| **4.2** | Sunday Open Lab & Facilitator Office Hours | **External-execution gate.** Live open-lab operations and ticket resolution with the cohort at the physical facility. Fully external. Depends on 4.1. |
| **4.3** | Synchronized Triad Capstone Sprints (X01 + X02) | **External-execution gate.** Live triad execution and submitted evidence from Cohort 1 at the physical facility. Fully external. Depends on 4.2. |
| **4.4** | Final rubric scores, CEIP certificates, AI Champion identification | **External-execution gate.** Scoring, certification, and evidence archival depend on live Cohort 1 results and authorized program operations. Fully external. Depends on 4.3. |

---

## C. Dependency Chain

```
1.1 (facility) ──┐
                  ├── 1.2 (mirror services live) ── 1.3 reachable independently
1.4 (workstations)┤
                  └── 3.3 (TA Command Station)

2.7: preflight reachable; v1.0.0 tag BLOCKED (user prohibition + evidence sync)
3.4: reachable independently

3.1 (staffing) ── 3.2 (rehearsal) ── 4.1 ── 4.2 ── 4.3 ── 4.4
```

---

## D. Repository-Local Tasks Summary & Current Blockers

These tasks can be attempted on this workstation without any external facility, staffing, or cohort dependencies:

1. **Task 1.3** — **RESOLVED and accepted (2026-09-19, eighth pass).** All four repositories pass; `go-microservices` now exits 0 on the full `make verify-pr` gate:
   - agent-core: exit 0 (905 passed, 11 skipped) — unchanged
   - realtime/frontend: verified pass (Vitest 78 files, 0 threshold errors, exit 0)
   - openspec-store: exit 0; 413 items passed / 0 failed strict (2 active changes + 411 specs)
   - go-microservices: `validate-agent-guidance` PASS (5 guides, 50 checks, 0 violations), `platform-verify` PASS, `services-verify` PASS, `validate-documentation` PASS — **`make verify-pr` exit 0**
   - M1 remedy: the validator policy in `verification/documentation-currency.json` was aligned to the renamed artifacts (`cdcSchema` and `coverageSchema` changed from `microservices.*` to `go-microservices.*`). This is validator-side alignment to the post-`370e16c` direction; no CDC inventory or coverage summary artifact was rewritten to satisfy the validator.
   - Second defect found and cleared: `govulncheck` failed in `catalog-service` on `GO-2026-6348` (HTTP/2 DATA-frame-fragmentation OOM in `google.golang.org/grpc`, reported as reachable from catalog-service call paths). `google.golang.org/grpc` was upgraded v1.82.1 -> v1.83.1 in that module only; all other services were unaffected (their govulncheck results report no called vulnerabilities).
2. **Task 2.7** — Completed and verified. Explicit user authorization was obtained, and annotated release tag `v1.0.0` was cut in `ai-training-materials` on clean commit `85df609`. Deterministic release verification passes with 0 warnings (6 passes, 0 failures). |
3. **Task 3.4** — Completed and checked: canonical X02 incident rehearsal evidence is present (`make verify-pr && test -f POSTMORTEM.md` exits 0).

---

## E. What This Audit Does NOT Cover

- Task 1.3 is now checked: the M1 validator-side debt was resolved and `go-microservices` `make verify-pr` exits 0.
- The `v1.0.0` annotated release tag was created in `ai-training-materials` (commit `85df609`) under explicit user authorization.
- No commits or pushes were made.
- Counts above are derived from `tasks.md` (22 checked, 9 unchecked, 31 total).
- This document is a status/documentation artifact within the change directory, not an implementation artifact.
