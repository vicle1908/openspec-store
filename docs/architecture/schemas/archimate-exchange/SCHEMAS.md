# ArchiMate Open Exchange Pinned Schemas

Normative, checksum-pinned XML Schema set for validating ArchiMate 3.2 Open
Exchange XML model files in this repository.

## Baseline statement

The ArchiMate 3.2 Modeling Language uses the same Open Exchange file format
schemas as ArchiMate 3.1: the "archimate3" 3.0 exchange schemas published by
The Open Group at <https://www.opengroup.org/xsd/archimate/> ("ArchiMate®
Model Exchange File Format for the ArchiMate 3.1/3.2 Modeling Language", last
updated 15 November 2019). There is no separate 3.2 XSD revision; the
`version="3.2"` attribute on repository model files denotes the modeling
language baseline, while structural validation always targets the 3.x
exchange schema chain below. Adopting a newer exchange format (for example a
future ArchiMate 4 set) is a separately validated compatibility change per the
governing OpenSpec change `add-enterprise-architecture-modeling`.

## Files and checksums (SHA-256)

| File | SHA-256 | Role |
| --- | --- | --- |
| `archimate3_Model.xsd` | `f47ff9d7fe5a21fec0ee806550f4e2b47aa716774f7fcf1d1da2a6ad19b63241` | Model exchange schema (elements, relationships, organizations, property definitions) |
| `archimate3_View.xsd` | `9fe3548d807b7fd1ea46ab059d2640a00e62147b2d4ea04da08adbf3ad6dd34b` | View exchange schema (redefines `ModelType` to add `views`) |
| `archimate3_Diagram.xsd` | `f41ee34b517377a0a0e0726d2c278c3cc4d55c7f7fb49700b272fbb918756698` | Diagram exchange schema (nodes, connections, bendpoints; entry point of the chain) |
| `dc.xsd` | `9285c1b57d8920b72101b4ba93416f32aa376087481f2b5b0c5d6c95f8def7cf` | Dublin Core namespace schema distributed with the exchange set |
| `xml.xsd` | `f0fa306f2951fb1a477220eb7bdeaa35959c8d0224258f2104d3c4724ba746f7` | W3C `xml` namespace schema (`xml:lang`); used for offline import resolution |
| `vendor-extension-1.0.xsd` | `c40236e2abed3b5ee306aca8b68c7f669f776199f4e6a1842920df92ef7347b0` | Repository vendor extension namespace (required by `processContents="strict"` wildcards) |
| `validate-archimate-exchange.xsd` | `f622e20aacc33e8f2849f256bc578eaacf5afdd10e9ae3fbf02f4b9e7d83c6fb` | Validation wrapper importing the exchange chain plus the vendor extension schema |
| `catalog.xml` | `35374abee9b9cc0611a064c8641e67b76b9cd82efffa065d74bb8fa85f4ad8c0` | XML catalog remapping `http://www.w3.org/2001/xml.xsd` to the local copy |

The first five files are byte-identical to the Open Group set mirrored at
<https://github.com/archimatetool/OpenGroupXMLExchange> (path
`org.opengroup.archimate.xmlexchange/xsd/`), which carries the same files the
Open Group publishes from its exchange format resource page; verify a pin
with `shasum -a 256 <file>` before relying on offline validation. The
remaining three files are repository-owned.

## Validation command

From `docs/architecture/`:

```sh
XML_CATALOG_FILES=$PWD/schemas/archimate-exchange/catalog.xml \
  xmllint --noout --nonet \
  --schema schemas/archimate-exchange/validate-archimate-exchange.xsd \
  models/canonical.xml
```

`archimate3_Model.xsd` imports the `xml` namespace from
`http://www.w3.org/2001/xml.xsd`; the catalog pins that import to the local
`xml.xsd` so validation never depends on network availability
(`--nonet` enforces it). Schema validation is the structural tier only;
relationship legality and direction require the separate semantic tier
(`scripts/archimate/`), because the XSD checks IDREF resolution but not
relationship semantics.

## Licensing

The five Open Group schema files are © The Open Group and redistributed here
for internal offline validation under the exchange format's published terms;
ArchiMate® is a registered trademark of The Open Group. The repository-owned
files carry no third-party license obligations.
