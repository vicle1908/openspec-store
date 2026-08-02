# Tasks: Setup TDT Python Workspace

## Section 1: Git Init (repos already pulled)

- [x] 1.1 Run `git init` + initial commit in each of the 16 repos
- [x] 1.2 Verify: 18 total git repos (16 Python + go-microservices + mcp-router)

## Section 2: Python .gitignore

- [x] 2.1 Add standard Python .gitignore to each of the 16 repos
- [x] 2.2 Commit .gitignore in each repo

## Section 3: rclone Bisync Setup

- [x] 3.1 Create filter file at ~/.config/rclone/tdt-filters.txt
- [x] 3.2 Run `rclone bisync --resync` for each repo (GDrive → local)
- [x] 3.3 All 16 repos resync'd successfully

## Section 4: Python Environments

- [x] 4.1 Run `uv sync` in each repo with pyproject.toml
- [x] 4.2 Verify: 16 virtual environments created
- [x] 4.3 All repos synced successfully

## Section 5: Workspace AGENTS.md

- [x] 5.1 Create ~/Developer/AGENTS.md listing all repos and workspace layout
- [x] 5.2 Content includes repo table, workspace rules, and sync command

## Section 6: Validate and Archive

- [x] 6.1 `openspec validate setup-tdt-python-workspace --store openspec-store` — valid
- [x] 6.2 Archive the OpenSpec change
