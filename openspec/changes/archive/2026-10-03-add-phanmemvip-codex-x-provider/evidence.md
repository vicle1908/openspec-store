# Verification Evidence: add-phanmemvip-codex-x-provider

**Date**: 2026-10-03
**Status**: Verified
**Verification timestamp**: 2026-10-03T14:37:20Z

---

## 1. Task 4.1 — Live Codex turn on `phanmemvip/codex-x`

| Item | Value |
|---|---|
| Command | `CODEX_HOME=/Users/androidteam/.codex codex exec --sandbox read-only --skip-git-repo-check` |
| Result | `CODEX-X-VERIFIED` (exit 0) |
| Provider / model | `model_provider=phanmemvip` / `model=codex-x`, **no fallback** to another provider |
| Wire | `responses` wire **ACCEPTED** (no `chat` fallback needed) |

Note: the ambient `CODEX_HOME` value is the Orca runtime home; `~/.codex` is the intended home.

---

## 2. Task 4.2 — `codex-x` resolves from the gateway

| Item | Value |
|---|---|
| Request | `GET https://api.phanmemvip.shop/v1/models` |
| Result | 28 models returned; `codex-x` listed: **True** |
| Consequence | No `cockpit-model-catalog.json` fallback entry required |

---

## 3. Task 4.3 — Bare `claude` using home defaults

| Item | Value |
|---|---|
| Effective model | `codex-x` |
| Base URL | `https://api.phanmemvip.shop` |
| `[1m]` suffix | Not applied |
| Secrets | No secret present in any modified JSON |
| Clean-environment run | exit 0, no auth error |

---

## 4. Investigated 401 (resolved, session-scoped)

A 401 was investigated and traced to a **stale `ANTHROPIC_AUTH_TOKEN`** present only in the agent session's inherited process environment.

- Claude sent **both** `Authorization: Bearer sk-ant…` (stale) and `x-api-key: <correct>`.
- The provider honors `Authorization`, so authentication failed.
- Proven session-scoped: clean login and non-login zsh both report `ANTHROPIC_AUTH_TOKEN` unset.
- Reproduced exactly with `curl` (stale `Authorization` + good `x-api-key` → same 401 message).
- The launchers avoid this because each performs `unset ANTHROPIC_AUTH_TOKEN` before `exec`.

---

## 5. Provenance

This evidence was recovered from the transient `.knowledge-refresh/evidence/add-phanmemvip-codex-x-provider/verification.txt` scratch file and placed in the archived change at the repository's `evidence.md` convention.
