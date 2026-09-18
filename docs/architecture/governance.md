# Enterprise Architecture Modeling Governance

**Status:** governed design for the `add-enterprise-architecture-modeling` change  
**Notation baseline:** ArchiMate 3.2 Open Exchange XML  
**Architecture owner:** Architecture Practice

This document maps the OpenSpec change artifacts to TOGAF Standard, 10th Edition Architecture Development Method (ADM) governance. It also defines the headless agent boundary for inspecting and mutating model files. OpenSpec is the change-control system for this implementation; it is **not** an enterprise-architecture repository, authoritative architecture catalog, or replacement for an ArchiMate model repository.

## Governance mapping

| OpenSpec artifact | ADM governance purpose | Required evidence and decision | Accountable owner |
| --- | --- | --- | --- |
| `proposal.md` | Preliminary and Phase A (Architecture Vision): establish the problem, scope, baseline, stakeholders, constraints, non-goals, and expected capability. | Confirm ArchiMate 3.2 and TOGAF 10 baselines; record explicit non-goals (including no mandatory GUI and no uncontrolled source ingestion); identify affected ownership boundaries and approval to proceed. | Architecture Practice sponsors the scope; platform and agent teams review feasibility. |
| `design.md` | Phase A vision refinement; Phases B–D architecture definition; Requirements Management traceability; early implementation/change governance. | Review normative decisions, ADM coverage, viewpoint/template layout, semantic validation, identity/preservation rules, safe persistence, risks, and tool/licensing boundaries. Architecture Practice accepts the modeling rules before implementation. | Architecture Practice is the design authority; DevOps reviews CI and persistence controls. |
| `specs/enterprise-architecture-modeling/spec.md` | Phases B–D architecture definition and Requirements Management: convert the approved intent into testable requirements and acceptance scenarios. | Verify each requirement has observable scenarios for exchange format, read/query behavior, structured mutation, semantic validation, preservation, atomic writes, ADM templates, CI gates, tooling, and authorization. | Architecture Practice owns semantic correctness and viewpoints; implementation teams own conformance evidence. |
| `tasks.md` | Phases E–G (Opportunities & Solutions, Migration Planning, Implementation Governance) plus Change Management: sequence delivery, verification, rollout, and operational evidence. | Execute tasks only after the change artifacts are approved; attach focused verification evidence to completed work; keep external/tool-dependent claims explicitly unverified until performed. | Architecture Practice approves architecture outcomes; delivery/DevOps owners execute and evidence implementation tasks. |

### ADM activity coverage

- **Preliminary:** establish Architecture Practice ownership, principles, repository boundaries, review authority, and the ArchiMate 3.2/TOGAF 10 baseline.
- **Phase A — Architecture Vision:** use the proposal to agree scope, stakeholders, concerns, viewpoints, non-goals, and authorization to design.
- **Phases B–D — Business, Information Systems, and Technology Architecture:** use the design and specification to define viewpoints, elements, relationships, exchange-file constraints, validation rules, and preservation obligations. The model remains an architecture work product; PlantUML is a view syntax, not the authoritative repository.
- **Phase E — Opportunities and Solutions:** use validated model changes to compare solution options and identify implementation increments without treating generated diagrams as proof of delivery.
- **Phase F — Migration Planning:** use task sequencing and model evidence to plan transition increments, dependencies, and acceptance gates. Do not claim migration completion from OpenSpec planning alone.
- **Phase G — Implementation Governance:** Architecture Practice reviews model mutations and conformance evidence; DevOps owns CI execution; rejected or unauthorized mutations must leave model files unchanged.
- **Phase H — Architecture Change Management:** new notation versions, relationship rules, repository integrations, and source-system mappings require a separately governed change. ArchiMate 4 adoption is not implied by this baseline.
- **Requirements Management:** maintain traceability from proposal intent through design decisions, specification scenarios, implementation tasks, validation results, and approved architecture changes.

## OpenSpec limitations and repository boundary

OpenSpec records change intent, design decisions, requirements, tasks, and evidence. It does not provide the authoritative EA repository, model versioning semantics, stakeholder approval workflow, architecture board record, or a certified ArchiMate tool. A model may be stored under `docs/architecture/models/` in canonical Open Exchange XML, but its authority and ownership remain governed by the Architecture Practice.

The implementation MUST NOT infer architecture from uncontrolled source systems. Any Graphify, code, inventory, or runtime integration requires a separate governed mapping and provenance decision. Schema validity alone is insufficient: Open Exchange XSD/IDREF checks must be paired with ArchiMate semantic validation, including legal relationship endpoints and directionality. If a mutation cannot preserve views, bendpoints, folders, documentation, namespaces, extensions, or other unmodified content, it must fail closed rather than silently rewrite the model.

## Headless agent capability boundary

### Read and query operations (side-effect free)

Agents MAY inspect model metadata, list organizations and views, filter elements or relationships by supported fields, and traverse bounded neighborhoods. Reads and queries:

- require no GUI, display server, Archi desktop application, or MCP server;
- do not alter bytes, modification time, backups, working-tree state, or model identifiers;
- return bounded, deterministic results and report truncation;
- may be exposed by an optional CLI or MCP adapter, but the canonical model remains Open Exchange XML.

### Mutation operations (explicit and structured)

Agents MAY create, update, or delete supported elements and relationships only through structured operations. The adapter MUST reject raw XML/text replacement, malformed operations, unsupported types, illegal endpoint pairs, reversed relationship direction, dangling-reference deletes, and preservation-unsafe changes. A batch is transactional: validate the complete proposed state before persistence and leave the file byte-identical if any operation fails.

Mutation persistence requires a single-writer/concurrency gate, a pre-mutation backup, temporary sibling output, flush/sync, structural plus semantic validation, and atomic rename with rollback. New identifiers use the documented deterministic NCName-compatible scheme; existing identifiers and unmodified content are retained. Reads never acquire mutation authority.

### Authorization and review limits

- Read/query permission is not mutation permission.
- Mutation authorization is limited to explicitly approved model paths and supported operation types; path traversal, arbitrary filesystem writes, credential access, and raw model-file replacement are outside the capability.
- The invoking workflow MUST identify the actor, requested operation, target model, and validation result in its audit evidence.
- Architecture Practice owns approval of model semantics, viewpoints, relationship direction, and baseline changes. DevOps/Infrastructure owns CI and toolchain execution. Platform/Agent Framework teams may propose changes but cannot self-approve architecture policy changes.
- Authorization does not waive validation, preservation, backup, atomic-write, or review gates. Failure is fail-closed with no partial persistence.

## Tooling and licensing

PlantUML and Graphviz are optional verification/rendering tools; CI should use PlantUML `-checkonly` for changed `.puml` files and the model validator for changed Open Exchange XML when those tools and validators exist in the repository. Archi/ACLI and a graphical repository are optional and must not be required for headless workflows. The ArchiMate standard-library include must be checked by the supported toolchain procedure rather than assumed from a local GUI installation.

GPL-licensed Python libraries such as `pyArchimate` are optional isolated tooling pending license and distribution review. They MUST NOT become a required runtime dependency or silently enter the core agent path. The canonical interchange and validation contract remains ArchiMate 3.2 Open Exchange XML plus the repository's structural and semantic validators.

## Verification and ownership

Architecture Practice reviews this document, the four OpenSpec artifacts, ADM viewpoint intent, semantic rules, and model-preservation evidence. DevOps/Infrastructure reviews CI/tool availability and atomic persistence controls. The implementation owner reports focused commands and exact paths; OpenSpec task checkboxes are updated only by the integration owner after verification. A passing OpenSpec validation confirms artifact structure, not architecture correctness, model completeness, or external tool installation.
