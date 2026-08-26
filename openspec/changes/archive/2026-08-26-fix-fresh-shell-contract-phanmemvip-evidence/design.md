## Context

See `proposal.md` for motivation. The canonical capability already carries the phanmemvip default in requirement bodies, but two inherited scenario headings still name Cockpit and the archived predecessor contains no completed verification tasks.

## Goals / Non-Goals

**Goals:**
- Preserve every canonical scenario heading required by MODIFIED-delta validation.
- Make the contradictory headings explicitly deprecated without renaming them.
- Capture raw output from the original three fresh-shell probes before completion.

**Non-Goals:**
- No runtime configuration, credential, loader, or shell-wiring changes.
- No provider fallback or routing redesign.

## Decisions

- Keep the canonical requirement and scenario names verbatim; place a deprecation note immediately below each contradictory scenario heading and make the normative body describe `phanmemvip/gpt-5.6-sol:max`.
- Execute probes from the planning root with `/bin/zsh -lc` so the evidence exercises the fresh-login-shell contract.
- Record command output directly in `tasks.md`; transaction boundaries are unaffected because all runtime probes are read-only and the only writes are OpenSpec artifacts.

## Risks / Trade-offs

- The retained Cockpit wording remains visible for validator compatibility, so the deprecation note must be explicit and adjacent.
- Provider-side availability can affect OMP probes; attribution and fallback events in JSON are authoritative evidence, not a plain-text `pong` alone.
