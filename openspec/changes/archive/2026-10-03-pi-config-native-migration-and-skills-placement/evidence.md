# Verification Evidence: pi-config-native-migration-and-skills-placement

**Date**: 2026-10-03
**Status**: Verified & Validated
**Pi version**: 1.0.0

---

## 1. Verification Summary

| Area | Command / Method | Observed Result | Status |
|---|---|---|---|
| Provider resolution | `pi --list-models` | All 6 providers resolve natively from `models.json` (cockpit 3, omniroute 6, shopapikey 1, phanmemvip 1, omniroute-anthropic 1, omniroute-responses 1) | Pass |
| Package inventory | `pi list` | 5 packages; `pi-setup-custom-providers` and `pi-mcp-adapter` absent | Pass |
| MCP exposure | `pi mcp list` | `mcp-router: connected, 139 tools (codemode, global)` | Pass |
| MCP exclusivity | Startup log inspection | No `registers command /mcp` warning | Pass |
| Host-provided packages | Startup log inspection | No `Host-provided extension packages` warning | Pass |
| Skill surfaces | Structural inventory | `~/.pi/agent/skills` removed; `~/.agents/skills` = 85 links + 11 real dirs | Pass |
| Link integrity | `find ~/.agents/skills -xtype l` | No broken links | Pass |
| Lockfile integrity | `~/.agents/.skill-lock.json` | 11 tracked entries intact and still real directories | Pass |
| Startup health | `pi --print` with stderr capture | Healthy; zero warnings | Pass |
| Change validation | `openspec validate` | Change is valid | Pass |

---

## 2. Before / After State

| Surface | Before | After |
|---|---|---|
| `~/.pi/agent/skills` | 47 copies (148K) | Removed |
| `~/.agents/skills` | 70 entries (mix of real dirs) | 85 links + 11 real dirs |
| `~/Developer/.agents/skills` | 37 skills | 37 skills (unchanged) |
| Pi packages | 7 | 5 |
| MCP implementations | 2 (built-in + adapter) | 1 (built-in) |

---

## 3. Structural Findings

- The product-specific root `~/.pi/agent/skills` was a **pure subset** of `~/.agents/skills`: 0 unique entries, 46 of 47 entries byte-identical. One entry (`graphify`) differed.
- Prelude to consolidation: 61 entries in `~/.agents/skills` duplicated a workspace skill root; all 61 were **byte-identical** and **none** were lockfile-tracked, so all were safe to convert to links.
- After conversion, the only real directories remaining are the 11 entries recorded in `~/.agents/.skill-lock.json`, which have no workspace counterpart. This is the correct distinction between a linked workspace skill and a globally installed one.

---

## 4. Correction Recorded

An earlier analysis in this effort claimed the MCP surface cost approximately 11,000–17,000 prompt tokens per turn because `mcp-router` used `directTools: true`.

- **Corrected fact**: `directTools` is a `pi-mcp-adapter` key. The adapter was removed, so native Pi ignores it. The native key is `exposure`, which was unset and therefore defaulted to `codemode`.
- **Verified**: `pi mcp list` reports `(codemode, global)`, and a direct tool-call probe returned not-declared. No MCP tools are declared to the model; all are reached through `codemode`.
- **Consequence**: migrating from the adapter to built-in MCP resolved the archived finding of an oversized direct MCP surface as a side effect.

---

## 5. Upstream Follow-Ups — Resolved

1. **Pi 1.0.0 fullscreen default — decision: keep the official default.** `tuiMode` remains unset, so fullscreen stays in effect and no settings write was required. Recorded as an explicit decision (task 8.1), not an unaddressed gap. All fullscreen sub-settings remain at their documented defaults.
2. **`graphify` skill — decision: option A, do not install the Pi variant.** The source repository was renamed from `safishamsi/graphify` to `Graphify-Labs/graphify` (old URL returns HTTP 301); the recorded path `graphify/SKILL.md` no longer exists; upstream generates per-agent variants via `tools/skillgen` on default branch `v8`. An earlier note claiming the installed copy referenced a non-existent `Task` tool is **withdrawn**.

   Resolution: the `graphifyy` CLI (`~/.local/bin/graphify`, 0.9.74) owns and self-refreshes the skill. `graphify install --platform agents` advanced `~/.agents/skills/graphify` from 0.9.71 to 0.9.74; only the version marker changed, because `SKILL.md` was already byte-identical to upstream `graphify/skill-agents.md` (41,456 bytes). `graphify install --platform copilot` brought `~/.copilot` from 0.9.69 to 0.9.74, and the CLI reports **zero** remaining staleness warnings.

   The Pi-specific path (`graphify install --platform pi`, which writes `~/.pi/agent/skills/graphify/SKILL.md`) was **deliberately not used**, because it targets the product-specific root that task 4.3 removed under the requirement that agents discover shared skills through standard `.agents/skills` locations without copied directories under product-specific configuration roots. Pi discovers `graphify` through `~/.agents/skills/graphify`, which resolves to `~/Developer/.agents/skills/graphify` and is current at 0.9.74. Amending the governing spec to permit a product-specific Pi copy was declined.

   Note: the local `skill-pi.md` remains an older rendering (48,797 bytes, 2026-05-05) versus upstream v8 (41,732 bytes). It is unused under option A; no action taken.

   This also corrected an inaccurate earlier framing: the skill content was **not** stale, only its version marker.

---

## 6. Retained Backups

| Backup | Contents |
|---|---|
| `/tmp/pi-skills-migrate-20261003104225` | Pre-migration `pi-agent-skills`, `agents-skills`, `dev-agents-skills`, both lock files |
| `/tmp/pi-link-convert-20261003105535` | Pre-link-conversion `~/.agents/skills` tree and lock file |
| `/tmp/pi-migrate/final` | Pre-migration `settings.json` and `models.json` |

Backups are in temporary storage and should be relocated if retention is required.

---

## 7. Out of Scope (tracked separately)

- `~/.pi/web-search.json` remains mode `0644` while holding inline secrets.
- `~/.pi-lens` occupies 339 MB; `~/.pi/agent/tmp` holds an 80 MB stale install.
- Project trust remains wide (`/Users/androidteam/Developer`) by explicit operator decision.
