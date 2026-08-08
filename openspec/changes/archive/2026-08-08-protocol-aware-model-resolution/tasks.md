# Tasks: Protocol-Aware Model Resolution

## Task 1: Document protocol routing
- [x] Analyze current proxy factory behavior
- [x] Map model kind prefixes to protocols
- [x] Identify gaps (openai-responses, google native)
- [x] Determine if explicit protocol config is needed

## Task 2: Enhance proxy factory (if needed)
- [x] Test current factory with all supported prefixes
- [ ] Add openai-responses routing (if giaoduc adds support)
- [ ] Add google-native routing (if needed)

## Task 3: Update documentation
- [x] Document model kind prefix → protocol mapping
- [x] Clarify that prefix IS the protocol
- [x] Note giaoduc limitation (no Responses API)

## Task 4: Verify
- [x] Real LLM calls for each supported prefix
- [x] Fallback model works across protocols
