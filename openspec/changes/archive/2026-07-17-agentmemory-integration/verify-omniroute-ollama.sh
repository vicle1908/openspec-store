#!/bin/bash
set -euo pipefail

echo "=== OmniRoute + Ollama Config Verification ==="
echo ""

echo "1. Checking OmniRoute LLM..."
# shellcheck source=/dev/null
source "$HOME/.tdt/.env"
RESP=$(curl -s "$OMNIROUTE_URL/chat/completions" \
  -H "Authorization: Bearer $OMNIROUTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"ai/deepseek-v4-pro[1m]","messages":[{"role":"user","content":"Reply with just: OK"}],"max_tokens":10,"stream":false}')
CONTENT=$(echo "$RESP" | python3 -c "import json,sys; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null)
if [ "$CONTENT" != "OK" ]; then
  echo "   FAIL: OmniRoute LLM response: $CONTENT"
  exit 1
fi
echo "   OK: OmniRoute LLM responded correctly"

echo "2. Checking Ollama embedding..."
EMBED=$(curl -s http://localhost:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"nomic-embed-text","prompt":"test"}')
DIM=$(echo "$EMBED" | python3 -c "import json,sys; print(len(json.load(sys.stdin)['embedding']))" 2>/dev/null)
if [ "$DIM" != "768" ]; then
  echo "   FAIL: Embedding dimension $DIM (expected 768)"
  exit 1
fi
echo "   OK: Ollama embedding: ${DIM}-dim"

echo ""
echo "=== ALL CHECKS PASSED ==="
