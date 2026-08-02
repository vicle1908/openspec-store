#!/usr/bin/env node
/*
 * Inject the PLAYER_STATS object into the deck for the peek panel. Mirrors the
 * inject-images.mjs pattern: replaces content between START/END markers.
 *
 * Reads:  stats-embed.json (name -> { card, ovr, era, gk, attrs })
 * Writes: the deck HTML, injecting the stats object between placeholders.
 *
 * Usage: node inject-stats.mjs
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHANGE_DIR = join(__dirname, "..");
const DECK = join(CHANGE_DIR, "..", "..", "..", "presentations", "efootball-playstyles.html");
const STATS = join(CHANGE_DIR, "stats-embed.json");

const START = "/*__PLAYER_STATS__*/";
const END = "/*__END_PLAYER_STATS__*/";

if (!existsSync(STATS)) {
  console.error("ERROR: stats-embed.json not found. Run gen-stats-embed.mjs first.");
  process.exit(1);
}

const json = readFileSync(STATS, "utf8").trim();
let html = readFileSync(DECK, "utf8");

const startIdx = html.indexOf(START);
const endIdx = html.indexOf(END);
if (startIdx === -1 || endIdx === -1) {
  console.error("ERROR: PLAYER_STATS markers not found in deck. Add them first:");
  console.error(`  const PLAYER_STATS = ${START}{}${END};`);
  process.exit(1);
}

const before = html.slice(0, startIdx + START.length);
const after = html.slice(endIdx);
html = before + json + after;

writeFileSync(DECK, html);
const count = Object.keys(JSON.parse(json)).length;
console.log(`Injected ${count} stat rows into deck (${(json.length / 1024).toFixed(1)}KB).`);
console.log(`Deck size now: ${(html.length / 1024 / 1024).toFixed(2)}MB`);
