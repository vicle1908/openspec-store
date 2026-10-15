# Verification Evidence: route-omp-gemini-4-argon-combo

## Live Catalog Resolution
- Verified `omp models --json` contains `omniroute/gemini-4-argon`:
  ```
  "selector":"omniroute/gemini-4-argon"
  ```
  Declaring `contextWindow: 1000000`, `maxTokens: 128000`, `reasoning: true`, and thinking effort levels `[low, medium, high]`.

## Configuration Validation
- `~/.omp/agent/config.yml`:
  - `modelRoles.default: omniroute/gemini-4-argon:high`
  - `retry.fallbackChains['omniroute/gemini-4-argon']: ['omniroute/gemini-3.8-flash-high', 'google-antigravity/gemini-3.8-flash:high']`
  - Validated syntax via PyYAML safe parser without warnings.

## Default Turn Live Probe
- Executed default turn probe without `--model` flag:
  ```bash
  omp --mode json --no-session --no-tools -p "reply only: pong"
  ```
- Output trace:
  ```json
  {
    "type": "turn_end",
    "message": {
      "role": "assistant",
      "content": [
        {"type": "text", "text": "Ready. State the task."},
        {"type": "text", "text": "pong"}
      ],
      "api": "openai-responses",
      "provider": "omniroute",
      "model": "gemini-4-argon",
      "usage": {
        "input": 75305,
        "output": 50,
        "totalTokens": 75355,
        "reasoningTokens": 40
      },
      "duration": 11305.04,
      "ttft": 10242.05,
      "stopReason": "stop"
    }
  }
  ```
- Result: Directly served by OmniRoute's `gemini-4-argon` combo in 11.3s with 40 reasoning tokens, with zero fallback events.
