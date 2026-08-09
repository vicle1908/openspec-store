# Tasks: TDT Config Consumer Alignment

## RED Tests

- [ ] Add test: `_create_runtime_model()` passes behavior settings to model
- [ ] Add test: `create_model()` accepts and forwards `model_settings`
- [ ] Add test: `create_fallback_model()` accepts and forwards `model_settings`
- [ ] Add test: empty/None settings produce no model_settings

## GREEN Implementation

- [ ] Update `create_model()` signature to accept optional `model_settings`
- [ ] Update `create_fallback_model()` signature to accept optional `model_settings`
- [ ] Update `_create_runtime_model()` to extract and pass behavior settings

## Quality Gates

- [ ] All tests pass (uv run pytest)
- [ ] Ruff clean (uv run ruff check)
- [ ] mypy --strict clean
- [ ] OpenSpec specs valid (openspec validate)
