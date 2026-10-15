# Tasks

## 1. Host Bridge Executable Authoring

- [x] 1.0 Confirm three-tier version parity before authoring the bridge: `~/Omniroute` checkout package version, running container version, and npm latest must all report `3.8.51`.
- [x] 1.1 Create `~/.local/bin/omniroute` executable script with Bun runtime, trailing-`/v1` URL normalization, key pass-through (helper only when unset), and stdout stream filtering for `📋 Loaded env from` and `[DB]` lines.
- [x] 1.2 Pin `DATA_DIR` to an ephemeral per-invocation directory so the CLI's local database fallback cannot open or mutate `~/.omniroute/storage.sqlite`.
- [x] 1.3 Route `[DB]` diagnostics to standard error and ensure offline commands exit 3 via the CLI's own `ServerOfflineError` instead of returning empty DB-backed results.
- [x] 1.4 Confirm the Bun dependency cache is warm (`~/.bun/install/cache` contains `tsx@4.23.15` and `update-notifier@7.3.1`) so no registry fetch occurs, and record the cache-resident footprint rather than claiming zero footprint.
- [x] 1.5 Set executable permissions (`chmod +x ~/.local/bin/omniroute`) and verify binary is resolvable on `$PATH`.

## 2. Interactive Shell Subcommand Multiplexing

- [x] 2.1 Update `omniroute()` in `~/.zshrc` (line 313) to multiplex CLI subcommands and flags to `command omniroute "$@"` while preserving default Claude Code launcher execution when subcommands are omitted.
- [x] 2.2 Verify interactive zsh execution dispatches `omniroute health` to the CLI binary while preserving Claude Code launch profile contracts for bare invocations.
## 3. Stdout Stream and JSON Pipeline Verification

- [x] 3.1 Verify `omniroute keys list --output json | jq '.keys | length'` succeeds with exit code 0 and zero banner corruption. Do NOT use `omniroute health --json` as the example — it emits no JSON payload on the v3.8.49 checkout.
- [x] 3.2 Verify `omniroute combo list --output json | jq .combos` returns a valid combos array (empty is acceptable) without syntax errors.
- [x] 3.3 Verify `omniroute keys list --output json | jq .keys` returns a valid JSON key array with exit code 0 against live server.
- [x] 3.4 Verify the orphan-leak block: with the server unreachable and the default `DATA_DIR`, `keys list --output json` returns stale orphan records (8 keys observed) with exit 0; with `DATA_DIR` pinned to an empty directory the same command returns `{"keys":[]}` and `~/.omniroute/storage.sqlite` mtime is unchanged.
- [x] 3.5 Verify server-dependent commands (`cost`, `health`) exit non-zero with an error rather than a successful empty dataset when the server is unreachable.

## 4. Documentation and End-to-End Smoke Testing
- [x] 4.1 Update `/Users/androidteam/Developer/docs/omniroute-agent-skills.md`: replace the "host CLI wrapper is being implemented under a dedicated separate change" boundary notice with the delivered CLI usage, and verify the inventory claims against the source tree — `~/Omniroute/skills/` contains 45 directories (21 `cli-*`, 22 `omni-*` REST, 2 specialized: `omni-github-skills`, `config-codex-cli`), while `~/.agents/skills/` holds 109 entries across all vendors, so the doc must not imply all 109 are OmniRoute skills.
- [x] 4.2 Execute comprehensive live smoke test across 5 primary `cli-*` skills (`cli-health`, `cli-models`, `cli-routing`, `cli-keys`, `cli-resilience`) asserting exit code 0.
- [x] 4.3 Confirm `omniroute()` in `~/.zshrc` still resolves to a function in interactive zsh (`whence -w omniroute`) and that `/v1/*` keyless inference paths remain unaffected by the added multiplexer branch.
