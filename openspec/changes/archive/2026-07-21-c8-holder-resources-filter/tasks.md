# Tasks: C8 holder.itemView.resources Filter

## 1. Implementation

- [ ] 1.1 Add `suppress_c8_holder_view_resources` to `code-daily-scan/src/code_daily_scan/plugins/android/post_filters.py`
- [ ] 1.2 Chain with existing `suppress_c8_lifecycle_safe` in combined filter
- [ ] 1.3 Register in `ANDROID_RULE_POST_FILTERS` under key `"C8"`

## 2. Validation

- [ ] 2.1 Run full test suite
- [ ] 2.2 Run `ruff check`, `ruff format --check`, `mypy --strict`
- [ ] 2.3 Run Android scan and verify C8 findings drop by 3
- [ ] 2.4 Spot-check 3 `holder.itemView.resources` findings are suppressed

## 3. Deploy & Archive

- [ ] 3.1 Commit changes
- [ ] 3.2 Rebuild scheduler
- [ ] 3.3 Run live review on MR !23873 to verify parity
- [ ] 3.4 Archive change
