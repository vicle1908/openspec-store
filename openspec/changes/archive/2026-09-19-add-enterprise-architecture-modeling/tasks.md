## 1. Standards and Toolchain Verification

- [x] 1.1 Record the ArchiMate 3.2 and TOGAF Standard, 10th Edition baselines with authoritative source links; verify the links and version statements are current.
- [x] 1.2 Install or verify PlantUML and Graphviz using the repository-supported package manager; verify version commands exit successfully.
- [x] 1.3 Verify the PlantUML ArchiMate standard-library include with a minimal smoke template; verify the include works without relying on undocumented output formats.
- [x] 1.4 Document Archi/ACLI as optional desktop/headless tooling and verify the core workflow does not require it.
- [x] 1.5 Obtain the official ArchiMate 3.2 Open Exchange XSD and record its authoritative source; verify the schema is pinned by checksum for offline validation.
- [x] 1.6 Evaluate the selected MCP/CLI adapter surface against the required read, query, mutation, validation, and persistence operations; verify unsupported operations are rejected without file changes.

## 2. Model Fixture and Interchange

- [x] 2.1 Create a canonical Open Exchange XML fixture covering all ArchiMate layers, at least one legal relationship of each core type, views with bendpoints, folders, documentation, and a vendor extension element; verify it validates structurally.
- [x] 2.2 Verify the fixture round-trips through Archi or ACLI without loss of elements, relationships, views, or folders; record the verification output.
- [x] 2.3 Document the deterministic identifier scheme (canonical identity inputs, hash/namespace, NCName formatting, collision handling); verify generated identifiers are unique and schema-valid.
- [x] 2.4 Add regression fixtures for failure modes: reversed Serving direction, forbidden element/relationship pairing, dangling IDREF, and duplicate identifier; verify each fails validation with a rule and construct identifier.

## 3. Agent Model Operations

- [x] 3.1 Implement or wire the read-only operation set: model metadata, filtered element query, filtered relationship query, bounded neighborhood traversal, and organization/view listing; verify all reads are side-effect-free (unchanged bytes, mtime, and working tree).
- [x] 3.2 Implement or wire element and relationship CRUD through the structured mutation interface; verify each operation accepts structured input and rejects malformed operations without file changes.
- [x] 3.3 Verify semantic validation rejects illegal relationship types and inverted directions with rule identifiers; verify rejected operations leave the model unchanged.
- [x] 3.4 Verify delete operations either remove dependent references within the same transaction or are rejected; verify no dangling IDREFs persist.
- [x] 3.5 Verify batch mutations are transactional: any single failing operation rolls back the entire batch to the byte-identical pre-batch state.
- [x] 3.6 Verify idempotent re-application: running the same logical mutation twice creates no duplicate objects and keeps identifiers stable.
- [x] 3.7 Verify preservation: a mutation touching one element leaves views, bendpoints, folders, documentation, properties, and extensions intact, with serialization differences limited to the mutation and deterministic formatting.

## 4. Safe Persistence and Recovery

- [x] 4.1 Implement atomic persistence: temporary sibling file, flush/sync, validation, atomic rename; verify an interrupted write leaves the previous file intact.
- [x] 4.2 Implement pre-mutation backup and rollback; verify a persistence-time validation failure restores the last known-good state with no working-tree modification.
- [x] 4.3 Implement the single-writer/concurrency gate; verify concurrent mutation attempts are serialized or rejected, never interleaved.
- [x] 4.4 Verify preservation failure fails closed: when the tooling cannot safely represent existing content, the mutation is refused rather than discarding content.

## 5. TOGAF ADM PlantUML Templates

- [x] 5.1 Add a Preliminary template under `docs/architecture/diagrams/preliminary/`; verify it contains ArchiMate macros and passes `plantuml -checkonly`.
- [x] 5.2 Add Phase A and Phase B templates under their ADM directories; verify each directory has a valid `.puml` file.
- [x] 5.3 Add Phase C and Phase D templates under their ADM directories; verify each directory has a valid `.puml` file.
- [x] 5.4 Add Phase E and Phase F templates under their ADM directories; verify each directory has a valid `.puml` file.
- [x] 5.5 Add Phase G and Phase H templates under their ADM directories; verify each directory has a valid `.puml` file.
- [x] 5.6 Add Requirements Management templates under its ADM directory; verify it has a valid `.puml` file.
- [x] 5.7 Run `plantuml -checkonly` over all ten ADM directories; verify every template exits successfully.

## 6. Governance and CI

- [x] 6.1 Document the mapping from proposal, design, specs, and tasks to TOGAF ADM governance activities in `docs/architecture/governance.md`; verify the mapping names limitations and Architecture Practice ownership.
- [x] 6.2 Add CI validation for changed `.puml` files using `plantuml -checkonly`; verify a valid fixture passes and an invalid fixture fails.
- [x] 6.3 Add CI validation for changed Open Exchange XML model files using the two-tier validation; verify valid fixtures pass and each regression fixture fails with a rule identifier.
- [x] 6.4 Add a CI replay of the canonical agent mutation sequence against repository fixtures; verify models remain valid, unmodified content is preserved, and identifier churn fails the gate.
- [x] 6.5 Document the agent capability boundary (read/query versus mutation), authorization limits, and the licensing note for GPL-licensed optional tooling; verify the documented workflow is executable without a GUI or desktop modeler.
