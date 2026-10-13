# Plan Review: durable-workstation-updater

**Reviewed:** 2026-10-13 14:15:00 +07:00
**Providers:** Hermes (Inline Orchestrator), Claude Code (Security), Codex (Quality & Tests), Antigravity (Architecture), Kimi (Product Scope), OpenCode (Cross-Cutting)
**Review Tier:** standard (fresh-context assurance active)

---

## Alignment Summary

| Edge | Status | Provider | Evidence / Resolution |
| :--- | :--- | :--- | :--- |
| **Spec ↔ Code** | PASS | Hermes | Delta spec defines normative `SHALL` requirements matching `shb-schedule/v1` DBOS workflows and discrete step execution. |
| **Code ↔ Docs** | PASS | Codex | Step structure adheres to `AGENTS.md` and `portable-workstation-toolchain` vendor precedence guidelines. |
| **Docs ↔ Skills** | PASS | Antigravity | Incorporates `skills update -y` (1800s bound) with 5 drift metric classifications and `.agents/skills/` symlink parity checks. |
| **Skills ↔ Specs** | PASS | Kimi | Spec delta mandates parity validation via `sync-workspace-agent-skills.py --check`. |
| **Spec ↔ Docs** | PASS | Hermes | Runbook and design document reflect identical non-interactive sentinels (`CI=1`, `NONINTERACTIVE=1`, `HOMEBREW_NO_AUTO_UPDATE=1`). |
| **Code ↔ Skills** | PASS | Antigravity | Preserves `AGENT_CLI_COVERED` static updater mappings and shields pinned coding agents (`codex`, `claude`, `pi`, `kilo`) from broad global upgrades. |
| **Spec ↔ Tests** | PASS | Codex | Every scenario in `spec.md` maps to concrete verification tasks in `tasks.md` and testable exit-code assertions. |
| **Knowledge ↔ Code**| PASS | OpenCode | Provenance hash checks bound to `platform/openspec-store/config/script-provenance-manifest.tsv`. |

---

## Security Lens (Claude Code Review & Resolution)

| Edge / Domain | Initial Finding | Resolution in Planning Artifacts | Final Status |
| :--- | :--- | :--- | :--- |
| **F1: Spec scenario structure** | Bare `- Scenario:` lines lacked executable `#### Scenario:` blocks. | Rewritten with full BDD-style `#### Scenario:` headers, `- **WHEN** ... **THEN** ... **AND** ...` blocks, and normative `SHALL`/`MUST` text. | PASS |
| **F2: Privilege & `sudo`** | Privilege escalation model unaddressed; risk of hanging on password prompts. | Mandated that workflow SHALL never invoke `sudo` or query interactive Keychain prompts; fail-fast skip on elevated packages. | PASS |
| **F3: Deletion boundaries** | Deletion steps lacked authorization allowlists and anti-globbing guards. | Pinned exact allowlist paths (`com.user.brew-npm-update.plist.disabled`, `com.microservices.developer-workstation-tool-update.plist.disabled`, `~/.local/bin/brew-npm-update.sh`, `~/Library/Application Support/...`), verified non-symlink, and required `launchctl bootout` before unlink. | PASS |
| **F4: Injection guards in loops**| Dynamic tool loops (`uv`, `npm`, `bun`) could allow command injection. | Enforced regex validation `^[A-Za-z0-9._@/+-]+$`, discrete argv passing with `--`, and static maps for Agent CLIs. | PASS |
| **F5: File modes & Secret isolation** | Unspecified permissions for logs/manifests; Telegram token exposure risk. | Explicit directory mode `0700` and file mode `0600`. Tokens read strictly from `~/.shb/.env` at runtime; secrets omitted from checkpoints, logs, and alert payloads. | PASS |
| **F6: Provenance definition** | Self-referential digest ambiguity. | Bound to expected SHA-256 recorded in store's `script-provenance-manifest.tsv`. | PASS |
| **F7: Process match predicate**| Ambiguous `pgrep` matching. | Pinned to exact match `pgrep -x "$APP_NAME"`, ignoring updater subprocesses. | PASS |

---

## Provider Findings & Architectural Assessment

### Antigravity (Architecture Lens)
* **Verdict:** PASS
* **Assessment:** Integrating with `shb-schedule` aligns workstation maintenance with our standard enterprise scheduling ecosystem. The 8 discrete DBOS workflow steps isolate failure domains so a transient network timeout on skills refresh does not trigger unnecessary rebuilds or reinstalls of Homebrew or NPM packages.

### Codex (Quality & Tests Lens)
* **Verdict:** PASS
* **Assessment:** Task decomposition in `tasks.md` provides clause-by-clause traceability to the delta spec. Non-interactive sentinels and process lock checks guarantee idempotency across multiple runs.

### Kimi (Product Scope Lens)
* **Verdict:** PASS
* **Assessment:** Scope is cleanly bounded: covers package managers (Homebrew, NPM, Bun), Mac App Store (`mas`), Python CLIs (`uv`), and remote skills while explicitly excluding persistent database engines, Docker daemon lifecycles, and quarantined credential stores.

### OpenCode (Cross-Cutting Lens)
* **Verdict:** PASS
* **Assessment:** Incorporates pre-flight battery checks (`pmset -g batt`), lockfile contention checks, non-interactive environment sentinels, and structured JSON telemetry.

---

## Final Review Verdict

**VERDICT: PASS**

The planning artifacts (`proposal.md`, `design.md`, `specs/portable-workstation-toolchain/spec.md`, `tasks.md`, `review-scope.yaml`) are fully aligned, vetted against official documentation and modern best practices, and ready to apply.
