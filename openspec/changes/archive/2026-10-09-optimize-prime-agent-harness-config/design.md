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

**Measured surface (Historical baseline vs active runtime).** Earlier historical surveys under unpruned exploratory harnesses recorded 12,728 prompt tokens at `/tmp` and 29,476 at `~/Developer`, attributing ~9.2k and ~18.1k tokens to the skills inventory and ~7.8k to `~/Developer/AGENTS.md`. In the active, installed TypeScript runtime v0.9.8, however, live measurement under standard session configuration demonstrates that the skills inventory contributes only minimal tokens (~56 tokens) when `~/.prime/agent/skills/` is unpopulated, while `~/Developer/AGENTS.md` accounts for the predominant delta (1,237 tokens at `/tmp` vs 9,064 tokens at `~/Developer`). The earlier ~18k survey figures are preserved as historical exploration context rather than active runtime fact.

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

**D4: Keep changes Prime-scoped: preserve shared workspace files and skills links, leveraging Prime-specific CLI controls for prompt budgeting.**

Prompt surface ablation demonstrates that workspace context files contribute significantly to the assembled prompt. However, `~/Developer/AGENTS.md` (505 lines) and all 51 symlinks in `~/.agents/skills` (resolving to 62 `SKILL.md` files) are shared across eight other client environments in the workspace (including Hermes, Codex, OpenCode, Goose, Pi). Per explicit user decision, these shared workspace roots remain completely intact to eliminate cross-client regression risks. Prompt budgeting is achieved exclusively via Prime Agent's native `-ns` (`--no-skills`) and `-nc` (`--no-context-files`) runtime flags when lightweight turns are required.

**Safety Policy:** The `-nc` (`--no-context-files`) flag strips `AGENTS.md` load-bearing safety boundaries and MUST strictly be an explicit per-turn opt-in used for diagnostic measurement or scoped ablation. It SHALL NEVER be made an inherited default or permanent policy setting.

**D5: Declare known rates or omit unpriced models conforming to optional schema; map thinking levels explicitly.**

Rates and level mappings are provider facts, so they are declared per model, not defaulted. Where a rate is genuinely unknown, the model is left un-priced by omitting the `cost` object (conforming to TypeBox's `Type.Optional(Type.Object({ input: Type.Number(), ... }))` schema) rather than given a fabricated zero — a `0` rate is indistinguishable from a real free tier in the usage report. While the client runtime defaults usage cost display to $0.00 when rates are omitted, audit evidence and probe reporting explicitly record unpriced endpoints as unknown/unreported rather than free. Alternatives considered: (a) compute cost client-side from an external catalog — rejected, introduces out-of-band pricing drift; (b) fabricate placeholder rates — rejected, misrepresents financial reporting. Thinking levels are explicitly mapped via `thinkingLevelMap` to prevent silent clamping or discards.

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
- **Preserving shared workspace roots and skills links** means Prime Agent continues loading workspace context by default → per user decision, all 51 shared skill symlinks and `~/Developer/AGENTS.md` (505 lines) remain untouched to prevent cross-client regression across all other 8 consumer CLIs. Prompt budgeting is controlled via Prime-specific per-turn execution flags (`-ns`, `-nc`).
- **The `-nc` flag strips workspace safety context** → strictly restricted to explicit per-turn diagnostic opt-in; never inherited or configured as a default.
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
5. Verify prompt-surface budgeting using Prime-specific runtime controls (`-ns`, `-nc`) without modifying any shared workspace files or skills links; re-run the workspace skill-index validation to confirm all shared links remain intact.
6. Verify each step against the new capability's scenarios.

**Rollback:** restore the captured `settings.json` and `models.json` wholesale, leaving all shared workspace files and skills links undisturbed. Restart the daemon if needed. The MCP export is inert if the reference is restored first, so profile and configuration roll back independently.

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
