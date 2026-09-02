## 1. Evidence collection

- [ ] 1.1 Write `evidence/erratum-mode-state.json`: authoritative state record — `~/.kimi-code/config.toml` mode is 0600 (verified by `stat -f '%Lp'`), no source chmod performed, byte-identity verified (SHA-256 `19103e4c…` identical pre/post), backup created at `~/.kimi-code/config.toml.mode600-backup-20260902T231238`. Cite the contradiction: archived `2.1-kimi-pm-sh-runbook.json` says 0644/drift=true, archived `2.0-hardening-evidence.json` says 0600/no-mutation. Verify: every claim cites archived file + line; zero credential values.

## 2. Validation

- [ ] 2.1 Run `openspec validate erratum-kimi-runbook-mode-stale-claim --strict --store openspec-store` and record the exact result. Verify: valid with zero issues.

## 3. Closure

- [ ] 3.1 Commit only this change directory (`git add -- openspec/changes/erratum-kimi-runbook-mode-stale-claim`; use `git commit --only` if foreign index entries must be preserved), no push. Verify: the resulting commit's file list is confined to this change directory.
- [ ] 3.2 Leave this change ACTIVE permanently — it records the erratum for future audit reference. Do not archive. Verify: no archive command is executed.
