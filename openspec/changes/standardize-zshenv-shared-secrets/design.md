# Design: standardize-zshenv-shared-secrets

## Context

Research verified the full credential landscape on 2026-08-27:

- **5 dotenv files** hold secrets: `~/.zshenv.secrets` (7 keys), `~/.hermes/.env`
  (60 keys), `~/.tdt/.env` (52 keys), adapter `.env` (1 key), webui `.env`
  (5 keys). `~/.zshrc` itself contains zero inline secrets.
- **4 keys drifted** across files (EXA, BRAVE, TAVILY, OMNIROUTE); 2 keys are
  consistent duplicates (SHOPAPIKEY, COCKPIT).
- **Shell visibility**: `~/.zshenv` runs in every zsh invocation (all 4 modes
  verified: `-c`, `-ic`, `-lc`, `-ilc`); startup cost 0.01–0.02s, silent.
- **launchd scope**: all 5 `HERMES_CUSTOM_*` keys unset (`launchctl getenv`);
  plists set only PATH/HOME/HERMES_HOME.
- **Hermes dotenv semantics** (source-verified in
  `hermes_cli/env_loader.py`): `load_hermes_dotenv()` loads `~/.hermes/.env`
  with `override=True` — the file clobbers shell-exported values.
  `get_env_value_prefer_dotenv()` checks the dotenv file first, falls back to
  `os.environ` only when the key is absent from the file.
  `_clear_known_keys_missing_from_dotenv()` is narrow-scoped (profile-routing
  keys only) and will NOT wipe shell-exported provider keys.
- **TDT dotenv semantics** (source-verified in `tdt_core/env.py`):
  `load_tdt_env()` uses `override=False` for the selected root env file —
  inherited environment values survive.
- **Official CLI mechanisms** (docs-verified): Claude Code `apiKeyHelper`
  (cached 5min, re-run on 401, prints key to stdout); Codex `env_key` in
  `[model_providers.X]`; OpenCode `{env:VAR}` config interpolation; Goose
  keychain + `GOOSE_PROVIDER`; Droid `FACTORY_API_KEY` / keyring; Pi
  `models.json` `apiKey` field.

## Goals / Non-Goals

**Goals:**
- `~/.zshenv` (mode 600) is the single source of truth for the shared tier:
  provider API keys + multi-consumer tool keys, values inline.
- Every coding-agent CLI resolves shared-tier keys from the process environment
  via its official mechanism.
- launchd-scoped services receive the shared tier through a zsh wrapper in
  `ProgramArguments`.
- All duplicates drained from service files; all drift resolved (newer wins).
- Claude helpers never export more than their one key.

**Non-Goals:**
- Moving service-private tokens (Telegram/Slack/Discord/Feishu/Matrix/WhatsApp/
  Buzz/Browserbase platform tokens, JIRA/GITLAB/ATLASSIAN service config,
  HERMES_WEBUI_*) into `.zshenv`. These stay in their service files — they have
  no shell consumer and moving them would widen exposure to every zsh
  subprocess.
- Changing any secret value (except the 4 approved drift resolutions).
- Modifying Hermes framework source or TDT application source.
- `launchctl setenv` global injection (leaks keys into every GUI process).

## Decisions

### D1: Tiered model (user-approved)

Shared tier in `~/.zshenv` (16 keys):

```
HERMES_CUSTOM_PHANMEMVIP_API_KEY
HERMES_CUSTOM_SHOPAPIKEY_API_KEY
HERMES_CUSTOM_COCKPIT_API_KEY
HERMES_CUSTOM_ANTIGRAVITY_API_KEY
HERMES_CUSTOM_LOCALHOST_51006_API_KEY
HERMES_CUSTOM_GIAODUC_API_KEY
BRAVE_SEARCH_API_KEY
EXA_API_KEY
TAVILY_API_KEY
OMNIROUTE_API_KEY
FIRECRAWL_API_KEY
OPENROUTER_API_KEY
GITHUB_TOKEN
API_KEY_SECRET
COPILOT_PROVIDER_API_KEY
NPMJS_TOKEN
POSTMAN_API_KEY
```

`MCPR_TOKEN` is intentionally excluded: verified client configurations carry
different client-specific tokens, so exporting one global value would be a
credential collision rather than standardization.

Service-private tier unchanged in `~/.hermes/.env`, `~/.tdt/.env`, webui `.env`.

### D2: Drift resolution — newer value wins (user-approved)

| Key | Winner | Evidence |
|---|---|---|
| `EXA_API_KEY` | `~/.hermes/.env` | mtime 08-25 21:32 > 08-25 14:13 > 08-08 |
| `BRAVE_SEARCH_API_KEY` | `~/.hermes/.env` | same |
| `TAVILY_API_KEY` | `~/.hermes/.env` | 08-25 > 08-08 |
| `OMNIROUTE_API_KEY` | `~/.zshenv.secrets` | 08-25 14:13 > 08-08 |

Canonical hashes recorded pre-migration; post-migration verification asserts
hash equality for every moved key.

### D3: `.zshenv` structure

```zsh
# BEGIN shared-agent-secrets (managed by standardize-zshenv-shared-secrets)
export HERMES_CUSTOM_PHANMEMVIP_API_KEY='...'
...
# END shared-agent-secrets
```

- `chmod 600` applied BEFORE any value is written (file is currently 644).
- Values single-quoted (shell-safe for all observed value charsets).
- The `~/.config/agent-llm/load-hermes-custom-credentials.zsh` loader and its
  source line are removed (values are now inline; loader retired, file kept
  with a deprecation header pointing at `.zshenv`).
- QODER PATH block preserved untouched.

### D4: Hermes override=True hazard

Because `load_hermes_dotenv()` uses `override=True`, any of the 17 shared-tier
keys present in `~/.hermes/.env` MUST be removed — otherwise the dotenv file silently
shadows `.zshenv`. Post-change invariant: `grep HERMES_CUSTOM_ ~/.hermes/.env`
returns nothing. Verification gate greps after drain.

Gateway plist gets the zsh wrapper so the gateway process inherits the shared
tier from `.zshenv`; `get_env_value_prefer_dotenv()` then falls back to
`os.environ` for keys absent from `.env`. Gateway restart is deferred to the
user (brief service interruption; current session runs on the gateway).

### D5: launchd bridge pattern

Per-service wrapper (scoped, unlike `launchctl setenv`):

```xml
<key>ProgramArguments</key>
<array>
  <string>/bin/zsh</string>
  <string>-c</string>
  <string>source "$HOME/.zshenv" &amp;&amp; exec &lt;original command…&gt;</string>
</array>
```

Applied to: `ai.hermes.gateway`, `com.tdt.ai-review`,
`com.tdt.webhook-receiver`, `com.workspace.claude-code-provider-adapter`.
Each plist backed up, then `launchctl bootout` + `bootstrap` to reload.

### D6: Claude apiKeyHelper rewrite

```sh
#!/bin/sh
# env-first: .zshenv already exported the key; fallback = restricted parse
if [ -n "${HERMES_CUSTOM_X_API_KEY:-}" ]; then
  printf '%s\n' "$HERMES_CUSTOM_X_API_KEY"; exit 0
fi
# fallback: parse ONLY this one key from ~/.zshenv (never source the file)
sed -n "s/^export HERMES_CUSTOM_X_API_KEY='\(.*\)'/\1/p" "$HOME/.zshenv"
```

Never `set -a; . file`. Helper output = exactly one line.

### D7: Pi cockpit fix

`~/.pi/agent/models.json` cockpit `apiKey` currently holds the URL
`http://localhost:51006/v1`. Replace it with
`${HERMES_CUSTOM_COCKPIT_API_KEY}`. Pi 0.84.3 source verification shows
`provider-composer.js` passes configured `apiKey` through
`resolveConfigValueOrThrow`, whose `${ENV_VAR}` template resolver reads the
process environment. The same env-template form is used for the other three
custom Pi providers. Backup first.

### D8: OpenCode rewiring

`auth.json` holds literal keys for shopapikey/cockpit/zai. OpenCode's official
mechanism is `{env:VAR}` interpolation in `opencode.json` provider options.
Migrate shopapikey + cockpit to `"apiKey": "{env:HERMES_CUSTOM_..._API_KEY}"`
in config; remove the literal auth.json entries for those two providers.
zai-coding-plan stays (different credential, not in shared tier).

### D9: .zshrc cleanup

- Remove the `~/.zshenv.secrets` source block (lines 54–64) — its 7 keys move
  to `.zshenv`. Delete `~/.zshenv.secrets` after hash-verified migration.
- Remove stale `cline_cockpit` / `cline_shopapikey` functions (binary not
  installed).
- Everything else untouched (oh-my-zsh, starship, launchers, PATH).

### D10: Adapter container

`start-adapter.sh` currently requires repo `.env`. After change: plist zsh
wrapper exports `HERMES_CUSTOM_COCKPIT_API_KEY` into the launcher env;
docker-compose `env_file` replaced by `environment:` passthrough of the single
variable. Repo `.env` drained of the key (file kept for other non-secret
compose vars if any — verified: it holds ONLY the key, so it is deleted).

## Risks / Mitigations

| Risk | Mitigation |
|---|---|
| Hermes `override=True` re-shadowing if keys get re-added to `.env` | Verification gate greps; documented invariant in EVIDENCE_MANIFEST |
| Gateway restart interrupts current session | Gateway plist edited but restart deferred to user |
| Value corruption during move | Hash equality assertion for every key, before/after |
| plist syntax error breaks service | `plutil -lint` before reload; backup; bootout/bootstrap one at a time |
| Pi literal key in models.json (mode 600) | Acceptable: file already 600, same posture as auth.json literals |
| .zshenv sourced by non-interactive shells → secrets in subprocess env | Exposure unchanged from current loader behaviour; documented trade-off of the approved design |

## Verification gates

1. `stat -f '%Lp' ~/.zshenv` = 600 (before values written).
2. All 17 keys present in all 4 zsh modes (presence + length only, never print values).
3. Hash equality: every moved key's sha256 in `.zshenv` == canonical source hash.
4. `grep -c HERMES_CUSTOM_ ~/.hermes/.env ~/.tdt/.env adapter/.env` = 0 after drain.
5. Claude helper: output is exactly 1 line; `set -a` absent from script.
6. `plutil -lint` passes on all 4 edited plists.
7. TDT services healthy after restart (health endpoint check).
8. `zsh -n ~/.zshrc` + `zsh -n ~/.zshenv` syntax clean; startup timing ≤ 0.1s.
9. Live sentinel: one provider call through a Claude launcher (user-run post-gateway-restart).
