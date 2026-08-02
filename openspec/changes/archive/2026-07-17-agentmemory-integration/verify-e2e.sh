#!/bin/bash
set -euo pipefail

echo "=== Agentmemory E2E Verification (real operations) ==="
echo ""

BASE_URL="${AGENTMEMORY_URL:-http://localhost:3111}"
export AGENTMEMORY_URL="$BASE_URL"

echo "1) Health check..."
curl -sf "$BASE_URL/agentmemory/health" >/dev/null
echo "   OK: health endpoint reachable"

echo "2) MCP tools/list (sanity)..."
node - <<'NODE'
const { spawnSync } = require('node:child_process');
function mcp(method, params) {
  const req = { jsonrpc: '2.0', id: 1, method, params };
  const p = spawnSync('npx', ['-y', '@agentmemory/mcp'], {
    input: JSON.stringify(req) + '\n',
    encoding: 'utf8',
    env: { ...process.env, AGENTMEMORY_URL: process.env.AGENTMEMORY_URL },
  });
  if (p.status !== 0) throw new Error(p.stderr);
  const line = (p.stdout || '').trim().split(/\n+/).pop();
  return JSON.parse(line);
}
const res = mcp('tools/list', {});
const tools = res?.result?.tools || [];
if (tools.length < 53) {
  throw new Error(`expected >=53 tools, got ${tools.length}`);
}
console.log(`   OK: ${tools.length} tools`);
NODE

echo "3) Save -> smart search -> export contains -> governance delete -> verify gone..."
node - <<'NODE'
const { spawnSync } = require('node:child_process');

function call(tool, args) {
  const req = {
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/call',
    params: { name: tool, arguments: args },
  };
  const p = spawnSync('npx', ['-y', '@agentmemory/mcp'], {
    input: JSON.stringify(req) + '\n',
    encoding: 'utf8',
    env: { ...process.env, AGENTMEMORY_URL: process.env.AGENTMEMORY_URL },
  });
  if (p.status !== 0) {
    console.error(p.stderr);
    process.exit(p.status);
  }
  const out = (p.stdout || '').trim().split(/\n+/).pop();
  return JSON.parse(out);
}

function parseTextPayload(res) {
  const t = res?.result?.content?.[0]?.text;
  if (!t) return null;
  try {
    return JSON.parse(t);
  } catch {
    return t;
  }
}

const tag = `tdt-agentmemory-e2e-${new Date().toISOString().replace(/[:.]/g, '-')}`;
const content = `E2E verification memory for ${tag}. Real operation test.`;

const saveRes = call('memory_save', { content, type: 'fact', concepts: tag });
const saveObj = parseTextPayload(saveRes);
const memId = saveObj?.memory?.id;
if (!memId) {
  console.error('save response:', JSON.stringify(saveRes, null, 2));
  throw new Error('could not determine memory id from memory_save response');
}

const searchRes = call('memory_smart_search', { query: tag, limit: 5 });
const searchObj = parseTextPayload(searchRes);
const searchText = JSON.stringify(searchObj);
if (!searchText.includes(tag)) {
  throw new Error('smart search did not return the saved memory');
}

const exportRes = call('memory_export', {});
const exportObj = parseTextPayload(exportRes);
const exportText = JSON.stringify(exportObj);
if (!exportText.includes(tag)) {
  throw new Error('export did not include the saved memory');
}

// IMPORTANT: memory_governance_delete schema takes memoryIds as a comma-separated string.
const delRes = call('memory_governance_delete', { memoryIds: memId, reason: 'e2e verification cleanup' });
const delObj = parseTextPayload(delRes);
if (!delObj || delObj.success !== true) {
  console.error('delete response:', JSON.stringify(delRes, null, 2));
  throw new Error('governance delete failed');
}

const afterRes = call('memory_smart_search', { query: tag, limit: 5 });
const afterObj = parseTextPayload(afterRes);
const afterText = JSON.stringify(afterObj);
if (afterText.includes(content)) {
  throw new Error('deleted memory still appears in search results');
}

console.log(`   OK: saved+found+exported+deleted memory id=${memId}`);
NODE

echo "4) Slots lifecycle (create/get/append/replace/delete)..."
node - <<'NODE'
const { spawnSync } = require('node:child_process');
function call(tool, args) {
  const req = { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: tool, arguments: args } };
  const p = spawnSync('npx', ['-y', '@agentmemory/mcp'], {
    input: JSON.stringify(req) + '\n',
    encoding: 'utf8',
    env: { ...process.env, AGENTMEMORY_URL: process.env.AGENTMEMORY_URL },
  });
  if (p.status !== 0) throw new Error(p.stderr);
  const out = (p.stdout || '').trim().split(/\n+/).pop();
  return JSON.parse(out);
}
function parse(res) {
  const t = res?.result?.content?.[0]?.text;
  try { return JSON.parse(t); } catch { return t; }
}

const label = `e2e_slot_${Date.now()}`;

parse(call('memory_slot_create', { label, scope: 'project', description: 'e2e temp slot', content: 'alpha', pinned: 'false', sizeLimit: 1000 }));
const g1 = parse(call('memory_slot_get', { label }));
if (!g1?.slot?.content?.includes('alpha')) throw new Error('slot get failed');

parse(call('memory_slot_append', { label, text: ' beta' }));
const g2 = parse(call('memory_slot_get', { label }));
if (!g2?.slot?.content?.includes('beta')) throw new Error('slot append failed');

parse(call('memory_slot_replace', { label, content: 'gamma' }));
const g3 = parse(call('memory_slot_get', { label }));
if (g3?.slot?.content !== 'gamma') throw new Error('slot replace failed');

parse(call('memory_slot_delete', { label }));
const g4 = parse(call('memory_slot_get', { label }));
if (g4?.success !== false) throw new Error('slot should not exist after delete');

console.log('   OK: slots lifecycle complete');
NODE

echo ""
echo "=== ALL E2E CHECKS PASSED ==="

