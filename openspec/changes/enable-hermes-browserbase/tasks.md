# Enable Hermes Browserbase Cloud Browsing

## 1. Plan and baseline

- [x] 1.1 Verified the installed runtime's routing split: `browser.cloud_provider` selects the cloud provider; `browser.backend` selects Browser Use/native implementation. Source evidence: `tools/browser_tool.py` reads `browser.cloud_provider`; `tools/browser_use_cli.py` documents `browser.backend: off` for native tools.
- [x] 1.2 Ran `hermes config check`; Config version 34 is valid and no blocking browser configuration error was reported. The custom `browser.cloud_provider` key is dynamically consumed by the browser dispatcher.
- [x] 1.3 Verified `~/.hermes/.env` permissions are `600`.
- [x] 1.4 Captured pre-change browser settings: provider `local`, backend unset, inactivity timeout `120`, private URLs `true`, auto-local routing `true`, dialog policy `auto_dismiss`, gateway use `false`.

## 2. Install Browserbase credentials

- [x] 2.1 Wrote `BROWSERBASE_API_KEY` to `~/.hermes/.env`; the value was never printed by the verification commands.
- [x] 2.2 Wrote `BROWSERBASE_PROJECT_ID` to `~/.hermes/.env`; the value was never printed by the verification commands.
- [x] 2.3 Verified both variables are active using presence-only checks with values masked.
- [x] 2.4 Verified `.env` remains mode `600`; unrelated existing entries remain present and no credential value appears in the OpenSpec change.

## 3. Select Browserbase and the compatible tool implementation

- [x] 3.1 Ran `hermes config set browser.cloud_provider browserbase`.
- [x] 3.2 Ran `hermes config set browser.backend off` to force native Hermes browser tools instead of Browser Use CLI mode.
- [x] 3.3 Verified `browser.cloud_provider=browserbase` and `browser.backend=off`.

## 4. Preserve existing browser settings

- [x] 4.1 Verified after mutation:
  - `browser.inactivity_timeout` = `120`
  - `browser.allow_private_urls` = `true`
  - `browser.auto_local_for_private_urls` = `true`
  - `browser.dialog_policy` = `auto_dismiss`
  - `browser.use_gateway` = `false`
- [x] 4.2 Verified the final browser configuration contains only the intended provider/backend changes relative to the captured baseline; no unrelated browser setting changed.

## 5. Restart and runtime loading

- [x] 5.1 User confirmed Hermes was restarted; the supervised gateway was subsequently started through the supported Hermes path before testing.
- [x] 5.2 `hermes gateway start` completed with `Updated gateway launchd service definition` and `Service started` before the smoke test.
- [x] 5.3 `hermes config check` reports Config version 34 and no new blocking configuration errors.

## 6. Native Browserbase smoke test

- [x] 6.1 In a fresh Python process using Hermes' native `tools.browser_tool.browser_navigate`, navigated to `https://example.com`.
- [x] 6.2 Navigation succeeded; page title and accessibility snapshot were present, with 2 elements detected.
- [x] 6.3 In-process redacted session inspection showed a non-empty Browserbase session ID and CDP URL, active feature `basic_stealth`, `fallback_from_cloud=false`, and no local feature.
- [x] 6.4 Closed/released the smoke-test session; the session was removed from the active-session registry.
- [x] 6.5 The earlier `browser_exec` failure was confirmed as a Browser Use CLI/CDP-mode incompatibility. With `browser.backend=off`, the tested native implementation created and drove the Browserbase session successfully. Browserbase returned HTTP 402 for optional keep-alive/proxy features and Hermes correctly retried without those optional features.

## 7. Security decision

- [x] 7.1 User explicitly authorized retaining the current Browserbase key despite its plaintext exposure in chat; rotation is out of scope for this verification change.
- [x] 7.2 Current key remains unchanged in `~/.hermes/.env`; its value was not printed by verification commands.
- [x] 7.3 The live native smoke test passed with the retained key, so no replacement-key smoke test is required.
- [x] 7.4 Accepted risk is recorded: the user owns the decision to retain the exposed credential.

## 8. Final verification and store hygiene

- [x] 8.1 Verified final `browser.*` configuration and `.env` presence/mode without exposing secrets.
- [x] 8.2 Verified no Browserbase credential value appears in proposal, tasks, specs, reports, or the OpenSpec Git diff.
- [x] 8.3 Ran `openspec validate enable-hermes-browserbase`; result: change is valid.
- [x] 8.4 Commit only the OpenSpec change in `~/Developer/openspec-store`; unrelated pre-existing changes remain unstaged.
