# Tasks: add-claude-code-omniroute-pm-launcher

## 1. Baseline research (done pre-change)

- [x] 1.1 Verify OmniRoute `/v1/messages` native protocol + full CC payload acceptance (live 200)
- [x] 1.2 Verify count_tokens endpoint (live 200)
- [x] 1.3 Capture-server proof of `[1m]` stripping and exact wire model
- [x] 1.4 Confirm loopback keyless state + keyed `/v1/models` gate

## 2. Implementation

- [x] 2.1 Write `~/.claude/helpers/omniroute-key.sh` (env-first, restricted parse fallback, mode 700)
- [x] 2.2 Write `~/.claude/profiles/omniroute-pm.json` (credential-free, mode 600, modelOverrides self-map)
- [x] 2.3 Insert `omniroute()` launcher in `~/.zshrc` after `cockpit()`, before `claude_reset()`
- [x] 2.4 `zsh -n` syntax check passes

## 3. Verification

- [x] 3.1 Helper returns single line with key from env-first path
- [x] 3.2 Helper fallback path works from clean env (`env -i HOME=... zsh`)
- [x] 3.3 Profile contains no secrets; perms 600
- [x] 3.4 `omniroute -p` returns PONG with exit 0 (live)
- [x] 3.5 Launcher guard fails cleanly when helper missing (temporarily renamed)
- [x] 3.6 `claude_reset` still clears state (env cleared; global settings resolution; PONG)

## 4. Spec + store

- [x] 4.1 Delta spec `claude-code-omniroute-pm-routing/spec.md` written
- [x] 4.2 `openspec validate --strict` passes
- [ ] 4.3 Commit change to openspec-store
