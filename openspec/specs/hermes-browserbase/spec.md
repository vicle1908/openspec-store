# hermes-browserbase Specification

## Purpose
Enable Hermes Agent to use Browserbase-managed cloud browsers for public web automation while preserving local routing for private URLs and selecting a compatible native browser-tool implementation.
## Requirements
### Requirement: Browserbase Credentials

Browserbase credentials SHALL be stored in `~/.hermes/.env` with restrictive file permissions (`600`). Credentials MUST NOT be added to repository files, OpenSpec artifacts, logs, or future output.

#### Scenario: Credentials are present and secure

- Given `~/.hermes/.env` contains `BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID`
- When `stat -f '%A' ~/.hermes/.env` is executed
- Then permissions SHALL be `600`

### Requirement: Native Tool Routing

When `browser.cloud_provider` is `browserbase`, `browser.backend` SHALL be `off` so Hermes exposes and invokes native `browser_*` tools. The Browser Use CLI wrapper MUST NOT be selected for this Browserbase configuration because the Browserbase provider's CDP endpoint is not compatible with that wrapper in the installed runtime.

#### Scenario: Native tools are selected

- Given `browser.cloud_provider` is `browserbase`
- And `browser.backend` is `off`
- When a fresh Hermes browser task starts
- Then the task SHALL use native `browser_navigate`/`browser_snapshot` tools
- And it SHALL NOT expose `browser_exec` as the active browser implementation

### Requirement: Cloud Provider Activation

`browser.cloud_provider` SHALL be set to `browserbase` via `hermes config set`. The Hermes runtime SHALL read this key through the plugin-bridged browser dispatcher.

#### Scenario: Provider is active

- Given `hermes config get browser.cloud_provider` returns `browserbase`
- When native `browser_navigate` is called with a public URL
- Then the response SHALL contain actual page content
- And the session metadata SHALL identify a Browserbase session without local fallback

### Requirement: Hybrid Routing

Public URLs SHALL route to Browserbase cloud. Private/loopback URLs SHALL automatically route to a local Chromium sidecar via the existing `auto_local_for_private_urls: true` setting.

#### Scenario: Public URL routes to cloud

- Given `browser.cloud_provider` is `browserbase`
- And `browser.backend` is `off`
- When native `browser_navigate` is called with `https://example.com`
- Then the request SHALL be routed to the Browserbase cloud provider

#### Scenario: Private URL uses local sidecar

- Given `browser.cloud_provider` is `browserbase`
- And `browser.auto_local_for_private_urls` is `true`
- When native `browser_navigate` is called with a loopback URL
- Then the request SHALL use a local Chromium sidecar and SHALL NOT send the URL to Browserbase

