# Design: correct-omp-native-cockpit-main-spec

## Current routing ground truth

- omp cockpit provider: `http://localhost:51006/v1`, `openai-responses`
- Cockpit Tools.app owns port 51006 (`cockpit-cliproxy`)
- Claude Code adapter: host `localhost:8788` → container `8787`, `anthropic-messages`
- The adapter mapping is owned by the archived WebUI/Tailscale setup work and
  remains in place for Claude Code. It is not an omp provider endpoint.

## Main spec correction

Replace the current Native Cockpit preflight requirement with:

```markdown
### Requirement: Native Cockpit preflight

Before live mutation, the preflight SHALL verify that Cockpit Tools.app
is listening on port 51006 and that native `/v1/responses` succeeds.
The current omp cockpit endpoint SHALL be `http://localhost:51006/v1`
with `api: openai-responses`.
The Claude Code compatibility adapter remains externally owned at host
port 8788 (container port 8787) and SHALL NOT be used by omp.

#### Scenario: port 51006 responds

Given the preflight check
When a valid OpenAI Responses request is sent to `http://localhost:51006/v1/responses`
Then the response SHALL be HTTP 200 with a valid JSON body containing `model: gpt-5.6-luna`.

#### Scenario: omp uses native cockpit

Given `models.yml` is inspected programmatically
Then `cockpit.baseUrl` SHALL be `http://localhost:51006/v1`
And `cockpit.api` SHALL be `openai-responses`.

#### Scenario: adapter remains external to omp

Given the adapter Docker Compose mapping `127.0.0.1:8788:8787`
When all omp provider base URLs are inspected
Then no omp provider SHALL reference `localhost:8787` or `localhost:8788`.
```

## Traceability

- Source of truth: `~/.hermes/config.yaml` cockpit provider and live
  `~/.omp/agent/models.yml`.
- Existing implementation change: `2026-08-12-use-native-cockpit-and-reassign-omp-model-roles`.
- Adapter mapping owner: archived `2026-08-12-setup-hermes-webui-tailscale-access`.
