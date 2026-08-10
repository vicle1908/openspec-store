## Why

npm audit identified 74 vulnerabilities across 3 projects (realtime/frontend, prime-agent, goose-docs/documentation) as of the initial audit. After running `npm audit fix` on all 3 projects, the following upgrades were applied:

### Completed Upgrades (evidence retained)

| Project | Package | Before | After | CVEs Fixed |
|---|---|---|---|---|
| realtime/frontend | axios | 1.13.2 | 1.19.0 | 28+ (SSRF, prototype pollution) |
| realtime/frontend | vitest ecosystem | 4.0.16 | 4.1.10 | Arbitrary file read |
| realtime/frontend | @vitejs/plugin-react | 5.1.2 | 5.2.0 | — |
| prime-agent | undici | 7.28.0 | 7.29.0 | CRLF injection, cache poisoning |
| prime-agent | postcss | 8.5.15 | 8.5.25 | Path traversal via sourceMappingURL |
| prime-agent | protobufjs | 7.6.4 | 7.6.5 | DoS via infinite loop |
| prime-agent | ip-address | 10.2.0 | 10.4.0 | — |
| prime-agent | brace-expansion | 5.0.7 | 5.0.9 | DoS via unbounded expansion |
| goose-docs/documentation | @docusaurus/* | 3.9.2 | 3.10.2 | Multiple transitive fixes |
| goose-docs/documentation | webpack, ws, yaml | various | patched | 17 vulnerabilities reduced |

### Residual Vulnerabilities (no upstream fix available)

| Package | Project | Severity | Rationale |
|---|---|---|---|
| image-size | goose-docs/documentation | Moderate | Transitive dep of @docusaurus/mdx-loader; no upstream fix |
| uuid | goose-docs/documentation | Low | Transitive dep of sockjs/webpack-dev-server |
| serialize-javascript | goose-docs/documentation | Moderate | Transitive dep of copy-webpack-plugin |
| dompurify | goose-docs/documentation | High | Transitive dep of @docusaurus packages |
| nanoid | prime-agent | Low | Transitive dep of postcss; no override possible |

## What Changes

Remaining work is validation only:
1. Run final `npm audit` on all 3 projects to confirm current state
2. Run build tests where applicable (documentation build, frontend build)
3. Document residual vulnerabilities with rationale
4. Commit changes with descriptive message

## Impact

- **Dependencies**: axios, vitest, postcss, undici, brace-expansion, protobufjs, @docusaurus/*, ws, and transitive deps
- **Projects affected**: realtime/frontend, prime-agent, goose-docs/documentation
- **Risk**: Low-Medium — all applied upgrades are semver-compatible patch/minor versions; residual transitive changes require build/test validation
- **Testing**: Existing test suites will validate compatibility

## Residual Risk Assessment

The 5 residual vulnerabilities are all transitive dependencies with no available upstream fixes. The risk is mitigated by:
- goose-docs is a documentation site, not a production service
- serialize-javascript and dompurify are build-time only
- nanoid is a low-severity transitive dep
- image-size is a DoS vector in the MDX pipeline, not runtime
