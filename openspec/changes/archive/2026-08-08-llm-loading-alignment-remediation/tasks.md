# Tasks: LLM Loading and CLI-Agent Alignment Remediation

## OpenSpec artifacts

- [x] Create proposal and design from verified review findings.
- [x] Add delta specification for provider routing, fallback loading, and verification evidence.

## Agent-core implementation

- [x] Add exact `model_names` provider routing and remove the ambiguous `fable-5` prefix mapping.
- [x] Validate `api_mode` compatibility before constructing a model.
- [x] Wire configured fallback models into the CLI prompt runtime.
- [x] Add focused tests for cockpit model-name routing, mismatch rejection, and fallback runtime selection.

## Docs and specs

- [x] Update `config.yaml.example` to native `model`/`providers` configuration.
- [x] Fix invalid YAML and stale routing tables in `docs/configuration.md` and `docs/extending.md`.
- [x] Synchronize the canonical `agent-core-model-resolution` spec and remove unsupported scenarios.
- [x] Update relevant CLI-agent skills with the verified stdin, MCP, timeout, and status-check pitfalls.

## Verification

- [x] Run focused and full agent-core tests, ruff, mypy, and pre-commit gates as available.
- [x] Validate the remediation change and all affected canonical specs.
- [x] Run the external CLI smoke/review matrix with bounded processes and record exit/status evidence.
- [x] Perform a final code/docs/spec/skill stale-reference sweep.
- [x] Commit each owning repository and verify clean status, excluding expected graphify generated changes.
