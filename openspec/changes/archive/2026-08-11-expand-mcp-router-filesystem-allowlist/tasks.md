# Tasks: Expand MCP Router Filesystem Allowlist

## Implementation

- [x] 1. Investigate current MCP Router config (`get_config`) and document baseline
- [x] 2. Write OpenSpec artifacts (proposal.md, design.md, tasks.md)
- [x] 3. Apply allowlist expansion via `set_config_value`
- [x] 4. Verify with `get_config` — confirm both entries present
- [x] 5. Smoke test: `list_directory("/Users/androidteam/.hermes/skills")`
- [x] 6. Smoke test: `read_file("/Users/androidteam/.hermes/config.yaml")` (non-secret)
- [x] 7. Archive OpenSpec change and commit

## Evidence

- Baseline `get_config`: `allowedDirectories: ["/Users/androidteam/Developer"]`
- Smoke test before change: all file tools work within `/Users/androidteam/Developer`
- MCP Router v0.2.47, port 3282, 126 tools registered
