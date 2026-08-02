## Why

The TDT mobile platform has two large native codebases (`poems-mobile3-android` Kotlin, `poems-mobile3-ios` Swift) plus worktrees per active build, but agents working on these repos have no repeatable way to verify behavior on a real device, simulator, or emulator. Code-review reasoning alone is insufficient for visual, gesture, or platform-API work. [Callstack's `agent-device`](https://github.com/callstack/agent-device) (v0.17.6, MIT, 2.8k★) is the de-facto CLI built for this: an `open -> snapshot -i -> act -> re-snapshot -> verify -> close` loop with structured accessibility refs (`@e3`), app install/reinstall, evidence capture, and an optional MCP server.

Callstack ships a maintained, version-matched skill at [`callstack/agent-device`](https://github.com/callstack/agent-device/blob/main/skills/agent-device/SKILL.md) that serves as the canonical agent router. This change installs that skill into the TDT **first-class skills root** (`.agents/skills/agent-device/SKILL.md`) using the `npx skills add` mechanism with `--copy` so the skill is **committed to the repo** alongside the 95 existing TDT skills. The matching `agent-device` CLI is installed **once at the operator level** via `npm install -g agent-device@<pinned-version>`; the agent never runs that command.

## What Changes

- **First-class skill install** — `npx skills add callstack/agent-device -a universal -a codex -a cursor --copy -y` from `tdt-meta/`. Targeting `universal` (the canonical `.agents/skills/` agent), `codex`, and `cursor` lands the skill in `.agents/skills/agent-device/SKILL.md` (and only that path). The `--copy` flag (vs the default symlink) makes the skill **portable across machines** — a symlink to a transient `npx` cache would be broken on the next `npx skills add` run, and the skill is intended to be **committed to git** like every other skill in the workspace.
- **Operator-level CLI install gate** — The `agent-device` npm CLI is installed once by the operator (`npm install -g agent-device@<pinned-version>`, **never `@latest` without explicit operator approval**). The agent verifies the install with `agent-device --version` and reads `agent-device help workflow` before planning. A version floor of `>= 0.14.0` is enforced; older CLIs lack the version-matched help topics.
- **Workspace rule in `INDEX.md`** — `tdt-meta/AGENTS.md` is 271 lines, well over the 150-line cap. The pointer goes to `tdt-meta/.agents/INDEX.md` (which already exists as a navigation file) under a new "Mobile Device Automation" section, with the canonical entry: "Device verification: see `.agents/skills/agent-device/SKILL.md` (Callstack bundled). Run `agent-device --version` then `agent-device help workflow`."
- **Skills index update** — append `agent-device` entry to `tdt-meta/.agents/SKILLS_INDEX.md` (and regenerate `.codex/skills-index.json`) under a new "Mobile Device Automation" category. Increment total from 95 → 96.
- **Document prerequisites** — the install spec pins the operator-side prerequisites (Xcode, Android SDK, macOS Accessibility, Node 22+) and the exact `npm install -g` command the operator runs (with version pin).

No source repos change. No TDT code is built. The skill is committed; the upstream `agent-device` npm CLI is installed by the operator.

## Capabilities

### New Capabilities
- `agent-device-skill-install`: First-class installation of the Callstack `callstack/agent-device` bundled skill into `tdt-meta/.agents/skills/agent-device/SKILL.md` via `npx skills add` (using `--copy` for git-portability), plus the operator-side rule that the agent MUST NOT autonomously run `npm install` / `npx -y agent-device@latest`. Pins the CLI version floor (`>= 0.14.0`) and documents operator-side prerequisites (Xcode, Android SDK, macOS Accessibility, Node 22+).
- `agent-device-verify-loop`: The canonical `open -> snapshot -i -> get/is/find or press/fill/scroll/wait -> verify -> close` loop for verifying POEMS Mobile 3 on simulators/emulators/physical devices. Includes critical rules: refs for exploration vs selectors for durable replay, mandatory session close, serial mutating commands, and version-matched help consulted before planning.
- `agent-device-command-surface`: Coverage of the full command surface surfaced by `agent-device help` and the llms-full.txt reference: navigation (`boot`, `open`, `close`, `back`, `home`, `rotate`), interaction (`click`, `fill`, `type`, `press`, `scroll`, `swipe`, `gesture`), inspection (`snapshot`, `get`, `is`, `find`, `wait`), evidence (`screenshot`, `record`, `logs`, `perf`, `network`, `trace`, `diff screenshot`), replay (`replay`, `test`), batch, settings helpers, and React Native helpers (`react-devtools`, `metro reload`).
- `agent-device-mcp-integration`: Optional MCP server wiring for Claude Code and Cursor that exposes the same commands as structured tools. Documents the opt-in per-operator setup and the rule that the MCP server MUST NOT be used as a generic shell runner.

### Modified Capabilities
<!-- No existing OpenSpec specs govern device automation today; all capabilities are new. -->

## Impact

**Dependencies (operator-machine, not TDT repos):**
- `agent-device` npm CLI installed globally: `npm install -g agent-device@<pinned-version>` (operator pins; never `@latest` without explicit approval). The agent verifies with `agent-device --version` and confirms `>= 0.14.0`.
- Node.js >= 22 (already required for several TDT tooling).
- For iOS verification: Xcode + Command Line Tools.
- For Android verification: Android SDK + ADB.
- For macOS desktop verification: macOS Accessibility permission.

**Affected files (workspace metadata only):**
- `tdt-meta/.agents/skills/agent-device/SKILL.md` — committed; produced by `npx skills add callstack/agent-device -a universal -a codex -a cursor --copy -y`. Not authored by TDT.
- `tdt-meta/.agents/SKILLS_INDEX.md` — add one entry under "Mobile Device Automation" (new category); total 95 → 96.
- `tdt-meta/.codex/skills-index.json` — regenerated by `bash config/codex/scripts/build-skills-index.sh`.
- `tdt-meta/.agents/INDEX.md` — add a section pointing to the new skill (the only `.md` change in the workspace; `AGENTS.md` is over the 150-line cap so it's not touched).
- `tdt-meta/openspec/INDEX.md` — register the four new capability names so other changes can reference them.

**Constraints:**
- The Callstack skill is canonical. TDT MUST NOT fork or diverge from it. Any TDT-specific overrides belong in `.agents/INDEX.md` or a TDT-specific supplement, not in the skill itself.
- Per the upstream `callstack/agent-device` AGENTS.md: "Skills are thin routers. Keep `skills/**/SKILL.md` focused on when to use the skill, version gating, which `agent-device help <topic>` page to read, and a short default loop. Do not duplicate full CLI manuals in skills." The Callstack skill is a router. The TDT OpenSpec (`agent-device-command-surface`, `agent-device-verify-loop`) is the TDT documentation layer that captures TDT-specific guardrails, common patterns, and POEMS Mobile 3 usage notes — the OpenSpec is NOT the skill, the spec lives in `openspec/changes/agent-device-skill/specs/` and is consumed by humans (reviewers, future maintainers), not by the agent at runtime.
- The operator installs `agent-device` globally; the agent verifies the install with `agent-device --version` and reads `agent-device help workflow` first.
- Session state lives in `~/.agent-device/` (upstream-owned), not `~/.tdt/`.
- Critical rule: agents MUST NOT silently run `npx -y agent-device@latest` or `npm install -g agent-device@latest`. The operator pins the version.
- macOS iOS simulator-set scoping must not hide the host macOS desktop target when `--platform macos` is requested (Callstack's own footgun, called out in their AGENTS.md).

**Non-goals:**
- Not authoring a custom skill. Callstack's bundled skill IS the skill.
- Not vendoring `agent-device` into the workspace.
- Not changing `playwright-cli` / `browser-cli` (web downloads, distinct surface).
- Not adding CI replay workflows (Callstack publishes an EAS template separately).
- Not adding a Python wrapper repo.
- Not running the agent autonomously in CI without a human reviewing first.

**Risk:**
- **LOW** (skill-only, operator-install model). The skill is upstream-maintained. Worst case is a bad upstream skill version; operator can reinstall with `npx skills add callstack/agent-device --copy -y`.
- **MEDIUM** (autonomy): if an agent runs `npx -y agent-device@latest` without prompting. Mitigation: the Callstack skill's critical rule forbids it; the `.agents/INDEX.md` rule reinforces it; the install spec makes the version pin mandatory.
- **MEDIUM** (first-run permissions): macOS Accessibility, Xcode license, Android SDK dialogs block first verification. Mitigation: skill documents prerequisites; agent reports blockers.
