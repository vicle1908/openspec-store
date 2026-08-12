# Tasks: correct-omp-native-cockpit-main-spec

## 1. Ground-truth verification

- [x] 1.1 Confirm live omp cockpit endpoint is `http://localhost:51006/v1`
- [x] 1.2 Confirm live omp cockpit transport is `openai-responses`
- [x] 1.3 Confirm native `/v1/responses` returns `pong`
- [x] 1.4 Confirm adapter Docker mapping is host `8788` → container `8787`
- [x] 1.5 Confirm no live omp provider uses `localhost:8787` or `localhost:8788`

## 2. Main spec correction

- [x] 2.1 Replace stale current endpoint wording in `openspec/specs/omp-provider-routing/spec.md`
- [x] 2.2 Replace stale adapter-port scenario with native cockpit scenario
- [x] 2.3 Preserve adapter ownership boundary for Claude Code/WebUI
- [x] 2.4 Validate the change strictly

## 3. Closeout

- [x] 3.1 Archive this correction change and update the main spec
- [x] 3.2 Run full store validation
- [x] 3.3 Verify archived change and clean diff

## Evidence

- Native cockpit: `http://localhost:51006/v1/responses` → `pong`
- Live `models.yml`: cockpit `baseUrl=http://localhost:51006/v1`, `api=openai-responses`
- Adapter Docker mapping: `8787/tcp -> 127.0.0.1:8788`
- Main spec correction is documentation-only; no live files modified.
