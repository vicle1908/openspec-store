## Why

The workspace lacks a governed enterprise-architecture modeling practice that connects TOGAF ADM work products with formal ArchiMate 3.2 views, agent-operable model exchange files, and repeatable validation. This change establishes the notation, templates, governance mapping, canonical interchange boundary, and CI gates.

## What Changes

- Establish ArchiMate 3.2 as the normative modeling baseline for architecture views, exchanged models, and PlantUML templates.
- Add PlantUML templates covering Preliminary, Phases A–H, and Requirements Management in the TOGAF ADM.
- Use ArchiMate Open Exchange XML as the canonical, vendor-neutral interchange format for agent-readable and agent-mutable models.
- Define a headless agent capability boundary for model inspection, filtered queries, controlled element/relationship mutations, validation, and atomic persistence; expose it through an optional CLI or MCP adapter without making a GUI mandatory.
- Add repository-supported toolchain verification for PlantUML, Graphviz, the ArchiMate stdlib include, and the model-validation workflow.
- Add CI syntax validation with `plantuml -checkonly` for changed `.puml` files and structural/semantic validation for changed exchange files.
- Document how proposal, design, specs, and tasks support TOGAF ADM governance activities without treating OpenSpec as an enterprise-architecture repository.

### Explicit Non-Goals

- No uncontrolled source-system parsing, automated aggregation, or provenance mapping; integrations must be separately governed.
- No ArchiMate 4 implementation; 3.2 is the current compatibility baseline for the selected open-source tooling.
- No mandatory MCP server deployment, desktop modeler, graphical repository, or production runtime changes.
- No raw whole-file model editing by agents. Mutations must use the validated capability boundary and preserve unsupported/unmodified XML content where feasible.
- No claim that OpenSpec replaces an EA repository, architecture repository, or certified modeling tool.

## Capabilities

### New Capabilities

- `enterprise-architecture-modeling`: TOGAF ADM-aligned ArchiMate modeling templates, governed agent manipulation of Open Exchange XML, and PlantUML/model validation.

### Modified Capabilities

<!-- None: greenfield modeling capability. -->

## Impact

### Affected Ownership Boundaries

- **Architecture Practice:** Owns the ArchiMate baseline, ADM viewpoints, governance mapping, and review criteria.
- **DevOps / Infrastructure:** Owns CI execution and toolchain availability for PlantUML validation.
- **Platform and Agent Framework Teams:** Contribute architecture views under the documented governance process.

### System & Infrastructure Impact

- New architecture diagram templates under `docs/architecture/diagrams/` and governance documentation under `docs/architecture/`.
- CI configuration changes limited to validation of changed PlantUML files and Open Exchange XML model files.
- No production runtime impact or mutation of application repositories.
