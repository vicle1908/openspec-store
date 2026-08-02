## Why

The previous `harden-store-multi-repo-wiring` change was archived before
completing the core multi-repo wiring. It set the global `defaultStore`,
removed the spurious `openspec/openspec/` directory, and added artifact
rules — but did NOT:

1. Create `store:` pointers in any of the 8 target code repos
2. Add a git remote for team sharing
3. Relocate non-standard files from `openspec/` root to `docs/governance/`

Without store pointers, the command-resolution chain still fails at layer 3
for every code repo. The global `defaultStore` (layer 4) works as a fallback
but is the lowest precedence and not the recommended pattern.

## What Changes

### 1. Per-repo store pointers

Create `openspec/config.yaml` with `store: openspec-store` in each target
repo. For `ai-harness-skills/`, add the pointer to the existing config while
preserving `openspec/schemas/harness-13/`.

After each pointer, run `openspec update` to generate AI tool skill files.

### 2. Git remote and store.yaml

Add a git remote and update `.openspec-store/store.yaml` with the `remote`
field so `openspec store doctor` prints actionable clone instructions.

### 3. Relocate non-standard root files

Move governance docs from `openspec/` root to `docs/governance/`:
- `AGENTS.md`, `INDEX.md`, `AUDIT_INDEX.md`, `ALIGNMENT_SUMMARY.md`,
  `SPEC_TO_CODE_ALIGNMENT_AUDIT.md`, `AUDIT_COMPLETION_SUMMARY.txt`
- `reports/` directory

Update cross-references in AGENTS.md (line 19: `openspec/config.yaml`,
line 49: `scripts/config/agent-skill-surfaces.json`).

## Impact

- All 8 wired repos auto-resolve to the shared store
- Teammates can clone via doctor output
- `openspec/` root conforms to official structure
- No application code or runtime change

## Non-Goals

- Workspace-level skill consolidation (already done in previous change)
- CI/CD validation gates
- Fixing 66 spec validation failures (covered by repair-openspec-main-spec-baseline)
