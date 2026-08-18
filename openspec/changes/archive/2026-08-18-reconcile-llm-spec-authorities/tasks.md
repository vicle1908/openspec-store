## 1. Protocol enum fix (provider-model-profile-resolution)

- [x] 1.1 Apply delta: update "Explicit typed provider protocol" requirement to list `messages`, `openai_chat`, `responses`
- [x] 1.2 Verify the three OpenAI Chat scenarios render correctly in the main spec

## 2. Registry claim correction (provider-model-profile-resolution Purpose)

- [x] 2.1 Edit `openspec/specs/provider-model-profile-resolution/spec.md` Purpose directly: replace "replaces ... the separate packaged `environment-key-registry.json`" with accurate statement that `auth_env`+canonical schema replaced the `api_key_env` YAML field while the registry persists as credential-metadata authority
- [x] 2.2 Confirm `register-custom-provider-credentials` spec remains consistent with the corrected Purpose

## 3. Effort split documentation (agent-core-model-resolution)

- [x] 3.1 Apply delta: add "Provider-specific reasoning effort validation sets" requirement with four scenarios
- [x] 3.2 Cross-check the documented sets against `agent_core/_ai/models.py:53-54` values

## 4. Claude Code authority boundary

- [x] 4.1 Apply delta to `claude-code-provider-routing`: add "Launcher routing and profile resolution own distinct surfaces" requirement
- [x] 4.2 Apply delta to `claude-code-provider-profile-resolution`: add matching authority requirement
- [x] 4.3 Edit `openspec/specs/claude-code-provider-profile-resolution/spec.md` Purpose directly to replace the TBD placeholder

## 4b. Credential spec field/mechanism correction (register-custom-provider-credentials)

- [x] 4b.1 Apply MODIFIED delta: replace `providers.*.api_key_env` references with `providers.*.auth_env` in both requirements
- [x] 4b.2 Replace `credential_entry()` mechanism description with `CredentialResolver.resolve()` over provider-bound route references
- [x] 4b.3 Cross-check against `tdt_core/agent_profile.py` (CredentialAvailability built from `provider.auth_env`; `credential_entry()` has zero callers)

## 5. Validation and archive

- [x] 5.1 Run `openspec validate reconcile-llm-spec-authorities --strict`
- [x] 5.2 Confirm all four main specs read coherently after edits
- [x] 5.3 Archive the change
