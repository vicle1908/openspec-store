## Context

See `proposal.md` for motivation. Pi is deliberately a minimal harness: its stable core is smaller than Claude Code or Codex, while extensions supply optional capabilities such as MCP, sub-agents, diagnostics, and GitNexus. Hermes therefore needs orchestration guidance that distinguishes Pi core contracts from locally installed extension flags.

The skill lives in the active Hermes profile outside the OpenSpec Git repository. The shared OpenSpec store records scope, decisions, and verification evidence while the skill file remains the implementation surface.

## Goals / Non-Goals

**Goals:**

- Use official Pi documentation plus installed `pi --help` as the evidence hierarchy.
- Prefer `pi -p` without PTY for bounded, non-interactive delegation.
- Scope tools explicitly and use external Git/test verification.
- Document session, model, thinking, extension, skill, and context-file controls.
- Make version and extension boundaries explicit.

**Non-Goals:**

- Hiding Pi behind a lowest-common-denominator abstraction.
- Changing the user's Pi packages, provider, model, or credentials.
- Treating optional extension flags as guaranteed Pi core features.
- Trusting the delegated agent's final narrative as completion evidence.

## Decisions

### Decision: Treat installed help as the executable contract

Exact flags and accepted values come from local `pi --help` for v0.83.0. Official pi.dev documentation remains authoritative for concepts and architecture. Extension-provided flags are labeled separately because they vary by installation.

### Decision: Prefer print mode for Hermes orchestration

Hermes uses `pi -p "<task>"` without PTY for one-shot work. Interactive TUI operation uses a PTY only when ongoing steering, model switching, or session-tree navigation is required.

### Decision: Bound execution with the host

Pi v0.83.0 has no native `--max-turns` flag. Hermes uses narrow prompts, explicit tool allowlists, complexity-adaptive host timeouts, and progress monitoring. A host timeout indicates partial work and requires inspection; it is not proof of failure or completion.

### Decision: Separate core features from extensions

The skill describes Pi core first. It notes that sub-agents, MCP, diagnostics/formatting, and GitNexus may be supplied by optional packages. Commands must be checked against `pi list` and current help before relying on extension behavior.

### Decision: Verification remains external

Hermes independently inspects Git status/diff, reads changed files, and runs focused tests. Process exit zero or Pi's final narrative alone is insufficient.

### Decision: Skip delta specs

This change adds procedural skill documentation only. No product or platform requirement changes; `.openspec.yaml` uses `skip_specs: true`.

## Risks / Trade-offs

- **CLI or extension drift** -> Version-qualify behavior and re-run `pi --help`, `pi list`, and `pi --version` before future updates.
- **Unbounded turns** -> Use host timeouts and split large tasks into milestones.
- **Broad Bash authority** -> Use disposable worktrees, narrow prompts, explicit working directories, and external verification.
- **Optional-package confusion** -> Clearly distinguish core flags from extension-provided flags.
- **Skill lives outside the store** -> Record exact path, version, checks, and outcomes in `verification.md`.
