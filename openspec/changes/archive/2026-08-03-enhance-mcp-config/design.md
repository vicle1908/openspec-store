## Context

The MCP Router (Desktop Commander) is configured via `set_config_value` at runtime. Current defaults were set during initial setup and haven't been tuned for the workspace's actual usage patterns. Over 160 sessions and 3900+ tool calls, the following pain points emerged:

- `defaultShell: /bin/sh` — system uses `zsh`; terminal commands may behave differently than expected
- `fileReadLineLimit: 500` — 1185 file reads recorded; large files (300+ lines) require re-reads
- `fileWriteLineLimit: 50` — 207 writes recorded; bulk writes require excessive chunking

## Goals / Non-Goals

**Goals:**
- Align `defaultShell` with system default (`zsh`) for consistent terminal behavior
- Increase read limit to 1000 lines to cover most source files in a single read
- Increase write limit to 100 lines to reduce chunking overhead

**Non-Goals:**
- Restructure the workspace or change `allowedDirectories`
- Modify `blockedCommands` list (already comprehensive)
- Change telemetry or feature flag settings
- Persist config in version control (runtime state only)

## Decisions

### 1. `defaultShell`: `/bin/sh` → `zsh`

**Decision:** Change to `zsh` to match `systemInfo.defaultShell`.

**Rationale:** Terminal commands via `start_process` and `terminal` use this shell. Mismatch can cause subtle differences (e.g., glob expansion, history, plugins). The system already reports `zsh` as default.

**Alternative considered:** Keep `/bin/sh` for maximum portability — rejected because this is macOS-only, `zsh` is the default since Catalina.

### 2. `fileReadLineLimit`: 500 → 1000

**Decision:** Double the limit.

**Rationale:** Most source files in the workspace are under 500 lines, but config files, handlers, and multi-function modules often exceed it. 1000 covers the vast majority without returning excessively large payloads.

**Alternative considered:** Remove limit entirely — rejected because it could cause context overflow for very large generated files.

### 3. `fileWriteLineLimit`: 50 → 100

**Decision:** Double the limit.

**Rationale:** Current 50-line limit forces 3+ chunks for typical file writes. 100 lines reduces chunking while staying within safe single-call bounds.

**Alternative considered:** 150 lines — rejected as too aggressive; the tool warns on large writes and 100 is a clean doubling.

## Risks / Trade-offs

- **[Risk] zsh-specific behavior in terminal commands** → Mitigated: workspace is macOS-only, zsh is standard since 2019
- **[Risk] Larger reads consume more context window** → Mitigated: 1000 lines is still modest; targeted reads use offset/length
- **[Risk] Config not persisted across MCP server restarts** → Accepted: config is runtime state; user can re-apply if needed
