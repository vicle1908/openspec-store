# Tasks: Cleanup legacy giaoduc references

## 1. Spec text cleanup

- [x] 1.1 Update `register-custom-provider-credentials/spec.md` line 6: replace `(shopapikey, giaoduc, cockpit)` with `(shopapikey, phanmemvip, cockpit)`.
- [x] 1.2 Update `agent-core-model-resolution/spec.md` line 5: replace "the active giaoduc Claude-Fable Messages setup" with "the active phanmemvip Codex Responses setup".
- [x] 1.3 Update `tdt-env-loader-tdt-home/spec.md` line 386: replace `provider: "giaoduc"` with `provider: "phanmemvip"` in the illustrative scenario.
- [x] 1.4 Update `omp-fresh-shell-contract/spec.md` line 4: replace "giaoduc/Advance preserved as the default role" with "shopapikey/Claude-Fable as the default routing role".
- [x] 1.5 Update `resilience/spec.md` lines 20-21: replace "giaoduc is the primary provider and it is unreachable" with "phanmemvip is the primary provider and it is unreachable".

## 2. Backup cleanup

- [x] 2.1 Remove pre-migration backup files (stale): `~/.kimi/config.toml.bak-pre-kimi-grok.20260826T084559`, `~/.grok/config.toml.bak-pre-phanmemvip.20260825T204602`, `~/.grok/config.toml.bak-pre-claude-fable.20260825T221454`. Keep only the latest rollback backup (`bak-pre-kimi-grok.20260826T084559` for Claude-Fible) and `bak-pre-envkey` (for grok auth changes).

## 3. Validation

- [x] 3.1 Audit: `grep -rn "giaoduc" ~/Developer/openspec-store/openspec/specs/` returns only intentional REMOVED assertions (absent/SHALL NOT lines). Verify: 0 unexpected matches.
- [x] 3.2 Validate: `openspec validate --all --strict --store openspec-store`. Verify: exit 0.
- [x] 3.3 Archive + commit.
