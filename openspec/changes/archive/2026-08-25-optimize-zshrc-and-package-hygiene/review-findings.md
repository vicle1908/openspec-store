# Review findings: optimize-zshrc-and-package-hygiene

Date: 2026-08-25

Five Orca-assigned review lanes were requested: Goose, Kimi, Prime Agent,
Pi, and OMP. Four produced substantive evidence; Pi's provider calls were
blocked and are recorded honestly below.

## Goose - substantive review

- Rejected the proposed `compinit -C`: it bypasses completion security checks.
- Recommended moving custom completion `fpath` entries before oh-my-zsh and
  relying on its audited initialization plus `compaudit`.
- Identified unsafe `exec node/npm/npx` lazy wrappers and incomplete nvm
  semantics.
- Identified the nvm/custom npm-prefix conflict and required fresh runtime,
  prefix, and global-root evidence before npm mutation.
- Flagged plugin ordering: `zsh-syntax-highlighting` must remain last.
- Recommended component profiling instead of an unsupported `<2s` promise.

## Kimi - substantive security review

- Corrected the first draft's false claim that `NPMJS_TOKEN` was already
  redacted; the live file contains a literal assignment (tool output is
  redacted here).
- Identified the shared OmniRoute/Copilot credential identity without storing
  its value.
- Flagged CCE's unrestricted `eval` of external output as a residual code
  injection risk.
- Required an explicit interactive-only secrets boundary, strict `0600`
  backup/file handling, and a tracked rotation follow-up.
- Required native absolute Claude verification and exact secrets backup path.

## Prime Agent - OpenSpec review

- Confirmed `skip_specs: true` is correct and no active-change overlap was
  found.
- Found the original plan broadly coherent but noted that CCE startup work,
  rollback evidence, and approximate line-number edits needed clearer task
  treatment. The revised plan uses semantic anchors and explicit residual
  risk/rollback gates.

## OMP - package and execution-gate review

- Required fresh Node/npm ownership evidence in the same shell used for
  mutation; do not hard-code `~/.npm-global` or `~/.local`.
- Required prefix-specific stale Claude removal and captured package version
  for rollback.
- Required Homebrew diagnostics to gate mutation and exact pre/post link/version
  evidence. The outdated cask upgrade was removed from this change.
- OMP's internal BrewSafety scout stalled; its available inventory and gate
  findings were retained, and the stall is not treated as a pass.

## Pi - blocked

- Initial Pi review hit an upstream 403/rate-limit response.
- One retry used an unregistered provider; the live Pi provider inventory was
  checked and a second retry through the registered cockpit model returned an
  invalid-key error.
- No Pi finding is treated as evidence. Goose's independent shell review and
  the direct live baseline cover the affected technical surface.

## Resulting adjustment

The Node/npm/Claude mutation scope is split into the active successor change
`reconcile-node-global-package-topology`. This change now contains only safe
completion/secret hygiene, a read-only package handoff, and bounded Homebrew
repairs. No live configuration, package, or credential state was changed by
this review pass.
