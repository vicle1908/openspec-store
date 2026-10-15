# Design

## Context

See `proposal.md` for background.
Kimi CLI on macOS was previously provided by Homebrew Core formula `kimi-code` (v2.1.1), which installed a Node.js-wrapped runner under `/opt/homebrew/Cellar/kimi-code/2.1.1/libexec/bin/kimi` and symlinked it to `/opt/homebrew/bin/kimi`. In parallel, user configuration remained partially split between legacy `~/.kimi` and `~/.kimi-code`.

Upstream Moonshot AI publishes standalone, single-binary native Mach-O distributions (`kimi-code` 2.2.0) with an integrated migration subcommand (`kimi migrate`) and official self-update telemetry. Additionally, workspace architecture requires all coding agents to standardize on OmniRoute's `gemini-3.8-flash-high` combo.

## Goals / Non-Goals

**Goals:**
- Transition Kimi Code CLI to Moonshot AI's official standalone native installer, targeting `~/.kimi-code/bin/kimi`.
- Remove the outdated Homebrew `kimi-code` formula to prevent binary shadowing and version divergence.
- Reconcile shell configuration (`~/.zprofile`, `~/.zshrc`) so `kimi` resolves strictly to `~/.kimi-code/bin/kimi`.
- Execute full legacy data migration (`~/.kimi` → `~/.kimi-code`) via `kimi migrate --run`.
- Set `default_model = "gemini-3.8-flash-high"` in `~/.kimi-code/config.toml` backed by OmniRoute Anthropic Messages ingress (`http://localhost:20128`) with 1,000,000 max context window and thinking/tool_use capabilities.
- Harden `~/.kimi-code/config.toml` permissions to `0600`.

**Non-Goals:**
- Creating ad-hoc symlinks across `/opt/homebrew/bin` or `~/.local/bin`.
- Modifying other coding agents' routing configurations.

## Decisions

1. **Vendor Standalone Native Binary Precedence**:
   - *Decision*: Adopt Moonshot AI's official installer (`https://code.kimi.com/kimi-code/install.sh`) and standalone binary distribution over third-party Homebrew package tracking.
   - *Rationale*: Homebrew formula 2.1.1 lagged behind the official 2.2.0 release and introduced unnecessary Node.js / libexec wrapping. Official binaries run self-contained and support native self-checks (`kimi doctor`).
   - *Alternative*: Updating the Homebrew formula locally was rejected because it introduces unmaintained tap maintenance debt.

2. **Native Migration Engine Execution (`kimi migrate --run`)**:
   - *Decision*: Execute the built-in migration command with directory cleanup of macOS `.DS_Store` metadata artifacts.
   - *Rationale*: Guarantees consistent schema translation for sessions, user history, MCP server configurations, and plans while recording an authoritative completion marker in `~/.kimi-code/migration-report.json`.

3. **OmniRoute Anthropic Dialect Mapping**:
   - *Decision*: Route `gemini-3.8-flash-high` via provider `omniroute-anthropic` targeting `http://localhost:20128`.
   - *Rationale*: Kimi Code's network client implements the Anthropic Messages wire format when communicating with custom providers. OmniRoute natively translates this format to the Antigravity backend, maintaining full streaming thinking token support and context caching.

## Risks / Trade-offs

- **Risk**: Shell PATH divergence between login sessions (`zsh -lc`) and interactive sessions (`zsh -ic`).
  - *Mitigation*: Configured `export PATH="$HOME/.kimi-code/bin:$PATH"` in both `~/.zprofile` and `~/.zshrc`, verifying that `zsh -lc 'which -a kimi'` resolves exclusively to `~/.kimi-code/bin/kimi`.
