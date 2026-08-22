# Provider Health — Post-Harness-Fix Diagnostic

## Cockpit (custom:gpt-5.6-sol)

- **Selector:** `custom:gpt-5.6-sol`
- **Provider adapter:** `openai`
- **Endpoint:** `http://localhost:51006/v1`
- **Diagnostic prompt:** `Return exactly COCKPIT_DIAG_OK`
- **Result:** success
- **Duration:** 5790ms
- **Turns:** 1
- **Credential source:** env-var `${HERMES_CUSTOM_COCKPIT_API_KEY}`
- **Credential value:** not recorded

The earlier Cockpit authentication failure was intermittent or context-dependent.
Cockpit is healthy and scored as an active provider for the benchmark.
