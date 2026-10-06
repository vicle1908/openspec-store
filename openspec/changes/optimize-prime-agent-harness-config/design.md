# Design

## Context

See proposal.md - Why. The constraints that shape the approach:

**What runs.** The installed Prime Agent is the npm/TS build v0.9.8 at
`/opt/homebrew/lib/node_modules/prime-agent/dist/bundle/cli.js`, symlinked from
`/opt/homebrew/bin/prime-agent`. The Rust port at `platform/prime-agent`
(`c24ac227f`, clean, in sync with `origin/main`) is **not built** — no `cargo` on
PATH and no `target/` directory — so it cannot currently serve as a verification
instrument. It is readable as a behavioral reference only.

**How the prompt is assembled.** The Rust source documents the layered structure
(`crates/pa-core/src/prompts/system_prompt.rs`): cache-stable static layers
(`core`, `usage`, `opinionated`, `per-model`) followed by a fixed-order dynamic
tail (`packages` → `project-context` → `skills-inventory` → `mcp-servers` →
`environment` → session role → additional guidance → appended prompt). Static
layers total ~5.8k tokens. The skills inventory is rendered by
`format_skills_for_prompt` with `<available_skills>` / `<skill>` XML, and the
context section is emitted as `# Project Context` with `## <filePath>` per file.
The TS bundle contains the equivalent `formatSkillsForPrompt` and `# Project
Context` emitters, confirming the installed build behaves the same way.

**Discovery roots.** Skills load from `~/.prime/agent/skills/`,
`~/.agents/skills/`, project `.prime/agent/skills/`, and an ancestor walk of
`.agents/skills/`; context files load from the agent dir then the nearest-to-root
ancestor chain. `~/.agents/skills` is 51 symlinks into
`~/Developer/.agents/skills`, and the ancestor walk finds that same directory
independently — so one physical skill set is exposed through two roots, with ~50
colliding names deduplicated by canonical path at load time.

**Measured surface.** On the `phanmemvip/codex-x` path (which does receive the
prompt): 12,728 prompt tokens at `/tmp` and 29,476 at `~/Developer`. Ablation
attributes ~9.2k and ~18.1k tokens to the skills inventory respectively, and
~7.8k at `~/Developer` to the 505-line, 30 KB `~/Developer/AGENTS.md`.

**The delivery defect.** Two providers share `baseUrl
https://api.phanmemvip.shop/v1` but differ in credential. Probing both directly
with an identical Responses request and a value supplied only in `instructions`:
the `HERMES_CUSTOM_PHANMEMVIP_API_KEY` credential honors it (input_tokens 330,
echoes the value); the `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` credential does not
(input_tokens 14, ignores it). The same asymmetry reproduces through Prime Agent
itself (prompt tokens ~1,023 vs 12,728; `--append-system-prompt` delta 0 vs
+6,001). A 200,000-character `instructions` body still returns input_tokens 14 on
the non-delivering credential, so the system prompt is discarded rather than
truncated.

**Measurement method (and a correction that matters).** Delivery is measured by
placing a unique code in the system prompt only, then asking for it, always
paired with a control run that omits the code so guessing cannot masquerade as
delivery. An earlier extractor that read only visible message text reported false
`IGNORES` verdicts for reasoning models: those models emit the answer inside a
`function_call`'s arguments (e.g. a `memory_save` call carrying the code) or
inside a reasoning summary, not in a text block. The corrected extractor reads
visible text, `function_call` arguments, and reasoning summaries, and gives
reasoning models a generous `max_output_tokens` so reasoning cannot starve the
visible reply. Every verdict below was re-derived with the corrected method.

**Route survey.** Registrations measured through Prime Agent, at `/tmp`:

| Registration | Backing | Prompt tokens | Delta from a 24k-char appended prompt | Verdict |
|---|---|---|---|---|
| `phanmemvip/codex-x` | remote reseller | 12,728 | +6,001 | delivers |
| `cockpit/gpt-5.6-sol` | local proxy | 12,366 | +6,001 | delivers |
| `cockpit/gpt-5.6-luna` | local proxy | 12,366 | +6,001 | delivers |
| `cockpit/gpt-5.6-terra` | local proxy | 12,366 | +6,001 | delivers |
| `shopapikey/Claude-Fable` | remote reseller | 971 | 0 | discards the prompt |
| `omniroute-anthropic/pm/Claude-Fable` | local gateway | 2,946 | 0 | counts it, discards it |
| `omniroute-responses/sh/codex-x` | local gateway | 0 | — | no credentials |

`cockpit` is a **local** proxy (Cockpit Tools.app / `cockpit-cliproxy` bound to
127.0.0.1:51006) pooling 7 subscription accounts with 561% aggregate remaining
in the 5-hour window (2 accounts currently exhausted). All 9 of its text models
deliver; the image and reserve ids fail by design. Measured latency 1.7-2.7s
averaged over three runs each, `low`/`high`/`max` thinking levels accepted, and
tool calling verified end-to-end.

**OmniRoute namespace survey.** One representative per namespace, same method:

- **Delivering and reachable:** `auto/*` (45), `agy/*` (32), `claude/agy/*` (10),
  `no-think/*` (63), `ddgw/*` (6), `openrouter/*` (80), and 37 bare ids.
- **Was delivering, then went down mid-session:** the entire `cx/*` namespace
  (7 models passed every test, then began failing with
  `Encountered invalidated oauth token for user`). It did not recover over
  repeated retries. This is the single most important operational finding in the
  survey: a route that verifies clean can fail wholesale minutes later.
- **Reachable but discards the system prompt:** `pm/*` (4 ids).
- **Broken, needs external setup:** `gh/*` and `github/*` (model not supported),
  `ollama-cloud/*` (401), `jina/*` (bad key), `dva/*` (`DEVIN_AGENTIC_HOME`
  unset), `aug/*` (CLI not found), `cfp/*` (browser unavailable), `oc/*` (free
  tier), `veo*/*` (upstream error), `unc/*`, `aihorde/*` (image model),
  `cxa/*` (app-server transport).

## Goals / Non-Goals

**Goals:**
- Make the delivered-prompt property an explicit, measured precondition on the
  default model selection rather than an assumption.
- Repair the MCP credential reference so the configured server resolves.
- Reduce the always-loaded prompt surface by acting on the two dominant
  contributors, and record the cost attribution so regressions are visible.
- Complete model metadata so usage reporting and thinking-level behavior are
  truthful.
- Configure degraded-mode recovery for reseller endpoints.
- Remove configuration drift.

**Non-Goals:**
- No change to the Prime Agent runtime contract, the tool surface, the wire
  protocol, or any tracked Prime Agent source file. `AGENTS.md` for the port pins
  the surface contract; this change stays entirely in user-level configuration.
- No change to the other eight consumer CLIs' registrations beyond what the
  `coding-cli-provider-registry` delta states (i.e. none).
- No attempt to fix the reseller endpoint's behavior. The endpoint is treated as
  an external constraint; the response is to stop selecting it as the default.
- No editing of `~/Developer/AGENTS.md` content beyond relocation decisions
  required to bound the prompt; its load-bearing safety boundaries stay.
- No new dependency, no build of the Rust port, no change to `openspec-store`
  tooling.

## Decisions

**D1: Treat prompt delivery as a per-registration measured property, verified by
differential token accounting.**

Probe each candidate with a baseline request and the same request carrying a
large appended system prompt; require the prompt-token delta to track the
appended size, and confirm the model echoes a value supplied only in the system
prompt. Alternatives considered: (a) trust the provider's advertised model ID —
rejected, the ID `Claude-Fable` is served identically under both credentials and
only one delivers; (b) trust the `models.json` `api` dialect — rejected, both
registrations declare the identical `openai-responses` API value; (c) assert identity from the model's
self-report — rejected as the primary signal, though it corroborates (the
non-delivering path self-identifies as a different product, so it is recorded as
supporting evidence only). The differential count is chosen because it is
observable from the client, needs no endpoint cooperation, and directly measures
the property in question.

**D2: Default to the local `cockpit` proxy, and leave the non-delivering
registration in place but unselected.**

Of the routes measured delivering — `phanmemvip`, `cockpit`, and (until it failed
wholesale) OmniRoute's `cx/*` — the `cockpit` provider is chosen as the default
because it is the only one that is both **local** and **pooled**:
`Cockpit Tools.app` / `cockpit-cliproxy` on 127.0.0.1:51006 aggregates 7
subscription accounts (561% aggregate remaining in the 5-hour window, 2
exhausted), so a single account's quota exhaustion does not take the route down,
and no request crosses the network to a third-party reseller. `gpt-5.6-sol` is the
default model.

Alternatives considered: (a) `phanmemvip/codex-x` — also delivers and is
already the working session model, but it is a single remote reseller credential
with no pool behind it; (b) any OmniRoute `cx/*` model — rejected on measured
reliability, not on capability: the whole namespace verified clean and then began
returning `Encountered invalidated oauth token for user` within the same session,
which is exactly the failure a default model must not have; (c) delete the
non-delivering `shopapikey` provider — rejected, it is referenced by
`coding-cli-provider-registry` and by eight other consumer CLIs, and removal is
outside this change's scope; (d) repoint `shopapikey` at `pm/Claude-Fable` —
rejected, see D7.

**D3: Repair the MCP reference by exporting the variable the reference names, and
report the token divergence without printing either value.**

The reference `{"MCPR_TOKEN": {"env": "MCPR_TOKEN"}}` names a variable the login
profile does not export; the profile exports a differently-named variable, and
the router's own client config holds a third value of the same length but a
different hash. Alternatives considered: (a) repoint the reference at the
existing exported name — viable, but it couples the router to a name owned by
another tool's config; (b) export the name the reference already uses — chosen,
because the reference is the configuration under our control and the name is the
router's own convention; (c) inline the token — rejected, static secret values
are not accepted by the MCP settings surface and inlining would put a credential
in a config file. Because the kernel environment is captured at spawn, the repair
requires a daemon and kernel restart to take effect.

**D4: Bound the prompt by removing duplicated discovery at the source, and by
relocating task-specific context out of the always-loaded ancestor path.**

Alternatives considered: (a) pass `--no-skills` — rejected, it removes the
capability rather than the duplication; (b) prune `~/.agents/skills` fanout links
to only the projects in use — chosen for the duplication, and it is already the
sanctioned shape under `workspace-openspec-skill-discovery`, which requires those
entries to be links rather than copies; (c) shrink `~/Developer/AGENTS.md` — chosen
for the context cost, consistent with `agent-instruction-hygiene`'s 150-line
target, keeping load-bearing boundaries in the discovered file and moving
task-specific content to an explicitly-referenced location. Relying on the
loader's canonical-path dedup was rejected: it prevents double-listing but does
not remove the traversal, and the surviving inventory still reflects an
unintended skill set.

**D5: Add cost and thinking-level metadata rather than synthesizing it.**

Rates and level mappings are provider facts, so they are declared per model, not
defaulted. Where a rate is genuinely unknown, the model is left identifiable as
unreported rather than given a fabricated zero — a `0` rate is
indistinguishable from a real free tier in the usage report. Alternatives
considered: (a) compute cost client-side from a table — rejected, it duplicates a
surface the runtime already owns; (b) leave it — rejected, `$0.00` for every
session is an actively misleading signal.

**D6: Configure recovery explicitly instead of relying on park behavior.**

Set a backup model so an exhausted primary degrades to a working model, and
record the wait/park bounds as intended behavior. Alternatives considered:
(a) rely on the existing bounded wait and park — rejected as the unstated
default, because parking is only useful when the reset time is near; (b) disable
retries — rejected, it trades one failure mode for another. The chosen approach
preserves the primary-probe-on-next-turn behavior the runtime already documents.

**D7: Do not repoint the `shopapikey` registration, and do not adopt any
OmniRoute route as the default.**

Both were live options and both are rejected on evidence. Repointing
`shopapikey` at OmniRoute's `pm/Claude-Fable` was rejected because `pm/Claude-Fable` was measured
*counting* the system prompt without honoring it: a code supplied only in the
system prompt was never echoed (input_tokens 946 with the code, 946 without),
across all three dialects (`/v1/messages`, `/v1/responses`,
`/v1/chat/completions`). A registration that inflates the token count while
discarding the content is worse than one that visibly ignores it, because it
looks healthy in usage reporting. Repointing would also change the endpoint a
credential points at, which the eight other consumer CLIs sharing the
`shopapikey` name inherit. Adopting an OmniRoute route as the default was
rejected for the reliability failure recorded in the Context section: the
`cx/*` namespace passed every delivery, tool-calling, and latency test, then
began failing wholesale mid-session. OmniRoute remains useful as a
manually-selected route; it is not trusted as the unattended default.

**Transaction boundaries:** Each configuration file is written atomically as a
whole document — `settings.json` and `models.json` are each replaced in one
write, with the pre-change document retained as the rollback artifact until
verification passes. The MCP repair spans two boundaries: the profile export
(`~/.zshenv`) and the running daemon/kernel, which must be restarted for the
export to be observed. No step leaves a partially-written configuration.

## Risks / Trade-offs

- **The replacement default may itself stop delivering** (endpoint-side change)
  → the delivery probe is a repeatable check, recorded as a task, so the property
  is re-verified rather than assumed once.
- **Exporting the router variable into the login profile widens its exposure**
  beyond the one client that needs it → the profile already exports this class of
  token, the file is not tracked, and the change records only length and hash.
- **Restarting the daemon interrupts running sessions** → verification is
  performed after restart, and sessions that must survive are identified before
  the restart rather than after.
- **Relocating content out of `~/Developer/AGENTS.md` removes guidance from the
  always-loaded surface** for every agent in the workspace, not just Prime Agent
  → load-bearing safety boundaries stay in the discovered file; only
  task-specific material moves, and it stays reachable by explicit path. This is
  the `agent-instruction-hygiene` contract, not a new trade-off.
- **Pruning `~/.agents/skills` links may remove a skill a workflow relies on**
  → links are removed only for skills whose canonical root remains discoverable
  from the workspace, and the pre-change link set is retained for rollback.
- **Declared cost rates can drift from real provider pricing** → rates are
  treated as metadata with a recorded provenance and a re-verification task, not
  as an authoritative billing record.
- **The non-delivering registration stays reachable** and can be selected
  manually → the selection is left intact for the other eight consumer CLIs, and
  the new spec requirement constrains the default rather than removing the entry.

## Migration Plan

1. Capture the pre-change state: copy `settings.json` and `models.json`, record
   the `~/.agents/skills` link set, and record the measured prompt-token baseline
   per working directory.
2. Apply the model-metadata and drift changes first — they are inert with respect
   to selection and cannot change behavior on their own.
3. Apply the default-selection change, then re-run the delivery probe and the
   prompt-token measurement to confirm the assembled prompt is now delivered.
4. Repair the MCP reference and restart the daemon and kernel; confirm the
   previously failing stdio handshake now resolves.
5. Apply the prompt-surface reduction last, since it changes what every agent in
   the workspace loads; re-measure the inventory and re-run the skill-index
   validation the workspace already uses.
6. Verify each step against the new capability's scenarios.

**Rollback:** restore the captured `settings.json` and `models.json` wholesale,
restore the `~/.agents/skills` link set, and restart the daemon. The MCP export is
inert if the reference is restored first, so profile and configuration roll back
independently.

## Open Questions

- What are the correct per-model cost rates for the reseller and proxy
  endpoints? Neither `api.phanmemvip.shop` nor `cockpit` exposes pricing in its
  `/v1/models` response (verified: no `pricing` field), so the rates are
  provider facts that must be supplied rather than derived. The design requires
  them to be declared or explicitly marked unreported; the actual figures can be
  filled in during apply without changing the approach.
- Will the `cx/*` OAuth invalidation resolve on its own? It is a provider-side
  credential state, outside this change's control. The decision not to depend on
  `cx/*` does not require the answer; it only requires that the default not be
  one of those routes. Re-checking is a task, not a blocker.
