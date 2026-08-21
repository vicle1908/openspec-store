## 1. Confirm Ownership and Documentation Boundaries

- [ ] 1.1 In `tdt-scheduler` only, document the scheduler deployment/runbook ownership for the scheduler Dockerfile, entrypoint, Compose runtime, port `9100`, and `/scheduler/health`; verify the runbook names no other repository as the Compose runtime owner.
- [ ] 1.2 In `agent-core` only, document the observability Compose integration environment for PostgreSQL, OTel Collector, Langfuse, and MLflow; verify each referenced service, network, and environment name against the `agent-core` Compose configuration.
- [ ] 1.3 Record `tdt-observability` as a library/dashboard source owner and integration dependency, not a current deployment Compose owner; verify no implementation or documentation task assigns it scheduler/runtime ownership.
- [ ] 1.4 Keep documentation writers restricted to their respective repositories (`tdt-scheduler` and `agent-core`); verify their staged changes contain no paths in another repository or `openspec-store`.

## 2. Preserve an Owned Unique-Stack Verification Procedure

- [ ] 2.1 In the `tdt-scheduler` runbook, document a collision-resistant Compose project, initial resource inventory, source/image identity capture, run-scoped `TDT_HOME`, and a non-default loopback mapping; verify the procedure identifies `tdt-scheduler-verification`, `127.0.0.1:19100:9100`, and `/tmp/tdt-scheduler-verification-home` only as reproduced evidence, not mandatory reusable names.
- [ ] 2.2 Document bounded scheduler verification of `http://127.0.0.1:19100/scheduler/health`, formatted `docker inspect`, and `docker logs --tail`; verify all commands terminate and health acceptance is based on the active HTTP endpoint rather than a stopped-container snapshot.
- [ ] 2.3 Document diagnostics-before-teardown and cleanup filtered to the unique Compose project; verify the procedure cannot remove an ambient container, volume, or network that lacks the run identity.

## 3. Classify Warnings and Defer the Source Defect

- [ ] 3.1 Document the preconditions and triage for bridge-network/Tailscale reachability timeouts, missing spreadsheet configuration, and optional Langfuse/MLflow credentials; verify the text does not classify all webhook failures as benign.
- [ ] 3.2 Capture the minimal reproduction showing `webhook-selftest` absent from the registered scheduler workflow/run list, including expected versus actual registration, source identity, and bounded diagnostics; verify the artifact is sufficient to open a separate implementation OpenSpec change.
- [ ] 3.3 Record the handoff requirements for a separate source implementation OpenSpec change for the unregistered `webhook-selftest` workflow: GitNexus impact analysis before source edits, a registration regression, and real scheduler acceptance separate from public-edge/Tailscale reachability. Verify this change neither creates that implementation change nor patches its source.

## 4. Store Validation and Archive Gate

- [ ] 4.1 In `openspec-store`, validate this planning change with `openspec doctor --store openspec-store` and `openspec validate local-compose-observability-deployment --strict --store openspec-store`; verify both commands exit 0 and `specs` remains skipped.
- [ ] 4.2 Stage and commit only the existing `proposal.md`, `design.md`, and `tasks.md` for this change; verify the staged path list contains exactly those three files and no documentation-writer worktree paths.
- [ ] 4.3 Archive only after the separately owned documentation updates, owned unique-stack acceptance, and deferred source-defect implementation change have their own evidence; verify archive review does not treat this planning commit or structural validation as implementation acceptance.
