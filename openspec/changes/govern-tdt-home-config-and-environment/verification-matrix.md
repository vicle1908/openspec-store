# Requirement-to-Test-to-Source Matrix

## MODIFIED Requirements

### `load_tdt_env()` honours `TDT_HOME` when set

| Scenario | Test File | Test Method | Source Module |
|---|---|---|---|
| TDT_HOME set | `test_profiles_and_config.py` | `test_unset_profile_defaults_to_development` | `env.py:load_tdt_env()` |
| TDT_HOME unset | `test_profiles_and_config.py` | `test_unset_profile_defaults_to_development` | `env.py:load_tdt_env()` |
| TDT_HOME empty | `test_profiles_and_config.py` | `test_empty_profile_defaults_to_development` | `env.py:load_tdt_env()` |
| Environment changes after import | `test_profiles_and_config.py` | `test_profile_resolved_on_each_call` | `env.py:get_profile()` |

### Tilde expansion is applied

| Scenario | Test File | Test Method | Source Module |
|---|---|---|---|
| Tilde-prefixed TDT_HOME | `test_paths_typed.py` | `test_tilde_expansion` | `paths.py:tdt_root()` |
| Relative TDT_HOME | `test_paths_typed.py` | `test_custom_root` | `paths.py:tdt_root()` |
| Runtime filename with extension | `test_paths_typed.py` | `test_filename_with_extension` | `paths.py:_validate_filename()` |

### Local `.env` override behaviour is preserved

| Scenario | Test File | Test Method | Source Module |
|---|---|---|---|
| Environment profile is unset | `test_env_profiles.py` | `test_development_loads_local_env` | `env.py:_do_load()` |
| Local .env exists (development) | `test_env_profiles.py` | `test_development_loads_local_env` | `env.py:_do_load()` |
| Local .env exists (production) | `test_env_profiles.py` | `test_production_skips_local_env` | `env.py:_do_load()` |
| Unknown environment profile | `test_env_profiles.py` | `test_unknown_profile_fails` | `env.py:_select_profile()` |

### Idempotency is preserved

| Scenario | Test File | Test Method | Source Module |
|---|---|---|---|
| Repeated calls | `test_profiles_and_config.py` | `test_concurrent_load_no_race` | `env.py:load_tdt_env()` |
| Isolated test context | `test_env_profiles.py` | `test_resets_loader_state` | `env.py:EnvironmentIsolation` |
| Concurrent first load | `test_env_profiles.py` | `test_concurrent_load_completes_once` | `env.py:load_tdt_env()` |
| Retry after failed load | `test_profiles_and_config.py` | `test_reset_allows_reloading` | `env.py:reset_env_state()` |

## ADDED Requirements

### Canonical runtime paths remain contained

| Scenario | Test File | Test Method | Source Module |
|---|---|---|---|
| Consumer requests runtime path | `test_paths_typed.py` | `test_config_path_yaml`, `test_credentials_path`, etc. | `paths.py:tdt_config_path()` etc. |
| Descendant escapes root | `test_paths_typed.py` | `test_unsafe_app_name_rejected`, `test_unsafe_filename_rejected` | `paths.py:_validate_component()` |
| Descendant ancestor is replaced | `test_fs_kernel.py` | `test_root_anchoring_*` | `fs_kernel.py:RootAnchor` |
| Unsupported secure mutation primitive | `test_fs_kernel.py` | `test_platform_capabilities_*` | `fs_kernel.py:platform_capabilities()` |
| First-run root creation | `test_fs_kernel.py` | `test_bootstrap_*` | `fs_kernel.py:RootAnchor.bootstrap()` |
| Standalone harness isolation | DEFERRED | — | Consumer migration (Phase 2) |

### Provider-owned private mutations fail closed

| Scenario | Test File | Test Method | Source Module |
|---|---|---|---|
| Symlink substitution | `test_fs_kernel.py` | `test_symlink_detection_*` | `fs_kernel.py:_stable_link_snapshot()` |
| Hard-link policy | `test_fs_kernel.py` | `test_file_handle_*` | `fs_kernel.py:DirectoryHandle.open_file()` |
| Object-type policy | `test_fs_kernel.py` | `test_verify_directory_*` | `fs_kernel.py:_verify_directory()` |
| Permission policy | `test_fs_kernel.py` | `test_bootstrap_mode_*` | `fs_kernel.py:RootAnchor.bootstrap()` |
| Descriptor cleanup | `test_fs_kernel.py` | `test_anchor_close_*` | `fs_kernel.py:RootAnchor.close()` |
| Concurrent directory creation | `test_fs_kernel.py` | `test_bootstrap_*` | `fs_kernel.py:RootAnchor.bootstrap()` |

### Typed configuration uses secret references

| Scenario | Test File | Test Method | Source Module |
|---|---|---|---|
| Valid reference accepted | `test_profiles_and_config.py` | `test_valid_reference_accepted` | `config_loader.py:validate_env_reference()` |
| Missing dollar rejected | `test_profiles_and_config.py` | `test_missing_dollar_rejected` | `config_loader.py:validate_env_reference()` |
| Partial reference rejected | `test_profiles_and_config.py` | `test_partial_reference_rejected` | `config_loader.py:validate_env_reference()` |
| Lowercase var rejected | `test_profiles_and_config.py` | `test_lowercase_var_rejected` | `config_loader.py:validate_env_reference()` |
| Empty var name rejected | `test_profiles_and_config.py` | `test_empty_var_name_rejected` | `config_loader.py:validate_env_reference()` |
| Secret key classified | `test_profiles_and_config.py` | `test_secret_key_detected` | `config_loader.py:classify_secret_key()` |
| Non-secret key not classified | `test_profiles_and_config.py` | `test_non_secret_key_not_classified` | `config_loader.py:classify_secret_key()` |
| Duplicate scheduler setting | `test_config_ownership.py` | `test_equal_duplicate`, `test_unequal_duplicate` | `config_ownership.py:detect_duplicates()` |
| Scheduler duplicate migration | `test_config_ownership.py` | `test_literal_secret_in_governed_key` | `config_ownership.py:validate_governed_config()` |
| Scheduler consumes governed config | `test_config_ownership.py` | `test_secret_env_reference_accepted` | `config_ownership.py:validate_governed_config()` |

### Configuration diagnostics are redacted and reproducible

| Scenario | Test File | Test Method | Source Module |
|---|---|---|---|
| Healthy alternate root | `test_doctor.py` | `test_doctor_healthy_root` | `cli.py:doctor()` |
| Multiple findings | `test_doctor.py` | `test_doctor_finds_issues` | `cli.py:doctor()` |
| Broken credential symlink | `test_doctor.py` | `test_doctor_broken_symlink` | `cli.py:doctor()` |
| Config ambiguity | `test_doctor.py` | `test_doctor_config_ambiguity` | `cli.py:doctor()` |
| JSON output | `test_cli.py` | `test_config_doctor_exists` | `cli.py:doctor()` |

### Packaged provider contracts are mandatory

| Scenario | Test File | Test Method | Source Module |
|---|---|---|---|
| Registry loaded | `test_source_registry.py` | `test_load_provider_registry` | `source_registry.py:load_provider_registry()` |
| 15 participants validated | `test_source_registry.py` | `test_registry_closed_world` | `source_registry.py:ProviderRegistry` |
| Missing registry fails | `test_source_registry.py` | `test_missing_registry_fails` | `source_registry.py:_load_provider_registry_neutral()` |
| Repository discovery | `test_source_registry.py` | `test_discover_manifests` | `source_registry.py:discover_repository_manifests()` |
| Missing repository reported | `test_source_registry.py` | `test_missing_repository` | `source_registry.py:discover_repository_manifests()` |
| Identity mismatch fails | `test_source_registry.py` | `test_identity_mismatch` | `source_registry.py:discover_repository_manifests()` |

### Provider artifact is internally consistent

| Scenario | Test File | Test Method | Source Module |
|---|---|---|---|
| Installed provider artifact | DEFERRED | Task 3.11 (build + wheelhouse verification) | — |
| tdt --help without extras | `test_cli.py` | `test_help_contains_version` | `cli.py:app` |
| Installed-wheel doctor | `test_doctor.py` | `test_doctor_healthy_root` | `cli.py:doctor()` |

## Deferred Scenarios (Phase 2)

- Standalone harness isolation (consumer migration)
- Consumer-first rollback (consumer migration)
- Clean consumer install from wheelhouse (build verification)
- Live-home migration (operator migration)
