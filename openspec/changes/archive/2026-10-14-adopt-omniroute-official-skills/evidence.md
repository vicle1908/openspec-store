# Verification Evidence: adopt-omniroute-official-skills

Executed: 2026-10-14  
Harness: Antigravity / OpenSpec Store  
Scope: OmniRoute official skills adoption, management authorization scopes, and shell environment normalization.

---

## 1. Skill Catalog Materialization Evidence

### Command
```bash
ls -d ~/.agents/skills/omni-* ~/.agents/skills/cli-* ~/.agents/skills/config-codex-cli | wc -l
```
### Result
```text
45
```
- Total 45 official skills installed globally via `npx skills add /Users/androidteam/Omniroute -g --all`.
- Symlinked into all configured agent profiles (e.g. `~/.claude/skills/omni-models -> ../../.agents/skills/omni-models`).

---

## 2. OmniRoute Management Authorization Evidence

### SQLite Scopes Inspection
```bash
docker exec omniroute node -e "
const Database = require('better-sqlite3');
const db = new Database('/app/data/storage.sqlite', { readonly: true });
console.log(db.prepare('SELECT id, name, scopes, is_active FROM api_keys WHERE name = ?').get('mac-mini-1'));
"
```
### Result
```json
{
  "id": "6a72d8ab-88db-4d49-973b-864c6cbdace5",
  "name": "mac-mini-1",
  "scopes": "[\"self:usage\",\"manage\",\"admin\"]",
  "is_active": 1
}
```

### Unauthenticated Request Rejection
```bash
curl -s -w "\nHTTP_STATUS:%{http_code}\n" http://127.0.0.1:20128/api/providers | tail -n 2
```
### Result
```text
{"error":{"code":"AUTH_001","message":"Authentication required","correlation_id":"52fd50ae-0551-492d-8343-bd16154beb21"}}
HTTP_STATUS:401
```

### Authenticated Request Acceptance
```bash
curl -s -w "\nHTTP_STATUS:%{http_code}\n" -H "Authorization: Bearer $(~/.claude/helpers/omniroute-key.sh)" http://127.0.0.1:20128/api/monitoring/health
```
### Result
```json
{"status":"healthy","setupComplete":true}
HTTP_STATUS:200
```

---

## 3. Shell Environment Normalization Evidence

### Non-Interactive Subshell
```bash
zsh -c 'echo "OMNIROUTE_URL=$OMNIROUTE_URL"; echo "OMNIROUTE_BASE_URL=$OMNIROUTE_BASE_URL"; [ "$OMNIROUTE_KEY" = "$OMNIROUTE_API_KEY" ] && echo "Key matches"'
```
### Result
```text
OMNIROUTE_URL=http://localhost:20128
OMNIROUTE_BASE_URL=http://localhost:20128
Key matches
```

### Interactive Subshell
```bash
zsh -i -c 'echo "OMNIROUTE_BASE_URL=$OMNIROUTE_BASE_URL"; echo "COPILOT_PROVIDER_BASE_URL=$COPILOT_PROVIDER_BASE_URL"'
```
### Result
```text
OMNIROUTE_BASE_URL=http://localhost:20128
COPILOT_PROVIDER_BASE_URL=http://localhost:20128/v1
```

---

## 4. Multi-Skill Live Execution Evidence

```bash
zsh -c '
curl -s -H "Authorization: Bearer $OMNIROUTE_KEY" "$OMNIROUTE_URL/v1/models" | jq ".data | length"
curl -s -H "Authorization: Bearer $OMNIROUTE_KEY" "$OMNIROUTE_URL/api/providers" | jq ".connections | length"
curl -s -H "Authorization: Bearer $OMNIROUTE_KEY" "$OMNIROUTE_URL/api/combos" | jq ".combos | length"
curl -s -X POST -H "Authorization: Bearer $OMNIROUTE_KEY" -H "Content-Type: application/json" \
  "$OMNIROUTE_URL/v1/chat/completions" \
  -d "{\"model\": \"gemini-3.8-flash-high\", \"messages\": [{\"role\": \"user\", \"content\": \"Respond with: LIVE_VERIFIED\"}]}" \
  | jq -r ".choices[0].message.content"
'
```
### Result
- Model catalog count: **1,166 models**
- Upstream connections: **32 connections** (26 active)
- Fallback combos: **3 combos** (`gemini-3.8-flash-high`, `phanmemvip`, `claude-opus-5.5`)
- Live prompt completion: `"LIVE_VERIFIED"`
