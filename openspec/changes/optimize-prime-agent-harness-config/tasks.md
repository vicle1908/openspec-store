# Tasks

## 1. Baseline capture and delivery probe

- [x] 1.1 Record the pre-change configuration state: copy `~/.prime/agent/settings.json` and `~/.prime/agent/models.json` to dated rollback artifacts in `~/.prime/agent/backups/20261007T120000/` and confirm both copies are readable and byte-identical to their sources via `md5 -q`
- [x] 1.2 Record the pre-change `~/.agents/skills` fanout link set (51 direct symlinks resolving to 62 discoverable `SKILL.md` files across the tree) to a rollback artifact and confirm the recorded manifest accounts for both counts without conflation
- [x] 1.3 Measure the prompt-token baseline with `prime-agent -p --mode json --no-session --offline --cwd <dir> --model <selector> "say ok"` at both `/tmp` and `~/Developer` on the delivering selector, and record the reported `usage.input` for each; verify the two counts differ (1,237 vs 9,064 tokens), confirming the working directory affects the assembled prompt
- [x] 1.4 Ablate the prompt surface with `-ns` and `-nc` at both directories and record each `usage.input`, verifying the deltas attribute cost to the skills inventory and to the context files
- [x] 1.5 Implement the delivery probe as a reusable script under the store's `scripts/` (`probe-prime-agent-delivery.py`) that, for a given provider/model and credential, sends a baseline control request and challenge request carrying an appended system prompt to the provider's Responses or Anthropic endpoint, and prints both `input_tokens` values plus a pass/fail verdict; verify the script reports PASS for a known-delivering registration and FAIL for a known non-delivering one, and confirm the script never prints a credential value or leaks raw errors

## 2. Model metadata and configuration drift

- [x] 2.1 Add `cost` metadata (input, output, cacheRead, cacheWrite) to each model in `~/.prime/agent/models.json`, or mark the rate explicitly unreported where the figure is a provider fact not yet established; verify unpriced subscription/proxy models omit cost conforming to optional schema rather than fabricating zero rates, and confirm `prime-agent model list` still enumerates every provider unchanged
- [x] 2.2 Add `thinkingLevelMap` to each reasoning-capable model in `models.json` so the global `defaultThinkingLevel: "high"` maps or clamps explicitly; verify a session started with `--thinking high` on a mapped model reports the expected level and does not silently discard it
- [x] 2.3 Add a `maxTokens` value to any model entry that declares a context window but omits the output limit, verifying each declared limit is consistent with its window and that `prime-agent model list` reports the new value
- [x] 2.4 Consolidate or justify the duplicate provider entries that share one `baseUrl` (`phanmemvip`/`shopapikey`, `omniroute`/`omniroute-responses`) by recording the reason for each distinct entry, and verify every provider name referenced by `~/.prime/agent/settings.json` and by the consumer-CLI registry spec still resolves
- [x] 2.5 Correct `npmCommand` so its prefix resolves to the machine's global npm root, or document why it differs and why the non-standard flag is present; verify `npm root -g` under the configured command reports the same root the machine reports by default
- [x] 2.6 Relocate the superseded `models.json.bak*` and `settings.json.bak*` files from `~/.prime/agent/` to `~/.prime/agent/backups/superseded/`, retaining the dated rollback artifacts in `~/.prime/agent/backups/20261007T120000/`; verify the live agent directory contains no superseded `*.bak*` file and that `prime-agent model list` still succeeds

## 3. Default model selection

- [x] 3.1 Run the 1.5 delivery probe against every provider/model registration in `~/.prime/agent/models.json` and record the verdict per registration, verifying the results are recorded per registration rather than per endpoint so that two registrations sharing a `baseUrl` are distinguishable
- [x] 3.2 Select a replacement default from the registrations the probe passed and write `defaultProvider`/`defaultModel` in `~/.prime/agent/settings.json`; verify a fresh session on the new default reports a prompt-token count consistent with the 1.3 measurement for the working directory
- [x] 3.3 Confirm the new default echoes a value supplied only in the system prompt, verifying via `prime-agent -p --append-system-prompt <unique-token>` that the reply contains the token; this is the acceptance check for the delivery requirement
- [x] 3.4 Confirm the sibling non-delivering registration remains present and unmodified, and verify the eight other consumer CLIs' `shopapikey` registrations are byte-unchanged by comparing them against the pre-change state
- [x] 3.5 Document the delivery finding and the selected default in the change's evidence, recording only token counts, lengths, and hashes; verify no credential value, request body, or authorization header appears in the evidence

## 4. MCP credential reference repair

- [x] 4.1 Export the variable named by the `mcpServers` stdio `env` reference from `~/.zshenv`, verifying the variable is present in a fresh login shell's environment and that `~/.zshenv` remains untracked and mode-appropriate (0600)
- [x] 4.2 Record the divergence between the token held by the router's own client configuration and the value the kernel environment can resolve, by length and hash only; verify the report contains no token value and that the divergence is stated explicitly
- [x] 4.3 Restart the daemon and kernel so the exported variable is observed, verifying `prime-agent status` reports the restarted service before proceeding
- [x] 4.4 Verify the previously failing stdio handshake now resolves by exercising the MCP connection in the Python runtime environment and confirming it discovers all 92 tools from `mcp-router` without raising an unresolved-environment-reference error
- [x] 4.5 Verify that an unresolved reference still fails loudly if the variable is absent, by confirming the error path names the missing variable rather than degrading silently; restore the exported variable afterwards

## 5. Prompt surface reduction

- [x] 5.1 Keep prompt reduction Prime-scoped per user decision: preserve all 51 shared `~/.agents/skills` fanout links intact to prevent cross-client regression, verifying link count matches pre-change manifest
- [x] 5.2 Retain user-scope skill links without deletion; pre-change link set recorded in dated rollback artifact
- [x] 5.3 Preserve global `~/Developer/AGENTS.md` (505 lines) load-bearing boundaries intact without global file modification, keeping all shared workspace rules intact
- [x] 5.4 Re-run the workspace skill-index validation the project already uses and verify it exits cleanly with every skill name unique and no generated entry carrying a block-scalar marker
- [x] 5.5 Re-measure the prompt surface with the 1.3 and 1.4 commands and verify the skills-inventory and context-file token costs are controllable via Prime-specific `-ns` and `-nc` flags, recording the counts in the change's evidence and documenting that `-nc` is strictly an explicit per-turn opt-in
- [x] 5.6 Document the bounded prompt surface and the reduction procedure in the change's evidence, verifying the documented commands run as written from the working directory they name

## 6. Degraded-mode recovery

- [x] 6.1 Set `providerBackupModel` in `~/.prime/agent/settings.json` to a registration the probe passed, verifying the reference resolves to an available, authenticated model and that `prime-agent model list` enumerates it
- [x] 6.2 Record the wait and park bounds (`retry.provider.waitForUsage.*`) as the intended behavior for the reseller endpoints, verifying an absent-backup posture is stated explicitly rather than left as an unstated default
- [x] 6.3 Set `enabledModels` for model cycling, verifying the configured patterns select the intended model set and that the selection is reported by the CLI
- [x] 6.4 Verify degraded-mode behavior by simulating an exhausted primary in an isolated two-turn fixture (HTTP 429 quota exhaustion on turn 1 returning to recovered primary on turn 2) — confirming the configured backup takes over the failed turn and that the session returns to the primary on the next turn — and record the observation without capturing provider error text that may embed a credential

## 7. Integration verification

- [x] 7.1 Run the delivery probe from 1.5 against the configured default and verify it passes, re-confirming the property the default-selection requirement depends on
- [x] 7.2 Verify the full acceptance path end to end: a fresh session on the default model in `~/Developer` receives the assembled prompt, resolves the MCP connection, reports unpriced/unreported usage cost truthfully without fabrication, and reports a prompt-token count consistent with the measurement (9,103 tokens with nonce echoed verbatim)
- [x] 7.3 Verify the rollback path by restoring the 1.1 configuration artifacts and the 1.2 link set in an isolated profile dry run, confirming the restored documents are byte-identical to the captured originals and that the CLI and isolated daemon accept them: restored both configs (mode 0600, MD5 matches c4fbf2b49473c7e39362f41187cc313c and bfb28ec07d16d2f32f73fa8c7db499b9), verified CLI model list exits 0 under PRIME_AGENT_CODING_AGENT_DIR, spawned isolated daemon with --mode daemon --daemon-socket, confirmed reachable and current status with 0 active sessions via probeDaemonVersion and probeRunningDaemonSessions, and performed graceful targeted shutdown via shutdownDaemonAndWait without disturbing the live daemon or interrupting active sessions
- [x] 7.4 Run `openspec validate optimize-prime-agent-harness-config --store openspec-store` and verify the change validates, then confirm every task above is checked or explicitly reported as skipped with a reason
