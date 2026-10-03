# Design

## Context

See `proposal.md` — Why. The relevant constraints:

- Pi 1.0.0 implements the Agent Skills specification and, per its loader source, reads skills from four locations in precedence order: project `.pi/skills`, project/ancestor `.agents/skills`, user `~/.pi/agent/skills`, and user `~/.agents/skills` (last wins on name collision).
- OpenSpec CLI assigns `skillsDir: .pi` to Pi and `.agents` to "Other / Universal (shared)"; user-level `~/.agents` is a Pi-added convention layered over the shared standard.
- The canonical workspace skill root is `~/Developer/.agents/skills/`, already governed by `workspace-openspec-skill-discovery`, which requires user-scope entries to resolve to the canonical root rather than hold copies.
- Project `.agents/skills` discovery is trust-gated; user `~/.agents/skills` is not.
- Pi 1.0.0's built-in `mcp` extension is `replaceable`, and a third-party extension registering `/mcp` displaces it.

## Goals / Non-Goals

**Goals:**
- Pi resolves providers, MCP, and skills entirely through Pi-native or standard mechanisms.
- Skills live at exactly one canonical location per ownership class.
- The setup remains reversible, with retained pre-change copies.

**Non-Goals:**
- Narrowing project trust. Trust remains wide by explicit operator decision.
- The separate security and disk-hygiene items (world-readable `~/.pi/web-search.json`, `~/.pi-lens` size). Tracked separately.
- Rewriting generator-owned skills or changing their generating tools.

## Decisions

### Decision: Providers remain in `~/.pi/agent/models.json`; the wizard package is removed

Pi resolves compatible endpoints and models natively from `models.json`. The removed `pi-setup-custom-providers` additionally declared host-provided packages (`@mariozechner/pi-coding-agent`, `@mariozechner/pi-tui`) in `dependencies`, which Pi flags because installed copies can bypass the extension loader and duplicate runtime modules. Removing it eliminates both problems.

*Alternatives considered:* patching the package manifest locally (rejected — Pi reconciles installs and overwrites such edits; and the fix is upstream's to make).

### Decision: Built-in MCP is the sole MCP implementation

Pi 1.0.0's built-in MCP covers server management (`pi mcp add|list`), `/mcp`, exposure control (`codemode`, `deferred`, `direct`, `hidden`), `toolExposure` overrides, OAuth, and `tool_search`, and reads the same `~/.pi/agent/mcp.json`. It also reads the `description`, `timeout`, and `enabled` fields. The removed `pi-mcp-adapter` was written before these capabilities landed.

*Rationale for exclusivity:* the built-in `mcp` extension is marked `replaceable`; if both are present one is silently dropped and the two connect the same servers. Exactly one implementation is a hard invariant, not a preference.

*Important correction recorded:* `directTools` is an adapter key. Native Pi ignores it. The server's effective exposure came from the default `codemode`, verified by `pi mcp list` reporting `(codemode, global)` and a direct-call probe returning not-declared.

### Decision: Delete the product-specific root; bridge workspace skills as links

`~/.pi/agent/skills` was a pure subset of `~/.agents/skills` (no unique entries; 46 of 47 byte-identical), and `~/.agents/skills` already wins precedence. The directory was removed after confirming no entry would be lost.

The 26 promoted skills were materialized as real directories. Because each duplicates a workspace skill root, the governing convention requires `~/.agents/skills/<name>` to be a **link** to the canonical root. Correcting these to links is a follow-up task in this change.

*Alternatives considered:* leaving the copies in place (rejected — violates the existing link convention and reintroduces drift); promoting everything as links from the outset (partially done; the remaining corrections are tracked as tasks).

### Decision: Placement rule is ownership-based

Machine/service-level and vendor/library guidance (for example agentmemory tooling, Redis library guidance, the Notion CLI) is exposed at user scope so it applies in every project. Generator-owned skills (OpenSpec CLI, GitNexus package) stay in the canonical workspace root and are exposed at user scope only through links.

## Risks / Trade-offs

- **Removing a package that provided a UI surface** → The provider wizard's interactive flow is lost; providers are edited as JSON. Acceptable because Pi has no native equivalent wizard, and the data already lived in `models.json`.
- **Deleting a product-specific root could lose a unique skill** → Mitigated by verifying zero unique entries before removal and retaining a full pre-change copy.
- **Link conversion could break discovery if a target moves** → Verification must report stale, broken, missing, or conflicting links, as the governing spec already requires.
- **Name collision between a link target and an existing global installation** → The governing spec requires verification to fail rather than overwrite; promotions skipped entries that already existed (`handoff`).
- **Trust remains wide, so project `.agents/skills` load in every trusted repo** → Accepted by operator decision; recorded as a non-goal rather than an unaddressed gap.

## Migration Plan

Applied in this order so nothing was transiently lost:

1. Back up both skill surfaces and their lock files; back up `settings.json` and `models.json`.
2. Promote the 26 machine/vendor skills into `~/.agents/skills` (verified no collisions).
3. Remove `~/.pi/agent/skills` after re-confirming zero unique entries.
4. Remove `pi-mcp-adapter`; set `extensions` to `+builtin:mcp`.
5. Verify: `pi --list-models` resolves all providers; `pi mcp list` reports one server on the built-in path; Pi starts with no warnings.

**Rollback:** restore the retained pre-change copies of both skill surfaces and their lock files, reinstall the removed packages with `pi install`, and restore `settings.json`. The `mcp.json` server definition was already in native format and is unaffected.

## Open Questions

- **TUI mode.** Pi 1.0.0 changed the default to fullscreen. `tuiMode` is unset, so the new fullscreen behavior is in effect. Whether to keep it or set `"regular"` is a user preference, not a correctness issue, and does not change the specs or the approach.
- **`graphify` skill provenance and refresh path.** Correction to an earlier note, which was wrong in three ways. The source repository was renamed: `github.com/safishamsi/graphify` returns HTTP 301 to `github.com/Graphify-Labs/graphify`, whose default branch is `v8`; the recorded path `graphify/SKILL.md` returns 404 because upstream now generates per-agent variants via `tools/skillgen`. The earlier assertion that the installed copy referenced a non-existent `Task` tool is withdrawn. Critically, the refresh path is **not** hand-editing or re-pinning a lockfile: the `graphifyy` CLI (installed at `~/.local/bin/graphify`, currently `0.9.74`) owns and self-refreshes this skill. Its own diagnostics report `~/.agents/skills/graphify` at `0.9.71` and advise `graphify install --platform agents`. Official platform targets also include `pi` (`graphify install --platform pi`). The `~/.agents/skills/graphify` symlink to `~/Developer/.agents/skills/graphify` pre-dates this change (created 2026-08-25) and is not something this change introduced. Action is tracked as tasks 7.4–7.6.
