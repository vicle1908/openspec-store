# Architecture Modeling Baselines

**Status:** governed baseline record for the `add-enterprise-architecture-modeling` change  
**Baseline owner:** Architecture Practice  
**Link check date:** 2026-09-09 (every URL below verified live with `curl -sI -L` returning HTTP 200 on that date)

This document records the normative standards baselines for the architecture
modeling practice: the notation baseline (ArchiMate 3.2), the method baseline
(TOGAF Standard, 10th Edition), and the interchange baseline (ArchiMate 3.x
Open Exchange XML). Any change to these baselines is a separately governed
OpenSpec change.

## Notation baseline: ArchiMate 3.2

| Attribute | Value |
| --- | --- |
| Standard | ArchiMate® 3.2 Specification |
| Document number | C226 |
| Publisher | The Open Group |
| Authoritative page | <https://www.opengroup.org/library/c226> (HTTP 200, 2026-09-09; page title verified: "ArchiMate® 3.2 Specification", SKU `C226`) |
| Forum landing | <https://www.opengroup.org/archimate> (HTTP 200, 2026-09-09) |

ArchiMate 3.2 is the **normative notation baseline** for every model file,
template, viewpoint, and semantic validation rule in this practice. Model files
carry `version="3.2"` on the `model` root to denote this baseline.

### Version currency (checked 2026-09-09)

The Open Group also publishes a newer **ArchiMate® 4 Specification**
(document C260, <https://www.opengroup.org/library/c260>, HTTP 200, page
title verified "ArchiMate® 4 Specification"). This practice deliberately
remains on ArchiMate 3.2 and does **not** claim ArchiMate 4 support:
templates, relationship-legality rules, exchange-file validation, and the
regression fixtures are all defined against the 3.2 metamodel. Adopting
ArchiMate 4 — notation, metamodel, or any newer exchange format — is a
**separately validated compatibility change**, not an implicit upgrade, per
the governing requirement *"ArchiMate baseline"* in the
`enterprise-architecture-modeling` spec. The 3.2 specification (C226)
remains published and available at the authoritative page above.

## Method baseline: TOGAF Standard, 10th Edition

| Attribute | Value |
| --- | --- |
| Standard | TOGAF® Standard, 10th Edition |
| Publisher | The Open Group |
| Downloads page (authoritative) | <https://www.opengroup.org/togaf-standard-10th-edition-downloads> (HTTP 200, 2026-09-09; page title verified: "TOGAF® Standard, 10th Edition Downloads") |
| Program landing | <https://www.opengroup.org/togaf> (HTTP 200, 2026-09-09) |

TOGAF Standard, 10th Edition is the **method and governance baseline**: the
Architecture Development Method (Preliminary, Phases A–H, Requirements
Management) structures the template library under
`docs/architecture/diagrams/` and the governance mapping in
`docs/architecture/governance.md`. OpenSpec is the change-control system for
this implementation; it is not an enterprise-architecture repository or a
substitute for TOGAF governance.

## Interchange baseline: ArchiMate 3.x Open Exchange XML

The interchange baseline statement of record lives in
`docs/architecture/schemas/archimate-exchange/SCHEMAS.md` and is restated
here for traceability:

- ArchiMate 3.2 uses the **same Open Exchange file format schemas as
  ArchiMate 3.1** — the "archimate3" 3.0 exchange schemas published by The
  Open Group at <https://www.opengroup.org/xsd/archimate/> ("ArchiMate®
  Model Exchange File Format for the ArchiMate 3.1/3.2 Modeling Language").
  **There is no separate 3.2 XSD revision.**
- The `version="3.2"` attribute on a repository model file denotes the
  modeling-language baseline; structural validation always targets the
  pinned 3.x exchange schema chain
  (`archimate3_Diagram.xsd` → `archimate3_View.xsd` → `archimate3_Model.xsd`
  plus `dc.xsd`, `xml.xsd`, and the repository vendor-extension schema).
- The schema resource page was verified live and current on 2026-09-09
  (HTTP 200, page title exactly "ArchiMate® Model Exchange File Format for
  the ArchiMate 3.1/3.2 Modeling Language", listing `archimate3_Diagram.xsd`,
  `archimate3_Model.xsd`, and `archimate3_View.xsd`), matching the
  checksum-pinned copies documented in SCHEMAS.md.
- Schema validation is the **structural tier only**; relationship legality
  and direction require the separate semantic tier implemented by
  `scripts/archimate/engine.py` (see
  `docs/architecture/toolchain-verification.md`).

Adopting a newer exchange format (for example a future ArchiMate 4 set) is a
separately validated compatibility change.

## Verification procedure for this record

Re-verify the links before relying on them:

```sh
for url in \
  https://www.opengroup.org/library/c226 \
  https://www.opengroup.org/library/c260 \
  https://www.opengroup.org/archimate \
  https://www.opengroup.org/xsd/archimate/ \
  https://www.opengroup.org/togaf \
  https://www.opengroup.org/togaf-standard-10th-edition-downloads ; do
  code=$(curl -sI -L -o /dev/null -w '%{http_code}' --max-time 20 "$url")
  echo "$code  $url"
done
```

Observed output on 2026-09-09: HTTP 200 for all six URLs. Record any changed
status (redirect, 404, superseded document number) here as part of the next
baseline review; a moved or retired authoritative page is a governance input,
not a silent break.
