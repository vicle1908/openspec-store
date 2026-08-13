## Why

The live omp role map uses `giaoduc/Advance` as the default, but three current
main specs contain stale claims about the Cockpit default and pinned v17.2.15.
The configuration is already correct. This change corrects the documentation to
match live ground truth.

## What Changes

1. MODIFIED `omp-fresh-shell-contract`: REMOVED Cockpit default requirement,
   ADDED Giaoduc default requirement.
2. MODIFIED `omp-provider-routing`: updated role-allocation scenarios to reflect
   Giaoduc as both `default` and `task`.
3. MODIFIED `omp-installation-management`: replaced pinned v17.2.15 with
   evidence-based version tracking.
4. Corrected Purpose sections for all four omp main specs (were TBD placeholders).
5. No live configuration changes.

## Non-Goals

- No credential rotation.
- No changes to `models.yml`, `config.yml`, `.zshenv`, `.zprofile`, or the
  loader.
- Historical archives remain untouched.
