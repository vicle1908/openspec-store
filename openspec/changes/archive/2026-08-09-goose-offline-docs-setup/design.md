# Design: Goose Offline Docs Setup

## Architecture

The goose-doc-guide skill checks `GOOSE_DOCS_ROOT` before answering goose-specific questions. When set to a local path, goose reads markdown files directly with its file tools — no network required.

```
~/.config/goose/config.yaml
  └── GOOSE_DOCS_ROOT: /opt/goose-docs

/opt/goose-docs/
├── goose-docs-map.md          ← index file
└── docs/
    ├── getting-started/...
    └── guides/...
```

## Steps

1. Clone `aaif-goose/goose` at tag `v1.45.0` (matching installed binary)
2. `cd documentation && npm install && npm run build`
3. Copy `build/` to `/opt/goose-docs`
4. Add `GOOSE_DOCS_ROOT: /opt/goose-docs` to `~/.config/goose/config.yaml`
5. Test with: `goose run -t "How do I configure a provider?" --no-session -q --max-turns 3`

## Trade-offs

- Requires ~200MB disk for the docs tree
- Docs version must match goose binary version
- Network docs are always canonical; local copy may drift
