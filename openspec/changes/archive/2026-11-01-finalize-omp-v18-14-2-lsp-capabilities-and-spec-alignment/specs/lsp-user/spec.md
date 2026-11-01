# lsp-user Specification Delta

## MODIFIED Requirements

### Requirement: official OMP config hierarchy

OMP SHALL merge LSP config from five sources (lowest to highest precedence): `~/lsp.json`, plugin configs, `~/.omp/agent/lsp.json`, `<cwd>/.omp/lsp.json`, and `<cwd>/lsp.json`, while reading runtime diagnostic and formatting flags (`lsp.enabled`, `lsp.diagnosticsOnWrite`, `lsp.diagnosticsOnEdit`, `lsp.formatOnWrite`) from `~/.omp/agent/config.yml`.

#### Scenario: config merge order
- **WHEN** an agent opens a file
- **THEN** OMP SHALL merge server configs from all five levels, with higher-precedence overriding lower

#### Scenario: cwd-only root markers
- **WHEN** the agent launches from the multi-repo workspace root (`/Users/androidteam/Developer/`)
- **THEN** servers in `~/.omp/agent/lsp.json` whose `rootMarkers` include `.git` and `.claude` (`gopls`, `basedpyright`, `ruff`, `sourcekit-lsp`, `yaml-language-server`) SHALL pass startup cwd root-marker detection

### Requirement: project-scoped LSP activation

`~/.omp/agent/lsp.json` SHALL declare `gopls` (`/Users/androidteam/go/bin/gopls`), `basedpyright` (`/opt/homebrew/bin/basedpyright-langserver`), `ruff` (`/opt/homebrew/bin/ruff`, `isLinter: true`), `sourcekit-lsp` (`/usr/bin/sourcekit-lsp`), and `yaml-language-server` (`/Users/androidteam/.local/bin/yaml-language-server`) with `.git` and `.claude` in `rootMarkers` so `xd://lsp` activates from both individual project directories and `/Users/androidteam/Developer`.

#### Scenario: LSP active from project dir
- **WHEN** the agent launches from a project directory or opens a sub-repository file
- **THEN** OMP SHALL attach the sub-repository workspace folder dynamically via `workspace/didChangeWorkspaceFolders` and merge any project-local `.omp/lsp.json` overrides

#### Scenario: LSP inactive from workspace root
- **WHEN** the agent launches from `/Users/androidteam/Developer/` and queries `xd://lsp` with `{"action": "status"}`
- **THEN** `gopls`, `basedpyright`, `ruff`, `sourcekit-lsp`, and `yaml-language-server` SHALL report `(ready)` while servers without matching binaries or root markers remain inactive

### Requirement: User-Level Python 3.15 Target Alignment in lsp.json

`~/.omp/agent/lsp.json` SHALL configure `servers.basedpyright.settings["python.version"]` as `"3.15"` alongside `gopls`, `ruff`, `sourcekit-lsp`, and `yaml-language-server`, and `~/.omp/agent/config.yml` SHALL set `lsp: { enabled: true, diagnosticsOnWrite: true, diagnosticsOnEdit: true, formatOnWrite: true }`.

#### Scenario: basedpyright user-level config targets Python 3.15
- **WHEN** `/Users/androidteam/.omp/agent/lsp.json` and `/Users/androidteam/.omp/agent/config.yml` are parsed
- **THEN** `servers.basedpyright.settings["python.version"]` SHALL equal `"3.15"` and `idleTimeoutMs` SHALL equal `300000`
- **AND** `config.yml` SHALL set `lsp.enabled`, `lsp.diagnosticsOnWrite`, `lsp.diagnosticsOnEdit`, and `lsp.formatOnWrite` to `true`
