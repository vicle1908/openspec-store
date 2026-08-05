# Design: Ecosystem Pydantic-Settings Migration

## Architecture

### Current State → Target State

| Current | Target |
|---------|--------|
| config.toml + config.yaml + .env | config.yaml + .env |
| load_tdt_env() + get_env() per field | TDTSettings.load() with BaseSettings |
| 3 secret classifiers | 1 consolidated in config_models.py |

### Source Precedence

```
env vars  >  YAML  >  .env file  >  code defaults
```

## Implementation

### TDTSettings Root Model

```python
class TDTSettings(BaseSettings):
    @classmethod
    def settings_customise_sources(cls, ...):
        yaml_source = YamlConfigSettingsSource(settings_cls=cls, yaml_file=tdt_root()/"config.yaml")
        return (env_settings, yaml_source, dotenv_settings, file_secret_settings)
```

### Migration Script

```python
def migrate_toml_to_yaml():
    # Parse TOML, convert sections, deep merge into YAML, archive TOML
```

## Trade-offs

- **Pro:** Single config file, typed validation, IDE autocomplete
- **Con:** Migration script must be exact, backward-compat shims needed
