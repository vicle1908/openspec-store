# Spec Delta: shb-ecosystem-tooling

## ADDED Requirements

### Requirement: Python 3.15 Runtime Floor and Bytecode Hygiene Across SHB Repositories
All 13 repositories in the `shb` ecosystem SHALL enforce `requires-python = ">=3.15"`, `.python-version` (`3.15`), and `required-version = ">=0.13.5"`, document `Python 3.15` consistently in `shb/README.md`, and maintain `__pycache__/` trees free of stale `cpython-314*.pyc` bytecode artifacts.

#### Scenario: SHB documentation and bytecode trees match Python 3.15
- **WHEN** inspecting `shb/README.md` and scanning `/Users/androidteam/Developer/shb/` for `*cpython-314*.pyc`
- **THEN** all 12 repository entries in `shb/README.md` (including `shb-webhook-receiver`) SHALL state `Python 3.15 (uv, hatchling)`
- **AND** zero `*cpython-314*.pyc` files SHALL remain across `/Users/androidteam/Developer/shb/`.
