# Proposal: Invalidate Cline cleanup archive without credential rotation

## Why

The archived `2026-09-03-fix-cline-stale-provider-registry` change treats a live positive sentinel as verified even though a raw provider-settings read exposed the provider’s credential token earlier in the session. The canonical `omniroute-agent-cli-routing` contract at `openspec/specs/omniroute-agent-cli-routing/spec.md:409-424` forbids treating live verification through exposed credentials as authorized unless the credential is rotated or the owner explicitly authorizes proceeding without rotation. The archive contains no rotation record and no accepted-risk release, so its live-sentinel closure claim is void.

## What Changes

- Records a fresh active invalidation of the archived Cline cleanup’s live-sentinel claim.
- Reopens the credential-rotation/accepted-risk gate as an explicit owner decision.
- Leaves the archived bytes untouched.
- Does not mutate Cline configuration or run new probes.
- Once the owner rotates/replaces the credential or explicitly authorizes accepted-risk continuation, only a fresh value-blind positive sentinel is required in this active change; the archived per-ID negative controls remain valid and are not reopened.

## Capabilities

### Modified Capabilities

- `omniroute-closure-integrity`: adds a requirement that a credential-disclosure incident SHALL block archive claims based on live verification through the disclosed credential until rotation or explicit owner accepted-risk release is recorded.

## Impact

- The archived Cline cleanup remains byte-identical and read-only.
- Downstream consumers must treat its positive live-sentinel evidence as void pending owner action.
- This change remains ACTIVE until the credential gate is resolved and a fresh positive sentinel is recorded.
