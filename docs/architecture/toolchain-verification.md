# Toolchain Verification

**Status:** verification procedure and evidence for the `add-enterprise-architecture-modeling` change  
**Verified on:** 2026-09-09 (all commands below were executed on that date from the repository root, `/Users/androidteam/Developer/openspec-store`, with `uv` providing Python 3.14)  
**Scope:** tasks 1.4, 1.6, 2.2, and verification support for 6.2–6.5

This document defines how the core architecture-modeling workflow is verified
headlessly, records Archi/ACLI as optional tooling — installed as of
2026-09-09, with installation details and the task 2.2 round-trip evidence
below — evaluates the agent operation surface against the engine CLI, and
wires the CI gates. The agent capability boundary, authorization limits, and
governance ownership are defined in `docs/architecture/governance.md` and are
not repeated here.

## Core vs. optional tooling

| Tool | Role | Status |
| --- | --- | --- |
| Python 3.14 via `uv` | runs `scripts/archimate/engine.py` (reads, queries, structured mutations, validation) and the replay gate | **required** — repository-internal, no GUI, no display server |
| PlantUML | `-checkonly` syntax gate for `docs/architecture/diagrams/**/*.puml` | **required when `.puml` files exist** (otherwise skipped); GUI-free |
| Graphviz | diagram layout backend for PlantUML rendering | optional — the `-checkonly` gate renders nothing |
| Archi / ACLI | desktop modeler and its headless CLI; used for round-trip spot checks (task 2.2) | **optional — INSTALLED 2026-09-09** (Archi 5.10.0); never required by the core workflow |
| MCP adapter | structured model operations over MCP | **optional future work** — the engine CLI is the current structured surface |

### Archi/ACLI is optional (task 1.4)

The core workflow — model inspection, filtered queries, neighborhood
traversal, view/organization listing, structured mutation, structural +
semantic validation, fixture checks, and the mutation replay gate — is
executed entirely by `scripts/archimate/engine.py` plus the pinned XSD set.
None of it loads a GUI, launches a desktop application, or requires a
display server; every core-workflow verification in this document ran on a
headless terminal without launching the modeler. Archi 5.10.0 / ACLI is
**installed** as of 2026-09-09 (details in the next section), which makes
the task 2.2 round-trip spot check verifiable on this workstation — but the
installation changes nothing about the boundary: the headless core workflow
still MUST NOT require the GUI. Archi or ACLI may be used opportunistically
(for example to eyeball a mutated model), and a failure or absence of either
tool MUST NOT fail the core gate. If a repository workflow ever
hard-requires Archi/ACLI, that is a governance violation, not a toolchain
gap.

### Archi/ACLI installation (2026-09-09)

Archi 5.10.0 is installed at `/Applications/Archi.app` — the official macOS
Silicon dmg from <https://www.archimatetool.com>, SHA-1
`c8047f8228dcaca0b9ba94c2902ea0da0c09677b` verified against the official
`SUMSSHA1` file — with the offline documentation set at
`/Applications/Archi-docs` (Archi User Guide.pdf, LICENSE.txt,
change-log.txt, known-issues.txt). ACLI, the bundled headless command-line
interface, is invoked through the application binary with the
`com.archimatetool.commandline.app` Eclipse application id (full invocation
in the round-trip section below); it runs without a GUI or display server,
so the optional-tooling spot checks remain headless. The installation makes
the task 2.2 round-trip evidence reproducible on this workstation; it does
not change the optional status above, and the `verify-architecture` gate
never invokes Archi/ACLI.

## Headless verification procedure

Run from the repository root. Exit codes below are the observed results from
2026-09-09.

### 1. Model inspection and queries (read-only, side-effect free)

```sh
MODEL=docs/architecture/models/canonical.xml

uv run python scripts/archimate/engine.py --model $MODEL inspect              # exit 0
uv run python scripts/archimate/engine.py --model $MODEL query --layer business --limit 3   # exit 0
uv run python scripts/archimate/engine.py --model $MODEL query-relationships --type Serving # exit 0
uv run python scripts/archimate/engine.py --model $MODEL neighbors --element ea-a87d473086132d9f --depth 1   # exit 0
uv run python scripts/archimate/engine.py --model $MODEL views                # exit 0
```

Observed: `inspect` reports 14 elements, 11 relationships, 1 view; `query
--layer business` returns bounded, deterministically ordered elements;
`query-relationships --type Serving` returns the one canonical Serving
relationship with provider as source; `neighbors` returns the depth-1
subgraph with `truncated: false` (the engine reports `"truncated": true`
when the depth/limit bound cuts the traversal — bounded reads are part of
the contract, not an error). Reads do not touch file bytes, mtime, or the
working tree.

### 2. Validation (two tiers)

```sh
uv run python scripts/archimate/engine.py --model $MODEL validate   # exit 0, {"valid": true}

for f in docs/architecture/models/regression/*.xml; do
  uv run python scripts/archimate/engine.py --model "$f" validate; echo "exit=$?"
done
```

Observed: the canonical fixture validates (exit 0). Each regression fixture
is rejected with exit 3 and exactly one rule:

| Fixture | Exit | Emitted rule |
| --- | --- | --- |
| `regression/dangling-idref.xml` | 3 | `STRUCTURAL_IDREF_UNRESOLVED` |
| `regression/duplicate-identifier.xml` | 3 | `STRUCTURAL_DUPLICATE_IDENTIFIER` |
| `regression/forbidden-pairing.xml` | 3 | `SEMANTIC_ILLEGAL_ENDPOINT_PAIR` |
| `regression/serving-reversed.xml` | 3 | `SEMANTIC_SERVING_REVERSED` |

These match `docs/architecture/models/manifest.json` rule-for-rule. The
structural tier is also independently enforced by the pinned XSD chain in
`docs/architecture/schemas/archimate-exchange/` (see `SCHEMAS.md` for the
`xmllint` command); the engine adds the semantic tier that the XSD cannot
express (reversed Serving direction, illegal endpoint pairings).

### 3. Structured mutation (happy path, on a scratch copy)

```sh
T=$(mktemp -d) && cp docs/architecture/models/canonical.xml $T/m.xml
cat > $T/ops.json <<'JSON'
[{"op": "create_element", "type": "BusinessRole", "name": "Gate Liaison"}]
JSON
uv run python scripts/archimate/engine.py --model $T/m.xml mutate $T/ops.json   # exit 0
uv run python scripts/archimate/engine.py --model $T/m.xml validate              # exit 0
```

Observed artifacts beside the scratch model: `.m.xml.lock` (the single-writer
lock file) and `m.xml.bak` (the pre-mutation backup — SHA-256 verified
byte-identical to the fixture before mutation). Passing `--no-backup` skips
the `.bak` and exits 0. Re-applying the same batch exits 0 and adds nothing
(idempotent re-application).

### 4. Rejection paths (fail closed, no file changes)

Against a scratch copy of the canonical fixture with SHA-256 recorded before
and after, all observed exit codes and the unchanged-digest result:

| Invocation | Exit code | stderr rule | File unchanged |
| --- | --- | --- | --- |
| `mutate` with JSON array containing `{"op": "frobnicate"}` | 4 | `MUTATION_UNSUPPORTED_OPERATION: 'frobnicate'` | yes (sha256 equal) |
| `mutate` with a JSON **object** (non-array) as the batch | 4 | `MUTATION_INVALID_BATCH: operations must be a JSON array` | yes |
| `mutate` with `[{"op": "create_element"}]` (missing type/name) | 4 | `MUTATION_INVALID_ELEMENT: type and name are required` | yes |
| `mutate` batch whose resulting model fails semantic validation (reversed Serving) | 4 | `MUTATION_REJECTED: … "rule": "SEMANTIC_SERVING_REVERSED"` | yes |

Batches are transactional: the engine deep-copies the tree, applies every
operation to the trial, validates the complete proposed state, and only then
persists through a temporary sibling file with fsync and atomic rename. Any
rejected batch leaves the target file byte-identical; the repository fixtures
are never written by a rejected operation.

### 5. Mutation replay gate (CI, task 6.4)

```sh
uv run python scripts/archimate/replay_canonical.py   # exit 0
```

`scripts/archimate/replay_canonical.py` copies the canonical fixture to a
temporary directory, applies the canonical mutation sequence (create element,
create Assignment relationship, update element name) **twice**, and asserts
21 checks: post-mutation validity via the API and the CLI, idempotence (the
second application adds no elements or relationships), identifier stability
(no churn), preservation of unmodified content (model identifier, views,
bendpoints, organization folders, property definitions, vendor extensions,
and every pre-existing element/relationship), and that the repository fixture
itself is untouched (same bytes, no `.bak`/`.lock` files created beside it).
A deliberately illegal sequence (reversed Serving) was replayed as a negative
control and failed the gate with exit 1 and the `SEMANTIC_SERVING_REVERSED`
rule.

## Archi/ACLI round-trip spot check (task 2.2)

The optional-tooling round-trip check for task 2.2 was executed headlessly
through ACLI on 2026-09-09: import the canonical fixture through the
exchange provider, export it back out, and compare the identity-relevant
content. It is a spot check of external-tool fidelity, not a gate —
`make verify-architecture` does not invoke Archi/ACLI.

```sh
mkdir -p /tmp/archi-rt
/Applications/Archi.app/Contents/MacOS/Archi \
  -application com.archimatetool.commandline.app -consoleLog -nosplash \
  --xmlexchange.import /Users/androidteam/Developer/openspec-store/docs/architecture/models/canonical.xml \
  --xmlexchange.export /tmp/archi-rt/canonical-archi-roundtrip.xml \
  --xmlexchange.exportFolders
```

Observed (comparing `docs/architecture/models/canonical.xml` against
`/tmp/archi-rt/canonical-archi-roundtrip.xml`; ACLI exit 0, with
`-consoleLog` reporting `Validating…/Validated!`, `XML Imported!`,
`XML Exported!`, then `Validating…/Validated!` again on the exported file):

- **Elements: 14 → 14, every identifier preserved.**
- **Relationships: 11 → 11, every identifier preserved.**
- **View: preserved with the identical identifier** (`view-07de3e07c916f9f7`).
- **Organization folders: all 8 original folder labels preserved** —
  Architecture, Business, Application, Technology, Physical, Implementation
  and Migration, Motivation, Strategy — along with all 14 original element
  references. Archi additionally materializes its own internal tree on
  export: per-layer grouping folders including renamed forms
  (`Technology & Physical`, `Implementation & Migration`), a `Relations`
  folder holding all 11 relationship items, and a `Views` folder holding
  the view item, with the original folders (including the original
  `Architecture` root) nested beneath them. The exported organization tree
  is a superset of the original; nothing is lost.
- **Pinned XSD validation of the round-trip output: exit 0** —
  `XML_CATALOG_FILES=docs/architecture/schemas/archimate-exchange/catalog.xml xmllint --noout --nonet --schema docs/architecture/schemas/archimate-exchange/validate-archimate-exchange.xsd /tmp/archi-rt/canonical-archi-roundtrip.xml`
  reports `canonical-archi-roundtrip.xml validates`.
- **Engine two-tier validation of the round-trip output: clean after the
  view-ref fix** — `uv run python scripts/archimate/engine.py --model
  /tmp/archi-rt/canonical-archi-roundtrip.xml validate` exits 0 with
  `{"issues": [], "valid": true}` (verified 2026-09-09, after the engine
  owner's same-day fix to the structural resolver). Before the fix, the
  structural tier mis-flagged the exported `Views` folder's organization
  item (`<item identifierRef="view-07de3e07c916f9f7"/>`) as
  `STRUCTURAL_IDREF_UNRESOLVED` — a false positive: the Open Exchange schema
  permits organization items to reference views, and the pinned XSD passed
  the same file. The resolver now accepts view identifiers on organization
  items.

Two ACLI operational notes, observed while reproducing this check on
2026-09-09:

- ACLI does not resolve `--xmlexchange.*` file arguments against the shell's
  working directory: from the repository root, a relative
  `--xmlexchange.import docs/architecture/models/canonical.xml` fails with
  `docs/architecture/models/canonical.xml does not exist` and
  `Model was not loaded`. Pass absolute paths, as in the invocation above.
- ACLI exits 0 even when a provider fails — the failed relative-path import
  above returned exit 0 and wrote no output file. Do not trust the exit
  code alone: check the `-consoleLog` transcript and that the output file
  was written.

## Verification gate (Makefile, tasks 6.2–6.4)

```sh
make verify-architecture   # observed exit 0 on 2026-09-09
```

The target runs five stages and fails non-zero on the first violation:

1. **PlantUML syntax gate (6.2):** runs `plantuml -checkonly` over every
   `docs/architecture/diagrams/**/*.puml`. When no `.puml` files exist yet it
   prints `verify-architecture: no .puml files under docs/architecture/diagrams
   - PlantUML check skipped` and continues (observed). When files exist but
   `plantuml` is missing it fails closed with a clear error. Verified with a
   temporary valid template (gate passed, exit 0) and a temporary invalid
   template (gate failed with `FAIL: PlantUML syntax check: <file>`, make
   exit 2); both temporary files were removed after the check.
2. **Canonical validation (6.3):** engine `validate` on
   `docs/architecture/models/canonical.xml` must exit 0 (observed).
3. **Regression fixtures (6.3):** each
   `docs/architecture/models/regression/*.xml` must be rejected with exit 3
   and the emitted rule must equal the `failure.rule` recorded for that
   fixture in `docs/architecture/models/manifest.json` (all four observed
   matching).
4. **Pinned exchange XSD validation (6.3):**
   `XML_CATALOG_FILES=docs/architecture/schemas/archimate-exchange/catalog.xml xmllint --noout --nonet --schema docs/architecture/schemas/archimate-exchange/validate-archimate-exchange.xsd docs/architecture/models/canonical.xml`
   must exit 0 (observed). When `xmllint` is missing the gate fails closed
   with a clear message before running the check. This is the independent
   structural tier of record for the exchange format — the same pinned chain
   that caught the view-referenced-delete defect below — and it runs on
   every gate invocation regardless of whether Archi/ACLI is installed.
5. **Canonical mutation replay (6.4):** `uv run python
   scripts/archimate/replay_canonical.py` must exit 0 (observed).

`make verify-pr` remains unchanged (pytest + `openspec validate --all
--strict`); CI wiring of `verify-architecture` into the pull-request pipeline
is owned by the integration owner.

## Adapter surface evaluation (task 1.6)

The engine CLI (`scripts/archimate/engine.py`) is the current structured
agent surface. Every operation the change requires maps to a subcommand:

| Required agent operation | CLI surface | Verified behavior |
| --- | --- | --- |
| Model metadata | `inspect` | exit 0; element/relationship/view counts, model identifier, namespaces |
| Filtered element query | `query --layer --type --name --limit` | exit 0; bounded, sorted, deterministic |
| Filtered relationship query | `query-relationships --type --source --target --limit` | exit 0; bounded, sorted |
| Neighborhood traversal | `neighbors --element --depth --limit` | exit 0; returns reachable subgraph plus `truncated` flag |
| Organization/view listing | `views` | exit 0; view identifiers, node/connection counts, and organization folder entries — traverses the exchange-schema `organizations`/`item` tree and lists all eight canonical folders (Architecture, Business, Application, Technology, Physical, Implementation and Migration, Motivation, Strategy) |
| Element CRUD | `mutate` ops `create_element` / `update_element` / `delete_element` | exit 0 on success; delete of an element that is a relationship endpoint is rejected (`MUTATION_REFERENCED_ELEMENT`, exit 4, file unchanged); unknown identifier rejected (`MUTATION_UNKNOWN_ELEMENT`, exit 4) |
| Relationship CRUD | `mutate` ops `create_relationship` / `delete_relationship` | exit 0 on success; unknown identifier rejected (`MUTATION_UNKNOWN_RELATIONSHIP`, exit 4); delete of a view-referenced relationship is rejected (`MUTATION_REFERENCED_RELATIONSHIP`, exit 4, file unchanged — re-verified 2026-09-09 after the engine fix) |
| Validation | `validate` | exit 0 valid / exit 3 invalid, one stable rule identifier per issue |
| Atomic persistence | engine internals behind `mutate` | single-writer lock (`.lock` sibling), temp sibling + fsync + atomic rename |
| Backup/rollback | `mutate` (backup by default) / `--no-backup` | `.bak` sibling byte-identical to pre-mutation state; rejected batches leave the file untouched |
| Unsupported/malformed rejection | `mutate` input validation | exit 4 (`MUTATION_UNSUPPORTED_OPERATION`, `MUTATION_INVALID_BATCH`, `MUTATION_INVALID_ELEMENT`) with the file unchanged |

### Operation-to-subcommand examples

```sh
uv run python scripts/archimate/engine.py --model $MODEL query --type BusinessActor --name 'Claims.*'
uv run python scripts/archimate/engine.py --model $MODEL neighbors --element <id> --depth 2 --limit 50
uv run python scripts/archimate/engine.py --model $MODEL mutate ops.json
```

### Rejection verification (no file changes)

Verified against a scratch copy with a SHA-256 digest recorded before and
after each rejected call — see the table in "Rejection paths" above; every
unsupported or malformed operation exited 4 with an equal digest, so the
model file was provably unchanged. Unknown operations are rejected before
any serialization, and a batch whose proposed state fails validation is
rejected before any write.

### MCP adapter

An MCP adapter remains **optional future work**; nothing in the repository
requires it. It must wrap the same structured operation set (and only that
set) — raw model-file text replacement is outside the capability boundary
defined in `docs/architecture/governance.md`. Until such an adapter exists
and is separately governed, the engine CLI is the structured surface of
record.

## Licensing note for optional tooling

Archi (GPL) and ACLI are optional, isolated tools; they must not become
required dependencies of the core workflow, and their GPL licensing has no
effect on repository-owned artifacts (models, templates, engine, gates).
The same boundary applies to GPL Python libraries such as `pyArchimate`
(see `docs/architecture/governance.md` for the full licensing boundary
statement).

## Engine gaps found on 2026-09-09 — fixed and re-verified same day

Two engine-side gaps were discovered during the task-1.6 adapter evaluation
and fixed by the engine owner (`scripts/archimate/engine.py` is owned by the
engine owner) on the same day. They are recorded here because the discovery
evidence and the re-verification are part of the toolchain record.

- **View-referenced deletes (fixed):** originally, `delete_relationship` of a
  relationship referenced by a view connection **attribute** — e.g.
  `rel-43946800a5879cc4`, referenced by `conn-f62b1d47f1f704d2` via
  `connection/@relationshipRef` — succeeded (exit 0, relationships 11 → 10)
  and persisted a file that the engine's own `validate` accepted but the
  pinned XSD chain rejected (`No match found for key-sequence
  ['rel-43946800a5879cc4'] of keyref 'RelationshipRefAttribute'`, exit 3):
  the reference-holder checks only saw `<relationshipRef ref="..."/>` child
  elements, which the exchange schema does not use. After the fix, the same
  operation is rejected fail-closed — `MUTATION_REFERENCED_RELATIONSHIP`,
  exit 4, scratch-file SHA-256 unchanged (re-verified 2026-09-09). The fix
  also covers `node/@elementRef` and `item/@identifierRef` attribute-form
  references, and structural validation now reports dangling attribute
  references as `STRUCTURAL_IDREF_UNRESOLVED`.
- **Organization listing (fixed):** originally the `views` subcommand
  returned `[]` for organization folders because it looked for `organization`
  elements while the exchange schema encodes folders as
  `organizations`/`item` trees. After the fix, `views` lists all eight
  canonical folders with identifiers and item counts (re-verified
  2026-09-09). The replay gate's census (`organization_items` identical to
  fixture) remains in place as independent preservation coverage.

The independent XSD tier (`xmllint` with the pinned exchange schema chain,
see `docs/architecture/schemas/archimate-exchange/SCHEMAS.md`) is what
caught the original defect, and running it over mutated models remains
recommended practice even with the engine fixed: the two tiers check
different things, and the pinned XSD is the normative structural authority
for the exchange format.

## Remaining limitations

- **PlantUML check scope:** the gate checks `.puml` files under
  `docs/architecture/diagrams/`; PlantUML and Graphviz installation is
  verified separately by task 1.2/1.3 tooling evidence.
- **TOGAF/ArchiMate baselines:** authoritative links and version currency
  are recorded in `docs/architecture/baselines.md`.
