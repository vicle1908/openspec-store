## Why

The Hermes Agent installation at `/Users/androidteam/.hermes/` has browser automation configured for local-only mode (`browser.cloud_provider: local`). The user has obtained a Browserbase subscription and provided credentials. Enabling Browserbase cloud browsing provides managed cloud browser sessions with anti-bot stealth, session isolation, and automatic cleanup.

The installed Hermes version has two independent browser settings: `browser.cloud_provider` selects the cloud provider, while `browser.backend` selects the agent-facing tool implementation. The default `browser.backend: ""` enables Browser Use CLI mode. Browser Use mode requires a CDP endpoint and cannot drive the Browserbase provider in this installation, so the native browser tool implementation must be selected explicitly with `browser.backend: off`.

## What Changes

- Install Browserbase credentials (`BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID`) in `~/.hermes/.env`. These are environment-only; no YAML, Git, or OpenSpec files contain credential values.
- Set `browser.cloud_provider` to `browserbase` via `hermes config set`.
- Set `browser.backend` to `off` via `hermes config set` so native `browser_navigate`, `browser_snapshot`, `browser_click`, and related tools drive the Browserbase CDP endpoint directly. This avoids the incompatible Browser Use CLI wrapper.
- Preserve existing browser safety and behavior settings: `inactivity_timeout: 120`, `allow_private_urls: true`, `auto_local_for_private_urls: true`, `dialog_policy: auto_dismiss`, and `use_gateway: false`.
- Validate with `hermes config check`, a fresh native `browser_navigate` smoke test, and post-test session metadata inspection proving a Browserbase session was created without local fallback.
- Record that the API key was exposed in plaintext chat. The user explicitly authorizes retaining the current key; rotation is out of scope for this change and the exposure risk is accepted.

## Capabilities

### New Capabilities

- `browserbase-cloud-browsing`: Hermes agent sessions can spawn managed Browserbase cloud browser instances for public-URL web automation with stealth, proxy support, and session isolation.

## Impact

- **Primary target:** the default Hermes profile at `/Users/androidteam/.hermes/`, specifically `config.yaml` and `.env`.
- **Behavioral impact:** Public-URL native browser tools route to Browserbase cloud. Private/localhost URLs continue to use the auto-local sidecar because `auto_local_for_private_urls` remains enabled.
- **Expected state changes:** `browser.cloud_provider: browserbase`, `browser.backend: off`, two environment variables populated in `.env`, and the running Hermes gateway/session loading the new settings.
- **External dependencies:** Browserbase cloud service must be reachable; credentials must be valid; `agent-browser` must be installed for native CDP driving.
- **Operational risk:** LOW for local configuration; Browserbase sessions incur provider usage and the exposed API key requires rotation.
- **Blast radius:** Only the Hermes browser tool surface. No terminal, file, code execution, MCP, or unrelated gateway behavior changes.

## Non-Goals

- Do not modify local Chromium, CDP, or agent-browser installation.
- Do not change `browser.allow_private_urls` or other security settings.
- Do not enable Camofox, Firecrawl, or Browser Use cloud providers.
- Do not rotate or revoke the exposed key without a replacement key or explicit dashboard/API operation.
- Do not create new Hermes profiles.
