# Proposal: Goose Offline Docs Setup

## Why

Goose has a built-in `goose-doc-guide` skill that reads official documentation. By default it fetches from `https://goose-docs.ai` — requiring network access. Setting `GOOSE_DOCS_ROOT` to a local docs tree enables offline/air-gapped documentation access, improves response speed, and removes network dependency for goose-specific questions.

## What Changes

1. **Clone goose documentation** from the aaif-goose/goose repo at the matching version (v1.45.0)
2. **Build the docs** using `npm run build` in the `documentation/` directory
3. **Copy the built docs** to a stable local path (e.g. `/opt/goose-docs`)
4. **Set `GOOSE_DOCS_ROOT`** in `~/.config/goose/config.yaml`
5. **Verify** the `goose-doc-guide` skill reads from the local path

## Compatibility

- Purely additive — no breaking changes
- Only affects goose's documentation reading behavior
- Network access still works as fallback when `GOOSE_DOCS_ROOT` is unset
