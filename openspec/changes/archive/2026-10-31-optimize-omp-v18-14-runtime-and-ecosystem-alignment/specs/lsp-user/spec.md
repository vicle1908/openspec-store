# lsp-user Specification Delta

## ADDED Requirements

### Requirement: User-Level Python 3.15 Target Alignment in lsp.json

`~/.omp/agent/lsp.json` SHALL configure `servers.basedpyright.settings["python.version"]` as `"3.15"`, aligning user-level Python language-server diagnostics with the workspace CPython `3.15.1` (`requires-python >=3.15`) standard while preserving `typeCheckingMode: "basic"` and `python.analysis.extraPaths: ["src"]`.

#### Scenario: basedpyright user-level config targets Python 3.15
- **WHEN** `/Users/androidteam/.omp/agent/lsp.json` is parsed as JSON
- **THEN** `servers.basedpyright.settings["python.version"]` SHALL equal `"3.15"`
- **AND** `diagnosticsOnWrite`, `diagnosticsOnEdit`, and `formatOnWrite` SHALL remain `true` with `idleTimeoutMs` equal to `300000`
