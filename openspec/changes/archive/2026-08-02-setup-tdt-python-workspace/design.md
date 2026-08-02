# Design: Setup TDT Python Workspace

## Workspace Layout (Target)

```
~/Developer/
├── go-microservices/     ← existing (Go monorepo)
├── mcp-router/           ← existing (Node.js/pnpm)
├── openspec-store/       ← existing (shared specs)
├── AGENTS.md             ← NEW workspace-level guide
├── agent-core/           ← NEW Python (workspace peer)
├── agent-docs-sync/      ← NEW Python
├── agent-harness/        ← NEW Python
├── ai-harness-skills/    ← NEW Python
├── ai-review/            ← NEW Python
├── browser-cli/          ← NEW Python
├── code-daily-scan/      ← NEW Python
├── jira-daily-reports/   ← NEW Python
├── jira-epic-report/     ← NEW Python
├── jira-kanban-from-spreadsheet/  ← NEW Python
├── jira-skill/           ← NEW Python
├── ops-automation-suite/ ← NEW Python
├── tdt-core/             ← NEW Python
├── tdt-observability/    ← NEW Python
├── tdt-sheets/           ← NEW Python
└── webhook-receiver/     ← NEW Python
```

## Steps

### 1. Git init each repo (already pulled)

```bash
for repo in $REPOS; do
  cd ~/Developer/$repo
  git init -q
  git add -A
  git commit -q -m "initial: pull from GDrive workspace sync"
done
```

### 2. Add .gitignore for Python repos

Each repo gets a standard Python `.gitignore`:
```
__pycache__/
*.pyc
*.pyo
.venv/
*.egg-info/
dist/
build/
.env
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

### 3. Setup rclone bisync per repo

Bisync provides bidirectional sync between local and GDrive:
```bash
FILTERS=~/.config/rclone/tdt-filters.txt
# Contains:
# - .git/
# - .venv/
# - __pycache__/
# - *.pyc
# - .env
# - node_modules/

for repo in $REPOS; do
  # First run: resync (GDrive → local)
  rclone bisync ~/Developer/$repo gdrive-tdt:TDT/$repo \
    --filters-file $FILTERS --resync --progress
done
```

### 4. Setup Python environments

```bash
for repo in $REPOS; do
  cd ~/Developer/$repo && uv sync
done
```

### 5. Workspace AGENTS.md

Create `~/Developer/AGENTS.md` as workspace-level agent guide listing all repos.

## Key Decisions

**Why bisync not copy:** bidirectional — changes on either side sync.
Local git commits flow to GDrive; GDrive edits flow to local.

**Why filters:** .git/, .venv/, __pycache__/ should NOT sync to GDrive.
They're local-only state.

**Why workspace peer layout:** matches go-microservices/ and mcp-router/.
Each repo is independent with its own .git.

## Verification

1. `ls ~/Developer/` — 16 Python repos + 3 existing repos
2. `find ~/Developer -maxdepth 2 -name ".git" -type d | wc -l` — 19
3. `find ~/Developer -maxdepth 2 -name ".venv" -type d | wc -l` — 16
4. `cd ~/Developer/tdt-core && uv run python --version` — works
5. `rclone bisync ~/Developer/tdt-core gdrive-tdt:TDT/tdt-core --dry-run` — no changes
