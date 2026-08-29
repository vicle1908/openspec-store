# Tasks: Stabilize Goose SOL transport and harden agent CLI config permissions

## Track 1: Goose transport stabilization

- [x] 1.1 Run isolated A/B/C/D matrix plus A/D ollamacloud extension (3x per model per variant, temp HOMEs, live hash guard, full error capture)
- [x] 1.2 Classify: ollamacloud 400s are pre-existing catalog unavailability identical at baseline; gate is baseline-relative; dedicated provider preferred, C as fallback
- [x] 1.3 Isolated test: dedicated provider `custom_omniroute_sh` (models exactly `sh/gpt-5.6-sol` + `sh/Claude-Fable`, `base_path: chat/completions`) in a temp HOME — 3/3 per model with assistant content and nonzero usage; unknown-provider negative control failed as expected; original-provider `sh/Claude-Fable` non-interference round passed; live hash unchanged
- [x] 1.4 Live application per decision (additive provider file with existing provider hash-verified, or single-field C on the original provider with mode-600 backup)
- [x] 1.5 Three consecutive live rounds across affected models (assistant `pong`, nonzero usage, no decode error)
- [x] 1.6 Record the pre-existing ollamacloud catalog finding for OmniRoute-side reconciliation

## Track 2: Droid default classification

- [x] 2.1 Record `claude-opus-5` vendor default and `sessionDefaultSettings.model` non-governance in the evidence manifest
- [x] 2.2 Recheck explicit OmniRoute custom models and the existing wrapper (one round each)
- [x] 2.3 No Droid mutation

## Track 3: Credential permission hardening

- [x] 3.1 Capture path/mode/size/SHA-256 for the four confirmed files
- [x] 3.2 Create timestamped mode-600 backups outside Git
- [x] 3.3 `chmod 600` on `~/.pi/agent/mcp.json`, `~/.config/opencode/opencode.json`, `~/.kimi/config.toml`, `~/.kimi-code/config.toml`; prove SHA-256 byte-identity before/after
- [x] 3.4 Post-change probes: Pi startup, OpenCode run, Kimi effective-config model call
- [x] 3.5 Record rotation as a user-owned follow-up (never print values, never rotate automatically)

## Track 4: Verification, rollback, cleanup

- [x] 4.1 Corruption guard + strict `openspec validate --strict` before any live mutation
- [x] 4.2 Preserve unrelated store work; scoped commit with explicit paths only (never `git add .`)
- [x] 4.3 Remove temp scripts/evidence/temp HOMEs/probe processes after evidence is captured
- [x] 4.4 Final status matrix
