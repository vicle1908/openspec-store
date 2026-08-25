# Planning context: reconcile-node-global-package-topology

Date: 2026-08-25

This successor was created from the review of
`optimize-zshrc-and-package-hygiene`.

The live audit found an active nvm path, an npm prefix mismatch, a separate
`~/.npm-global` package tree, and duplicate Claude installations. Goose and
OMP independently identified the nvm/custom-prefix conflict and required
runtime/package ownership evidence before mutation. Kimi and OMP also required
absolute native Claude verification, prefix-specific uninstall, exact package
version capture, and non-hard-coded rollback.

This is a tooling/config-only change and therefore uses `skip_specs: true`.
It is intentionally proposal-only: no npm prefix, package, Node, or Claude
state was changed while creating it.
