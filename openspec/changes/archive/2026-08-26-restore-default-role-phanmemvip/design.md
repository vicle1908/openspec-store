## Context

See `proposal.md` — Why. The live YAML already contains the intended bindings for every other role; only the absent `default` mapping is in scope. The implementation path is outside the planning repository and was explicitly authorized by the user.

## Goals / Non-Goals

**Goals:**

- Add one YAML mapping without reserializing or otherwise altering the file.
- Prove a no-flag OMP request is directly served by phanmemvip without fallback.

**Non-Goals:**

- Reorder, normalize, or rewrite unrelated YAML.
- Modify `models.yml`, fallback chains, or credentials.

## Decisions

- Follow the existing live `modelRoles` mapping format and place `default` directly beneath `modelRoles:`.
- Treat the live-file replacement as a single-file transaction: copy a pre-edit baseline, produce a staged file on the same filesystem, preserve permissions, validate YAML, then atomically rename the staged file over `config.yml`.
- Compare the post-edit file against the baseline and accept only the single intended added line.
- Use JSON-mode served-provider/model attribution and fallback-event inspection as the behavioral gate.

## Risks / Trade-offs

- A concurrent writer could change `config.yml` between baseline capture and replacement. The implementation SHALL recheck the baseline immediately before the atomic rename and stop rather than overwrite concurrent work.
- The clean environment may expose provider or shell initialization failures. Such a failure blocks archive rather than being masked by fallback success.
