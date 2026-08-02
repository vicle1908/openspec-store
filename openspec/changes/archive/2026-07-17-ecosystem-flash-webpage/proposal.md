## Why

TDT has strong ecosystem capabilities, but current `docs/presentation.html` is static,
partly stale-prone, and not governed by a formal spec contract. We need a spec-driven
flash webpage that presents only validated, current, supportable features.

## What Changes

- Add a new OpenSpec capability for a flash ecosystem showcase webpage.
- Define mandatory content blocks (foundation, Jira automation, reporting, GitLab review, tooling, impact).
- Define strict claim-governance: every feature claim must map to a live source-of-truth.
- Define maturity labels (`live`, `stable`, `planned`, `archived`) and usage rules.
- Define presentation behavior contract (viewport-fit, no internal scroll, keyboard/touch/wheel navigation, reduced-motion).
- Define consistency validation workflow between spec, code, docs, skills.

## Capabilities

### New Capabilities
- `ecosystem-showcase-webpage`: Spec for a single-file flashy webpage/presentation that covers TDT ecosystem features with validated claims, maturity labeling, and accessibility/interaction requirements.

### Modified Capabilities
- None.

## Impact

- Affects docs artifact: `docs/presentation.html` (or replacement file in `docs/`).
- Affects OpenSpec workflow for ecosystem communication assets.
- Uses existing local sources only (repo READMEs, skill docs, OpenSpec reports, AGENTS guidance).
- No runtime API changes.
- No new backend dependency.
- Improves stakeholder-facing accuracy and reduces stale/unsupported claims.
