# Proposal

## Why

While 45 official OmniRoute skills are installed in `~/Omniroute/skills/` (21 `cli-*`, 22 `omni-*` REST, plus 2 specialized: `omni-github-skills`, `config-codex-cli`), the 21 `cli-*` skills cannot execute on the host because no `omniroute` executable exists on `$PATH` — verified: `command -v omniroute` returns nothing, while interactive zsh resolves the name to a Claude Code launcher function. Upstream's default `npm install -g` distribution would add a measured 546 MB / 26,761-file payload in a global prefix the workstation toolchain inventory does not own. The official image does not rescue this: `docker exec omniroute ls /app/bin` shows `cli/commands` but `/app/bin/omniroute.mjs` is **absent**, so there is no in-container CLI either. With the workstation running the official latest release `diegosouzapw/omniroute:latest` (v3.8.51, digest `sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218`) and the local repository checkout refreshed to commit `fd95f823d` (v3.8.51, achieving three-tier version parity with npm and the container), establishing a Bun bridge at `~/.local/bin/omniroute` unlocks these 21 CLI skills with ~0.25–1.6s execution over loopback HTTP, prevents offline invocations from mutating a stale orphan database, and suppresses unparsed startup banners from stdout JSON streams without disrupting existing Claude Code launchers.

## What Changes

- **Host Bun Bridge Binary (`~/.local/bin/omniroute`)**: Install an executable Bun wrapper that forwards CLI subcommands to `/Users/androidteam/Omniroute/bin/omniroute.mjs`, normalizing `OMNIROUTE_BASE_URL` by stripping a trailing `/v1` and passing through the `OMNIROUTE_API_KEY`/`OMNIROUTE_KEY` already exported by `~/.zshenv`, falling back to the read-only helper `~/.claude/helpers/omniroute-key.sh` only when unset.
- **Offline Fail-Closed and Host-Database Isolation**: Pin `DATA_DIR` to an ephemeral directory per invocation and let server-dependent commands exit 3 via the CLI's own `ServerOfflineError` instead of silently opening the stale host-side `~/.omniroute/storage.sqlite` and returning plausible empty results.
- **Stdout Banner Suppression**: Intercept early `console.log` lines matching `📋 Loaded env from` produced by `bin/omniroute.mjs:142` before argument parsing, plus `[DB]` diagnostics, ensuring stdout remains pure, valid JSON for piped workflows (`omniroute health --json | jq .`).
- **Interactive Shell Function Multiplexing**: Update the `omniroute()` shell function in `~/.zshrc` (line 313) so that when invoked with known CLI subcommands or flags (`health`, `models`, `providers`, `combo`, `combos`, `keys`, `resilience`, `doctor`, `serve`, `chat`, `repl`, `status`, `--help`, `-h`, `--version`, `-v`), it dispatches to `command omniroute "$@"`, while preserving default Claude Code launcher behavior when no subcommands are supplied.
- **Operational Guide & Documentation Update**: Update `/Users/androidteam/Developer/docs/omniroute-agent-skills.md` to remove the deferred CLI notice and document both REST and CLI syntax parity across all 45 skills.
- **Non-Goals**:
  - Modifying the running Docker container or rebuilding the Next.js standalone image.
  - Installing global npm packages in `/opt/homebrew` or host `node_modules` in `~/Omniroute`.
  - Directly accessing or binding `/app/data/storage.sqlite` from host processes (HTTP loopback only).
  - Altering upstream `bin/omniroute.mjs` git-tracked source files.

## Capabilities

### New Capabilities
<!-- No new capability paths; extending existing capability -->

### Modified Capabilities
- `omniroute-agent-skills`: Updates the capability to formally require the host CLI bridge execution contract, stdout stream cleanliness, and interactive zsh subcommand multiplexing, replacing the previous CLI deferral boundary.

## Impact

- **Affected Files**:
  - `~/.local/bin/omniroute` (New executable bridge script)
  - `~/.zshrc` (Multiplexing inside existing `omniroute()` function)
  - `/Users/androidteam/Developer/docs/omniroute-agent-skills.md` (CLI usage documentation)
- **Toolchain Governance**: Introduces no global npm packages and no Homebrew formula alterations, so it stays clear of `inventory-workstation-toolchain.py` `DENY_ROSTER` rules. It is **not** footprint-free: dependencies resolve into Bun's global cache (~1.0 GB observed, already warm), and a cold cache requires one-time registry egress.
- **Agent Ecosystem**: Activates the 21 `cli-*` skills for Claude Code, Antigravity, Codex, Cursor, and terminal agents.
- **Backwards Compatibility**: Preserved for the launcher contract. `omniroute-pm.json` continues to drive bare invocations; the new branch only intercepts recognized CLI subcommands and flags, which previously fell through to Claude Code arguments rather than executing a CLI.
- **Disclosure**: Diagnostic research advanced the mtime of the stale `~/.omniroute/storage.sqlite` orphan. It is unused by the container (which uses the `omniroute-data` named volume), but the change records the mutation rather than implying a pristine probe.
