## Why

npm audit identified 74 vulnerabilities across 3 projects (realtime/frontend, prime-agent, goose-docs/documentation), including 5 critical, 46 high, and 16 moderate severity issues. Several packages have known CVEs for SSRF, prototype pollution, XSS, and DoS attacks. These must be patched to maintain security posture.

## What Changes

- Upgrade `axios` from 1.13.2 to 1.19.0 in realtime/frontend (fixes 28+ CVEs including SSRF, prototype pollution)
- Upgrade `vitest` ecosystem from 4.0.16 to 4.1.10 in realtime/frontend (fixes arbitrary file read vulnerability)
- Upgrade `postcss` to 8.5.26 in prime-agent (fixes path traversal via sourceMappingURL)
- Upgrade `undici` to 8.10.0 in realtime/frontend (fixes CRLF injection, cache poisoning)
- Upgrade `brace-expansion` to 5.0.8 across all projects (fixes DoS via unbounded expansion)
- Upgrade `protobufjs` to 7.6.5+ in prime-agent (fixes DoS via infinite loop)
- Run `npm audit fix` on all 3 projects to address remaining transitive dependency vulnerabilities
- Note: `image-size` (DoS) has no upstream fix available - transitive dep of Docusaurus

## Capabilities

### New Capabilities

None - this is a security patch upgrade with no new features.

### Modified Capabilities

None - dependency versions are implementation details, not spec-level behavior changes.

## Impact

- **Dependencies**: axios, vitest, postcss, undici, brace-expansion, protobufjs, ws, dompurify, and transitive deps
- **Projects affected**: realtime/frontend, prime-agent, goose-docs/documentation
- **Risk**: Low - all upgrades are semver-compatible patch/minor versions
- **Testing**: Existing test suites will validate compatibility
