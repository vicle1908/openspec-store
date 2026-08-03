## Context

See `proposal.md` for motivation. Three external coding CLIs evolve independently, while Hermes orchestration guidance is durable procedural documentation. The installed binary can be newer than its public documentation, and a successful agent response does not prove that files landed in the requested workspace or that tests passed.

The affected skills live in the active Hermes profile, outside the OpenSpec Git repository. The shared OpenSpec store therefore records scope, decisions, and verification evidence, while skill files remain the implementation surface.

## Goals / Non-Goals

**Goals:**

- Use official documentation plus installed `--help` and bounded live probes as the evidence hierarchy.
- Encode distinct contracts for headless automation, interactive TUI operation, permissions, and sandboxing.
- Require external verification of file placement, structured output, diffs, and tests.
- Preserve reusable guidance without exposing credentials or mutating unrelated configuration.

**Non-Goals:**

- Standardizing all three CLIs behind one lowest-common-denominator interface.
- Treating undocumented aliases or UI layouts as stable contracts.
- Persisting local credential state or model quotas in OpenSpec.
- Creating normative platform requirements for user-level procedural documentation.

## Decisions

### Decision: Treat installed help as the executable contract

For exact flags and accepted values, the installed binary's help surface takes precedence over memory and over documentation examples that the binary rejects. Official documentation remains authoritative for conceptual behavior not exposed in help.

Alternative considered: rely only on public documentation. Rejected because Antigravity documentation currently contains version skew and an unsupported `--cwd` example.

### Decision: Keep filesystem workspace, logical project, permissions, and sandbox as separate concepts

- Antigravity process CWD identifies the filesystem workspace; `--new-project` creates logical project/session state.
- Claude Code tool visibility, permission rules, and Bash sandbox are independent controls.
- Codex approval policy and filesystem sandbox are independent controls; unattended editing explicitly sets both.

Alternative considered: recommend one dangerous bypass flag for simplicity. Rejected because it broadens authority and obscures failures.

### Decision: Prefer headless modes for bounded automation

Hermes uses `agy --print`, `claude -p`, and `codex exec` without PTY for one-shot work. PTY or tmux is reserved for interactive TUI behavior. Claude's native background-agent surface is preferred where appropriate.

Alternative considered: route every task through tmux. Rejected because it adds brittle dialog handling and ignores native noninteractive/background interfaces.

### Decision: Verification is external to the delegated agent

A delegated agent's final narrative is not completion evidence. Hermes reads target files, checks Git diff/status, parses structured result status, and runs focused tests independently.

Alternative considered: trust successful process exit or agent self-report. Rejected because headless soft denials and partial artifacts can coexist with misleading completion text or exit status.

### Decision: Skip delta specs

The change records procedural skill corrections and verification only. No platform requirement changes, so `.openspec.yaml` uses `skip_specs: true`.

## Risks / Trade-offs

- **CLI drift** → Version-qualify validated behavior and require runtime `--help` probes before future updates.
- **Documentation drift** → Link official sources but avoid copying unstable UI sequences as contracts.
- **Unattended authority is too broad** → Keep sandbox and approval controls explicit; reserve bypass modes for externally isolated environments.
- **Skill files are outside this Git store** → Record exact paths, versions, checks, and outcomes in `verification.md`; validate the loaded skill catalog after edits.
- **Sensitive output leakage** → Record auth presence/status only and never credential values.

## Migration Plan

1. Reload the updated skills in the active Hermes profile.
2. Run local help/version probes and bounded headless execution checks.
3. Verify skill text contains the corrected contracts and no stale positive guidance.
4. Run strict OpenSpec validation.
5. Commit this change to the shared store.

Rollback consists of reverting the OpenSpec commit and restoring the prior skill versions from the profile's backup or source package if a verified regression is found.
