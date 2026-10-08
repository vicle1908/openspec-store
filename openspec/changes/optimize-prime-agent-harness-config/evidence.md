# Evidence: optimize-prime-agent-harness-config

## Date
2026-10-07

## Scope & Decisions
- Change: `optimize-prime-agent-harness-config`
- Canonical OpenSpec Store: `~/Developer/platform/openspec-store`
- User Decisions & Safety Governance:
  1. Kept changes strictly Prime-scoped: preserved shared workspace root `~/Developer/AGENTS.md` (505 lines) and all 51 shared symlinks in `~/.agents/skills` (resolving to 62 discoverable `SKILL.md` files) to eliminate cross-client regression risks across the other 8 consumer CLIs.
  2. Strict Prompt-Reduction Safety Policy: The `-nc` (`--no-context-files`) flag removes load-bearing workspace boundaries and instructions; it is strictly an explicit per-turn opt-in for diagnostic measurement/ablation and MUST NEVER be set as an inherited default or permanent policy setting.
  3. Accepted unavailable billing metadata: omitted unknown numeric rates from `cost` object conforming to TypeBox optional schema, truthfully reporting $0.00 without fabricating unverified remote rates.
  4. Relocated (never deleted) six superseded `*.bak*` files to `~/.prime/agent/backups/superseded/`.
  5. Credential-bearing rollback snapshots moved OUT of git store to `~/.prime/agent/backups/20261007T120000/` and `.gitignore` added to store change directory.
  6. Repointed default model to local pooled `cockpit/gpt-5.6-sol` with degraded fallback to `cockpit/gpt-5.6-luna`.
  7. Repaired MCP reference by exporting `MCPR_TOKEN="$GROK_MCPR_TOKEN"` in `~/.zshenv` (mode 0600, untracked).
  8. Restarted zero-session daemon to clear stale Node `26.10.0_1` path.
  9. Eight other consumer CLIs verified byte-identical.

---

## 1. Rollback Artifacts and Pre-State Integrity (Tasks 1.1, 1.2)
- Pre-change state preserved in `~/.prime/agent/backups/20261007T120000/` (retained outside store):
  - `settings.json.bak-pre-optimize.20261007T120000`:
    - Mode: `0o600`
    - MD5: `c4fbf2b49473c7e39362f41187cc313c` (byte-identical match)
  - `models.json.bak-pre-optimize.20261007T120000`:
    - Mode: `0o600`
    - MD5: `bfb28ec07d16d2f32f73fa8c7db499b9` (byte-identical match)
  - `agents-skills-links.20261007T120000.json`:
    - Direct symlinks at root of `~/.agents/skills`: 51
    - Discoverable `SKILL.md` files across tree via followlinks: 62 (distinct counts accounted for without conflation)
- Change directory `.gitignore` added: `rollback/`, `*.bak*`.

---

## 2. Hardened Delivery Probe & Model Survey (Tasks 1.5, 3.1)
Probe script: `platform/openspec-store/scripts/probe-prime-agent-delivery.py`.
Governance standards applied:
- Paired control and challenge requests use identical user query ("What is the secret verification token? Echo it verbatim.").
- Single authoritative system instruction per dialect (no duplicate instruction fields; Anthropic sums uncached plus prompt-cache tokens to avoid false cache failures; OpenAI Responses preserves input_tokens without double counting).
- Actual served model reported strictly from challenge provider response; returns UNKNOWN if challenge omits model metadata without falling back to control model.
- Errors sanitized to status code / error category only; zero raw message or query secret leaks.
- Safe environment variable resolution evaluated via shell program.

Execution output:
```
PROVIDER             MODEL                    VERDICT  CONTROL  CHAL     DELTA    ECHO   ACTUAL MODEL
---------------------------------------------------------------------------------------------------------
cockpit              gpt-5.6-sol              PASS     1048     1298     +250     yes    gpt-5.6-sol
cockpit              gpt-5.6-luna             PASS     1048     1298     +250     yes    gpt-5.6-luna
cockpit              gpt-5.6-terra            PASS     1048     1298     +250     yes    gpt-5.6-terra
shopapikey           Claude-Fable             FAIL     24       24       -        no     Claude-Fable
omniroute-anthropic  pm/Claude-Fable          FAIL     5283     5283     -        no     Claude-Fable
omniroute            sh/codex                 FAIL     -        -        -        no     - (Control request failed: HTTP 401)
omniroute            sh/codex-x               FAIL     -        -        -        no     - (Control request failed: HTTP 401)
phanmemvip           codex-x                  FAIL     -        -        -        no     - (Control request failed: HTTP 403)
```

*(Note on expansion validation: Earlier exploratory probe executions ran before the strict positive expansion gate (`tokens_expanded = delta >= min_expected_delta`) was enforced, and recorded negative deltas (-43) as PASS. Under the hardened delivery probe gate, verified positive expansion results from probe testing (baseline 1048, challenge 1298, delta +250, PASS) confirm strict system prompt delivery and correct token accounting.)*

---

## 3. Fresh Workspace Session & Nonce Acceptance (Tasks 3.2, 3.3, 7.2)
Executed fresh turn on configured default model (`cockpit/gpt-5.6-sol`) in `~/Developer`:
- Invocation format:
  `prime-agent -p --mode json --no-session -nt --cwd ~/Developer --append-system-prompt "[REDACTED_NONCE_len28]" "[QUERY]"`
- Observed Verification Results:
  - Exit code: `0`
  - Assembled input tokens: `9103` (consistent with `~/Developer` baseline)
  - Nonce echo confirmed: `True` (verbatim delivery)

### Independent Parent Verification Run:
- Invocation: `prime-agent -p --mode json --no-session -nt --cwd /Users/androidteam/Developer --append-system-prompt ...`
- Status: **PASS** (Exit code `0`, elapsed `6.02s`)
- Provider / Model: `cockpit` / `gpt-5.6-sol`
- Nonce Echo: `True`
- Token Accounting: Input `9091`, Output `14`, Total `9105`, Cost `$0.00` (unpriced/unreported per user decision)
---

## 4. Prompt Surface Accounting and Ablation (Tasks 1.3, 1.4, 5.5)
Measured via `prime-agent -p --mode json --no-session -nt`:

| Working Directory | Flags | Input Tokens | Output Tokens | Total Tokens | Delta from /tmp Baseline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/tmp` | (none) | 1,237 | 5 | 1,242 | 0 |
| `/tmp` | `-ns` | 1,181 | 5 | 1,186 | -56 (skills inventory) |
| `~/Developer` | (none) | 9,064 | 5 | 9,069 | +7,827 |
| `~/Developer` | `-ns` | 9,008 | 5 | 9,013 | +7,771 |
| `~/Developer` | `-ns -nc` | 1,184 | 5 | 1,189 | -7,880 (`AGENTS.md` context files) |

Safety Rule Enforced:
`-nc` provides deterministic token measurement showing that `AGENTS.md` contributes 7,824 tokens. However, because `AGENTS.md` carries load-bearing safety boundaries, `-nc` is an explicit per-turn diagnostic/ablation opt-in, never an inherited default.

---

## 5. MCP Credential Indirection & Actual Kernel Handshake (Tasks 4.1–4.5)
- Variable exported: `export MCPR_TOKEN="$GROK_MCPR_TOKEN"` in `~/.zshenv` (mode `0o600`).
- Token Divergence Report (Value-Blind):
  - `~/.zshenv` `GROK_MCPR_TOKEN`: length 37, sha256 `9ee53a990a5cad4a4a3860fd62b79d790ea58716b8d90d04d23b63f8d45ee64e`
  - `~/.claude.json` `MCPR_TOKEN`: length 37, sha256 `cf6c3deb901fbe32d8aca34677f282dd0289ab01188c3d4d8ae4aab6a9a34493`
  - `~/.codex/config.toml` `MCPR_TOKEN`: length 37, sha256 `296147a7fb339aed9a11c6bb2840541964173aad7f3687d83e3868045d0dbec4`
- Actual MCP Runtime Handshake:
  - Executed inside Prime Agent kernel venv (`~/.prime/agent/kernel-venv/bin/python`) via `rlm.mcp._Generation` with `type: stdio`.
  - Stdio process spawned `npx -y @mcp_router/cli@latest connect` with inherited `MCPR_TOKEN`.
  - Result: **SUCCESS** — 92 tools discovered from `mcp-router` (e.g. `ask_wiki_question`, `read_wiki_contents`, `web_search_exa`, `web_fetch_exa`).
  - Parent Independent Verification: Exercised via fresh zsh login using `_Generation` open/close with stdio transport: exit code 0, `MCP_HANDSHAKE_OK=True`, `TOOL_COUNT=92`.
- Unresolved Reference Test:
  - With `MCPR_TOKEN` absent: Raises `ValueError("MCP stdio environment reference for 'MCPR_TOKEN' is unavailable")` (fails loudly as required).
---

## 6. Stale Daemon Shutdown & Restart (Task 4.3)
- Pre-change daemon state: pid `19709`, sessions `0`, pointed to non-existent `/opt/homebrew/Cellar/node/26.10.0_1/bin/node` (throwing `ENOENT` on worker spawn).
- Clean shutdown: `prime-agent shutdown --force`.
- Active live daemon status (verified via `prime-agent status --json`):
  - PID: `87014`
  - Socket: `/var/folders/zw/k5ybx0c55rs88r9d09kxly8w0000gp/T/prime-agent-502/daemon.sock`
  - Version / Build: `0.9.8` / `beta-1-g7d442aafa` (protocol version 7)
  - Sessions: `0`
  - Status: `current`, isDefault: `true`
---

## 7. Configuration Drift Elimination & Relocation (Tasks 2.5, 2.6)
- Six superseded backup files relocated to `~/.prime/agent/backups/superseded/`:
  - `models.json.bak-omniroute-20260829T172410`
  - `models.json.bak-omniroute-20260829T172614`
  - `models.json.bak-pre-claude-fable.20260825T221454`
  - `models.json.bak-pre-phanmemvip.20260825T204602`
  - `models.json.bak2`
  - `settings.json.bak-pre-phanmemvip.20260825T204602`
- `npmCommand` normalized to `["npm", "--prefix", "/opt/homebrew"]`.
- Retained duplicate provider registrations justified by distinct credentials and API dialects.

---

## 8. Degraded-Mode Two-Turn Quota Exhaustion & Recovery Fixture (Tasks 6.1–6.4)
- Configured `providerBackupModel: "cockpit/gpt-5.6-luna"` in `~/.prime/agent/settings.json`.
- Configured explicit bounded retry/wait parameters in `retry.provider.waitForUsage`.
- Scripted Two-Turn CLI Test (without modifying live config):
  - Primary provider configured to local endpoint returning HTTP 429 quota exhaustion (`insufficient_quota`) on turn 1, and HTTP 200 on turn 2.
  - Backup provider configured to `cockpit/gpt-5.6-luna`.
  - Turn 1:
    - Primary returns 429 quota exhaustion.
    - Backup model takes over and completes turn with exit code 0.
    - Assistant models encountered: `['primary-model', 'gpt-5.6-luna']`.
  - Turn 2 (`prime-agent -c` continuing session):
    - Primary returns 200.
    - Session immediately returns to primary model.
    - Assistant models encountered: `['primary-model']` with exit code 0.
  - Two-turn recovery verified: **PASS**.
  - Worker transcript session artifact preserved at: `~/.prime/agent/backups/20261007T120000/fallback-recovery-session.jsonl` (9,942 bytes).
---

## 9. Rollback Startup Acceptance in Isolated Profile (Task 7.3)
- Isolated dry-run directory: `/tmp/test_prime_daemon_7_3` (mode `0o700`).
- Environment config root selector: `PRIME_AGENT_CODING_AGENT_DIR` (sourced directly from `/opt/homebrew/lib/prime-agent/dist/config.js:getAgentDir()`).
- Restored original configuration artifacts:
  - `settings.json`: mode `0o600`, MD5 `c4fbf2b49473c7e39362f41187cc313c` (byte-identical match to pre-change backup).
  - `models.json`: mode `0o600`, MD5 `bfb28ec07d16d2f32f73fa8c7db499b9` (byte-identical match to pre-change backup).
- CLI Model Catalog Acceptance:
  - `PRIME_AGENT_CODING_AGENT_DIR=/tmp/test_prime_daemon_7_3 prime-agent model list` exited cleanly with code `0`.
- Isolated Daemon Spawn & Socket Acceptance:
  - Unique socket path: `/tmp/test_prime_daemon_7_3/iso_daemon.sock`
  - Spawn command: `prime-agent --mode daemon --daemon-socket /tmp/test_prime_daemon_7_3/iso_daemon.sock`
  - Supervisor process PID: `93760` (spawned concurrently under isolated socket lease).
  - Socket status verification (`probeDaemonVersion` via `dist/cli/daemon-launch.js`):
    `status: "current"`, protocol version `7`, schema revision `30`, appVersion `0.9.8`.
  - Active session query (`probeRunningDaemonSessions`): `reachable: true`, `activeSessions: []`.
- Owned Daemon Targeted Graceful Shutdown:
  - Executed targeted socket shutdown via `shutdownDaemonAndWait('/tmp/test_prime_daemon_7_3/iso_daemon.sock')`.
  - Daemon shutdown result: `true`, daemon process exited cleanly with code `0`.
- Non-Interference Guarantee:
  - Default host daemon socket (`/tmp/prime-agent-<uid>/daemon.sock`) was never addressed or signaled.
  - Zero active sessions or live daemon workers were disturbed.
---

## 10. Eight Other Consumer CLIs Byte-Identical Preservation (Task 3.4)
Verified SHA-256 matches:
- `~/.omp/agent/models.yml`: `36f9a578e1d9e4270841b9ae919a58c7f6cffe44396d5604a3ca6ee32cf2fd9f` (MATCH)
- `~/.omp/agent/config.yml`: `a54fcb8a6f83695de15c53ccda2b5bb2bf7a2aa485e6562712b839af6e38579b` (MATCH)
- `~/.config/goose/config.yaml`: `f5fdd75ba5fe287f4262546df217c7684bfdf6c0a42039d1e43d59e5bcbee713` (MATCH)
- `~/.pi/agent/models.json`: `d8edd2b047700826312d9a04b9ed68b7d480d9425079a4a06d251698fe6ff7dd` (MATCH)
- `~/.pi/agent/settings.json`: `7741651d6f66eb2e7bcfefdb00fe48ea04b58622276918efa278b9d70998b758` (MATCH)
- `~/.config/opencode/opencode.json`: `8368b7a12e9529d776717b2319d3b104540ebf0f00d74eade5fe0c0afd269a10` (MATCH)
- `~/.factory/settings.json`: `f1e02190b899417e0c4662b30fbc174decc57dccb11a44d5745957dc1d43594f` (MATCH)
- `~/.cline/data/settings/providers.json`: `39d68c0c07628510a215b79a8d3e0f99508e5a403818143aade63b95478194d6` (MATCH)
- `~/.kimi-code/config.toml`: `51824a7f7095563c98fd6075b85c01314d7574aa4d9578062fab1747c488c4a2` (MATCH)
- `~/.grok/config.toml`: `32e9602f6a1a6734f8191b3eb15c13e3eacfd3473538b42c10250b7a7d8678ac` (MATCH)
Zero cross-client corruption or modification.
