# Tasks

## 1. Baseline capture and delivery probe

- [ ] 1.1 Record the pre-change configuration state: copy `~/.prime/agent/settings.json` and `~/.prime/agent/models.json` to dated rollback artifacts and confirm both copies are readable and byte-identical to their sources via `md5 -q`
- [ ] 1.2 Record the pre-change `~/.agents/skills` fanout link set (name plus resolved target for every symlink) to a rollback artifact and confirm the recorded link count matches `find -L ~/.agents/skills -name SKILL.md | wc -l`
- [ ] 1.3 Measure the prompt-token baseline with `prime-agent -p --mode json --no-session --offline --cwd <dir> --model <selector> "say ok"` at both `/tmp` and `~/Developer` on the delivering selector, and record the reported `usage.input` for each; verify the two counts differ, confirming the working directory affects the assembled prompt
- [ ] 1.4 Ablate the prompt surface with `-ns` and `-nc` at both directories and record each `usage.input`, verifying the deltas attribute cost to the skills inventory and to the context files
- [ ] 1.5 Implement the delivery probe as a reusable script under the store's `scripts/` that, for a given provider/model and credential, sends a baseline request and the same request carrying a large appended system prompt to the provider's Responses endpoint, and prints both `input_tokens` values plus a pass/fail verdict; verify the script reports PASS for a known-delivering registration and FAIL for a known non-delivering one, and confirm the script never prints a credential value

## 2. Model metadata and configuration drift

- [ ] 2.1 Add `cost` metadata (input, output, cacheRead, cacheWrite) to each model in `~/.prime/agent/models.json`, or mark the rate explicitly unreported where the figure is a provider fact not yet established; verify every model entry either declares all four rates or is identifiable as unreported, and confirm `prime-agent model list` still enumerates every provider unchanged
- [ ] 2.2 Add `thinkingLevelMap` to each reasoning-capable model in `models.json` so the global `defaultThinkingLevel: "high"` maps or clamps explicitly; verify a session started with `--thinking high` on a mapped model reports the expected level and does not silently discard it
- [ ] 2.3 Add a `maxTokens` value to any model entry that declares a context window but omits the output limit, verifying each declared limit is consistent with its window and that `prime-agent model list` reports the new value
- [ ] 2.4 Consolidate or justify the duplicate provider entries that share one `baseUrl` (`phanmemvip`/`shopapikey`, `omniroute`/`omniroute-responses`) by recording the reason for each distinct entry, and verify every provider name referenced by `~/.prime/agent/settings.json` and by the consumer-CLI registry spec still resolves
- [ ] 2.5 Correct `npmCommand` so its prefix resolves to the machine's global npm root, or document why it differs and why the non-standard flag is present; verify `npm root -g` under the configured command reports the same root the machine reports by default
- [ ] 2.6 Remove the superseded `models.json.bak*` and `settings.json.bak*` files from `~/.prime/agent/`, retaining the dated rollback artifacts from 1.1; verify the agent directory contains no `*.bak*` file other than the rollback artifacts and that `prime-agent model list` still succeeds

## 3. Default model selection

- [ ] 3.1 Run the 1.5 delivery probe against every provider/model registration in `~/.prime/agent/models.json` and record the verdict per registration, verifying the results are recorded per registration rather than per endpoint so that two registrations sharing a `baseUrl` are distinguishable
- [ ] 3.2 Select a replacement default from the registrations the probe passed and write `defaultProvider`/`defaultModel` in `~/.prime/agent/settings.json`; verify a fresh session on the new default reports a prompt-token count consistent with the 1.3 measurement for the working directory
- [ ] 3.3 Confirm the new default echoes a value supplied only in the system prompt, verifying via `prime-agent -p --append-system-prompt <unique-token>` that the reply contains the token; this is the acceptance check for the delivery requirement
- [ ] 3.4 Confirm the sibling non-delivering registration remains present and unmodified, and verify the eight other consumer CLIs' `shopapikey` registrations are byte-unchanged by comparing them against the pre-change state
- [ ] 3.5 Document the delivery finding and the selected default in the change's evidence, recording only token counts, lengths, and hashes; verify no credential value, request body, or authorization header appears in the evidence

## 4. MCP credential reference repair

- [ ] 4.1 Export the variable named by the `mcpServers` stdio `env` reference from `~/.zshenv`, verifying the variable is present in a fresh login shell's environment and that `~/.zshenv` remains untracked and mode-appropriate
- [ ] 4.2 Record the divergence between the token held by the router's own client configuration and the value the kernel environment can resolve, by length and hash only; verify the report contains no token value and that the divergence is stated explicitly
- [ ] 4.3 Restart the daemon and kernel so the exported variable is observed, verifying `prime-agent status` reports the restarted service before proceeding
- [ ] 4.4 Verify the previously failing stdio handshake now resolves by exercising the MCP connection in the Python REPL and confirming it no longer raises an unresolved-environment-reference error
- [ ] 4.5 Verify that an unresolved reference still fails loudly if the variable is absent, by confirming the error path names the missing variable rather than degrading silently; restore the exported variable afterwards

## 5. Prompt surface reduction

- [ ] 5.1 Prune the `~/.agents/skills` fanout links to the set of skills the workspace actually uses, keeping each remaining entry a link rather than a copy as the workspace skill-discovery spec requires; verify `find -L ~/.agents/skills -name SKILL.md | wc -l` reports the intended count and that no entry holds duplicated content
- [ ] 5.2 Verify no skill lost from the user-scope surface has lost its canonical root, confirming each removed skill remains discoverable from `~/Developer/.agents/skills` and that the pre-change link set from 1.2 is retained for rollback
- [ ] 5.3 Relocate the task-specific content of `~/Developer/AGENTS.md` to an explicitly-referenced location while keeping the load-bearing boundaries (secrets, factory-only clients, local scope, destructive and outward actions, blocked work, instruction provenance, pre-edit gates) in the discovered file; verify the discovered file's line count moves toward the 150-line target in `agent-instruction-hygiene` and that every relocated section is reachable by its stated path
- [ ] 5.4 Re-run the workspace skill-index validation the project already uses and verify it exits cleanly with every skill name unique and no generated entry carrying a block-scalar marker
- [ ] 5.5 Re-measure the prompt surface with the 1.3 and 1.4 commands and verify the skills-inventory and context-file token costs both decreased against the recorded baseline, recording the new counts in the change's evidence
- [ ] 5.6 Document the bounded prompt surface and the reduction procedure in the change's evidence, verifying the documented commands run as written from the working directory they name

## 6. Degraded-mode recovery

- [ ] 6.1 Set `providerBackupModel` in `~/.prime/agent/settings.json` to a registration the probe passed, verifying the reference resolves to an available, authenticated model and that `prime-agent model list` enumerates it
- [ ] 6.2 Record the wait and park bounds (`retry.provider.waitForUsage.*`) as the intended behavior for the reseller endpoints, verifying an absent-backup posture is stated explicitly rather than left as an unstated default
- [ ] 6.3 Set `enabledModels` for model cycling, verifying the configured patterns select the intended model set and that the selection is reported by the CLI
- [ ] 6.4 Verify degraded-mode behavior by simulating an exhausted primary — confirming the configured backup takes over the failed turn and that the session returns to the primary on the next turn — and record the observation without capturing provider error text that may embed a credential

## 7. Integration verification

- [ ] 7.1 Run the delivery probe from 1.5 against the configured default and verify it passes, re-confirming the property the default-selection requirement depends on
- [ ] 7.2 Verify the full acceptance path end to end: a fresh session on the default model in `~/Developer` receives the assembled prompt, resolves the MCP connection, reports non-zero usage cost, and reports a prompt-token count consistent with the post-reduction measurement
- [ ] 7.3 Verify the rollback path by restoring the 1.1 configuration artifacts and the 1.2 link set in a dry run, confirming the restored documents are byte-identical to the captured originals and that the daemon starts on them
- [ ] 7.4 Run `openspec validate optimize-prime-agent-harness-config --store openspec-store` and verify the change validates, then confirm every task above is checked or explicitly reported as skipped with a reason
