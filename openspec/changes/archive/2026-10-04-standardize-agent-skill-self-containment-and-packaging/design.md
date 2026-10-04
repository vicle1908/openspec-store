# Design: Standardize Agent Skill Self-Containment, Modular Packaging, and Progressive Disclosure

## Architecture Overview
This design updates the governing specification `workspace-openspec-skill-discovery` in `openspec-store` to establish formal standards for shared agent skills across the multi-repository workspace.

By elevating skill self-containment, structured subdirectories, progressive disclosure, and prompt economy into normative requirements, autonomous coding agents (Hermes, Claude Code, Codex, Pi, Goose) gain reliable, deterministic operational tools that function identically across any workspace repository or clean container environment.

---

## 1. Modular Directory Layout Standard

Every canonical skill in `~/Developer/.agents/skills/<skill-name>/` must adhere to this standardized layout:

```text
.agents/skills/<skill-name>/
├── SKILL.md                          # Primary specification, quickstart, and procedure
├── scripts/                          # Portable execution scripts (optional if purely guidance)
│   └── <tool>.py / <tool>.sh         # Executable, self-contained CLI tool
├── references/                       # Deep documentation, schemas, and taxonomies
│   └── <topic>.md                    # Loaded on-demand; not injected into default turn context
└── templates/                        # Configuration or manifest templates (optional)
    └── <template>.yaml / <template>.json
```

---

## 2. Progressive Disclosure & Context Budget Rules

### Frontmatter Standard
- Standard YAML frontmatter starting at byte 0 (`---`), ending with `\n---\n`.
- Required fields:
  - `name`: lower-case, hyphens/underscores, matching directory name.
  - `description`: Single sentence ending with a period. The active, unambiguous trigger condition MUST be fully self-contained within the first 57 characters. Total length MUST NOT exceed 60 characters.
  - `user-invocable`: boolean (`true`).
  - `metadata.hermes`: tags and related skills.

### Body Progressive Disclosure
1. **Quick Start**: Concrete command examples with immediate utility.
2. **When to Use**: Clear operational scenarios for invocation.
3. **When NOT to Use (Negative Counter-Triggers)**: Explicit exclusions preventing hallucinated or misdirected invocations.
4. **Procedure**: Step-by-step instructions framed strictly through native agent tools (`terminal`, `read_file`), never raw shell lines.
5. **Pitfalls**: Root-cause failure taxonomy referencing `references/` subfiles.
6. **Verification**: Checkable assertions to prove the skill succeeded.

---

## 3. Machine-Readable Interface Standard

Any execution script bundled within a skill (`scripts/*.py` or `scripts/*.sh`) MUST:
- Accept `--root <path>` to target arbitrary workspace repositories.
- Support `--json` returning structured JSON objects with `success`, `passed_checks`, and `violations`.
- Exit with status code `0` on clean pass, non-zero on violation.
- Degrade gracefully when optional external binaries (e.g. `actionlint`, `zizmor`) are absent from the environment.

---

## 4. Verification & Discovery Synchronization
- The skill must be verified with `sync-workspace-agent-skills.py --check` to guarantee:
  - Exactly one `SKILL.md` at root.
  - Zero `.claude-plugin` or `.cursor-plugin` subdirectories.
  - Accurate symlink creation across user-level agent roots (`~/.agents/skills/`, `~/.claude/skills/`).
