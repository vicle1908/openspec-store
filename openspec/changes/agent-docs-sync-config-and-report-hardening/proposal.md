# agent-docs-sync-config-and-report-hardening

## Why

The ecosystem review identified test coverage gaps in the configuration precedence chain and report/exit-code semantics.

1. **Config precedence untested**: 4-layer precedence (env > repo > TDT global > code defaults). No tests for alternate TDT_HOME, absent config, malformed YAML, env var type coercion, or precedence ordering.

2. **Report semantics untested**: No tests for generation failure + gaps together, provider error variants, `generation_completed` interaction, or nested `results.report` unwrapping.

3. **Untracked files need disposition**: `.scratch/e2e_test.py` (4274 bytes) and `doc-sync/SKILL.md` (295-byte placeholder stub) require inspection and decision.

## What Changes

### Testing
- Add config precedence tests for each layer
- Add config edge-case tests: malformed YAML, missing config, alternate TDT_HOME
- Add env var type coercion tests: string to int/float
- Add report semantics tests: generation failure + gaps, provider error variants, generation_completed interaction
- Add exit code tests mapping report states to exit codes

### Cleanup
- Inspect `.scratch/e2e_test.py` for valid tests, move or remove
- Remove `doc-sync/SKILL.md` placeholder stub
- Separate graphify-generated changes from functional changes

### Repos in scope
- `agent-docs-sync` (config.py, cli.py, tests/)
