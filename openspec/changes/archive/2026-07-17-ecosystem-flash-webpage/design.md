## Context

The TDT workspace already has a strong ecosystem story: shared infra in `tdt-core`, Jira automation in `jira-kanban-from-spreadsheet` and `jira-daily-reports`, analytics in `jira-epic-report`, GitLab review automation in `webhook-receiver`, and browser/document support in `browser-cli`. The current `docs/presentation.html` is a hand-authored static page, but it is not a true slide deck and lacks formal contract boundaries for feature claims, motion, navigation, and viewport fit.

This change defines a spec-driven flash webpage that curates only validated, current ecosystem capabilities and presents them in a slide-based experience.

Constraints:
- The page should be single-file or near-single-file for easy distribution.
- Claims must be grounded in repo READMEs, skill docs, OpenSpec docs, and validated research notes.
- The experience must remain usable on desktop, tablet, and mobile.
- Motion must be optional and reduced-motion friendly.
- The spec must avoid overclaiming native Jira sprint-report APIs; the showcase should present current support surfaces, not invented platform features.

Stakeholders:
- Maintainers who need an accurate ecosystem overview
- Agents that need a concise authoritative summary of supported features
- Reviewers who need a consistent docs/spec/code/skills alignment surface

## Goals / Non-Goals

**Goals:**
- Create a canonical OpenSpec capability for the ecosystem flash webpage.
- Define a slide-based UX contract with viewport fit and interactive navigation.
- Define a validated feature taxonomy covering the TDT ecosystem.
- Ensure claims are versioned by maturity: live, stable, planned, archived.
- Establish a repeatable consistency check between spec, docs, skills, and implementation.

**Non-Goals:**
- Build a new runtime backend or API service.
- Redesign or reimplement the underlying ecosystem tools.
- Add live data fetching from Jira/GitLab into the webpage itself.
- Replace the existing long-form documentation with the webpage.

## Decisions

### Decision 1: Separate capability spec for the showcase page
Use a new capability spec instead of mutating existing reporting specs.

Rationale:
- The page is a communication layer, not a core automation tool.
- A dedicated capability keeps scope tight and avoids accidental behavior changes in Jira/reporting specs.
- It makes the claim-governance contract explicit.

Alternatives considered:
- Modify `jira-reports-consolidation` directly — rejected because that spec is about ecosystem architecture, not a presentation contract.
- Keep as an informal doc — rejected because stale claims would remain hard to govern.

### Decision 2: Slide-based webpage, not long-scroll article
Use a viewport-fit slide deck model.

Rationale:
- The user explicitly wants a flash webpage; `frontend-slides` is a strong fit.
- A slide model forces content prioritization and keeps the deck readable on mobile.
- It supports progressive reveal and structured storytelling.

Alternatives considered:
- Single long-scroll landing page — rejected because it encourages dense bullet walls and no natural pacing.
- SPA with routing — rejected because the spec asks for a simple distributable artifact.

### Decision 3: Claim governance from source-of-truth docs
Every feature must be grounded in local repo READMEs, AGENTS.md, skill docs, OpenSpec artifacts, or validated research notes.

Rationale:
- The ecosystem changes quickly.
- This prevents stale claims in stakeholder-facing material.
- It keeps the webpage aligned with current support.

Alternatives considered:
- Manual copywriting only — rejected because it drifts too easily.
- Runtime scraping of repos — rejected because the spec should not depend on live extraction.

### Decision 4: Maturity labels are part of the contract
Each item must be labeled live/stable/planned/archived.

Rationale:
- The ecosystem mixes production systems, stable libraries, and roadmap work.
- Stakeholders need to understand which features are real today versus planned.
- Prevents misleading equal-weight presentation.

Alternatives considered:
- Binary shipped/not-shipped — rejected because too coarse for the current ecosystem.

### Decision 5: Presentation behavior is first-class
Navigation, reduced motion, and viewport fit are requirements, not implementation details.

Rationale:
- The deck must work as a real artifact in browsers and on mobile.
- Accessibility and readability are part of stakeholder trust.
- These are easy to regress without explicit spec coverage.

Alternatives considered:
- Leave interaction unspecified — rejected because slide UX quality would drift.

## Risks / Trade-offs

- Content density may exceed one viewport → split into more slides and prioritize fewer claims per slide.
- Source-of-truth docs may diverge over time → require periodic consistency review before release.
- Some ecosystem areas are partially implemented → label them planned or archived instead of overstating support.
- A single-file implementation may grow large → keep assets abstract and reuse existing CSS patterns.
- Mobile readability may suffer if too many cards are used → enforce compact taxonomy and short labels.

## Migration Plan

1. Finalize the capability spec and make it the source of truth for the webpage.
2. Align the webpage content to validated current repo/skill/docs claims.
3. Update or replace the existing `docs/presentation.html` with the slide-based deck.
4. Verify viewport fit and navigation behavior on desktop/tablet/mobile.
5. Run a consistency review against the source docs before release.

Rollback:
- Keep the old page until the new one is validated.
- If the new deck drifts or overclaims, revert to the prior HTML artifact while keeping the spec intact.

## Open Questions

- Should the deck remain one file forever, or may it split into supporting assets if needed?
- Do we want a future path to auto-generate the feature matrix from source docs, or keep it hand-curated?
- Should the current long-form `docs/presentation.html` be replaced or preserved as an archive copy?
