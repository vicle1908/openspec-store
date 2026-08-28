# Evidence Manifest: extend-omniroute-sh-models-to-remaining-agent-clis

Captured 2026-08-28 (Asia/Ho_Chi_Minh, +07:00). Evidence is value-blind: no credential values are recorded.

## 1. Live registry baseline

- Source: `GET http://localhost:20128/v1/models` using the existing environment-backed OmniRoute credential.
- Live registry count at apply time: **968 models**.
- Approved model IDs present:
  - `sh/gpt-5.6-sol`
  - `sh/Claude-Fable`
- The endpoint used here is the working local OmniRoute model endpoint (`localhost:20128/v1`). A historical manifest referenced `127.0.0.1:20129`, which is a separate API port; it was not used for this change.

## 2. Planning and approval evidence

- OpenSpec change: `extend-omniroute-sh-models-to-remaining-agent-clis`.
- Strict target validation passed before apply: `Change 'extend-omniroute-sh-models-to-remaining-agent-clis' is valid`, exit 0.
- User instruction authorized configuration of OmniRoute `sh/*` models for other CLIs; scope was registration-only with no default-model changes.
- Five existing registrations were treated as verify-only baselines: Kilo, Pi, OMP, Goose, and Kimi.
- Excluded from mutation: Prime Agent (separate change), Cline, Copilot, Cursor Agent, Auggie, AGY, Qoder, and Claude Code.

## 3. Backup evidence

Initial target backup directory:

```text
~/.config/agent-llm/backups/20260828T170907-extend-omniroute-sh/
```

The directory was created mode 700 and target backup files mode 600. Value-blind SHA-256 prefixes captured before mutation:

| Target | Backup | SHA-256 prefix | Size |
|---|---|---:|---:|
| OpenCode | `opencode.json` | `40861390dcdb9a10` | 5206 |
| Droid | `droid.json` | `d20b32af6c697dd3` | 6147 |
| Grok | `grok.toml` | `26bea01c97dfca8a` | 1897 |
| Codex | `codex.toml` | `9b0136d0f46c05e1` | 9557 |

Grok's file changed externally after the initial capture (defaults changed to `cockpit-sol`, web search to `grok-4.6`, and fork model to `cockpit-sol`). The change was preserved and rebased before mutation:

```text
~/.config/agent-llm/backups/20260828T181541-extend-omniroute-sh-rebase-grok/grok.toml
mode=600
sha256_prefix=c902f9e5a055fa48
```

## 4. Mutations applied

### OpenCode

File: `~/.config/opencode/opencode.json`

- Added provider `omniroute` using the existing `@ai-sdk/openai` provider shape.
- Endpoint: `http://localhost:20128/v1`.
- Credential: `{env:OMNIROUTE_API_KEY}`.
- Models: `sh/gpt-5.6-sol`, `sh/Claude-Fable`.
- Existing providers retained: `cockpit`, `phanmemvip`, `shopapikey`, `zai`.
- `model` and `small_model` remained `phanmemvip/gpt-5.6-sol`.
- Active file mode remains 644; its backup is mode 600. Permission hardening is a separate follow-up.
- Post-apply SHA-256 prefix: `864e90297bd1f21a`.

### Droid

File: `~/.factory/settings.json`

- Added two official BYOK `customModels` entries:
  - `sh/gpt-5.6-sol`
  - `sh/Claude-Fable`
- Endpoint: `http://localhost:20128/v1`.
- Credential form: `${OMNIROUTE_API_KEY}`.
- Provider type: `openai`.
- All three pre-existing custom-model IDs retained.
- Session and mission defaults unchanged.
- Active file mode: 600.
- Post-apply SHA-256 prefix: `3f72ec8d5b6af9b1`.

### Grok

File: `~/.grok/config.toml`

- Added `[model_providers.omniroute]` using the proven Messages backend.
- Endpoint: `http://localhost:20128/v1`.
- Credential form: `env_key = "OMNIROUTE_API_KEY"`.
- Backend: `api_backend = "messages"`.
- Added aliases:
  - `omniroute-sol` → `sh/gpt-5.6-sol`
  - `omniroute-claude-fable` → `sh/Claude-Fable`
- Existing providers retained: `cockpit`, `phanmemvip`, `shopapikey`.
- Current defaults preserved from the rebased baseline: `cockpit-sol`, `grok-4.6`, `cockpit-sol`, and `cockpit-sol` for the inspected default/web/session/fork fields.
- The Grok CLI auto-persisted the selected alias as the default during its sentinel attempt; this was detected and atomically restored to `cockpit-sol`.
- Active file mode: 600.
- Post-apply SHA-256 prefix: `a4941ef5fcfaae64`.

### Codex

File: `~/.codex/config.toml`

- Added `[model_providers.omniroute]`.
- Endpoint: `http://localhost:20128/v1`.
- Wire mode: `responses`.
- Credential form: `env_key = "OMNIROUTE_API_KEY"`.
- Both live model IDs are selectable through the official `-c model_provider` / `-c model` overrides without changing defaults.
- Existing provider `codex_local_access` retained.
- Top-level `model = "gpt-5.6-sol"` and `model_provider = "codex_local_access"` unchanged.
- Active file mode: 600.
- Post-apply SHA-256 prefix: `2069569af69889eb`.

## 5. Protocol and real sentinel evidence

### Direct OmniRoute protocol matrix (2026-08-28)

The live registry returned 968 models during the matrix run; both approved IDs were present. The matrix used both approved IDs across chat-completions, Responses, and Messages, streaming and non-streaming:

- All six streaming paths passed exact `pong` (chat, Responses, and Messages × two models).
- Chat non-streaming returned HTTP 502 `upstream_empty_response` for both models.
- Messages non-streaming returned a 90-second no-byte timeout for `sh/gpt-5.6-sol` and HTTP 502 `upstream_empty_response` for `sh/Claude-Fable`.
- Responses non-streaming returned a completed response; full-body capture confirmed `output_text` was present. An earlier matrix extractor incorrectly treated `error: null` as an error; that parser issue was corrected before CLI verification.
- Responses streaming contained a malformed bare heartbeat, `data: {"type":"response.in_progress"}`, before a later valid event carrying the response and sequence number. This is the source of Grok's native `serialization error: missing field sequence_number` under the original Responses backend.

### Final end-to-end CLI sentinels (2026-08-29)

Each target was run in a fresh login shell, in a unique disposable directory, with file-backed stdout/stderr, bounded process-group cleanup, and exact response-line matching. No literal credentials were recorded.

| CLI | Selector | Result |
|---|---|---|
| OpenCode | `omniroute/sh/gpt-5.6-sol`, `--auto --pure --format default` | exact `pong`, exit 0, 15.52s |
| OpenCode | `omniroute/sh/Claude-Fable`, pure mode | exact `pong`, exit 0 |
| Droid | `custom:OmniRoute-gpt-5-6-sol` | exact `pong`, exit 0 |
| Droid | `custom:OmniRoute-Claude-Fable` | exact `pong`, exit 0 |
| Grok | `omniroute-sol`, `--single`, Messages backend | exact `pong`, exit 0 |
| Grok | `omniroute-claude-fable`, `--single`, Messages backend | exact `pong`, exit 0 |
| Codex | `sh/gpt-5.6-sol`, `codex exec`, Responses | exact `pong` in `--output-last-message`, exit 0 |
| Codex | `sh/Claude-Fable`, `codex exec`, Responses | exact `pong` in `--output-last-message`, exit 0 |

OpenCode's first fresh SOL attempt reached its 180-second bound without output; a distinct fresh-shell invocation with `--auto --pure --format default` then passed in 15.52 seconds. The timeout did not mutate configuration. The final per-CLI probes passed 8/8.

### Evidence-based fixes and drift repair

- Grok's OmniRoute provider changed only `api_backend = "responses"` → `api_backend = "messages"`; both aliases passed afterward, all inspected defaults/providers were preserved, and mode remained 600.
- Droid's CLI had rewritten semantically equivalent JSON (escaped `\\u00b7` to literal UTF-8) and mode 0644 during an earlier test. The exact registered baseline was restored atomically, mode 600 enforced, and both final Droid sentinels passed under `umask 077` with no subsequent drift.
- Final value-blind active hashes were: OpenCode `864e90297bd1f21a`, Droid `3f72ec8d5b6af9b1`, Grok `a49b78c89b32e084`, Codex `2069569af69889eb`. Final modes were 644, 600, 600, and 600 respectively.
- The final live registry returned 966 models; both approved IDs remained present.

## 6. Preservation and security audit

A post-repair value-blind audit returned `AUDIT_SUMMARY failures=0` and exit 0. It verified:

- all four changed files parse;
- both approved live `sh/*` models are registered in every changed target;
- endpoint and credential indirection are correct;
- all pre-existing providers are retained;
- all inspected defaults are preserved;
- active changed files contain no `dlg/*` routes;
- Droid, Grok, and Codex are mode 600;
- all six verify-only baseline hashes match their pre-change capture:
  - Kilo
  - Pi
  - OMP
  - Goose catalog
  - Goose config
  - Kimi

## 7. OpenSpec status

- The previously blocked Grok and Codex sentinel tasks are resolved: Grok uses the evidence-based Messages backend, and Codex passes the Responses path.
- All approved runtime and preservation gates pass; the package is ready for final strict validation, scoped commit, and archive.
- No default model changes were approved or retained.
- No provider-side credential rotation was performed.
- Unrelated store work remains untouched.
