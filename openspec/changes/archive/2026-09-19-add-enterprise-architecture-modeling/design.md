## Context

See `proposal.md` for motivation. The core change establishes a repository-level architecture modeling practice and a headless, agent-operable ArchiMate model boundary. The normative baseline is ArchiMate 3.2, aligned to the ten TOGAF Standard, 10th Edition ADM areas. PlantUML provides diagram syntax and ArchiMate standard-library macros; ArchiMate Open Exchange XML provides canonical model interchange.

**Goals:**

- Provide consistent ADM-area viewpoints and a predictable architecture documentation layout.
- Make PlantUML ArchiMate syntax validation cheap, deterministic, and CI-friendly.
- Define a headless agent capability boundary for inspection, filtered queries, controlled element/relationship mutations, validation, and safe persistence of Open Exchange XML.
- Define governance responsibilities and the relationship between OpenSpec artifacts and ADM work products.
- Keep the modeling baseline explicit so future ArchiMate 4 adoption is a deliberate compatibility change.

**Non-Goals:**

- Transform uncontrolled source systems into model exchange XML or infer authoritative architecture without governed mappings.
- Provide a graphical repository, model database, or certification claim.
- Require Archi desktop/ACLI, an MCP server, or a particular programming language for the core workflow.
- Permit raw whole-file agent rewrites that can discard views, organizations, extensions, namespaces, or references.

## Decisions

1. **Normative baseline.** Use ArchiMate 3.2 Specification and its Open Exchange XML format for the initial templates and agent-manipulable model files. ArchiMate 4 is future context only.
2. **ADM coverage.** Treat Preliminary, Phases A–H, and Requirements Management as ten distinct template areas.
3. **Template layout.** Store at least one `.puml` template in each ADM directory. Templates use `!include <archimate/Archimate>` and show the viewpoint's intended concern rather than pretending to be generated from runtime data.
4. **Agent boundary.** Expose read-only model inspection, filtered element/relationship queries, neighborhood/view queries, validation, and explicit mutation operations through an optional CLI or MCP adapter. Mutation APIs accept structured operations, not arbitrary XML text.
5. **Validation.** Every mutation must pass XML well-formedness, ArchiMate Open Exchange XSD/IDREF checks, and semantic metamodel rules including legal relationship endpoints and directionality before persistence. PlantUML syntax uses `-checkonly`; Graphviz is verified for rendering workflows.
6. **Identity and preservation.** Preserve existing identifiers on updates; allocate deterministic NCName-compatible identifiers for new objects; preserve unknown/unmodified XML content, views, organizations, namespaces, and extensions where feasible.
7. **Persistence.** Use a single-writer/concurrency gate, pre-mutation backup, temporary sibling write, flush/sync, validation, and atomic rename with rollback on failure. Reads are side-effect-free.
8. **Governance mapping.** Document how proposal, design, specs, and tasks contribute to ADM vision, architecture definition, migration/implementation governance, and change management. OpenSpec governs changes; it is not the EA repository.
9. **Tooling boundary.** Archi/ACLI, PlantUML, Graphviz, and MCP/CLI adapters are optional downstream tools; no GUI is mandatory for agent operation.
10. **Licensing.** Treat GPL-licensed Python libraries such as pyArchimate as optional isolated tooling pending license review; do not make them a required runtime dependency.

## Risks / Trade-offs

- PlantUML templates are readable and CI-friendly but do not replace a full model repository or enforce every ArchiMate semantic constraint.
- XML schema validation cannot prove all metamodel semantics; a separate relationship/type/direction validator is required.
- Lossless round-tripping is harder than parsing and rewriting: naive serializers can drop diagram views, bendpoints, organizations, or vendor extensions. Unknown content must be preserved or the mutation must fail closed.
- Deterministic identifiers improve reviewability and idempotence but require a documented canonical identity and collision handling.
- Atomic writes and backups reduce corruption risk but require filesystem permissions and a single-writer boundary.
- ArchiMate 3.2 is not the newest published notation context; migration to 4.x requires a separately validated plan.
- Ten directories improve discoverability but can duplicate common viewpoint scaffolding; shared includes may be introduced only when they preserve clear ownership and validation.
- Source-derived diagrams remain input-dependent and require separate integration governance.
