## 1. omp boundary exclusion

- [x] 1.1 Apply MODIFIED delta to `cli-provider-profile-resolution`: add omp scenario to "Separate runtime boundaries remain explicit"
- [x] 1.2 Confirm the requirement still lists prime-agent and provider-adapter scenarios intact

## 2. Hermes runtime surface statement

- [x] 2.1 Apply ADDED delta to `hermes-moa-configuration`: add "Hermes provider configuration is a separate runtime surface" requirement
- [x] 2.2 Confirm the new requirement is consistent with the existing "Context-window ownership" requirement

## 3. Validation and archive

- [x] 3.1 Run `openspec validate document-llm-runtime-boundaries --strict`
- [x] 3.2 Archive the change
