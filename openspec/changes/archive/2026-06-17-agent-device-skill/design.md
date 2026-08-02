## Context

The TDT workspace has no skill for verifying POEMS Mobile 3 on a real device, simulator, or emulator. Agents can reason about code and run JVM unit tests, but there is no in-session path to open the iOS Simulator app, interact with it via structured accessibility refs, and verify the UI end-to-end.

`agent-device` from Callstack (MIT, v0.17.6, 2.8k★) is purpose-built for this. Callstack ships a **bundled skill** at [`callstack/agent-device`](https://github.com/callstack/agent-device/blob/main/skills/agent-device/SKILL.md) that is ~30 lines of pure router — no command syntax duplication, version-matched via `agent-device help workflow`. The skill's `name` field is `agent-device` and it uses `npx skills add` as its installation mechanism. This change adopts that skill wholesale instead of writing a custom one, and installs it into the **first-class TDT skills root** (`.agents/skills/`) so it is indexed by `config/codex/scripts/build-skills-index.sh` and committed to git alongside the 95 existing TDT skills.

The matching `agent-device` CLI is installed once at the **operator level** via `npm install -g agent-device@<pinned-version>`; the agent never runs that command. The agent verifies the install with `agent-device --version` and reads `agent-device help workflow` before any device verification work.

## Goals / Non-Goals

**Goals:**
- Install Callstack's canonical `callstack/agent-device` bundled skill into the **first-class TDT skills root** (`tdt-meta/.agents/skills/agent-device/SKILL.md`) via `npx skills add`, with `--copy` for git-portability.
- Make the operator-level `npm install -g agent-device@<pinned-version>` a **documented, gated prerequisite** with a version floor (`>= 0.14.0`) and explicit version-pinning.
- Wire the skill into `.agents/INDEX.md` (not `AGENTS.md`, which is over the 150-line cap), `.agents/SKILLS_INDEX.md`, and `openspec/INDEX.md`.
- Keep the Callstack skill canonical: TDT does not fork it or add TDT-specific rules to it. Any TDT overrides go in `.agents/INDEX.md`, not in the skill itself.

**Non-Goals:**
- Not authoring a custom skill. The Callstack skill IS the skill.
- Not vendoring `agent-device` into the workspace (it stays a global npm install).
- Not duplicating command surface from `agent-device help` into the skill.
- Not replacing or competing with `playwright-cli` / `browser-cli` (web downloads).
- Not CI automation. Callstack publishes an EAS workflow template separately.
- Not autonomous npm installation by the agent.

## Decisions

### D1: First-class install into `.agents/skills/`, not an agent-specific fallback

**Decision:** Install the skill into `tdt-meta/.agents/skills/agent-device/SKILL.md` using `npx skills add callstack/agent-device -a universal -a codex -a cursor --copy -y` from `tdt-meta/`. This is the **first-class TDT skills root** that the build index script reads from, and the canonical home for the 95 existing committed TDT skills.

**Rationale:** From the `npx skills` README (vercel-labs/skills v1.5.11), the following agents all use `.agents/skills/` as their project path: `universal`, `codex`, `cursor`, `cline`, `dexto`, `gemini-cli`, `github-copilot`, `firebender`, `deepagents`, and others. Targeting any of them — but NOT `claude-code` (which uses `.claude/skills/`) — lands the skill in the canonical TDT root. Choosing `universal`, `codex`, and `cursor` covers the three agents the TDT workspace explicitly supports. The skill becomes a peer of `playwright-cli`, `openspec-propose`, `openspec-apply-change`, and the other 95 committed TDT skills.

**Alternatives considered:**
- **Target only `claude-code`**: Rejected. Claude Code installs to `.claude/skills/`, not `.agents/skills/`. The skill would not be discovered by `config/codex/scripts/build-skills-index.sh` and would not appear in the human-readable `SKILLS_INDEX.md` or the generated `skills-index.json`. The TDT skills root is `.agents/skills/`; the skill must live there.
- **Target only `codex`**: Acceptable as a minimum (Codex uses `.agents/skills/`), but `universal` is the official "Universal" agent and explicitly maps to `.agents/skills/` in the `npx skills` README. Targeting both `universal` and `codex` is the safest minimal set.
- **Target `claude-code` AND `codex` and let the CLI create the skill in two locations**: Rejected. Creates a duplicate skill in two paths; the TDT skills index picks up only the `.agents/skills/` one, so the `.claude/skills/` one is dead weight unless a Claude Code user specifically wants it. If a Claude Code user wants it, they can re-run `npx skills add -a claude-code` separately; that's a per-operator decision, not a workspace decision.

### D2: `--copy` for git-portability, not the default symlink

**Decision:** Pass `--copy` to `npx skills add` so the installed `SKILL.md` is a regular file in `.agents/skills/agent-device/`, not a symlink to an `npx` cache directory.

**Rationale:** The TDT convention is to commit skills to git (the 95 existing skills are all committed, including `openspec-propose`, `playwright-cli`, etc.). The default `npx skills add` install method is **symlink** — this points into a per-process cache that breaks across machines, on `npx` cache eviction, and when other contributors clone the repo. A symlinked skill in git is fragile. The `--copy` flag creates a regular file that survives `npx` cache eviction, works for every contributor after `git pull`, and behaves identically to a hand-written skill.

**Trade-off:** `--copy` means that a re-run of `npx skills add callstack/agent-device --copy -y` overwrites the committed file in-place with the upstream's latest version. That is exactly the right model for "operator-driven upgrade" — it gives the operator a single, discoverable command to refresh the skill to the upstream version. The 95 existing TDT skills are hand-maintained; the `agent-device` skill is the first one in the workspace that is **explicitly an upstream-mirrored copy**, and that distinction is worth a one-line note in the skill's `INDEX.md` entry.

### D3: Operator-level CLI install with a pinned version, not `@latest`

**Decision:** The operator runs `npm install -g agent-device@<pinned-version>` exactly once, where `<pinned-version>` is a specific version chosen by the operator (the proposal mentions `0.17.6` as the current latest, but the operator may pin to any version that satisfies the `>= 0.14.0` floor). The agent MUST NOT run this command and MUST NOT run `npx -y agent-device@latest`.

**Rationale:** Per the Callstack bundled skill: "Do not run `npm install -g agent-device@latest` or `npx -y agent-device@latest` autonomously, and do not include version/upgrade commands in final plans." Mutable package execution is a supply-chain risk; the agent must surface the install command to the operator and let the human pin and approve. The operator's pinned version is the single source of truth, and the agent's job is to verify (`agent-device --version` returns a string `>= 0.14.0`) and use it.

**Path when binary is missing but operator has it elsewhere:**
The Callstack skill says: "If that fails but the user may have installed `agent-device` globally, check the user's configured login/interactive shell and environment before using `npx`. Resolve the command the same way the user would from a normal terminal session, then run the absolute binary path if found." The TDT install spec enforces this: the agent reports the missing binary and prints the exact `npm install -g agent-device@<pinned-version>` command the operator should run; the agent does not run any npm install command autonomously.

### D4: Session state in `~/.agent-device/`, not `~/.tdt/`

**Decision:** Document `~/.agent-device/` as the canonical daemon state directory. Do not redirect it.

**Rationale:** Per callstack's AGENTS.md: packaged installs use `~/.agent-device`; source checkouts use worktree-scoped dirs under `~/.agent-device/dev/`. The operator manages this path. It is explicitly **outside** `~/.tdt/` because upstream owns it. This is a documented exception to the `~/.tdt/` canonical root.

### D5: Skill is read-only; TDT overrides go in `.agents/INDEX.md`

**Decision:** If TDT ever needs a workspace-specific rule (e.g., "always use a specific simulator name"), add it to `.agents/INDEX.md` (or a dedicated TDT supplement), not as a modification to the installed Callstack skill.

**Rationale:** Modifying the installed skill would create a divergence from upstream that TDT must manually track. The `.agents/INDEX.md` supplemental pattern is cleaner and avoids divergence. This matches the existing TDT pattern where `AGENTS.md` is the override layer for upstream skills.

### D6: MCP wiring is opt-in, documented as a reference
The MCP integration capability (`agent-device-mcp-integration`) covers the opt-in `agent-device mcp` server. No `.cursor/mcp.json` or `.mcp.json` is committed to the workspace.

### D7: `.agents/INDEX.md` (not `AGENTS.md`) gets the pointer

**Decision:** Add the device-verification pointer to `tdt-meta/.agents/INDEX.md` (which already exists and serves as the navigation file for the `.agents/` directory) under a new "Mobile Device Automation" section, not to `AGENTS.md`.

**Rationale:** `AGENTS.md` is 271 lines, well over the 150-line cap. The workspace already routes some navigation to `.agents/INDEX.md`; this is the established pattern for "I want to mention a skill without bloating AGENTS.md." It also gives the operator a single file to grep for "device verification" without opening `AGENTS.md`.

### D8: The skill is a router; the OpenSpec is the documentation layer

**Decision:** The installed Callstack skill remains a thin router (per upstream AGENTS.md: "Skills are thin routers. Keep `skills/**/SKILL.md` focused on when to use the skill, version gating, which `agent-device help <topic>` page to read, and a short default loop. Do not duplicate full CLI manuals in skills."). The TDT OpenSpec (`agent-device-command-surface`, `agent-device-verify-loop`) is the TDT documentation layer that captures TDT-specific guardrails, common patterns, and POEMS Mobile 3 usage notes. The OpenSpec is consumed by humans (reviewers, future maintainers) and by the TDT agent only at design time, NOT at runtime by the installed skill.

**Rationale:** The installed skill is upstream-mirrored and refreshed via `npx skills add ... --copy`. Any change to the skill from the agent side is overwritten on the next refresh. TDT-specific behavior belongs in TDT-owned files (`.agents/INDEX.md`, OpenSpec specs, AGENTS.md overrides), not in the skill. This separation also means TDT can have richer documentation than the skill (which intentionally stays minimal) without forking the upstream skill.

## Risks / Trade-offs

- **[R1: Agent runs `npx -y agent-device@latest`** → The Callstack skill explicitly forbids it. `.agents/INDEX.md` reinforcement makes it a double-barrier. The install spec requires a version pin.
- **[R2: Operator does not have Xcode / Android SDK installed** → Skill documents prerequisites in a reference section. Agent reports blocker; does not proceed.
- **[R3: Skill drifts from upstream after `npx skills add ... --copy` update** → The skill is a copy in `.agents/skills/agent-device/SKILL.md`. The operator controls when to re-run `npx skills add callstack/agent-device --copy -y` to refresh. Until re-installed, the skill is frozen at the committed version. The git diff after a refresh will show the upstream diff verbatim.
- **[R4: macOS iOS simulator-set scoping hides macOS desktop** → Callstack's own AGENTS.md calls this out. Not TDT-specific; agents reading `agent-device help workflow` will encounter the correct behavior.
- **[R5: Session left open** → The default loop (`open -> snapshot -i -> ... -> close`) is the skill's default. The agent's responsibility is to close before finishing.
- **[R6: Node version mismatch** → `agent-device` requires Node 22+. TDT tooling already requires Node 22+ per `package.json` of mcp-router and other repos.
- **[R7: Symlink method (default) accidentally used in CI** → Mitigation: install spec mandates `--copy`; `tasks.md` step 2.1 enforces it; a verification step (`file tdt-meta/.agents/skills/agent-device/SKILL.md`) confirms the file is regular, not a symlink.

## Migration Plan

**Apply order:**
1. Confirm `npx` is on PATH and `npx --version` succeeds.
2. Confirm `npm config get prefix` is on PATH (operator's global install will land there).
3. Operator installs `agent-device@<pinned-version>` globally: `npm install -g agent-device@<pinned-version>` (NEVER `@latest`). Verify: `agent-device --version` returns a version `>= 0.14.0`.
4. From `tdt-meta/`, run `npx skills add callstack/agent-device -a universal -a codex -a cursor --copy -y`.
5. Verify the skill file is a regular file (not a symlink): `file tdt-meta/.agents/skills/agent-device/SKILL.md` returns "ASCII text" or similar.
6. Verify the skill's `name` frontmatter is `agent-device` and references `agent-device help workflow`.
7. Append the `agent-device` entry to `.agents/SKILLS_INDEX.md` under a new "Mobile Device Automation" category; increment total 95 → 96.
8. Run `bash config/codex/scripts/build-skills-index.sh` to regenerate `.codex/skills-index.json` (and the markdown copy).
9. Run `bash config/codex/scripts/skill-validation-check.sh` to confirm the new skill passes validation.
10. Add a "Mobile Device Automation" section to `.agents/INDEX.md` pointing to the new skill.
11. Register the four new capability names in `openspec/INDEX.md`.
12. Validate with `openspec validate agent-device-skill --strict`.
13. `git status` inside `tdt-meta/`: confirm only the expected new files (the skill body, the index entry, the `INDEX.md` bullet, the four spec files, the openspec `INDEX.md` update).
14. Commit inside `tdt-meta/`. Do NOT archive the OpenSpec change until at least one real device-verification task has used it successfully.

**Rollback:** Delete `tdt-meta/.agents/skills/agent-device/SKILL.md`, revert the index entries, revert `.agents/INDEX.md` bullet, revert `openspec/INDEX.md` registration. The `agent-device` npm package on the operator machine is independent of the workspace.

## Open Questions

- **Q1: Does `npx skills add callstack/agent-device` install into the current working directory?** Yes — it installs into `./skills/agent-device/` by default. To land in the canonical TDT path (`./.agents/skills/`) the operator MUST pin agent flags from the `.agents/skills/`-using set: `universal`, `codex`, `cursor`, `cline`, `dexto`, `gemini-cli`, `github-copilot`, `firebender`, `deepagents`. This change uses `-a universal -a codex -a cursor` as the minimal correct set.
- **Q2: What if `npx skills` is not available on the operator's machine?** The skill install assumes `npx` is available (Node 22+). If `npx` is missing, the operator must install Node first. The prerequisite table in the skill's reference section will document this.
- **Q3: Should we version-lock the skill to a specific release?** The Callstack skill is lightweight and the risk of an upstream breaking change is low. We install the latest; the operator re-runs `npx skills add callstack/agent-device --copy -y` to refresh. Each refresh is a one-line git diff in `tdt-meta/.agents/skills/agent-device/SKILL.md`.
- **Q4: Which version of `agent-device` should the operator pin?** Per the Callstack bundled skill, the floor is `0.14.0`. The current latest is `0.17.6`. The operator picks; the agent verifies `>= 0.14.0`.
- **Q5: Should the install also target `claude-code`?** Optional, per-operator. The TDT workspace does not need it (the canonical skills root is `.agents/skills/`, and Claude Code reads from `.claude/skills/`). If a Claude Code user wants the same skill in their own Claude Code skills directory, they can run `npx skills add callstack/agent-device -a claude-code --copy -y` themselves; that lives outside the TDT workspace and is not a workspace concern.
- **Q6: Will the symlink install (without `--copy`) work for git?** No. A symlink points into the operator's `npx` cache, which is per-machine. Other contributors cloning the repo would see a broken symlink. The `--copy` flag is mandatory for committed skills.
