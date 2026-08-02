# Design: Initialize OpenSpec Store as Git Repository

## Current State

```
~/Developer/openspec-store/
├── .openspec-store/
│   └── store.yaml          ← identity file (version: 1, id: openspec-store)
├── openspec/
│   ├── config.yaml          ← merged Go + TDT context
│   ├── AGENTS.md            ← store-specific instructions
│   ├── specs/               ← 328 main specs
│   ├── changes/
│   │   ├── archive/         ← 255 archived changes
│   │   └── 12 active changes
│   └── reports/             ← 8 alignment reports
└── (no .git, no .gitignore)
```

## Proposed State

```
~/Developer/openspec-store/
├── .git/                    ← NEW: git repository
├── .gitignore               ← NEW: excludes .DS_Store, logs, temp
├── .openspec-store/
│   └── store.yaml           ← committed (identity)
├── openspec/                 ← committed (all specs, changes, reports)
│   ├── config.yaml
│   ├── AGENTS.md
│   ├── specs/ (328)
│   ├── changes/archive/ (255)
│   └── reports/ (8)
```

## Steps

### 1. Create .gitignore

```gitignore
.DS_Store
**/.DS_Store
*.log
__pycache__/
*.pyc
*.tmp
```

### 2. Initialize git

```bash
cd ~/Developer/openspec-store
git init
git add -A
git status  # verify: all openspec/ content staged
```

### 3. Commit

```bash
git commit -m "init: openspec store — 328 specs, 255 archives, 12 active changes

Merged workspace: Go microservices (8 services + platform) and
TDT Python ecosystem (16 repos). Specs include agent-core,
agent-docs-sync, platform-*, order-*, redis-*, temporal-*, and more.
Store identity: openspec-store (openspec store doctor verified)."
```

### 4. Verify

- `git log --oneline -1` shows initial commit
- `openspec store doctor` shows "Git: ok"
- `openspec validate --all --store openspec-store` still passes
- `make validate-agent-guidance` still passes

## Key Decisions

**Why `.DS_Store` in .gitignore:** 37 macOS metadata files scattered
throughout the store. These are machine-specific and should never be
committed.

**Why no remote yet:** Remote URL depends on whether this becomes a
shared team store or stays personal. That's a separate decision.

**Why initial commit includes everything:** The store is the single source
of truth. All 328 specs + 255 archives represent the current baseline.
Future commits track incremental changes.
