## MODIFIED Requirements

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

#### Scenario: current cockpit uses adapter port

Given the pre-change state before this correction
When `models.yml` is inspected programmatically
Then `cockpit.baseUrl` SHALL have been `http://localhost:8788`
And `cockpit.api` SHALL have been `anthropic-messages`.

#### Scenario: no adapter port dependency after change

Given the corrected `models.yml`
When all omp provider base URLs are inspected
Then no omp provider SHALL reference `localhost:8787` or `localhost:8788`.

#### Scenario: omp uses native cockpit

Given the corrected `models.yml`
Then `cockpit.baseUrl` SHALL be `http://localhost:51006/v1`
And `cockpit.api` SHALL be `openai-responses`.

#### Scenario: adapter remains external to omp

Given the adapter Docker Compose mapping `127.0.0.1:8788:8787`
When all omp provider base URLs are inspected
Then no omp provider SHALL reference `localhost:8787` or `localhost:8788`.
