# Verification Evidence: standardize-archive-evidence-convention

**Date**: 2026-10-03
**Status**: Verified
**Store**: `openspec-store`

---

## 1. Immutability violation recorded

| Item | Value |
|---|---|
| Archived change | `openspec/changes/archive/2026-10-03-add-phanmemvip-codex-x-provider/` |
| Offending path | `…/2026-10-03-add-phanmemvip-codex-x-provider/evidence.md` |
| Introducing commit | `6f274f8d` — *docs(archive): add missing evidence.md to archived add-phanmemvip-codex-x-provider* |
| Added files in that commit | 1 (`git show --name-status` lists a single `A`) |
| Pre-edit revision | `ed231341` (`6f274f8d^`) |
| Original archive files | `.openspec.yaml`, `design.md`, `proposal.md`, `tasks.md`, `specs/claude-code-provider-profile-resolution/spec.md`, `specs/codex-cli-provider-routing/spec.md` |

Before removal, the six original files were confirmed **byte-identical** to the archived revision (all `SAME`); `evidence.md` was the sole deviation.

---

## 2. Reversion

| Check | Result |
|---|---|
| Added file removed | yes |
| Archived directory contents | exactly the 6 original files; no `evidence.md` |
| `git status` | single `D` for the offending path; no other archived change touched |
| In-place edits to archived files | none (`git status` shows no `M` under `archive/`) |
| Diff against pre-edit revision `ed231341` | **empty** — archive restored byte-identically |
| Captured content checksum (pre-removal) | `sha256:07a652aa565571fe7e0cc0370603ebdb632208fdda699e547e598b72afd2f8c5` (2127 B, matches disk at capture) |

---

## 3. Recovered evidence — `add-phanmemvip-codex-x-provider`

Recovered from the removed file so the verification record survives outside the archive.

### 3.1 Task 4.1 — Live Codex turn on `phanmemvip/codex-x`

| Item | Value |
|---|---|
| Command | `CODEX_HOME=/Users/androidteam/.codex codex exec --sandbox read-only --skip-git-repo-check` |
| Result | `CODEX-X-VERIFIED` (exit 0) |
| Provider / model | `model_provider=phanmemvip` / `model=codex-x`, **no fallback** |
| Wire | `responses` wire **ACCEPTED** (no `chat` fallback needed) |

Note: the ambient `CODEX_HOME` value is the Orca runtime home; `~/.codex` is the intended home.

### 3.2 Task 4.2 — `codex-x` resolves from the gateway

| Item | Value |
|---|---|
| Request | `GET https://api.phanmemvip.shop/v1/models` |
| Result | 28 models returned; `codex-x` listed: **True** |
| Consequence | No `catalog` fallback entry required |

### 3.3 Task 4.3 — Bare `claude` using home defaults

| Item | Value |
|---|---|
| Effective model | `codex-x` |
| Base URL | `https://api.phanmemvip.shop` |
| `[1m]` suffix | Not applied |
| Secrets | No secret present in any modified JSON |
| Clean-environment run | exit 0, no auth error |

### 3.4 Investigated 401 (resolved, session-scoped)

A 401 was traced to a **stale `ANTHROPIC_AUTH_TOKEN`** present only in the agent session's inherited process environment.

- Claude sent **both** `Authorization: Bearer sk-ant…` (stale) and `x-api-key: <correct>`.
- The provider honors `Authorization`, so authentication failed.
- Proven session-scoped: clean login and non-login zsh both report `ANTHROPIC_AUTH_TOKEN` unset.
- Reproduced exactly with `curl` (stale `Authorization` + good `x-api-key` → same 401 message).
- The launchers avoid this because each performs `unset ANTHROPIC_AUTH_TOKEN` before `exec`.

---

## 4. Archive guidance update

`openspec/config.yaml` — `operations.archive.guidance` gained two entries:

| Entry | Purpose |
|---|---|
| Evidence artifact | Requires a single `evidence.md` from changes that performed verification work; states a change that performed no verification is not required to carry one. |
| Archive immutability | Prohibits adding, removing, editing, moving, or rewriting files in an already-archived change directory; corrects via a new active change; grandfathers the legacy `evidence/` form. |

YAML validity confirmed by `openspec validate --specs --store openspec-store` parsing the file successfully.

---

## 5. Validation results

| Check | Command | Result |
|---|---|---|
| Change validity | `openspec validate standardize-archive-evidence-convention --store openspec-store` | Change is valid |
| Store specs | `openspec validate --specs --store openspec-store` | 434 passed, 0 failed |
| Store health | `openspec doctor --store openspec-store` | Root ok; Store metadata ok |
| Archive integrity | file count after reversion | 6 files (matches original) |
| Archive vs pre-edit revision | `git diff ed231341 -- <archive path>` | empty (restored byte-identically) |

---

## 6. Provenance

The recovered evidence in §3 originated in the transient `.knowledge-refresh/evidence/add-phanmemvip-codex-x-provider/verification.txt` scratch file. It was briefly placed in the archived change (the violation this change reverts), then recovered into this active change per the requirement that corrective evidence is written to the active change only.
