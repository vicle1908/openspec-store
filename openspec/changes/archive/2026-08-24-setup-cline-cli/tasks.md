## 1. Pre-flight: Backup and Install

- [x] 1.1 Backup existing Cline config
- [x] 1.2 Backup globalState
- [x] 1.3 Verify Node.js 20+ installed
- [x] 1.4 Install Cline CLI v3.0.57
- [x] 1.5 Verify installation
- [x] 1.6 Run cline doctor

## 2. Configure MCP Router

- [x] 2.1 Create ~/.cline/mcp.json with mcp-router config
- [x] 2.2 Verified: cline config mcp shows mcp-router [stdio]

## 3. Configure cockpit Provider (openai-native, Responses API)

- [x] 3.1 Verify cockpit-cliproxy running
- [x] 3.2 Configure: cline auth -p openai-native -k <key> -m gpt-5.6-luna -b http://localhost:51006/v1
- [x] 3.3 Test end-to-end: responds "OK"
- [x] 3.4 Verify tool calls work

## 4. Configure shopapikey Provider (openai-native, Responses API)

- [x] 4.1 Configure: cline auth -p openai-native -k <key> -m fable-5 -b https://api.phanmemvip.shop/v1
- [x] 4.2 Test end-to-end: responds correctly
- [x] 4.3 Verified Responses API streaming works

## 5. Configure giaoduc Provider (openai-compatible, Chat Completions)

- [x] 5.1 Configure: cline auth -p openai-compatible -k <key> -m Advance -b https://api.giaoduc.online/v1
- [x] 5.2 Test end-to-end: responds "OK"
- [x] 5.3 Verify tool calls work

## 6. Add Shell Launchers to ~/.zshrc

- [x] 6.1 cline_cockpit() — runs cline auth then cline -P openai-native -k <key>
- [x] 6.2 cline_shopapikey() — runs cline auth then cline -P openai-native -k <key>
- [x] 6.3 cline_giaoduc() — runs cline auth then cline -P openai-compatible -k <key>
- [x] 6.4 Verify launchers defined in ~/.zshrc
- [x] 6.5 Test each launcher: all 3 return "OK"

## 7. Validate End-to-End

- [x] 7.1 cockpit provider responds correctly
- [x] 7.2 shopapikey provider responds correctly
- [x] 7.3 giaoduc provider responds correctly
- [x] 7.4 MCP router configured and verified
- [x] 7.5 OpenSpec validation passed
