# Verification Evidence: `standardize-goose-omniroute-runtime`

## Execution Summary

- **Date**: 2026-10-15
- **Workstation**: macOS arm64 Darwin 27.0.0
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Target Application**: Goose CLI `v1.54.0` (`/opt/homebrew/bin/goose`)

## 1. Preflight Backups & State

Mode `0600` backups created outside Git:
```text
-rw-------  1 androidteam  staff  4972 Oct 15 12:06 /Users/androidteam/.config/goose/config.yaml.bak-20261015120603
-rw-------  1 androidteam  staff  1581 Oct 15 12:06 /Users/androidteam/.config/goose/custom_providers/custom_omniroute.json.bak-20261015120603
```

OmniRoute loopback health on `http://localhost:20128/v1/combos`:
```json
{
  "name": "gemini-3.8-flash-high",
  "strategy": "auto",
  "model_count": 15
}
```

## 2. Configuration Mutations & Verification

### A. Provider Definition (`~/.config/goose/custom_providers/custom_omniroute.json`)
- Declared `context_limit: 1048576` ($2^{20}$ true 1M capacity) for `gemini-3.8-flash-high`.
- Declared `timeout_seconds: 600`.
- Pruned decommissioned routes (`ollamacloud/*`, `sh/*`).

### B. Runtime Configuration (`~/.config/goose/config.yaml`)
- `GOOSE_CONTEXT_LIMIT: 1048576`
- `GOOSE_PLANNER_CONTEXT_LIMIT: 1048576`
- `GOOSE_MAX_TOKENS: 65536`
- `GOOSE_AUTO_COMPACT_THRESHOLD: 0.8`
- `GOOSE_CONTEXT_STRATEGY: summarize`
- `GOOSE_TOOL_CALL_CUTOFF: 10`
- `GOOSE_THINKING_EFFORT: high`
- `GEMINI3_THINKING_LEVEL: high`
- `GOOSE_CLI_SHOW_THINKING: 1`
- `OPENAI_BASE_URL: http://localhost:20128/v1`
- `OPENAI_HOST: http://localhost:20128/v1`
- `OPENAI_BASE_PATH: chat/completions` (purged legacy Cockpit port 51006 and `v1/response`)

### C. Permissions Hardening
```text
drwx------  14 androidteam  staff   448 Oct 15 12:06 /Users/androidteam/.config/goose
drwx------  10 androidteam  staff   320 Oct 15 12:06 /Users/androidteam/.config/goose/custom_providers
-rw-------   1 androidteam  staff  5153 Oct 15 12:07 /Users/androidteam/.config/goose/config.yaml
-rw-------   1 androidteam  staff   742 Oct 15 12:06 /Users/androidteam/.config/goose/custom_providers/custom_omniroute.json
```

## 3. Live Sentinel Verification

Non-interactive sentinel probe:
```bash
goose run --no-session --text "Respond with exactly: PONG"
```
Output:
```text
    __( O)>  ● new session · custom_omniroute gemini-3.8-flash-high
   \____)    20261015_1 · /Users/androidteam/Developer
     L L     goose is ready
PONG
```
Exit code: 0, duration: 17.49s.

OmniRoute Container Ingress Log (`omniroute-base`):
```text
omniroute | {"level":30,"time":"2026-10-15T05:09:43.739Z","service":"omniroute","module":"sse","tag":"COMBO","msg":"Trying model 1/15: agy/gemini-3.8-flash-high"}
omniroute | {"level":30,"time":"2026-10-15T05:09:43.740Z","service":"omniroute","module":"sse","tag":"ROUTING","msg":"agy/gemini-3.8-flash-high → antigravity/gemini-3.8-flash-high"}
omniroute | {"level":30,"time":"2026-10-15T05:09:43.790Z","service":"omniroute","module":"sse","tag":"CONTEXT","msg":"Attempting to resolve combo limits for comboName=gemini-3.8-flash-high"}
omniroute | {"level":30,"time":"2026-10-15T05:09:43.800Z","service":"omniroute","module":"sse","tag":"CONTEXT","msg":"Adjusted invalid or oversized output token fields (max_tokens); 854305 tokens remain for output (output ceiling in effect: 65536, antigravity/gemini-3.8-flash-high's own cap)"}
omniroute | {"level":30,"time":"2026-10-15T05:09:47.736Z","service":"omniroute","module":"sse","tag":"COMBO","msg":"Model agy/gemini-3.8-flash-high succeeded (3999ms, 0 fallbacks)"}
```

## 4. OpenSpec Strict Validation
```bash
openspec validate standardize-goose-omniroute-runtime --strict --json --store openspec-store
```
Result: 1/1 valid, 0 issues.
