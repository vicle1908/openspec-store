# Tasks: Standardize client_type=0 Bundle Attribution for Workstation TCC Permissions

## 1. TCC Provenance Verifier Alignment

- [x] 1.1 Update `scripts/tcc_provenance.py` to support and verify `client_type = 0` (`CFBundleIdentifier`) bundle identities (`org.python.python`, `com.stablyai.orca`, `com.trycua.driver`, `com.electron.goose`, `ai.opencode.desktop`, `com.openai.codex`, `com.nousresearch.hermes`, `org.p0deje.Maccy`) with native `Security.framework` `csreq` signature validation, and verify execution via `python3 scripts/tcc_provenance.py --json`.
- [x] 1.2 Ensure `tcc_provenance.py` evaluates bundle identities without reporting ephemeral `client_type = 1` Cellar path updates as missing grants, and verify fail-closed error handling remains active for true signature or permission denials.

## 2. Maintenance Runners and Post-Upgrade Code Signing

- [x] 2.1 Update `platform/openspec-store/scripts/workstation-daily-update.sh` and `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` to ensure post-upgrade re-signing (`sign_agent_binaries`) unconditionally restores bundle invariants and signs `Python.app` with `Developer Agent Code Signing` (`H"65340d85afd298131c682d8463087891292a2b59"`).
- [x] 2.2 Synchronize `platform/openspec-store/scripts/workstation-daily-update.sh` to `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` (`cp then chmod 755`) and verify zero SHA-256 drift in `config/script-provenance-manifest.tsv`.

## 3. Script Provenance and Snapshot Growth Hygiene

- [x] 3.1 Synchronize `/Users/androidteam/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh` to `platform/openspec-store/scripts/knowledge-refresh/refresh-knowledge-indexes.sh` (`cp then chmod +x`), update `config/script-provenance-manifest.tsv`, and verify `diff -u` returns zero.
- [x] 3.2 Verify `~/.agentmemory/snapshots` loose object hygiene and ensure the daily maintenance runner maintains snapshot repository size below the 1.0 GiB ceiling.

## 4. OpenSpec Strict Validation and Verification

- [x] 4.1 Validate the change strictly via `~/.npm-global/bin/openspec validate standardize-client-type-0-tcc-governance --strict --json --store openspec-store` and verify exit code 0.
- [x] 4.2 Execute `python3 scripts/tcc_provenance.py --bundles --json` and `bash /Users/androidteam/Developer/scripts/workstation-daily-update.sh --check` to verify zero drift.
