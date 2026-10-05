# Plan Review: correct-tool-version-authority-enforcement

**Reviewed:** 2026-10-05T01:30:00Z  
**Providers:** Hermes (Spec Compliance), Claude Code (Security), Codex (Quality & Tests), Antigravity (Architecture), Kimi (Product Scope), OpenCode (Failure Modes)  
**Status:** Approved for Apply  

## Alignment Summary

| Edge | Status | Provider | Evidence |
| :--- | :--- | :--- | :--- |
| **Spec ↔ Code** | PASS | Hermes | Delta specs align with updater commands (`kilo upgrade`, `pi update`, `prime-agent update`) and Homebrew vs npm provenance rules. |
| **Code ↔ Docs** | PASS | Codex | Code patterns adhere to AGENTS.md single source of truth; docs reflect exact CLI invocation contracts. |
| **Docs ↔ Skills** | PASS | Antigravity | Tool skills (`research/web-search-clis`, `autonomous-ai-agents`) match declared updater commands and path precedence. |
| **Skills ↔ Specs** | PASS | Kimi | Spec requirements preserve existing skill invocation flags without breaking non-interactive modes (`pi -p`, `prime-agent -p`). |
| **Spec ↔ Docs** | PASS | Hermes | Runbooks and ecosystem inventories mirror the 3 delta specs (`agent-cli-inventory-coverage`, `workstation-toolchain-inventory`, `archive-integrity-reconciliation`). |
| **Code ↔ Skills** | PASS | Antigravity | Normalization of scoped npm packages (`@scope/package@version` → `@scope/package`) prevents unintended skill breakage. |
| **Spec ↔ Tests** | PASS | Codex | Scenarios specify executable criteria for Homebrew Cellar ownership, deny list normalization, and currency separation. |
| **Code ↔ Tests** | PASS | Codex | Verification plan incorporates unit tests for updater registry mapping and CLI provenance resolution. |
| **Knowledge ↔ Code** | PASS | Hermes | Reconciled against live package listings: `@kilocode/cli@7.8.3`, `anomalyco/tap/opencode 1.18.34`, `/opt/homebrew/bin/prime-agent`. |

---

## Security Lens (Claude Code)

| Edge | Status | Evidence |
| :--- | :--- | :--- |
| **Credential & Secret Protection** | PASS | Value-blind inspection of LaunchAgents (`~/Library/LaunchAgents/`) and crontab (`crontab -l`) ensures no env values, API keys, or tokens are logged in reports. |
| **Privilege Separation** | PASS | Automated updater restricts commands to sanctioned user-level paths (`~/.npm-global`, `~/.local/bin`, Homebrew prefix) and suppresses unauthorized sudo/root mutations. |
| **Deny Roster Enforcement** | PASS | Normalized identity matching prevents bypasses via version suffixes or alternate scoped formatting. |

---

## Provider Findings & Adjustments Applied

### 1. Hermes (Spec Compliance)
- **Finding**: Kilo updater was historically referenced as `update` instead of `upgrade`.
- **Adjustment Applied**: Standardized command to `kilo upgrade` in delta specs, proposal, and tasks.

### 2. Antigravity (Architecture)
- **Finding**: Opencode exists in both Homebrew tap (`anomalyco/tap/opencode`) and global npm (`opencode-ai`).
- **Adjustment Applied**: Added provenance precedence rule: resolve via active PATH execution target (`command -v opencode`) and map authority to the underlying install directory rather than package name ambiguity.

### 3. Codex (Quality & Tests)
- **Finding**: Differentiating local updater exit code from upstream currency.
- **Adjustment Applied**: Added Requirement: *Post-update reporting separates idempotence from channel currency*, ensuring zero exit on no-op is not conflated with verified upstream currency.

---

## Verdict
```
VERDICT: PASS
```
The plan is strictly validated and ready for apply via `openspec instructions apply --change correct-tool-version-authority-enforcement`.
