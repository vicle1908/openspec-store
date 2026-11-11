# Spec Delta

## MODIFIED Requirements

### Requirement: Progressive disclosure layout and size boundaries
Locally authored skills SHALL keep `SKILL.md` <= 500 lines by factoring deep material into conditional `references/` or `assets/`. Upstream vendor skills in `skills-lock.json` and CLI-generated skills declaring `metadata.author: openspec` with `metadata.generatedBy` SHALL remain exempt from local splitting so `skills update -y` and `openspec update` stay idempotent.

#### Scenario: Lean skill body delegates deep references to secondary files
- **WHEN** a locally authored skill defines extensive domain documentation or schema catalogs
- **THEN** the `SKILL.md` body SHALL remain under 500 lines and cite the relative path in `references/`
- **AND** the instruction SHALL specify the exact condition under which the agent should read the reference

#### Scenario: Upstream vendor skill integrity preserved
- **WHEN** an upstream vendor skill tracked in `skills-lock.json` exceeds 500 lines
- **THEN** the file SHALL NOT be split into local reference files
- **AND** its upstream layout and provenance hash SHALL remain tracked without divergence

#### Scenario: Generator-owned OpenSpec workflow skill remains unsplit for idempotent updates
- **WHEN** `openspec update` generates an OpenSpec workflow skill (such as `openspec-onboard/SKILL.md`) declaring `metadata.author: openspec` and `metadata.generatedBy` that exceeds 500 lines
- **THEN** the generated `SKILL.md` SHALL remain intact as emitted by the OpenSpec CLI without manual local `references/` splitting
- **AND** re-running `openspec update` at the same CLI version SHALL produce zero Git diff and leave zero orphaned split files

#### Scenario: Locally authored skill body stays within size budget
- **WHEN** validating locally authored non-generated skills in `~/Developer/.agents/skills/` or `openspec-store`
- **THEN** every locally authored `SKILL.md` body SHALL NOT exceed 500 lines
- **AND** detailed guides and templates SHALL be located in `references/` or `assets/`
