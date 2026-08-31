# Write-Set Reconciliation — 2026-08-30

Value-blind planning evidence. Reconciles the frozen pre-apply manifest's
planning scope ("12 provider surfaces"; `apply_safety.backup_file_mode` "all
12 mutate targets") against the actual live write set after ownership changes.

## Surface-to-file mapping (12 surfaces → 11 file writes)

| Surface | Live file | Action by this change |
|---|---|---|
| claude-code | `~/.claude/settings.json`, `profiles/`, `helpers/` | VERIFY-ONLY — externally owned by archived `2026-08-30-add-claude-code-omniroute-pm-launcher`; task 4.1 reads as verify/preserve |
| codex | `~/.codex/omniroute.config.toml` (new) | CREATE mode 0600; base `~/.codex/config.toml` untouched |
| goose | `~/.config/goose/custom_providers/custom_omniroute_anthropic.json` (new) | CREATE mode 0600; SH provider `custom_omniroute_sh.json` already live (archived owner) |
| kilo | `~/.config/kilo/kilo.jsonc` | MODIFY additive |
| opencode | `~/.config/opencode/opencode.json` | MODIFY additive |
| droid | `~/.factory/settings.json` | MODIFY additive (`customModels` entries only) |
| grok | `~/.grok/config.toml` | MODIFY additive (`[model]` rows + `[model_providers]` per FBC-3) |
| kimi-code | `~/.kimi-code/config.toml` | MODIFY additive; literal-key bytes preserved |
| omp | `~/.omp/agent/models.yml` | MODIFY additive; `config.yml` roles untouched |
| pi | `~/.pi/agent/models.json` | MODIFY additive |
| prime-agent | `~/.prime/agent/models.json` | MODIFY additive |
| cline | `~/.cline/data/settings/providers.json` | MODIFY additive (new provider entry only) |

The Copilot `.zshrc` launcher binding remains DEFERRED (drift-provenance.md);
no `.zshrc` write by this change.

## Backup scope correction

`pre-apply-manifest.json` `apply_safety.backup_file_mode` ("0o600 (all 12
mutate targets)") is planning-scoped and predates the claude-code ownership
transfer. Authoritative backup set: the **9 existing modify targets** (mode
0600, atomic copy, `evidence/apply-backups.py`, fail-closed on baseline
drift). The **2 created-file targets** carry no backup: their frozen baseline
absence is the rollback record (rollback = delete the created file).

## Rollback map vs write set

The manifest `rollback` map enumerates 31 entries (all surfaces planned at
freeze time). 11 are in this change's write set. The remaining 20 receive no
write from this change; their baseline hashes are re-verified post-apply as
preservation evidence (tasks 4.6/5.6), including: the 7 claude-code surfaces,
codex base `config.toml`, goose `config.yaml` + 4 live provider files + the
removed responses-template slot, omp `config.yml`, pi `settings.json`, prime
`auth.json`/`settings.json`/`telemetry.json`, and `.zshrc`.

## Go/no-go state (2026-08-30)

- `apply-backups.py` rewritten **fail-closed**: full read-only preflight
  (9 modify targets == frozen baseline sha+mode, 2 create targets absent, 20
  non-targets == baseline or == drift register, destinations inside the 0700
  backup root, no foreign files) runs BEFORE any byte is copied; then atomic
  mode-600 copies; then hash verification; value-blind
  `apply-backups.json`. `--preflight-only` proves the gate without copying.
- Baseline drift on the three non-targets reconciled WITHOUT regenerating the
  baseline: `evidence/baseline-drift-register.json` (externally-owned helper,
  churned codex base config, deferred `.zshrc` — with value-blind parsed
  metadata and the enforcement rule that the apply preflight and post-apply
  gates compare these paths against the registered current hashes).
- Fresh integrity precheck (2026-08-30): 9/9 modify targets match frozen
  baseline; 2/2 create targets absent; 20/20 non-targets stable (17 baseline
  match + 3 registered).
- Backup execution remains HELD for the three outstanding task-2.2 reviewer
  verdicts (protocol reviewer already returned PASS); live apply is locked
  behind the same verdicts.
- Cline credential classification recorded: `cline-credential-classification.md`.
- No live configuration write has occurred yet.
