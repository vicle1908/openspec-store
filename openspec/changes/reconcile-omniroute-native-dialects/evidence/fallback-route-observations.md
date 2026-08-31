# Fallback Route Observations

Change: `reconcile-omniroute-native-dialects`
Evidence status: historical isolated candidate evidence, not a fresh post-apply result.

## OMP

- Candidate provider API: `openai-completions`
- Candidate base URL: `http://localhost:20128`
- Candidate model: `sh/gpt-5.6-sol`
- Probe result: exit code 0; exact sentinel `CANDIDATE_OMP_SH_CHAT_OK`
- Source: retained isolated candidate probe record from the prior planning session.

## Goose

- Candidate provider: dedicated `custom_omniroute_sh`
- Engine: `openai`
- Base URL: `http://localhost:20128/v1`
- Base path: `chat/completions`
- Model: `sh/gpt-5.6-sol`
- Streaming: enabled
- Source contract: installed Goose source defines `OPEN_AI_DEFAULT_BASE_PATH = "v1/chat/completions"` and `OPEN_AI_VERSIONLESS_BASE_PATH = "chat/completions"`; its base-URL parser normalizes `/v1` as the authority before applying the configured base path.
- Probe result: exit code 0; exact sentinel `CANDIDATE_GOOSE_CHAT_OK` in the retained candidate matrix.
- This `/v1` + `base_path=chat/completions` tuple is the passing Goose compatibility configuration. It is not equivalent to the rejected versioned `/v1/chat/completions` endpoint: the Goose provider's base-path composition was tested as a client configuration variant and the resulting CLI call passed.

## Boundary

These observations establish candidate compatibility only. Live application still requires a fresh isolated selectability check, a post-apply endpoint/path assertion where the client exposes one, and the required consecutive live route checks. No credential values or raw response bodies are retained here.
