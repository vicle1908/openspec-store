## Context

The archived Cline cleanup change contains:

- a verified cleanup mutation,
- a verified static 17/17 route-contract check,
- verified isolated per-ID negative controls,
- and a positive live-sentinel record.

The positive sentinel was executed through a credential-carrying configuration file after that credential had been exposed in a session transcript. The canonical `omniroute-agent-cli-routing` requirement at `openspec/specs/omniroute-agent-cli-routing/spec.md:409-424` blocks live verification through such a file until the owner records upstream rotation or explicit accepted-risk authorization. The archived change contains neither release.

## Goals / Non-Goals

**Goals**

- Keep the archived bytes unchanged.
- Preserve the cleanup mutation, static 17/17 check, and isolated negative controls.
- Reopen only the credential-release and positive live-sentinel gate.
- Record the invalidation in a fresh active change.
- Leave the change ACTIVE until the owner resolves the credential gate.

**Non-Goals**

- Do not invalidate or rerun the static route-contract check.
- Do not invalidate or rerun the isolated per-ID negative controls.
- Do not mutate Cline configuration.
- Do not archive this corrective change while the owner gate is open.

## Decisions

- Treat the archived positive sentinel as void only because it was executed through a disclosed credential without a recorded rotation or accepted-risk release.
- Preserve all evidence that does not depend on the disclosed credential.
- Do not perform a new positive sentinel until the owner records:
  - upstream credential rotation, or
  - explicit accepted-risk authorization to proceed without rotation.

## Risks / Trade-offs

- Treating the entire archived cleanup as void would discard valid cleanup, static, and negative-control evidence; this change avoids that overreach.
- Leaving the change active preserves the owner gate and prevents another premature archive.

## Gate Resolution

The owner released the credential gate with the explicit current-conversation
decision `address blocker, no need rotate`. Rotation was not performed and no
credential value is recorded. The release is captured in
`evidence/owner-credential-gate-release.json`.

After release, a fresh positive Cline sentinel used `openai-compatible` / `sh/gpt-5.6-sol` and
passed with exit 0 and `OMNIROUTE_DIALECT_OK`; evidence is in
`evidence/fresh-cline-positive-sentinel.json`. The active correction can now
be closed after its path-limited commit and archive validation.
