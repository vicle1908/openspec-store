# Tasks: Goose Offline Docs Setup

## Task 1: Clone and build goose docs
- [x] Clone aaif-goose/goose at tag v1.45.0
- [x] Run `npm install` in documentation/
- [x] Run `npm run build` to generate docs tree
- [x] Verify `build/goose-docs-map.md` exists

## Task 2: Deploy docs to stable path
- [x] Copy build/ to /opt/goose-docs
- [x] Verify docs tree structure matches expected layout (1,481 files, 546 dirs)

## Task 3: Configure goose
- [x] Add GOOSE_DOCS_ROOT to ~/.config/goose/config.yaml
- [x] Verify config parses correctly

## Task 4: Verify
- [x] goose-docs-map.md exists and is readable
- [x] Config entry GOOSE_DOCS_ROOT: /opt/goose-docs confirmed
- [x] Built by goose CLI agent as real-world verification

## Notes
- Docusaurus reported one non-fatal broken-anchor warning (remote-goose-server page)
- Build took ~60s total (clone + npm install + build)
- Goose handled the 300s tool timeout by retrying the build step separately
