# Tasks: Centralize TDT Scheduler YAML Bootstrap

## 1. Specification and Design Planning

- [ ] 1.1 Draft proposal and capability mappings for scheduler YAML bootstrap and verify with `openspec status --change centralize-tdt-scheduler-yaml-bootstrap --store openspec-store`
- [ ] 1.2 Author delta specification for `schedule-registry-loader` capability defining manifest discovery, parsing, and apply_from_yaml execution, and verify file presence
- [ ] 1.3 Author delta specification for `scheduler-engine` specifying YAML bootstrap before schedule application, and verify file presence
- [ ] 1.4 Author technical design detailing bootstrap sequence, error isolation, and transaction boundaries, and verify file presence
- [ ] 1.5 Validate change proposal strictly using `openspec validate centralize-tdt-scheduler-yaml-bootstrap --strict --store openspec-store`

## 2. Store Health and Conformance Verification

- [ ] 2.1 Verify relationship health using `openspec doctor --store openspec-store`
- [ ] 2.2 Verify full repository specification validity using `openspec validate --all --strict --store openspec-store`
