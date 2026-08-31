# Drift Provenance and Ownership Disposition — 2026-08-30

Value-blind record. No credential values, raw bodies, or secret-shaped literals are retained.

## Drift audit (retained baseline `pre-apply-manifest.json` vs live, 2026-08-30)

The baseline tracks 31 entries. Exactly three changed between the 2026-08-29 capture and
this audit; the other 28 entries retain their baseline state: 24 byte-identical files and
4 still-absent paths (`~/.claude/profiles/omniroute.json`, `~/.codex/omniroute.config.toml`,
`~/.config/goose/custom_providers/custom_omniroute_anthropic.json`,
`~/.config/goose/custom_providers/custom_omniroute_responses.json`).

Live evidence for the three drifted paths:

1. `~/.claude/helpers/omniroute-key.sh` — absent at baseline; now exists: 962 bytes,
   mode 0o700, mtime 2026-08-30T12:16:09. (Distinct from the same-named file that had
   existed under `evidence/candidate-templates/`; that template copy was removed by this
   change's ownership correction below.)
2. `~/.zshrc` — 10459 → 11411 bytes, mode 0o600 unchanged. The retained baseline
   manifest records a mixed inventory (6 function launchers + 5 `COPILOT_*`
   environment bindings); the current file contains 9 function launchers — the
   externally owned `omniroute()` launcher plus `_path_append`/`_path_prepend`
   from the PATH-normalization owner — and preserves all 5 frozen `COPILOT_*`
   bindings. Function launchers and environment bindings are tracked as separate
   classes in `evidence/baseline-drift-register.json` (v2 semantics); no launcher
   and no Copilot binding was removed.
3. `~/.codex/config.toml` — byte length stable at 9918 and mode stable at 0o600,
   whole-file sha churned (mtime 12:04:24). Current parsed routing fields:
   `model = gpt-5.6-sol`, `model_provider = codex_local_access`, provider set
   {codex_local_access, omniroute}, `[model_providers.omniroute]` with
   `wire_api="responses"`, `base_url http://localhost:20128/v1`,
   `env_key OMNIROUTE_API_KEY`. Of these, the retained baseline manifest directly
   records the default selector (`codex.model`, `codex.model_provider`) and the
   codex provider inventory — both unchanged from baseline. The per-provider wire
   fields are live observations, not baseline-recorded values.

## Provenance (conservative attribution)

### Claude surface — separately owned active change

The helper (12:16), `~/.claude/profiles/omniroute-pm.json` (12:17, undeclared new file),
and the `.zshrc` launcher (12:18) correlate strongly with the active change
`add-claude-code-omniroute-pm-launcher` (16/17 tasks; store commit `82879dd` at
2026-08-30T12:27+07:00, author vinhlk2, whose content is only that change's OpenSpec
directory). This is correlated external-owner evidence: timestamps, file roles, and the
commit message align, but the commit itself contains only store files and does not by
itself prove who wrote the home-directory files. Attribution is "external owner,
correlated," not definitive Git provenance.

Note the external surface created `omniroute-pm.json`, not `omniroute.json`; the
baseline-tracked `~/.claude/profiles/omniroute.json` remains absent, so there is no path
collision with this change's tracked targets.

That change's retained evidence reports live verification: Claude Code 2.1.251
end-to-end through OmniRoute returns the sentinel with exit 0, and the `[1m]` suffix is
stripped client-side before the wire model is sent. `pm/Claude-Fable[1m]` in that
profile is therefore a client-local selector, not a gateway model ID. This change does
not correct or overwrite it.

Disposition: Claude Code's PM route is satisfied by the external owner. This change has
no Claude candidate templates, contract entries, or route checks; no competing surface
on the same paths is created.

### `~/.zshrc` — protected for this change

Two active changes own `.zshrc` edits: `add-claude-code-omniroute-pm-launcher`
(launcher) and `normalize-shell-cli-path` (PATH normalization, 0/11). This change
treats `.zshrc` as protected: no writes. The externally owned `omniroute()` launcher
already satisfies the Claude opt-in route.

GitHub Copilot CLI: native PM and SH BYOK probes both passed
(`CANDIDATE_COPILOT_PM_OK` / `CANDIDATE_COPILOT_SH_OK`, env-based opt-in). Persistent
`.zshrc` launchers are deferred because `.zshrc` is protected; the proven route remains
available through `COPILOT_PROVIDER_*` environment opt-in. Deferred, not blocked.
The route checker follows the same deferral: its named check
`shell.copilot-opt-in-surface-preserved` asserts only preservation of the COPILOT
opt-in surface (the `COPILOT_PROVIDER_TYPE` and `COPILOT_PROVIDER_BASE_URL` hook
identifiers), never an applied OmniRoute model binding, and no `.zshrc` write is
invented to satisfy it.

### `~/.codex/config.toml` — protected ambient/external drift

The file's mtime (12:04:24) correlates with a ChatGPT.app relaunch at 12:04, and
ChatGPT/Codex Framework processes are running. Correlation is not proof of writer; the
file is classified as protected ambient/external drift. Across observed rewrites: byte
length stable at 9918, mode stable 0o600, parsed routing fields stable (listed above);
only the whole-file sha churns.

Policy: structural preservation only — mode, existence, defaults, provider inventory,
model inventory, and the omniroute routing fields are enforced; whole-file sha equality
is not. `~/.codex/omniroute.config.toml` (the selectable profile) remains this change's
owned new file.

## Template and contract corrections recorded with this disposition

- Removed from `evidence/candidate-templates/` (verified on disk):
  - `claude-omniroute.json` and `omniroute-key.sh` — the Claude surface is externally
    owned; this change keeps no competing Claude candidate.
  - `custom_omniroute_responses.json` — goose native Responses is FBC-4 failed-native;
    no known-broken route is registered.
  - `custom_omniroute_sh.json` — the live goose SH fallback provider is owned by the
    archived `stabilize-goose-sol` change; this change's goose apply set is PM-only
    (`custom_omniroute_anthropic.json`).

  The overlay contract references exactly the remaining templates;
  `overlay-contract-check.py` rejects any template file not referenced by the contract.
- No failed-native provider registration is applied anywhere: Kimi Code Responses
  (FBC-2), omp responses provider (FBC-1), and goose Responses (FBC-4) are absent from
  the apply templates.
- Kimi Code SH alias `or-gpt-5-6-sol` rebound to the proven versionless chat provider
  `omniroute-chat` (exact model `sh/gpt-5.6-sol`, FBC-2 disposition); PM alias
  `or-claude-fable` binds `omniroute-anthropic` with exact `pm/Claude-Fable`. A dormant
  native Responses provider may exist elsewhere without failing acceptance, but no active
  SH alias may select it. The template mirrors the live Kimi schema — capabilities and
  effort at model level only, no provider-level capability fields, no `max_output_size`
  key — and sets SH `default_effort = "high"` with the `thinking` capability: the
  retained FBC-2 chat probe passed without an effort override (so the alias default must
  remain a supported tier), the live config uses `high` for the same model ID, and the
  proven omp chat fallback on the same versionless route used `--thinking=high`
  explicitly. `none` is not inferred from the Chat Completions dialect. The model-level
  capabilities mirror the live `or-gpt-5-6-sol` row for the same model ID (`thinking`,
  `image_in`, `tool_use`); the gateway catalog lists vision for `sh/gpt-5.6-sol`, so the
  rebinding removes no capability.
- goose SH fallback needs no apply: the archived owner already applied the dedicated
  `custom_omniroute_sh` provider live with the probe-proven tuple; this change only adds
  the PM provider `custom_omniroute_anthropic`.
- Droid's SH acceptance pins the exact tuple the isolated probe proved
  (`CANDIDATE_DROID_SH_OK`: customModels `provider="openai"`, `baseUrl
  http://localhost:20128/v1`, env-keyed credential, model `sh/gpt-5.6-sol`). The wire
  dialect is established by that live probe, not inferred from the base URL; the static
  check binds the probe-proven tuple, and no chat-fallback branch exists for Droid
  because its native Responses route passed.
- omp template credential fields corrected to the documented env-name reference
  (`OMNIROUTE_API_KEY`); no literal credentials in any template.

## Deferred stale selectors (observed, not owned here)

- kilo `agent.debug.model` selects the legacy `omniroute/sh/Claude-Fable` chat route;
  existing defaults are preserved per policy and reported as deferred.
- opencode legacy `omniroute` provider retains `sh/Claude-Fable` with a chat endpoint hint.
- goose legacy `custom_omniroute` and the applied `custom_omniroute_sh` retain
  `sh/Claude-Fable` rows.
- `~/.zshrc` `COPILOT_MODEL=deepseek-v4-pro` (existing default, preserved).

These are legacy registrations on preserved providers/selectors. This change does not
delete preserved provider entries; retirement of stale selectors is a separately named
task if required.

## Baseline policy

The retained `pre-apply-manifest.json` (captured 2026-08-29, producer schema v1) is the
single rollback anchor for every apply under this change. It is preserved unchanged and
is never regenerated or superseded; no re-capture of the 2026-08-29 state is performed or
planned. Its rollback records are planning-only (templated backup locations, no backups
created), so the manifest consumer derives v1 transitions and expected rollback bytes
from the recorded baseline file metadata, never from live state.

"Schema v2" refers only to future producer output: post-apply captures and lifecycle
fixtures emit an explicit `schema` field, and the consumer accepts both the retained v1
baseline and v2 producer output. It does not replace the historical baseline.
