## Why

The archived `omp-provider-routing` spec still describes the pre-migration
cockpit adapter endpoint (`localhost:8788`) as the current live omp endpoint.
The implementation now routes omp natively through Cockpit Tools.app at
`localhost:51006/v1` using OpenAI Responses. The adapter remains on host port
8788 for Claude Code, so the main spec must distinguish those ownership boundaries.

## What Changes

- Correct the main `omp-provider-routing` spec's Native Cockpit preflight
  requirement to describe the native endpoint as the current omp endpoint.
- Preserve the adapter's `8788 -> container 8787` mapping as an external
  Claude Code / WebUI boundary, not an omp provider endpoint.
- Remove the stale scenario that treats `localhost:8788` as current cockpit
  routing for omp.

## Non-Goals

- No live configuration changes.
- No changes to Docker Compose, Claude Code, Hermes WebUI, or Cockpit Tools.app.
- No changes to archived historical artifacts.
